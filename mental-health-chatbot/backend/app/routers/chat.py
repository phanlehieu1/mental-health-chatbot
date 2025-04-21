from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, AsyncGenerator
from app.models.schemas import ChatRequest, ChatResponse
from app.services.embedding import get_embedding
from app.services.retrieval import get_similar_documents
from app.services.llm import generate_response, generate_stream_response

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # In ra lịch sử nhận được để debug
        print(f"Nhận được {len(request.history)} tin nhắn từ lịch sử")

        # Tạo embedding cho tin nhắn người dùng
        embedding = get_embedding(request.message)

        # Truy xuất tài liệu tương tự
        docs = await get_similar_documents(embedding)

        # Tạo phản hồi với LLM, truyền toàn bộ lịch sử
        response = await generate_response(request.message, request.history, docs)

        return ChatResponse(response=response)
    except Exception as e:
        print(f"Lỗi xử lý tin nhắn: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    try:
        # Tạo embedding cho tin nhắn người dùng
        embedding = get_embedding(request.message)

        # Truy xuất tài liệu tương tự
        docs = await get_similar_documents(embedding)

        # Trả về streaming response
        return StreamingResponse(
            generate_stream_response(request.message, request.history, docs),
            media_type="text/event-stream"
        )
    except Exception as e:
        print(f"Lỗi xử lý tin nhắn stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))
