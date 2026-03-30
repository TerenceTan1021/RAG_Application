# app/document_processor.py
import pdfplumber
from typing import List, Dict
import hashlib
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class PDFProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
        
        return text
    
    def get_document_metadata(self, pdf_path: str) -> Dict:
        """Extract metadata from PDF"""
        file_name = os.path.basename(pdf_path)
        file_size = os.path.getsize(pdf_path)
        file_hash = self.get_file_hash(pdf_path)
        
        return {
            "source": pdf_path,
            "filename": file_name,
            "file_size": file_size,
            "file_hash": file_hash,
        }
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate hash for file to avoid duplicates"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Process PDF and create document chunks"""
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return []
        
        # Get metadata
        metadata = self.get_document_metadata(pdf_path)
        
        # Create base document
        base_doc = Document(page_content=text, metadata=metadata)
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([base_doc])
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Document]:
        """Process multiple PDF files"""
        all_chunks = []
        for pdf_path in pdf_paths:
            chunks = self.process_pdf(pdf_path)
            all_chunks.extend(chunks)
        return all_chunks