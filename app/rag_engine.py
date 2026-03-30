# app/rag_engine.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import os
from typing import List, Dict
import openai

class RAGEngine:
    def __init__(self, vector_store_manager, api_key=None):
        self.vector_store = vector_store_manager
        if api_key:
            openai.api_key = api_key
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000
            )
        else:
            # Use a local model or mock responses if no API key
            self.llm = None
            
    def format_docs(self, docs):
        """Format documents for context"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def answer_question(self, question: str, k: int = 4) -> Dict:
        """Answer a question based on the documents"""
        # Retrieve relevant documents
        relevant_docs = self.vector_store.similarity_search(question, k=k)
        
        if not relevant_docs:
            return {
                "answer": "No relevant documents found. Please upload a PDF first.",
                "sources": []
            }
        
        # If no LLM, return raw chunks
        if not self.llm:
            return {
                "answer": self.format_docs(relevant_docs),
                "sources": [doc.metadata.get("source", "Unknown") for doc in relevant_docs]
            }
        
        # Create prompt
        template = """You are a helpful assistant that answers questions based on the provided context.
        Use only the context below to answer the question. If you cannot answer based on the context, say so.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer: """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create chain
        chain = (
            {"context": lambda x: self.format_docs(x["docs"]), "question": lambda x: x["question"]}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Generate answer
        answer = chain.invoke({"docs": relevant_docs, "question": question})
        
        return {
            "answer": answer,
            "sources": list(set([doc.metadata.get("source", "Unknown") for doc in relevant_docs])),
            "chunks_used": len(relevant_docs)
        }
    
    def generate_summary(self, max_chunks: int = 20) -> Dict:
        """Generate a summary of all documents"""
        # Get all documents (this might need optimization for large collections)
        # For now, we'll need to implement a way to get all chunks
        # This is a simplified version
        
        # Alternative: Use a map-reduce approach
        return {
            "answer": "To summarize all documents, please specify which document or section you're interested in.",
            "sources": []
        }
    
    def extract_key_points(self, document_source: str = None) -> List[str]:
        """Extract key points from a document"""
        # Search for important sections
        queries = [
            "key points",
            "main ideas",
            "important concepts",
            "conclusions",
            "summary"
        ]
        
        all_points = []
        for query in queries:
            docs = self.vector_store.similarity_search(query, k=3)
            for doc in docs:
                if document_source and doc.metadata.get("source") != document_source:
                    continue
                all_points.append(doc.page_content[:500])
        
        return all_points[:10]  # Return top 10 key points