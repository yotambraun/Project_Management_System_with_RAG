import faiss
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model="all-minilm")
        self.vector_store = None

    def create_vector_store(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        documents = [Document(page_content=text, metadata=metadata) for text, metadata in zip(texts, metadatas)]
        try:
            print(f"Creating FAISS index with {len(documents)} documents")
            print(f"Embedding dimension: {len(self.embeddings.embed_query('test'))}")
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            print("FAISS index created successfully")
        except Exception as e:
            print(f"Error creating vector store: {e}")
            print("Falling back to in-memory storage without embeddings.")
            self.vector_store = InMemoryStore(documents)
            
    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        if self.vector_store is None:
            self.create_vector_store(texts, metadatas)
        else:
            try:
                self.vector_store.add_texts(texts, metadatas=metadatas)
            except Exception as e:
                print(f"Error adding texts to vector store: {e}")

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        if self.vector_store is None:
            self.initialize_with_dummy_data()
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error performing similarity search: {e}")
            return []

    def initialize_with_dummy_data(self):
        dummy_texts = [
            "This is a dummy task for initializing the vector store.",
            "Another dummy task to ensure the vector store is not empty.",
            "A third dummy task for good measure."
        ]
        dummy_metadatas = [
            {"title": "Dummy Task 1", "project_id": 0},
            {"title": "Dummy Task 2", "project_id": 0},
            {"title": "Dummy Task 3", "project_id": 0}
        ]
        self.create_vector_store(dummy_texts, dummy_metadatas)
        print("Vector store initialized with dummy data.")

class InMemoryStore:
    def __init__(self, documents: List[Document]):
        self.documents = documents
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        return self.documents[:k]

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        new_docs = [Document(page_content=text, metadata=metadata) for text, metadata in zip(texts, metadatas)]
        self.documents.extend(new_docs)

vector_store = VectorStore()