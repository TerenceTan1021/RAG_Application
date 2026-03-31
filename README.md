RAGS PDF FILE READER
To start the application 
------
1. Make sure you're in the right directory
pwd  # Shows current path - should show something like /c/Users/.../Downloads/Rag_APp
2. Create virtual environment
python -m venv venv
3. Activate (Git Bash specific)
source venv/Scripts/activate
** You should now see (venv) at the beginning of your prompt **
4. Install requirements
pip install -r requirements.txt
5. Run the app
streamlit run run.py

# PDF RAG Assistant

A Retrieval-Augmented Generation (RAG) application that helps you extract, understand, and interact with information from PDF documents. Designed for engineers, students, and professionals who need to quickly digest technical documents, contracts, lecture notes, and research papers.

## Features

- Upload and process multiple PDF files with text extraction
- Semantic search using AI-powered embeddings
- Interactive Q&A to ask questions and get answers from documents
- Text-to-speech support for listening to responses (offline and online options)
- Source tracking to see which documents answers come from
- Local vector database for fast retrieval
- Open source with free deployment options

## Technology Stack

- Frontend: Streamlit
- RAG Framework: LangChain
- Vector Database: ChromaDB
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- PDF Processing: pdfplumber
- Text-to-Speech: pyttsx3 (offline) or gTTS (online)
- LLM Support: OpenAI GPT (optional)

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Optional: OpenAI API key for GPT-powered answers
