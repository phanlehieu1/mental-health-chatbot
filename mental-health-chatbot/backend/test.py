import asyncio
from app.services.embedding import get_embedding
from app.services.retrieval import get_similar_documents


async def test_retrieval(query):
    """
    Test truy xuất context từ vector database
    """
    print(f"Query: {query}")

    # Tạo embedding cho query
    embedding = get_embedding(query)

    # Lấy các tài liệu tương tự
    docs = await get_similar_documents(embedding, top_k=3)

    # In ra kết quả
    print(f"\nTìm thấy {len(docs)} tài liệu tương tự:\n")

    for i, doc in enumerate(docs, 1):
        print(f"==== Kết quả #{i} ====")
        print(f"Nguồn: {doc['source']}")
        print(f"Score: {doc['score']:.4f}")
        print(f"Nội dung: {doc['text'][:200]}...\n")


async def main():
    # Danh sách các câu query để test
    queries = [
        "Ai là cha đẻ của bạn?",
        "Bạn là ai?",
        # Thêm các câu query liên quan đến nội dung của bạn
    ]

    for query in queries:
        await test_retrieval(query)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
