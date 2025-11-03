from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
import aiofiles
import os
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from services.text_extractor import extract_text_from_file
from services.chunker import chunk_by_paragraphs, chunk_by_size
from services.embeddings import generate_embeddings
from services.vectorstore_pinecone import PineconeVectorStore
from models import Document
from database import get_db

vectorstore = PineconeVectorStore()
router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunk_strategy: str = Form("paragraph"),
    chunk_size: Optional[int] = Form(1000),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Upload a .pdf or .txt file, extract text, chunk it, and store in vector database + SQL.
    chunk_strategy: 'paragraph' or 'fixed'
    chunk_size: integer number of characters (used for 'fixed' strategy)
    """
    filename = file.filename.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    tmp_dir = "tmp_uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    saved_path = os.path.join(tmp_dir, file.filename)

    try:
        # Save uploaded file
        async with aiofiles.open(saved_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
            file_size = len(content)

        # Extract text
        text = await extract_text_from_file(saved_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")

        # Chunking
        if chunk_strategy == "paragraph":
            chunks = chunk_by_paragraphs(text)
        elif chunk_strategy == "fixed":
            chunks = chunk_by_size(text, size=chunk_size)
        else:
            raise HTTPException(status_code=400, detail="Unknown chunk strategy. Use 'paragraph' or 'fixed'")

        # Store vectors in Pinecone
        if chunks:
            ids = [str(uuid.uuid4()) for _ in chunks]
            embeddings = await generate_embeddings(chunks)
            metadata_list = [
                {
                    "filename": file.filename,
                    "chunk_index": i,
                    "content": chunks[i],
                    "chunk_strategy": chunk_strategy,
                    "chunk_size": chunk_size if chunk_strategy == "fixed" else 0
                }
                for i in range(len(chunks))
            ]
            await vectorstore.add_vectors(embeddings, metadata_list, ids)

        # Store document metadata in SQL
        document = Document(
            filename=file.filename,
            file_size=file_size,
            text_length=len(text),
            num_chunks=len(chunks),
            chunk_strategy=chunk_strategy,
            chunk_size=chunk_size,
            document_metadata={
                "original_filename": file.filename,
                "content_preview": text[:200] + "..." if len(text) > 200 else text
            }
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        return {
            "document_id": str(document.id),
            "filename": document.filename,
            "file_size": document.file_size,
            "text_length": document.text_length,
            "num_chunks": document.num_chunks,
            "chunk_strategy": document.chunk_strategy,
            "chunk_size": document.chunk_size,
            "document_metadata": document.document_metadata,
            "message": "Document successfully processed and stored"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        if os.path.exists(saved_path):
            os.remove(saved_path)


@router.get("/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10
) -> dict:
    from sqlalchemy import select
    from sqlalchemy.sql import func

    try:
        total_count_result = await db.execute(select(func.count(Document.id)))
        total_count = total_count_result.scalar()

        documents_result = await db.execute(
            select(Document)
            .order_by(Document.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        documents = documents_result.scalars().all()

        return {
            "documents": [
                {
                    "id": str(doc.id),
                    "filename": doc.filename,
                    "file_size": doc.file_size,
                    "text_length": doc.text_length,
                    "num_chunks": doc.num_chunks,
                    "chunk_strategy": doc.chunk_strategy,
                    "chunk_size": doc.chunk_size,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "document_metadata": doc.document_metadata
                }
                for doc in documents
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    from sqlalchemy import select

    try:
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "document_id": str(document.id),
            "filename": document.filename,
            "file_size": document.file_size,
            "text_length": document.text_length,
            "num_chunks": document.num_chunks,
            "chunk_strategy": document.chunk_strategy,
            "chunk_size": document.chunk_size,
            "uploaded_at": document.uploaded_at.isoformat(),
            "document_metadata": document.document_metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    from sqlalchemy import select, delete

    try:
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        await db.execute(delete(Document).where(Document.id == document_id))
        await db.commit()

        return {
            "message": "Document metadata deleted successfully",
            "document_id": str(document.id),
            "filename": document.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
