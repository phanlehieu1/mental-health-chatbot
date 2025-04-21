import os
from typing import List, Dict, Any, AsyncGenerator
from dotenv import load_dotenv
from openai import OpenAI
from app.models.schemas import MessageHistory

load_dotenv()

# Thay đổi cấu hình để sử dụng Together AI
client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    # Base URL của Together AI
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


async def generate_response(
    message: str,
    history: List[MessageHistory],
    documents: List[Dict[str, Any]]
) -> str:
    """
    Tạo phản hồi cho người dùng dựa trên tin nhắn, lịch sử và tài liệu liên quan
    """
    # In ra để debug
    print(f"Lịch sử có {len(history)} tin nhắn")

    # Tạo context từ tài liệu tương tự
    context = "\n\n".join([doc["text"]
                          for doc in documents]) if documents else ""

    # Tạo system prompt
    system_prompt = f"""Bạn là Trầm một trợ lý hỗ trợ tinh thần, thấu hiểu và đồng cảm. 
    Nhiệm vụ của bạn là lắng nghe, cung cấp sự hỗ trợ và lời khuyên hữu ích cho người dùng.
    
    Hãy sử dụng thông tin trong tài liệu sau để trả lời nếu phù hợp:
    
    {context}
    
    Lời khuyên của bạn nên dựa trên các phương pháp khoa học về sức khỏe tâm thần, nhưng diễn đạt một cách thân thiện.
    Nếu người dùng có dấu hiệu của vấn đề tâm lý nghiêm trọng, hãy nhẹ nhàng khuyên họ tìm đến chuyên gia.
    Trả lời bằng tiếng Việt, với giọng điệu thân thiện, đồng cảm và tích cực."""

    # Chuẩn bị messages cho API
    messages = [{"role": "system", "content": system_prompt}]

    # Thêm lịch sử trò chuyện - đảm bảo sử dụng tất cả lịch sử
    if history:
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

    # Thêm tin nhắn của người dùng
    messages.append({"role": "user", "content": message})

    try:
        # Gọi API của LLM
        response = client.chat.completions.create(
            model="gemini-2.5-pro-exp-03-25",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn. Vui lòng thử lại sau."


async def generate_stream_response(
    message: str,
    history: List[MessageHistory],
    documents: List[Dict[str, Any]]
) -> AsyncGenerator[str, None]:
    """
    Tạo phản hồi streaming cho người dùng
    """
    # Tạo context từ tài liệu tương tự
    context = "\n\n".join([doc["text"]
                          for doc in documents]) if documents else ""

    # Tạo system prompt
    system_prompt = f"""Bạn là Trầm một trợ lý hỗ trợ tinh thần, thấu hiểu và đồng cảm. 
    Nhiệm vụ của bạn là lắng nghe, cung cấp sự hỗ trợ và lời khuyên hữu ích cho người dùng.
    
    Hãy sử dụng thông tin trong tài liệu sau để trả lời nếu phù hợp:
    
    {context}
    
    Lời khuyên của bạn nên dựa trên các phương pháp khoa học về sức khỏe tâm thần, nhưng diễn đạt một cách thân thiện.
    Nếu người dùng có dấu hiệu của vấn đề tâm lý nghiêm trọng, hãy nhẹ nhàng khuyên họ tìm đến chuyên gia.
    Trả lời bằng tiếng Việt, với giọng điệu thân thiện, đồng cảm và tích cực."""

    # Chuẩn bị messages cho API
    messages = [{"role": "system", "content": system_prompt}]

    # Thêm lịch sử trò chuyện
    if history:
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

    # Thêm tin nhắn của người dùng
    messages.append({"role": "user", "content": message})

    try:
        # Gọi API của LLM với chế độ stream
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            stream=True  # Bật chế độ stream
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield f"data: {chunk.choices[0].delta.content}\n\n"

        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"Error generating stream response: {e}")
        yield "data: Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn.\n\n"
        yield "data: [DONE]\n\n"
