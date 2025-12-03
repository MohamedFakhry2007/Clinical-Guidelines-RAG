import os
import sys
import time
import json
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Try to load from Streamlit secrets first, then environment variables, then default
API_URL = "http://localhost:8000"
try:
    API_URL = st.secrets.get("API_URL", os.getenv("BACKEND_API_URL", API_URL))
except FileNotFoundError:
    # Fallback for local development if secrets.toml is not found
    API_URL = os.getenv("BACKEND_API_URL", API_URL)
APP_TITLE = "🩺 Clinical AI Co-pilot"
APP_DESCRIPTION = "Professional Clinical Decision Support System"
VERSION = "1.0.0"

# Set page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stMarkdown {
        line-height: 1.6;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 10%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 10%;
    }
    .source-doc {
        font-size: 0.85rem;
        color: #666;
        border-left: 3px solid #4a90e2;
        padding-left: 0.5rem;
        margin: 0.5rem 0;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def display_chat_message(role: str, content: str, confidence: float = None):
    """Display a chat message with appropriate styling."""
    if role == "user":
        st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>', 
                   unsafe_allow_html=True)
    else:
        # Format the assistant's response with proper line breaks
        formatted_content = content.replace('\n', '<br>')
        confidence_badge = ""
        
        if confidence is not None:
            confidence_pct = int(confidence * 100)
            confidence_class = ""
            if confidence >= 0.8:
                confidence_class = "confidence-high"
            elif confidence >= 0.5:
                confidence_class = "confidence-medium"
            else:
                confidence_class = "confidence-low"
                
            confidence_badge = f'<div class="confidence-badge"><small>Confidence: <span class="{confidence_class}">{confidence_pct}%</span></small></div>'
        
        st.markdown(
            f'<div class="chat-message assistant-message">'
            f'<strong>Assistant:</strong><br>{formatted_content}<br>{confidence_badge}'
            f'</div>', 
            unsafe_allow_html=True
        )

def display_sources(sources: list):
    """Display source documents in an expandable section."""
    if not sources:
        return
        
    with st.expander("📚 Source Evidence", expanded=False):
        st.caption("The following sources were used to generate the response:")
        
        for i, source in enumerate(sources, 1):
            with st.container():
                st.markdown(
                    f"<div class='source-doc'>"
                    f"<strong>Source {i}</strong> (Page {source.get('page_number', 'N/A')} of {source.get('file_name', 'Unknown')}):<br>"
                    f"{source.get('text_snippet', 'No content available')}"
                    f"</div>",
                    unsafe_allow_html=True
                )

def upload_document():
    """Handle document upload and processing."""
    st.sidebar.header("1. Knowledge Base")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Medical Guidelines (PDF)", 
        type=["pdf"],
        help="Upload clinical guidelines or medical documents in PDF format"
    )
    
    if uploaded_file is not None and st.sidebar.button("Process Guidelines"):
        with st.sidebar.status("Processing document...", expanded=True) as status:
            try:
                st.write("Uploading file...")
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                response = requests.post(f"{API_URL}/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    status.update(
                        label="Document processed successfully!", 
                        state="complete", 
                        expanded=False
                    )
                    st.sidebar.success(f"✅ Indexed {result.get('chunks', 0)} clinical chunks.")
                    return True
                else:
                    st.sidebar.error(f"Error: {response.text}")
                    return False
                    
            except Exception as e:
                st.sidebar.error(f"Error processing document: {str(e)}")
                return False
    return None

def display_chat_interface():
    """Display the main chat interface."""
    st.header("Clinical Query Assistant")
    st.caption(f"Ask questions about the uploaded clinical guidelines. Version {VERSION}")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(
            role=message["role"], 
            content=message["content"],
            confidence=message.get("confidence")
        )
        
        # Display sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            display_sources(message["sources"])
    
    # Chat input
    if prompt := st.chat_input("Ask a clinical question (e.g., 'What is the recommended treatment for condition X?')"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        display_chat_message("user", prompt)
        
        # Prepare and send API request
        with st.spinner("Consulting guidelines..."):
            try:
                payload = {
                    "question": prompt,
                    "session_id": st.session_state.get("session_id", "default_session")
                }
                
                response = requests.post(f"{API_URL}/query", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Add assistant response to chat history
                    assistant_message = {
                        "role": "assistant",
                        "content": data["answer"],
                        "sources": data.get("sources", []),
                        "confidence": data.get("confidence_score")
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    # Display assistant response
                    display_chat_message(
                        role="assistant",
                        content=data["answer"],
                        confidence=data.get("confidence_score")
                    )
                    
                    # Display sources if available
                    if "sources" in data and data["sources"]:
                        display_sources(data["sources"])
                        
                else:
                    error_msg = f"Error: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"I encountered an error: {error_msg}"
                    })
                    
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"I'm having trouble connecting to the server: {error_msg}"
                })

def display_sidebar():
    """Display the sidebar with app information and controls."""
    st.sidebar.title(APP_TITLE)
    st.sidebar.caption(APP_DESCRIPTION)
    
    # Document upload section
    upload_success = upload_document()
    
    # App information
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.markdown("""
    This is a Clinical AI Co-pilot designed to assist healthcare professionals 
    in quickly finding information from clinical guidelines.
    """)
    
    # Status indicators
    st.sidebar.markdown("### System Status")
    try:
        # Check backend status
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            st.sidebar.success("✅ Backend API is running")
        else:
            st.sidebar.error("❌ Backend API is not responding")
    except:
        st.sidebar.error("❌ Cannot connect to backend API")
    
    # Clear chat button
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Version info
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Version {VERSION}")

def main():
    """Main application function."""
    # Set up the page title and description
    st.title(APP_TITLE)
    
    # Display the sidebar
    display_sidebar()
    
    # Display the main chat interface
    display_chat_interface()

if __name__ == "__main__":
    main()
