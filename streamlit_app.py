import streamlit as st
import asyncio
import os
import logging

# Import your existing backend logic
from clinical_chatbot.rag import initialize_retrieval_system, generate_response, retrieve_relevant_documents
from clinical_chatbot.database import init_database
from clinical_chatbot.data.policies import populate_database
from clinical_chatbot.logger import setup_logger

# Page Config
st.set_page_config(
    page_title="المساعد الطبي الذكي - Clinical AI",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for RTL and Styling (Mimicking your style.css)
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', sans-serif;
    }
    .stChatMessage {
        direction: rtl; 
        text-align: right;
    }
    /* Fix alignment for chat input */
    .stChatInputContainer {
        direction: rtl;
    }
    h1 {
        text-align: center;
        color: #20c997;
    }
</style>
""", unsafe_allow_html=True)

# Initialize System (Cached to run only once)
@st.cache_resource
def system_startup():
    # Setup Logger
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # Initialize DB
    # Note: On Streamlit Cloud, SQLite is ephemeral (resets on reboot). 
    # This is fine for a demo.
    init_database()
    populate_database()
    
    # Initialize RAG
    initialize_retrieval_system()
    return logger

logger = system_startup()

# Header
st.title("نظام المساعد الطبي للبروتوكولات")
st.markdown("<p style='text-align: center; color: gray;'>البحث في الأدلة السريرية والبروتوكولات المعتمدة</p>", unsafe_allow_html=True)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحبًا دكتور. أنا المساعد الطبي الذكي. يمكنك سؤالي عن بروتوكولات الإنتان، الجلطات، أو إجراءات الطوارئ."}
    ]

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Input
if prompt := st.chat_input("اكتب سؤالك هنا..."):
    # 1. Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        with st.spinner("جاري البحث في البروتوكولات..."):
            try:
                # Retrieve docs
                relevant_docs = retrieve_relevant_documents(prompt)
                
                # Run Async generation function in sync Streamlit environment
                response_text = asyncio.run(generate_response(prompt, relevant_docs))
                
                st.markdown(response_text)
                
                # Add assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
                logger.error(f"Streamlit Error: {e}")