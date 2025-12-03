import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import google.generativeai as genai

# Configure GenAI once
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ClinicalRAG:
    def __init__(self):
        # 🟢 OPTIMIZATION: Use Google's API for embeddings instead of local PyTorch
        # This saves ~400MB of RAM and fixes the crash.
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # Initialize Vector DB (In-memory for speed/low resource)
        self.vector_db = None

    def ingest_document(self, file_path: str):
        """Ingests a PDF, chunks it, and stores in Vector DB."""
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # Split text (smaller chunks are better for context window)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Store in ChromaDB
        # We re-initialize the DB on every upload for this demo to keep it clean
        self.vector_db = Chroma.from_documents(
            documents=splits, 
            embedding=self.embedding_model,
            collection_name="clinical_guidelines"
        )
        return len(splits)

    def query(self, query: str):
        if not self.vector_db:
            return None
            
        # 1. Retrieve top 4 relevant chunks
        retriever = self.vector_db.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(query)
        
        # 2. Construct Context
        context_text = "\n\n".join([f"[Page {d.metadata.get('page', 0)}] {d.page_content}" for d in docs])
        
        # 3. Generate Answer with Citations using ChatGoogleGenerativeAI (LangChain wrapper)
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-lite-latest",
            temperature=0.3,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        system_prompt = f"""
        You are a Senior Clinical AI Assistant. Answer the question STRICTLY based on the context below.
        
        Context:
        {context_text}
        
        Requirements:
        1. Answer in professional medical terminology.
        2. CITE YOUR SOURCES. At the end of every specific claim, add [Source: Page X].
        3. If the answer is not in the context, say "Information not found in guidelines."
        """
        
        response = llm.invoke([
            ("system", system_prompt),
            ("human", query)
        ])
        
        return {
            "answer": response.content,
            "docs": docs
        }