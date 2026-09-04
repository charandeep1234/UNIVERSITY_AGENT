"""
Module 1: Student Query Processing & Classification
Handles student input validation, text cleaning, normalization,
keyword extraction, and category classification.
"""
import re
import unicodedata

# Defined Category taxonomy as required by project specification
CATEGORIES = [
    "Attendance",
    "Examination",
    "Fees",
    "Academic",
    "Course Information",
    "Admission",
    "General"
]

# Domain Keyword Dictionary for Explainable Viva Demonstration
CATEGORY_KEYWORDS = {
    "Attendance": [
        "attendance", "attend", "present", "absent", "75%", "75 percent", "percent",
        "medical leave", "medical certificate", "condonation", "detention", "detained",
        "shortage", "duty leave", "od", "leave application", "absence"
    ],
    "Examination": [
        "exam", "examination", "test", "hall ticket", "admit card", "malpractice",
        "revaluation", "supplementary", "arrear", "backlog", "invigilator", "grading",
        "answer script", "paper correction", "cat-1", "cat-2", "midterm", "end semester",
        "rules for examination", "exam rules", "exam timings", "cloakroom"
    ],
    "Fees": [
        "fee", "fees", "tuition", "payment", "pay", "due date", "deadline",
        "late fee", "penalty", "installment", "scholarship", "refund", "upi",
        "net banking", "finance portal", "challan", "receipt", "surcharge"
    ],
    "Academic": [
        "calendar", "academic calendar", "semester start", "commencement",
        "holiday", "vacation", "winter break", "festival break", "instruction day",
        "working days", "convocation", "fest", "schedule", "events", "academic year"
    ],
    "Course Information": [
        "course", "curriculum", "syllabus", "subject", "credits", "btech",
        "b.tech", "mtech", "computer science", "artificial intelligence", "ai",
        "machine learning", "data science", "electives", "prerequisites",
        "duration", "internship", "capstone", "degree requirements"
    ],
    "Admission": [
        "admission", "eligibility", "apply", "application", "document", "documents",
        "required for admission", "admission documents", "marksheet", "10th", "12th",
        "entrance exam", "rank", "cutoff", "jee", "counseling", "transfer certificate",
        "migration", "caste certificate", "quota", "seat allocation"
    ]
}

def clean_query_text(raw_text: str) -> str:
    """
    Clean and normalize user query text.
    - Strips leading/trailing whitespaces.
    - Normalizes unicode characters.
    - Removes unnecessary punctuation while preserving question words and percentages.
    - Reduces repeated spaces.
    """
    if not raw_text:
        return ""
    
    # Normalize unicode (e.g., curly quotes, special symbols)
    text = unicodedata.normalize("NFKD", raw_text)
    
    # Remove unwanted special characters but keep alphanumeric, %, ?, and spaces
    text = re.sub(r"[^\w\s%?.,-]", " ", text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_keywords(cleaned_text: str) -> list[str]:
    """
    Extract meaningful keywords by filtering out common English stop words.
    """
    stop_words = {
        "what", "when", "how", "why", "where", "which", "who", "whom", "is", "are",
        "the", "a", "an", "for", "to", "of", "in", "on", "at", "by", "with", "about",
        "can", "i", "my", "me", "we", "our", "you", "your", "tell", "please", "give",
        "know", "conduct", "conducted", "there", "do", "does", "did", "and", "or", "as"
    }
    
    words = re.findall(r"\b[a-zA-Z0-9%]+\b", cleaned_text.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 1]
    return keywords

def classify_query(cleaned_text: str) -> tuple[str, float, str]:
    """
    Classify the student query into one of the designated categories.
    Uses pattern matching and keyword score weighting.
    
    Returns:
        tuple: (detected_category, confidence_score, matched_reason)
    """
    lower_text = cleaned_text.lower()
    
    # Check specific high-priority multi-word phrases first
    if "admission" in lower_text or "documents required" in lower_text or "eligibility" in lower_text:
        return "Admission", 0.95, "Matched admission keyword pattern"
    if "fee" in lower_text or "tuition" in lower_text or "pay" in lower_text or "late fee" in lower_text:
        return "Fees", 0.95, "Matched financial/fees keyword pattern"
    if "attendance" in lower_text or "75%" in lower_text or "75 percent" in lower_text or "medical leave" in lower_text:
        return "Attendance", 0.95, "Matched attendance policy keyword pattern"
    if "calendar" in lower_text or "holiday" in lower_text or "commence" in lower_text or "vacation" in lower_text:
        return "Academic", 0.92, "Matched academic schedule keyword pattern"
    if "course" in lower_text or "syllabus" in lower_text or "ai course" in lower_text or "curriculum" in lower_text or "btech" in lower_text:
        return "Course Information", 0.94, "Matched course & curriculum keyword pattern"
    if "exam" in lower_text or "hall ticket" in lower_text or "malpractice" in lower_text or "revaluation" in lower_text:
        return "Examination", 0.94, "Matched examination rules keyword pattern"
        
    # Score against keyword dictionary
    scores = {cat: 0 for cat in CATEGORIES if cat != "General"}
    
    for cat, kw_list in CATEGORY_KEYWORDS.items():
        for kw in kw_list:
            if kw in lower_text:
                # Give higher weight to exact multi-word matches
                weight = 2 if " " in kw else 1
                scores[cat] += weight
                
    best_cat = max(scores, key=scores.get)
    max_score = scores[best_cat]
    
    if max_score > 0:
        confidence = min(0.60 + (max_score * 0.15), 0.98)
        return best_cat, round(confidence, 2), f"Matched {max_score} category keyword signals"
    
    return "General", 0.50, "Default classification (general university inquiry)"

def process_student_query(raw_query: str) -> dict:
    """
    Main entry point for Module 1: Student Query Processing.
    
    Args:
        raw_query (str): The raw input query typed by the student.
        
    Returns:
        dict: Processed query details or error details if invalid.
    """
    if not raw_query or not raw_query.strip():
        return {
            "is_valid": False,
            "error_message": "Please enter a question before submitting.",
            "raw_query": "",
            "cleaned_query": "",
            "category": "General",
            "confidence": 0.0,
            "keywords": []
        }
        
    cleaned = clean_query_text(raw_query)
    category, confidence, reason = classify_query(cleaned)
    keywords = extract_keywords(cleaned)
    
    return {
        "is_valid": True,
        "raw_query": raw_query.strip(),
        "cleaned_query": cleaned,
        "category": category,
        "confidence": confidence,
        "reason": reason,
        "keywords": keywords
    }
