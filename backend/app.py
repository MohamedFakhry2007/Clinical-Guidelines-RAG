from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import ClinicalRAG
from models import QueryRequest, QueryResponse, Source
import time
import shutil
import os

app = FastAPI(title="Clinical RAG API", version="1.0")

# CORS middleware to allow frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = ClinicalRAG()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Endpoint for the Frontend to upload PDFs."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    file_location = f"uploads/{file.filename}"
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        num_chunks = rag_system.ingest_document(file_location)
        return {"message": "Guidelines processed successfully", "chunks": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_guidelines(request: QueryRequest):
    start_time = time.time()
    
    try:
        result = rag_system.query(request.question)
        if not result:
            raise HTTPException(status_code=400, detail="No guidelines loaded. Please upload PDF files first.")
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Map sources for the UI
        sources = [
            Source(
                file_name=os.path.basename(doc.metadata.get("source", "Unknown")),
                page_number=doc.metadata.get("page", 0) + 1,  # Convert to 1-based page numbering
                text_snippet=doc.page_content[:150] + ("..." if len(doc.page_content) > 150 else "")
            ) for doc in result["docs"]
        ]
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            confidence_score=result.get("confidence_score", 0.9),  # Default to 0.9 if not provided
            processing_time=process_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for monitoring and load balancing."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "rag_initialized": hasattr(rag_system, 'vector_db')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
