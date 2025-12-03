from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    question: str = Field(..., description="The user's question about clinical guidelines")
    session_id: str = Field(default="default_session", description="Unique session identifier")

class Source(BaseModel):
    """Model representing a source document or snippet."""
    file_name: str = Field(..., description="Name of the source file")
    page_number: int = Field(..., description="Page number in the source document (1-based)")
    text_snippet: str = Field(..., description="Relevant text snippet from the source")

class QueryResponse(BaseModel):
    """Response model for query results."""
    answer: str = Field(..., description="Generated answer to the query")
    sources: List[Source] = Field(..., description="List of sources used to generate the answer")
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confidence score of the answer (0.0 to 1.0)"
    )
    processing_time: float = Field(..., description="Time taken to process the query in seconds")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of the response in ISO format"
    )

class HealthCheck(BaseModel):
    """Health check response model."""
    status: str = Field("healthy", description="Service status")
    version: str = Field("1.0.0", description="API version")
    model: str = Field("gemini-flash-lite-latest", description="Currently active LLM model")
