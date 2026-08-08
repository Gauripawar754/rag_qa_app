from pydantic import BaseModel
from typing import List, Dict, Any


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    total_chunks: int


class AskRequest(BaseModel):
    document_id: str
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    llm_model: str
    embedding_model: str