# 🩺 Clinical Guidelines RAG System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://clinical-guidelines-rag-ibsbcobwevafwaagbpiiyq.streamlit.app/)

> **Try the Live Demo:** [Click Here to test the App](https://clinical-guidelines-rag-ibsbcobwevafwaagbpiiyq.streamlit.app/)

## Overview

The **Clinical Guidelines RAG System** is a specialized Clinical Decision Support System (CDSS) designed to assist healthcare professionals by providing instant, accurate answers based strictly on approved medical protocols.

Unlike generic LLMs which can "hallucinate" or invent treatments, this system utilizes **Retrieval-Augmented Generation (RAG)** to ground every response in a verified internal knowledge base. It is engineered to handle complex queries in **Arabic**, supporting medical staff in high-pressure environments like ER Triage and ICU by retrieving protocols for Sepsis, Stroke, and Hypertensive Crises.

## ✨ Key Features

### 1. Hallucination-Free Clinical Answers
- **Strict RAG Implementation:** The AI is architecturally constrained to answer *only* using the retrieved context from uploaded medical PDFs/documents.
- **Safety Fallbacks:** If a procedure is not found in the approved protocols, the system explicitly states "Information not available in protocols" rather than fabricating advice.

### 2. Specialized Medical Knowledge Base
- **Triage & Emergency Protocols:** Pre-loaded with standard guidelines for **Chest Pain (MONA)**, **Stroke (tPA criteria)**, **Sepsis (Hour-1 Bundle)**, and **Epistaxis**.
- **Drug Dosage & Contraindications:** Retrieves specific dosage instructions (e.g., Labetalol for Hypertensive Crisis) and safety warnings.

### 3. Arabic Medical NLP
- **Native Arabic Support:** Optimized to process and generate complex medical terminology in Arabic while maintaining English clinical acronyms (e.g., ECG, CT, IV).
- **RTL Interface:** A clean, dark-mode UI fully optimized for Right-to-Left languages using Bootstrap 5 RTL.

### 4. Lightweight Vector Search
- **TF-IDF & Cosine Similarity:** Implements an efficient, in-memory retrieval engine using Scikit-Learn, ensuring sub-second retrieval latency without the need for heavy external vector databases.

## 🛠️ Technical Architecture

### Backend
- **Python 3.11+**
- **Flask:** Lightweight web server handling API requests.
- **Google Gemini 1.5 Pro:** The LLM engine used for synthesis and reasoning.
- **Scikit-Learn:** Used for TF-IDF vectorization and cosine similarity calculations.
- **SQLite:** Stores chat logs and metadata for audit trails.

### Frontend
- **Jinja2 Templates:** Server-side rendering for speed and security.
- **Bootstrap 5 RTL:** Responsive, mobile-friendly clinical dashboard.
- **Vanilla JS:** Handles asynchronous chat interactions and typing animations.

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Poetry** (dependency management) - [Install Poetry](https://python-poetry.org/docs/)
- **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))

### 1. Clone and Setup

```bash
git clone https://github.com/MohamedFakhry2007/Clinical-Guidelines-RAG.git
cd Clinical-Guidelines-RAG
poetry install
```

### 2. Configure Environment

Create a `.env` file from the example and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
GEMINI_API_KEY=your_actual_api_key_here
LOG_LEVEL=DEBUG
```

### 3. Initialize & Run

This command will automatically populate the database with the medical protocols if it's empty.

**Windows (PowerShell) - Force UTF-8 for Arabic logs:**
```powershell
$env:PYTHONIOENCODING = "utf-8"
poetry run start
```

**Linux / Mac:**
```bash
poetry run start
```

Visit `http://localhost:5000` to access the system.

## 📖 Usage Scenarios

Try asking these clinical questions (in Arabic):

- **Sepsis:** "ما هو بروتوكول علاج الإنتان؟" (What is the sepsis protocol?)
- **Stroke:** "متى نعطي tPA لمريض الجلطة؟" (When to give tPA for stroke patient?)
- **Emergency:** "ماذا أفعل مع مريض ضغط مزمن أتى بنزيف من الأنف؟" (How to manage hypertensive epistaxis?)

## 📋 Project Structure

```
Clinical-Guidelines-RAG/
├── clinical_chatbot/       # Main Package
│   ├── data/              # Medical Protocols (The Knowledge Base)
│   ├── static/            # CSS (RTL), JS
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