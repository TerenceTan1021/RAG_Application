# app/vector_store.py
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from typing import List, Optional
import os
import shutil

class VectorStoreManager:
    def __init__(self, persist_directory="./data/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = None
        
    def create_vector_store(self, documents, collection_name="pdf_docs"):
        """Create a new vector store from documents"""
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        self.vector_store.persist()
        return self.vector_store
    
    def load_vector_store(self, collection_name="pdf_docs"):
        """Load existing vector store"""
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=collection_name
            )
            return self.vector_store
        return None
    
    def add_documents(self, documents):
        """Add documents to existing vector store"""
        if self.vector_store:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
        else:
            self.create_vector_store(documents)
    
    def similarity_search(self, query: str, k: int = 4) -> List:
        """Search for similar documents"""
        if self.vector_store:
            return self.vector_store.similarity_search(query, k=k)
        return []
    
    def similarity_search_with_score(self, query: str, k: int = 4):
        """Search with relevance scores"""
        if self.vector_store:
            return self.vector_store.similarity_search_with_relevance_scores(query, k=k)
        return []
    
    def delete_collection(self):
        """Delete the vector store collection"""
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            self.vector_store = None