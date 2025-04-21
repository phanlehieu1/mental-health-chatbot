import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from app.services.faiss_service import faiss_service

load_dotenv()


async def get_similar_documents(embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Truy xuất các tài liệu tương tự dựa trên embedding vector sử dụng FAISS
    """
    try:
        documents = faiss_service.search(embedding, top_k)
        return documents
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []
