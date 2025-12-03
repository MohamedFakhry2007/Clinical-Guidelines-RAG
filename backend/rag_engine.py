import os
import logging
from typing import Dict, List, Optional, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ClinicalRAG:
    """
    Clinical RAG system for processing and querying medical guidelines.
    Uses ChromaDB for vector storage and Gemini 1.5 Flash for generation.
    """
    
    def __init__(self):
        """Initialize the RAG system with default settings."""
        # Configure Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        else:
            genai.configure(api_key=self.gemini_api_key)
        
        # Initialize embedding model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        # Initialize ChromaDB
        self.vector_db = None
        self.collection_name = "clinical_guidelines"
        
        # Text splitter configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        
        logger.info("ClinicalRAG system initialized")

    def _load_document(self, file_path: str) -> List[Document]:
        """Load a document based on its file extension."""
        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.lower().endswith(('.txt', '.md')):
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
            
        return loader.load()

    def ingest_document(self, file_path: str) -> int:
        """
        Ingest a document into the vector database.
        
        Args:
            file_path: Path to the document file (PDF or text)
            
        Returns:
            int: Number of chunks created from the document
        """
        try:
            # Load and split the document
            docs = self._load_document(file_path)
            splits = self.text_splitter.split_documents(docs)
            
            # Add metadata to each document
            for doc in splits:
                doc.metadata["source"] = os.path.basename(file_path)
                
            # Create or update the vector store
            if self.vector_db is None:
                self.vector_db = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embedding_model,
                    collection_name=self.collection_name,
                    persist_directory="./chroma_db"
                )
                self.vector_db.persist()
            else:
                # Add to existing collection
                self.vector_db.add_documents(splits)
                self.vector_db.persist()
            
            logger.info(f"Ingested {len(splits)} chunks from {file_path}")
            return len(splits)
            
        except Exception as e:
            logger.error(f"Error ingesting document {file_path}: {str(e)}")
            raise

    def _generate_answer(self, query: str, context: str) -> Dict[str, Any]:
        """Generate an answer using Gemini 1.5 Flash."""
        try:
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not configured")
                
            model = genai.GenerativeModel('gemini-flash-lite-latest')
            
            prompt = f"""You are a Senior Clinical AI Assistant. Answer the question STRICTLY based on the context below.
            
            Context:
            {context}
            
            Question: {query}
            
            Requirements:
            1. Answer in professional English medical terminology.
            2. CITE YOUR SOURCES. At the end of every specific medical claim, add [Source: Page X].
            3. If the answer is not in the context, state "Information not found in guidelines."
            """
            
            response = model.generate_content(prompt)
            
            # Check for safety ratings - handle potential missing attributes
            if hasattr(response, 'prompt_feedback') and hasattr(response.prompt_feedback, 'block_reason'):
                if response.prompt_feedback.block_reason != 0:  # 0 = BLOCK_REASON_UNSPECIFIED
                    logger.warning(f"Content blocked: {response.prompt_feedback}")
                    return {
                        "answer": "I'm sorry, but I can't provide a response to that query due to content safety restrictions.", 
                        "sources": []
                    }
            
            # Safely get the response text
            if hasattr(response, 'text'):
                return {"answer": response.text, "sources": []}
            else:
                raise ValueError("No text in response from Gemini API")
                
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {"answer": "I encountered an error while generating a response. Please try again.", "sources": []}

    def _check_faithfulness(self, context: str, answer: str) -> float:
        """
        Evaluate if the generated answer is faithful to the provided context.
        
        Returns:
            float: Faithfulness score between 0.0 (not faithful) and 1.0 (completely faithful)
        """
        try:
            if not self.gemini_api_key:
                logger.warning("GEMINI_API_KEY not configured, skipping faithfulness check")
                return 0.8  # Default to medium confidence if we can't check
                
            model = genai.GenerativeModel('gemini-flash-lite-latest')
            
            prompt = f"""Evaluate the faithfulness of the following answer to the provided context.
            
            Context:
            {context}
            
            Answer to evaluate:
            {answer}
            
            Rate the faithfulness of the answer to the context on a scale of 0.0 to 1.0.
            Consider these criteria:
            - 0.0: The answer contains information not in the context (hallucination)
            - 0.5: The answer is somewhat related but contains inaccuracies
            - 1.0: The answer is completely faithful to the context
            
            Return ONLY a float number between 0.0 and 1.0.
            """
            
            response = model.generate_content(prompt)
            
            if not hasattr(response, 'text'):
                logger.warning("No text in faithfulness check response")
                return 0.8  # Default to medium confidence
                
            try:
                score = float(response.text.strip())
                return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse faithfulness score: {e}")
                return 0.8  # Default to medium confidence on parsing error
            
        except Exception as e:
            logger.error(f"Error in faithfulness check: {str(e)}")
            return 0.5  # Default to neutral score on error

    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query the RAG system with a clinical question.
        
        Args:
            question: The clinical question to answer
            top_k: Number of document chunks to retrieve
            
        Returns:
            Dict containing the answer, sources, and metadata
        """
        if not self.vector_db:
            logger.warning("No documents have been loaded into the vector database")
            return None
            
        try:
            # Retrieve relevant documents
            retriever = self.vector_db.as_retriever(search_kwargs={"k": top_k})
            docs = retriever.invoke(question)
            
            if not docs:
                return {
                    "answer": "No relevant information found in the guidelines.",
                    "docs": [],
                    "confidence_score": 0.0
                }
            
            # Combine context from all retrieved documents
            context_text = "\n\n".join([f"[Document {i+1}, Page {doc.metadata.get('page', '?')}]\n{doc.page_content}" 
                                     for i, doc in enumerate(docs)])
            
            # Generate answer using the context
            result = self._generate_answer(question, context_text)
            
            # Evaluate faithfulness of the answer
            if result["answer"] and "not found" not in result["answer"].lower():
                confidence = self._check_faithfulness(context_text, result["answer"])
                result["confidence_score"] = confidence
            else:
                result["confidence_score"] = 0.0
            
            # Add source documents to the result
            result["docs"] = docs
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
