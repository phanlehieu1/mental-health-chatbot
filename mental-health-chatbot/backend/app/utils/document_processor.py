import os
import glob
from typing import List, Optional
from datetime import datetime
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.embedding import get_embedding
from app.services.faiss_service import faiss_service
import asyncio


async def process_document(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> int:
    """
    Xử lý một tài liệu, chia nhỏ và lưu vào vector database
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)

    # Đọc nội dung tài liệu
    if file_extension == '.pdf':
        text = ''
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    else:  # .txt, .md, etc.
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

    # Chia nhỏ văn bản
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    chunks = splitter.split_text(text)
    print(f"Split document into {len(chunks)} chunks")

    # Xử lý từng chunk và lưu vào Pinecone
    vectors = []
    for i, chunk in enumerate(chunks):
        # Tạo embedding
        embedding = get_embedding(chunk)

        # Tạo vector record
        vectors.append({
            "id": f"{file_name}-{i}",
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": file_name,
                "chunk": i,
                "created_at": str(datetime.now().isoformat())
            }
        })

        # Upsert theo batches để tối ưu
        if len(vectors) >= 100:
            texts = [v["metadata"]["text"] for v in vectors]
            embeddings = [v["values"] for v in vectors]
            sources = [v["metadata"]["source"] for v in vectors]
            faiss_service.add_documents(texts, embeddings, sources)
            vectors = []

    # Upsert phần còn lại
    if vectors:
        texts = [v["metadata"]["text"] for v in vectors]
        embeddings = [v["values"] for v in vectors]
        sources = [v["metadata"]["source"] for v in vectors]
        faiss_service.add_documents(texts, embeddings, sources)

    return len(chunks)


async def process_directory(directory_path: str) -> int:
    """
    Xử lý tất cả tài liệu trong một thư mục
    """
    file_types = ['*.txt', '*.pdf', '*.md']
    all_files = []

    for file_type in file_types:
        all_files.extend(glob.glob(os.path.join(directory_path, file_type)))

    total_chunks = 0
    for file_path in all_files:
        print(f"Processing {file_path}...")
        chunks = await process_document(file_path)
        total_chunks += chunks

    print(f"Total chunks processed: {total_chunks}")
    return total_chunks

if __name__ == "__main__":
    # Script để chạy xử lý tài liệu trực tiếp
    import sys
    from datetime import datetime

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(__file__))), "data", "documents")

    print(f"Processing documents in: {directory}")
    asyncio.run(process_directory(directory))
