"""
Module 4: Knowledge Base Management
Handles reading, listing, adding, and refreshing university knowledge base documents.
"""
import os
import glob
import re
from datetime import datetime
from services.document_retrieval import get_retrieval_engine, DOCUMENTS_DIR

# Nice display titles and descriptions for default documents
DOC_METADATA = {
    "attendance_policy.txt": {
        "title": "Attendance Policy",
        "category": "Attendance",
        "description": "University attendance regulations, 75% minimum requirement, medical leave, and condonation rules."
    },
    "exam_rules.txt": {
        "title": "Examination Rules",
        "category": "Examination",
        "description": "Rules and guidelines for semester examinations, hall tickets, timings, and malpractice policies."
    },
    "academic_calendar.txt": {
        "title": "Academic Calendar",
        "category": "Academic",
        "description": "Important academic dates, semester commencement, mid-term tests, final exams, and holidays."
    },
    "fees_information.txt": {
        "title": "Fees Information",
        "category": "Fees",
        "description": "Tuition fee structure, online payment portal, payment deadlines, and late fee penalties."
    },
    "course_information.txt": {
        "title": "Course Information",
        "category": "Course Information",
        "description": "B.Tech and M.Tech curriculum, core subjects, AI specialization, and capstone project requirements."
    },
    "admission_information.txt": {
        "title": "Admission Information",
        "category": "Admission",
        "description": "Undergraduate admission eligibility, required certificates checklist, and application process."
    }
}

def sanitize_filename(name: str) -> str:
    """Convert user title to safe filename ending in .txt."""
    clean = re.sub(r"[^\w\s-]", "", name).strip().lower()
    clean = re.sub(r"[\s-]+", "_", clean)
    if not clean.endswith(".txt"):
        clean += ".txt"
    return clean

def get_all_documents() -> list[dict]:
    """
    Retrieve metadata and summary for all documents currently in the knowledge base.
    """
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.txt"))
    
    docs_list = []
    for fpath in files:
        filename = os.path.basename(fpath)
        stats = os.stat(fpath)
        mod_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
        size_kb = round(stats.st_size / 1024, 2)
        
        # Read snippet
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            word_count = len(content.split())
            first_lines = [line for line in content.splitlines() if line.strip()]
            preview = " ".join(first_lines[:3])[:220] + "..." if first_lines else ""
        except Exception:
            content = ""
            word_count = 0
            preview = ""
            
        meta = DOC_METADATA.get(filename, {
            "title": filename.replace(".txt", "").replace("_", " ").title(),
            "category": "General",
            "description": preview or "Custom university document."
        })
        
        docs_list.append({
            "filename": filename,
            "title": meta.get("title", filename),
            "category": meta.get("category", "General"),
            "description": meta.get("description", preview),
            "word_count": word_count,
            "size_kb": size_kb,
            "last_modified": mod_time,
            "content": content
        })
        
    return sorted(docs_list, key=lambda d: d["title"])

def get_document_by_name(filename: str) -> dict | None:
    """Fetch full document content and metadata by filename."""
    # Prevent path traversal
    safe_name = os.path.basename(filename)
    fpath = os.path.join(DOCUMENTS_DIR, safe_name)
    
    if not os.path.exists(fpath):
        return None
        
    try:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        stats = os.stat(fpath)
        meta = DOC_METADATA.get(safe_name, {
            "title": safe_name.replace(".txt", "").replace("_", " ").title(),
            "category": "General",
            "description": "University document."
        })
        return {
            "filename": safe_name,
            "title": meta["title"],
            "category": meta["category"],
            "content": content,
            "word_count": len(content.split()),
            "last_modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
        }
    except Exception as e:
        print(f"[KnowledgeBase] Error loading document {safe_name}: {e}")
        return None

def add_document(title: str, content: str, category: str = "General") -> tuple[bool, str, str]:
    """
    Save a new document into the knowledge base and rebuild vector index.
    
    Returns:
        tuple: (success: bool, filename_or_error: str, message: str)
    """
    if not title or not title.strip():
        return False, "", "Document title cannot be empty."
    if not content or not content.strip():
        return False, "", "Document content cannot be empty."
        
    filename = sanitize_filename(title)
    fpath = os.path.join(DOCUMENTS_DIR, filename)
    
    try:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content.strip())
            
        # Register in metadata dictionary
        DOC_METADATA[filename] = {
            "title": title.strip(),
            "category": category.strip() or "General",
            "description": content.strip()[:180] + "..."
        }
        
        # Rebuild vector index
        engine = get_retrieval_engine()
        engine.build_index()
        
        return True, filename, f"Document '{title}' added and indexed successfully."
    except Exception as e:
        return False, "", f"Failed to save document: {str(e)}"

def refresh_knowledge_base() -> dict:
    """
    Reload all documents and rebuild the semantic search vector index.
    """
    engine = get_retrieval_engine()
    engine.build_index()
    docs = get_all_documents()
    return {
        "status": "success",
        "total_documents": len(docs),
        "total_chunks": len(engine.chunks),
        "message": f"Successfully refreshed Knowledge Base with {len(docs)} documents and {len(engine.chunks)} semantic chunks."
    }

def get_knowledge_base_stats() -> dict:
    """Get high-level summary of knowledge base for the dashboard."""
    docs = get_all_documents()
    engine = get_retrieval_engine()
    return {
        "total_documents": len(docs),
        "total_chunks": len(engine.chunks),
        "documents": [{"title": d["title"], "filename": d["filename"], "category": d["category"]} for d in docs]
    }
