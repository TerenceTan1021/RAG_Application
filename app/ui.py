# app/ui.py
import streamlit as st
import os
from pathlib import Path
import tempfile
from .document_processor import PDFProcessor
from .vector_store import VectorStoreManager
from .rag_engine import RAGEngine
from .text_to_speech import TextToSpeech

class PDFRAGUI:
    def __init__(self):
        self.processor = PDFProcessor()
        self.vector_manager = VectorStoreManager()
        self.setup_session_state()
        
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'rag_engine' not in st.session_state:
            st.session_state.rag_engine = None
        if 'current_documents' not in st.session_state:
            st.session_state.current_documents = []
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'tts_enabled' not in st.session_state:
            st.session_state.tts_enabled = False
            
    def run(self):
        st.set_page_config(
            page_title="PDF RAG Assistant",
            page_icon="📚",
            layout="wide"
        )
        
        st.title("📚 PDF RAG Assistant")
        st.markdown("Upload PDFs and ask questions - with text-to-speech support!")
        
        # Sidebar
        with st.sidebar:
            st.header("Configuration")
            
            # API Key input
            api_key = st.text_input("OpenAI API Key (optional)", type="password")
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            
            # TTS settings
            st.subheader("Text-to-Speech")
            st.session_state.tts_enabled = st.checkbox("Enable TTS", value=False)
            tts_engine = st.selectbox("TTS Engine", ["gtts", "pyttsx3"])
            
            if st.session_state.tts_enabled:
                tts = TextToSpeech(engine=tts_engine)
            else:
                tts = None
            
            # File upload
            st.subheader("Upload PDFs")
            uploaded_files = st.file_uploader(
                "Choose PDF files",
                type=['pdf'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                if st.button("Process PDFs"):
                    self.process_uploaded_files(uploaded_files, tts)
            
            # Clear data button
            if st.button("Clear All Data"):
                self.clear_data()
                st.rerun()
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("💬 Chat with your PDFs")
            
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if st.session_state.tts_enabled and message["role"] == "assistant":
                        if st.button("🔊", key=f"tts_{len(st.session_state.chat_history)}"):
                            tts.speak(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask a question about your PDFs"):
                self.handle_question(prompt, tts)
        
        with col2:
            st.header("📄 Document Info")
            if st.session_state.rag_engine and st.session_state.rag_engine.vector_store.vector_store:
                st.success("✅ Documents loaded and ready!")
                
                # Document list
                if st.session_state.current_documents:
                    st.subheader("Loaded Documents:")
                    for doc in st.session_state.current_documents:
                        st.write(f"- {doc.metadata.get('filename', 'Unknown')}")
                    
                    if st.button("📖 Read Document Summary"):
                        self.read_document_summary(tts)
            else:
                st.info("No documents loaded. Please upload PDFs to begin.")
    
    def process_uploaded_files(self, uploaded_files, tts):
        """Process uploaded PDF files"""
        with st.spinner("Processing PDFs..."):
            temp_dir = tempfile.mkdtemp()
            all_chunks = []
            document_names = []
            
            for uploaded_file in uploaded_files:
                # Save temporarily
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process PDF
                chunks = self.processor.process_pdf(temp_path)
                if chunks:
                    all_chunks.extend(chunks)
                    document_names.append(uploaded_file.name)
            
            if all_chunks:
                # Create or update vector store
                if not st.session_state.rag_engine:
                    vector_manager = VectorStoreManager()
                    vector_store = vector_manager.create_vector_store(all_chunks)
                    st.session_state.rag_engine = RAGEngine(
                        vector_manager,
                        api_key=os.getenv("OPENAI_API_KEY")
                    )
                else:
                    st.session_state.rag_engine.vector_store.add_documents(all_chunks)
                
                st.session_state.current_documents.extend(all_chunks)
                st.success(f"Successfully processed {len(uploaded_files)} PDFs!")
                
                if st.session_state.tts_enabled and tts:
                    tts.speak(f"Processed {len(uploaded_files)} PDF files. You can now ask questions.")
            else:
                st.error("Failed to process PDFs. Please check the files.")
    
    def handle_question(self, question, tts):
        """Handle user question"""
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        # Generate response
        if st.session_state.rag_engine and st.session_state.rag_engine.vector_store.vector_store:
            with st.spinner("Thinking..."):
                response = st.session_state.rag_engine.answer_question(question)
                answer = response["answer"]
                sources = response.get("sources", [])
                
                # Add sources to answer
                if sources:
                    answer += f"\n\n*Sources: {', '.join(sources)}*"
        else:
            answer = "Please upload some PDFs first using the sidebar."
        
        # Add assistant response to chat
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        
        # Speak if TTS enabled
        if st.session_state.tts_enabled and tts:
            tts.speak(answer)
        
        st.rerun()
    
    def read_document_summary(self, tts):
        """Read a summary of the document"""
        if st.session_state.rag_engine:
            # Get the first few chunks
            chunks = st.session_state.current_documents[:5]
            summary_text = "\n\n".join([chunk.page_content[:500] for chunk in chunks])
            
            if st.session_state.tts_enabled and tts:
                tts.speak("Here's a summary of your documents:")
                tts.speak(summary_text)
            else:
                st.info("Enable TTS in the sidebar to hear the summary.")
    
    def clear_data(self):
        """Clear all stored data"""
        st.session_state.rag_engine = None
        st.session_state.current_documents = []
        st.session_state.chat_history = []
        
        # Clear vector store
        vector_manager = VectorStoreManager()
        vector_manager.delete_collection()
        
        st.success("All data cleared!")

def main():
    ui = PDFRAGUI()
    ui.run()

if __name__ == "__main__":
    main()