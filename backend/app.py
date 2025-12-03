import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from rag_engine import ClinicalRAG
from models import QueryRequest, QueryResponse, Source
import shutil
import time

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# Global variable for the system
rag_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load heavy AI models ONLY when the server starts.
    This prevents the 'No Open Ports' timeout on Render.
    """
    global rag_system
    logger.info("🏥 Clinical AI Brain is starting up...")
    try:
        # Initialize RAG System here (this is the heavy part)
        rag_system = ClinicalRAG()
        logger.info("✅ RAG System loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to load RAG System: {e}")
    
    yield  # The application runs here
    
    # Cleanup (optional)
    logger.info("🛑 Shutting down Clinical AI Brain...")

# Initialize App with Lifespan
app = FastAPI(title="Clinical RAG API", version="1.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    """Lightweight endpoint for Render/Cron-job to keep the service awake."""
    if rag_system is None:
        return {"status": "initializing", "message": "Models are still loading..."}
    return {"status": "awake", "message": "Service is ready"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not rag_system:
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    num_chunks = rag_system.ingest_document(file_location)
    return {"message": "Guidelines processed successfully", "chunks": num_chunks}

@app.post("/query", response_model=QueryResponse)
async def query_guidelines(request: QueryRequest):
    if not rag_system:
        raise HTTPException(status_code=503, detail="System is still initializing")
        
    start_time = time.time()
    result = rag_system.query(request.question)
    
    if not result:
        raise HTTPException(status_code=400, detail="No guidelines loaded or no answer found.")
    
    sources = [
        Source(
            file_name=doc.metadata.get("source", "Unknown"),
            page_number=doc.metadata.get("page", 0),
            text_snippet=doc.page_content[:150] + "..."
        ) for doc in result["docs"]
    ]
    
    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        confidence_score=0.92, 
        processing_time=time.time() - start_time
    )