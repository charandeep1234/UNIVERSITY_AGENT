"""
Database management module for Smart University Academic Assistant.
Handles SQLite operations for query logging, history retrieval, and analytics.
"""
import sqlite3
import os
import uuid
from datetime import datetime

# Resolve absolute path to database file
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "university.db")

def get_connection():
    """Create and return a database connection with dictionary row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database schema if not already created."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id TEXT UNIQUE NOT NULL,
            student_query TEXT NOT NULL,
            query_category TEXT NOT NULL,
            agent_decision TEXT,
            retrieved_document TEXT,
            relevance_score REAL,
            retrieved_context TEXT,
            generated_response TEXT NOT NULL,
            is_fallback INTEGER DEFAULT 0,
            latency_ms INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for fast lookup and filtering
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_timestamp ON query_history(timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_category ON query_history(query_category)")
    
    conn.commit()
    conn.close()

def save_query_log(data):
    """
    Save a completed student query resolution record to the database.
    
    Args:
        data (dict): Contains student_query, query_category, agent_decision,
                     retrieved_document, relevance_score, retrieved_context,
                     generated_response, is_fallback, latency_ms.
    Returns:
        str: Generated unique query_id.
    """
    query_id = data.get("query_id") or f"QRY-{uuid.uuid4().hex[:8].upper()}"
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO query_history (
            query_id, student_query, query_category, agent_decision,
            retrieved_document, relevance_score, retrieved_context,
            generated_response, is_fallback, latency_ms, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        query_id,
        data.get("student_query", "").strip(),
        data.get("query_category", "General"),
        data.get("agent_decision", "Search University Knowledge Base"),
        data.get("retrieved_document", "None"),
        float(data.get("relevance_score", 0.0)),
        data.get("retrieved_context", ""),
        data.get("generated_response", ""),
        1 if data.get("is_fallback", False) else 0,
        int(data.get("latency_ms", 0)),
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    conn.commit()
    conn.close()
    return query_id

def get_query_history(limit=50, category=None, search=None):
    """
    Retrieve query history with optional filtering.
    
    Args:
        limit (int): Maximum records to fetch.
        category (str, optional): Filter by category.
        search (str, optional): Search keyword inside student query or response.
    Returns:
        list[dict]: List of query history records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM query_history WHERE 1=1"
    params = []
    
    if category and category.lower() != "all":
        query += " AND query_category = ?"
        params.append(category)
        
    if search:
        query += " AND (student_query LIKE ? OR generated_response LIKE ? OR retrieved_document LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = [dict(row) for row in rows]
    conn.close()
    return result

def get_query_by_id(query_id):
    """Fetch details of a single query by query_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM query_history WHERE query_id = ?", (query_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_analytics_stats():
    """Calculate summary statistics for dashboard display."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total queries
    cursor.execute("SELECT COUNT(*) as total FROM query_history")
    total_queries = cursor.fetchone()["total"]
    
    # Average relevance score
    cursor.execute("SELECT AVG(relevance_score) as avg_score FROM query_history WHERE relevance_score > 0")
    avg_row = cursor.fetchone()
    avg_score = round(avg_row["avg_score"] or 0.0, 1)
    
    # Average latency
    cursor.execute("SELECT AVG(latency_ms) as avg_lat FROM query_history WHERE latency_ms > 0")
    avg_lat_row = cursor.fetchone()
    avg_latency = round(avg_lat_row["avg_lat"] or 0, 0)
    
    # Queries by category
    cursor.execute("""
        SELECT query_category, COUNT(*) as count 
        FROM query_history 
        GROUP BY query_category 
        ORDER BY count DESC
    """)
    category_counts = [dict(row) for row in cursor.fetchall()]
    
    # Most accessed documents
    cursor.execute("""
        SELECT retrieved_document, COUNT(*) as count 
        FROM query_history 
        WHERE retrieved_document != 'None' AND retrieved_document != '' 
        GROUP BY retrieved_document 
        ORDER BY count DESC LIMIT 5
    """)
    top_documents = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_queries": total_queries,
        "avg_relevance_score": avg_score,
        "avg_latency_ms": avg_latency,
        "category_counts": category_counts,
        "top_documents": top_documents
    }

def clear_history():
    """Clear all records from query_history table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM query_history")
    conn.commit()
    conn.close()
