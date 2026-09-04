# Smart University Academic Assistant using AI Agents for Student Query Resolution and Document Retrieval

> **Generative AI Capstone Project**  
> A complete, production-grade, and beginner-friendly intelligent university query resolution system built with Python, Flask, RAG (Retrieval-Augmented Generation), SQLite, and Autonomous AI Agent Architecture.

---

## 🎯 Main Objective

The primary objective of this project is to provide a unified, intelligent academic assistant where university students can ask questions regarding **Attendance Rules**, **Semester Examinations**, **Tuition Fees**, **Academic Calendars**, **Degree Courses**, and **Admissions**, and receive verified, hallucination-free answers synthesized directly from official university policy documents.

---

## 🏗️ End-to-End System Architecture

```text
┌────────────────────────────────────────────────────────┐
│ 1. Student Query Input (Web UI / Suggestion Chips)     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. Module 1: Query Processing & Classification         │
│    (Cleans text, extracts keywords, identifies category)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 3. Module 2: University Query Agent                    │
│    (Orchestrates reasoning, logs telemetry steps)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 4. Module 3: Document Retrieval (Vector RAG Search)    │
│    (Matches query against sliding-window text chunks)  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 5. Module 4: Knowledge Base Store                      │
│    (Ingests documents, live vector index rebuild)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 6. Generative AI / Smart Fallback Synthesizer          │
│    (Grounds answer strictly on retrieved context)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 7. Module 5: Modern Light UI & Step-by-Step Delivery   │
│    (Visualizes live reasoning timeline & score cards)  │
└────────────────────────────────────────────────────────┘
```

---

## 📦 Explanation of the Five Core Modules

### 🔹 Module 1: Student Query Processing
- **Validation:** Ensures non-empty, meaningful query submissions with actionable user guidance.
- **Normalization:** Strips linguistic noise, standardizes casing, and filters stop words while extracting high-signal domain keywords.
- **Intent & Category Classification:** Categorizes questions into one of 7 distinct taxonomy classes:
  1. `Attendance`
  2. `Examination`
  3. `Fees`
  4. `Academic`
  5. `Course Information`
  6. `Admission`
  7. `General`

### 🔹 Module 2: AI Agent-Based Query Resolution
- **Autonomous Coordinator (`UniversityQueryAgent`):** Acts as the single central cognitive orchestrator.
- **Decision Engine:** Determines whether vector knowledge base retrieval is required.
- **Transparent 7-Stage Reasoning Trail:**
  1. *Query Received*
  2. *Understanding Query*
  3. *Classifying Request*
  4. *Deciding Agent Action*
  5. *Searching Knowledge Base*
  6. *Generating AI Response*
  7. *Response Ready*
- **Audit Logging:** Every query, latency, score, and generated answer is logged to SQLite.

### 🔹 Module 3: Academic Document Retrieval
- **Document Chunking:** Splits policies into semantic paragraphs with overlapping window boundaries.
- **Vector Embeddings & Semantic Search:** Uses Scikit-learn TF-IDF Vectorizer and Cosine Similarity to score query similarity against knowledge base chunks.
- **Relevance Metrics:** Computes calibrated relevance scores (e.g. `92.4%`) and pinpoints the exact source document.

### 🔹 Module 4: Knowledge Base Management
- **Verified University Policies:** Preloaded with:
  - `attendance_policy.txt` (75% rule, medical condonation, detention)
  - `exam_rules.txt` (Hall ticket, reporting time, malpractice rules)
  - `academic_calendar.txt` (Odd/Even terms, exams, holidays)
  - `fees_information.txt` (Payment portal, deadlines, late fine slabs)
  - `course_information.txt` (B.Tech CSE/AI curriculum, credits, capstone)
  - `admission_information.txt` (Eligibility, document checklist, counseling)
- **Dynamic Ingestion:** Add custom documents via web UI with instant automatic vector re-indexing.
- **Index Refresh:** Rebuilds the search index at runtime with a single click.

### 🔹 Module 5: User Interface and Response Delivery
- **Modern Light Theme:** Designed with pristine white cards (`#ffffff`), soft background (`#f8fafc`), dark slate typography, and elegant indigo accents (`#4f46e5`).
- **Interactive Step Timeline:** Live animated progress indicator showing each stage of agent execution.
- **Module Output Breakdown:** Clear visual cards displaying Detected Category, Retrieved Document, Relevance Score %, Grounded Context snippet, and the Final AI Answer with copy-to-clipboard functionality.

---

## 🤖 RAG (Retrieval-Augmented Generation) Workflow

1. **User asks:** *"What is the minimum attendance requirement?"*
2. **Retrieval:** System searches `documents/` and identifies `attendance_policy.txt` with **92.0% Relevance**.
3. **Context Extraction:** Chunks containing the 75% attendance rule and condonation policy are isolated.
4. **Prompt Construction:**
   ```text
   You are a helpful Smart University Academic Assistant.
   Answer the student's question using only the information provided in the university knowledge base.
   
   Retrieved Context:
   Students must maintain a minimum attendance of 75 percent in each registered theory and laboratory subject...
   
   Student Question:
   What is the minimum attendance requirement?
   ```
