from typing import Optional
from pypdf import PdfReader
import asyncio
import os


async def extract_text_from_file(path:str) -> str:
    
    """
    Detect file type by extension and extract text.
    Supports .pdf and .txt only
    """

    if path.lower().endswith(".txt"):

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _read_txt_sync, path)
    if path.lower().endswith(".pdf"):
        return await asyncio.get_event_loop().run_in_executor(None, _read_pdf_sync, path)
    
    return ""



def _read_txt_sync(path: str) -> str:
    with open(path, "r",encoding="utf-8", errors="ignore") as f:
        return f.read()
    


def _read_pdf_sync(path: str) -> str:
    try:
        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text()or "")
        return "\n".join(texts)
    except Exception:
        return ""