
import asyncio
import sys
import os

# Add current directory to path to import our modules
sys.path.append('.')

from services.embeddings import generate_embeddings
from services.vectorstore_pinecone import PineconeVectorStore
from services.chunker import chunk_by_paragraphs

async def test_embeddings():
    """Test if embeddings are generated correctly"""
    print("🔍 Testing Embeddings Generation...")
    
    # Test texts
    test_texts = [
        "This is a test document about artificial intelligence.",
        "Machine learning is a subset of AI.",
        "Python programming language is used for data science.",
        "FastAPI is a modern web framework for Python."
    ]
    
    try:
        # Generate embeddings
        embeddings = await generate_embeddings(test_texts)
        
        print(f"✅ Successfully generated embeddings for {len(test_texts)} texts")
        print(f"📊 Number of embeddings: {len(embeddings)}")
        print(f"🔢 Embedding dimensions: {len(embeddings[0]) if embeddings else 0}")
        print(f"📐 First embedding sample: {embeddings[0][:5]}...")  # Show first 5 values
        
        return embeddings
        
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return None

async def test_pinecone_connection():
    """Test Pinecone connection and index"""
    print("\n🔍 Testing Pinecone Connection...")
    
    try:
        vectorstore = PineconeVectorStore()
        print("✅ Pinecone connection successful")
        return vectorstore
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return None

async def test_vector_operations():
    """Test complete vector operations pipeline"""
    print("\n🔍 Testing Vector Operations Pipeline...")
    
    # Sample document
    sample_document = """
    Artificial Intelligence (AI) is intelligence demonstrated by machines.
    Machine Learning (ML) is a subset of AI that focuses on algorithms.
    Deep Learning uses neural networks with multiple layers.
    Natural Language Processing (NLP) helps computers understand human language.
    """
    
    try:
        # Step 1: Chunk the document
        chunks = chunk_by_paragraphs(sample_document)
        print(f"✅ Document chunking: {len(chunks)} chunks created")
        
        # Step 2: Generate embeddings
        embeddings = await generate_embeddings(chunks)
        print(f"✅ Embeddings generated: {len(embeddings)} vectors")
        
        # Step 3: Test with vector store
        vectorstore = PineconeVectorStore()
        
        # Create test metadata and IDs
        test_metadata = [{"filename": "test_doc.txt", "chunk_index": i, "content": chunks[i]} for i in range(len(chunks))]
        test_ids = [f"test_{i}" for i in range(len(chunks))]
        
        # Step 4: Add vectors to Pinecone
        await vectorstore.add_vectors(embeddings, test_metadata, test_ids)
        print("✅ Vectors successfully added to Pinecone")
        
        # Step 5: Test query
        query_text = "What is machine learning?"
        query_embedding = await generate_embeddings([query_text])
        results = await vectorstore.query(query_embedding[0], top_k=2)
        
        print(f"✅ Query successful: Found {len(results)} results")
        for i, result in enumerate(results):
            print(f"   Result {i+1}: {result.get('content', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector operations test failed: {e}")
        return False

async def test_similarity_search():
    """Test semantic similarity search"""
    print("\n🔍 Testing Similarity Search...")
    
    test_queries = [
        "artificial intelligence",
        "neural networks", 
        "computer programming",
        "web frameworks"
    ]
    
    try:
        vectorstore = PineconeVectorStore()
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            query_embedding = await generate_embeddings([query])
            results = await vectorstore.query(query_embedding[0], top_k=1)
            
            if results:
                print(f"   ✅ Found match: {results[0].get('content', '')[:80]}...")
            else:
                print("   ❌ No matches found")
                
        return True
        
    except Exception as e:
        print(f"❌ Similarity search test failed: {e}")
        return False

async def run_all_tests():
    """Run all vector tests"""
    print("🚀 Starting Vector Store Tests...")
    print("=" * 50)
    
    # Test 1: Embeddings
    embeddings = await test_embeddings()
    
    # Test 2: Pinecone Connection
    vectorstore = await test_pinecone_connection()
    
    # Test 3: Vector Operations
    operations_ok = await test_vector_operations()
    
    # Test 4: Similarity Search (only if operations were successful)
    if operations_ok:
        await test_similarity_search()
    
    print("\n" + "=" * 50)
    print("🎯 Vector Testing Complete!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
