import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional

# Đường dẫn để lưu index và metadata
INDEX_PATH = "data/faiss_index"
METADATA_PATH = "data/faiss_metadata.json"

# Đảm bảo thư mục tồn tại
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)


class FAISSService:
    def __init__(self, dimension=768):
        self.dimension = dimension
        self.index = None
        self.metadata = []
        self.load_or_create_index()

    def load_or_create_index(self):
        """Tải index từ file hoặc tạo mới nếu chưa tồn tại"""
        try:
            if os.path.exists(INDEX_PATH):
                self.index = faiss.read_index(INDEX_PATH)
                with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"Đã tải index FAISS với {len(self.metadata)} tài liệu")
            else:
                # Tạo index mới với cosine similarity
                # Inner product cho cosine similarity
                self.index = faiss.IndexFlatIP(self.dimension)
                self.metadata = []
                print("Đã tạo index FAISS mới")
        except Exception as e:
            print(f"Lỗi khi tải index FAISS: {e}")
            # Khởi tạo lại index nếu có lỗi
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def add_documents(self, texts: List[str], embeddings: List[List[float]], sources: List[str] = None):
        """Thêm tài liệu mới vào index"""
        if not texts or not embeddings:
            return

        if sources is None:
            sources = ["unknown"] * len(texts)

        # Chuẩn hóa các vector embedding (cần thiết cho inner product)
        vectors = np.array(embeddings).astype('float32')
        faiss.normalize_L2(vectors)

        # Thêm vào index
        self.index.add(vectors)

        # Lưu metadata
        for i, (text, source) in enumerate(zip(texts, sources)):
            self.metadata.append({
                "text": text,
                "source": source
            })

        # Lưu index và metadata vào đĩa
        self._save_index()

    def search(self, embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """Tìm kiếm các tài liệu tương tự dựa trên embedding vector"""
        if self.index.ntotal == 0:
            return []

        # Chuẩn hóa query vector
        query_vector = np.array([embedding]).astype('float32')
        faiss.normalize_L2(query_vector)

        # Thực hiện tìm kiếm
        scores, indices = self.index.search(query_vector, top_k)

        # Tạo kết quả
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.metadata) and idx != -1:
                results.append({
                    "text": self.metadata[idx]["text"],
                    "source": self.metadata[idx]["source"],
                    # Convert numpy float to Python float
                    "score": float(score)
                })

        return results

    def _save_index(self):
        """Lưu index và metadata vào đĩa"""
        try:
            faiss.write_index(self.index, INDEX_PATH)
            with open(METADATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu index FAISS với {len(self.metadata)} tài liệu")
        except Exception as e:
            print(f"Lỗi khi lưu index FAISS: {e}")


# Tạo instance global
faiss_service = FAISSService()
