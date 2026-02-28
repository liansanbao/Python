# _*_ coding: utf-8 _*_
# @Time : 2026/2/25 星期三 8:21
# @Author : 韦丽
# @Version: V 1.0
# @File : RAGService.py
# @desc :


import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import pickle
import os


class RAGService:
    def __init__(self, vector_dim=768):
        self.vector_dim = vector_dim
        self.vectorizer = TfidfVectorizer()
        self.index = faiss.IndexFlatIP(vector_dim)
        self.documents = []

    def add_documents(self, docs):
        self.documents.extend(docs)
        # 模拟向量化过程
        vectors = np.random.rand(len(docs), self.vector_dim).astype('float32')
        faiss.normalize_L2(vectors)
        self.index.add(vectors)

    def search(self, query, top_k=3):
        # 模拟查询向量化
        query_vector = np.random.rand(1, self.vector_dim).astype('float32')
        faiss.normalize_L2(query_vector)
        scores, indices = self.index.search(query_vector, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    'content': self.documents[idx],
                    'score': float(scores[0][i])
                })
        return results

    def save_index(self, filepath):
        faiss.write_index(self.index, filepath)
        with open(filepath + '.docs', 'wb') as f:
            pickle.dump(self.documents, f)

    def load_index(self, filepath):
        self.index = faiss.read_index(filepath)
        with open(filepath + '.docs', 'rb') as f:
            self.documents = pickle.load(f)