5. **Generation:** Google Gemini API (or the built-in Smart Fallback RAG Synthesizer) produces an accurate, student-friendly answer cited with the source file.

---

## 🛡️ Zero-Crash Fallback Mode

If no Google Gemini API key is provided, or if the external API is offline or rate-limited:
- The system engages the **Smart Fallback RAG Synthesizer**.
- It structures a verified response strictly from the retrieved document context.
- **The application never crashes or shows technical Python errors to the user.**

---

## 💻 Technologies Used

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 3.x |
| **Database** | SQLite 3 |
| **Information Retrieval** | Scikit-learn (TF-IDF & Cosine Similarity), NumPy |
| **Generative AI** | Google Gemini API (`google-genai` / `google-generativeai`) + RAG Synthesizer |
| **Frontend** | HTML5, Modern Light CSS3, JavaScript (Fetch API & DOM Animations) |
| **Icons & Typography** | FontAwesome 6, Google Fonts (Plus Jakarta Sans & Inter) |

---

## 📁 Project Directory Structure

```text
smart-university-academic-assistant/
│
├── app.py                      # Main Flask application & routing
├── requirements.txt            # Project dependencies
├── README.md                   # Comprehensive capstone documentation
├── .env.example                # Environment variable configuration template
│
├── agents/                     # Module 2: AI Agent Layer
│   ├── __init__.py
│   └── query_agent.py          # UniversityQueryAgent cognitive pipeline
│
├── services/                   # Business Logic & Core Modules
│   ├── __init__.py
│   ├── query_processor.py      # Module 1: Query cleaning & classification
│   ├── document_retrieval.py   # Module 3: Semantic search & vector scoring
│   ├── knowledge_base.py       # Module 4: Document CRUD & index refresh
│   └── llm_service.py          # Gemini API + Fallback RAG synthesizer
│
├── documents/                  # Official University Knowledge Base Files
│   ├── attendance_policy.txt
│   ├── exam_rules.txt
│   ├── academic_calendar.txt
│   ├── fees_information.txt
│   ├── course_information.txt
│   └── admission_information.txt
│
├── database/                   # Persistence Layer
│   ├── __init__.py
│   ├── db.py                   # SQLite helper functions
│   └── university.db           # SQLite database (auto-created)
│
├── templates/                  # Frontend HTML Templates (Jinja2)
│   ├── base.html               # Base layout, sidebar & modals
│   ├── index.html              # Main dashboard & live query interface
│   ├── knowledge_base.html     # Document catalog & add knowledge form
│   ├── history.html            # Searchable query history & audit logs
│   └── about.html              # Viva defense guide & module breakdown
│
└── static/                     # Frontend Assets
    ├── style.css               # Modern light theme SaaS styling
    └── script.js               # Client-side AJAX controller & step animations
```

---

## 🚀 Installation and Setup

### Step 1: Clone or Navigate to the Project Directory
```bash
cd GEN-AI
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: (Optional) Configure Google Gemini API Key
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Add your API key inside `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_PORT=5000
FLASK_DEBUG=True
```
*(Note: If no API key is provided, the application automatically runs in Smart Fallback RAG mode.)*

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Open in Browser
Visit: **`http://127.0.0.1:5000`**

---

## 🧪 Sample Queries to Test

Try submitting these questions from the suggestion chips:
1. **Attendance:** `"What is the minimum attendance requirement?"`
2. **Examination:** `"When are semester examinations conducted?"`
3. **Fees:** `"How can I pay my tuition fees?"`
4. **Exam Rules:** `"What are the examination rules?"`
5. **Courses:** `"Tell me about the AI course."`
6. **Admissions:** `"What documents are required for admission?"`

---

## 📸 Screenshots

### 1. Dashboard & Live AI Agent Pipeline
> *(Place dashboard screenshot here: `assets/dashboard.png`)*

### 2. Module Output Cards & Relevance Score
> *(Place module results screenshot here: `assets/module_results.png`)*

### 3. Knowledge Base Management & Document Ingestion
> *(Place knowledge base screenshot here: `assets/knowledge_base.png`)*

### 4. SQLite Query History & Audit Trail
> *(Place history screenshot here: `assets/query_history.png`)*

---

## 🔮 Future Improvements

1. **Multi-turn Chat Memory:** Extend the single-agent pipeline to maintain session conversational context across consecutive turns.
2. **Voice Query Support:** Incorporate Web Speech API for voice-to-text queries.
3. **Multilingual Resolution:** Add automatic language translation for international exchange students.
4. **PDF/DOCX Document Ingestion:** Extend knowledge base parser to support structured PDF uploads with table extraction.

---

## 🎓 Capstone Viva Summary

- **Title:** Smart University Academic Assistant using AI Agents for Student Query Resolution and Document Retrieval
- **Core Concept:** Autonomous Agent-driven RAG architecture with explainable step telemetry.
- **Key Innovation:** Zero-hallucination grounded responses with dynamic fallback and transparent multi-module execution.
