# 🏥 Clinical AI Copilot: Medical Guidelines Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-app-url.streamlit.app/)

> **Modern, Fast, and Reliable Clinical Decision Support System**

## 🚀 Overview

The **Clinical AI Copilot** is a state-of-the-art Clinical Decision Support System (CDSS) that leverages the power of **Gemini 1.5 Flash** and **ChromaDB** to provide accurate, evidence-based answers to medical queries. This system is designed to assist healthcare professionals by providing instant access to medical guidelines and protocols.

## ✨ Key Features

### 1. Advanced RAG Architecture
- **Semantic Search**: Utilizes ChromaDB with all-MiniLM-L6-v2 embeddings for precise document retrieval
- **Hallucination Prevention**: Built-in faithfulness scoring to ensure answers are grounded in source material
- **Multi-document Support**: Process and query multiple PDF documents simultaneously

### 2. Modern Tech Stack
- **Backend**: FastAPI for high-performance API serving
- **Vector Database**: ChromaDB for efficient document retrieval
- **LLM**: Google Gemini 1.5 Flash for fast, accurate responses
- **Frontend**: Streamlit for an intuitive, responsive UI

### 3. Professional Features
- **Source Citation**: Every claim is backed by specific document references
- **Confidence Scoring**: Visual indicators of answer reliability
- **Document Management**: Easy upload and processing of new guidelines
- **Session Persistence**: Maintains conversation context

## 🏗️ Architecture

```
clinical-ai-copilot/
├── backend/                 # FastAPI Service
│   ├── app.py              # Main API endpoints
│   ├── rag_engine.py       # RAG implementation
│   ├── models.py           # Data models
│   └── requirements.txt    # Python dependencies
├── frontend/               # Streamlit UI
│   ├── streamlit_app.py    # User interface
│   └── requirements.txt    # Frontend dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/clinical-ai-copilot.git
cd clinical-ai-copilot
```

### 2. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Gemini API key
```

### 3. Set Up Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
pip install -r requirements.txt
```
│   ├── templates/         # HTML Interface
│   ├── rag.py             # RAG Logic (Retrieval & Generation)
│   ├── database.py        # SQLite Operations
│   ├── app.py             # Flask Routes
│   └── main.py            # Entry Point
├── poetry.lock            # Locked Dependencies
├── pyproject.toml         # Project Configuration
└── README.md              # Documentation
```

## 🐛 Troubleshooting

- **"Model not found" Error:** Ensure you have the latest version of google-generativeai. Run `poetry update`.
- **Unicode/Encoding Errors on Windows:** If the app crashes when logging Arabic text, run this before starting: `set PYTHONIOENCODING=utf-8` (CMD) or `$env:PYTHONIOENCODING = "utf-8"` (PowerShell).

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created by Mohamed Fakhry

- **GitHub:** [@MohamedFakhry2007](https://github.com/MohamedFakhry2007)
- **Email:** mohamedfakhrysmile@gmail.com

## ⚠️ Disclaimer

This system is a proof-of-concept for Clinical AI engineering. While based on real medical protocols, it should not be used for actual patient care without further validation and regulatory approval.