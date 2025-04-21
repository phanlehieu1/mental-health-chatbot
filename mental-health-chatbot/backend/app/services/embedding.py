import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Thay đổi cấu hình để sử dụng Together AI
client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"  # Base URL của Together AI
)


def get_embedding(text: str) -> List[float]:
    """
    Tạo embedding vector cho văn bản đầu vào sử dụng Together AI API
    """
    try:
        # Sử dụng mô hình embedding của Together AI
        # Thay "togethercomputer/m2-bert-80M-8k-retrieval" bằng mô hình thực tế bạn muốn dùng
        response = client.embeddings.create(
            model="togethercomputer/m2-bert-80M-8k-retrieval",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error creating embedding: {e}")
        # Trả về vector rỗng trong trường hợp lỗi
        return []
