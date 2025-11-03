
##  Installation

1. **Clone the repository**

   git clone https://github.com/prajwalmaka/Backend.git
   cd Backend


2. **Create virtual environment**

   python -m venv venv
   # Windows:


3. **Install dependencies**

   pip install -r requirements.txt


4. **Set up environment variables**

   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   DATABASE_URL=sqlite:///./backend.db
   REDIS_URL=redis://localhost:6379


5. **Run the application**

   uvicorn main:app --reload --host 0.0.0.0 --port 8000


## API Documentation

Once running, access the interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- \`POST /ingest/\` - Upload and process documents
- \`POST /rag/query/\` - Query the RAG system
- \`GET /rag/documents/\` - List ingested documents

##  Configuration

### Vector Store Setup
The application supports multiple vector stores:
- **ChromaDB**: Local vector store (default)
- **Pinecone**: Cloud vector store (configure via environment variables)

### Embedding Models
- Default: OpenAI embeddings
- Configurable via services/embeddings.py


## Testing
Run the simple test application:
python simple_app.py


##  Author

**Prajwal Maka**
- GitHub: [@prajwalmaka](https://github.com/prajwalmaka)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- LangChain for RAG pipeline components
- OpenAI for embedding models
"@ > README.md
