"""
Smart University Academic Assistant
Main Flask Application Server
"""
import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Configure utf-8 encoding for Windows standard output
import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import project modules and services
from database.db import (
    init_db,
    get_query_history,
    get_query_by_id,
    get_analytics_stats,
    clear_history
)
from agents.query_agent import get_university_agent
from services.knowledge_base import (
    get_all_documents,
    get_document_by_name,
    add_document,
    refresh_knowledge_base,
    get_knowledge_base_stats
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "smart_university_academic_assistant_secret_2026")

# Initialize SQLite database on startup
init_db()

# Sample prompt chips for convenient student testing
SAMPLE_QUESTIONS = [
    "What is the minimum attendance requirement?",
    "When are semester examinations conducted?",
    "How can I pay my tuition fees?",
    "What are the examination rules?",
    "Tell me about the AI course.",
    "What documents are required for admission?"
]

@app.context_processor
def inject_global_data():
    """Inject common metadata into all Jinja2 templates."""
    kb_stats = get_knowledge_base_stats()
    return {
        "sample_questions": SAMPLE_QUESTIONS,
        "total_kb_docs": kb_stats["total_documents"],
        "app_version": "v1.0.4 - Capstone Edition",
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY", "").strip() and os.getenv("GEMINI_API_KEY") != "your_api_key_here")
    }

# =========================================================================
# APPLICATION ROUTES
# =========================================================================

@app.route("/")
def index():
    """Main Dashboard & Ask Assistant Page."""
    analytics = get_analytics_stats()
    documents = get_all_documents()
    recent_queries = get_query_history(limit=5)
    return render_template(
        "index.html",
        analytics=analytics,
        documents=documents,
        recent_queries=recent_queries,
        active_page="dashboard"
    )

@app.route("/ask", methods=["POST"])
def ask():
    """
    Primary API Endpoint: Process student academic query through the AI Agent.
    Accepts JSON or Form data.
    """
    data = request.get_json(silent=True) or request.form
    raw_query = data.get("query", "").strip()
    
    agent = get_university_agent()
    resolution = agent.execute(raw_query)
    
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(resolution)
        
    # If standard form POST without AJAX
    if not resolution.get("success"):
        flash(resolution.get("error", "An error occurred while processing your query."), "error")
        return redirect(url_for("index"))
        
    return render_template(
        "index.html",
        result=resolution,
        initial_query=raw_query,
        analytics=get_analytics_stats(),
        documents=get_all_documents(),
        recent_queries=get_query_history(limit=5),
        active_page="dashboard"
    )

@app.route("/knowledge-base")
def knowledge_base():
    """Knowledge Base Management Page."""
    docs = get_all_documents()
    stats = get_knowledge_base_stats()
    return render_template(
        "knowledge_base.html",
        documents=docs,
        stats=stats,
        active_page="knowledge_base"
    )

@app.route("/add-document", methods=["POST"])
def handle_add_document():
    """Add a new academic document into the Knowledge Base."""
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "General").strip()
    content = request.form.get("content", "").strip()
    
    success, filename, message = add_document(title, content, category)
    
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": success, "filename": filename, "message": message})
        
    if success:
        flash(f"Document '{title}' added to Knowledge Base and indexed successfully!", "success")
    else:
        flash(f"Error adding document: {message}", "error")
        
    return redirect(url_for("knowledge_base"))

@app.route("/refresh-knowledge-base", methods=["POST"])
def handle_refresh_knowledge_base():
    """Rebuild the vector search index from the documents folder."""
    result = refresh_knowledge_base()
    
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(result)
        
    flash(result["message"], "info")
    return redirect(url_for("knowledge_base"))

@app.route("/history")
def history():
    """View logged queries and resolution audit trail."""
    category_filter = request.args.get("category", "all")
    search_query = request.args.get("search", "").strip()
    
    history_items = get_query_history(limit=100, category=category_filter, search=search_query)
    analytics = get_analytics_stats()
    
    return render_template(
        "history.html",
        history=history_items,
        analytics=analytics,
        current_category=category_filter,
        search_query=search_query,
        active_page="history"
    )

@app.route("/clear-history", methods=["POST"])
def handle_clear_history():
    """Clear all past query logs."""
    clear_history()
    flash("Query history cleared successfully.", "info")
    return redirect(url_for("history"))

@app.route("/about")
def about():
    """About Page detailing the 5 Capstone Modules & Architecture."""
    return render_template("about.html", active_page="about")

@app.route("/api/document/<path:doc_name>")
def api_get_document(doc_name):
    """API endpoint to retrieve specific document text."""
    doc = get_document_by_name(doc_name)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(doc)

@app.route("/api/stats")
def api_get_stats():
    """API endpoint for live dashboard telemetry."""
    stats = get_analytics_stats()
    kb_stats = get_knowledge_base_stats()
    return jsonify({**stats, **kb_stats})

# =========================================================================
# APPLICATION ENTRYPOINT
# =========================================================================

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print("\n" + "="*70)
    print(" 🎓 SMART UNIVERSITY ACADEMIC ASSISTANT - GENERATIVE AI CAPSTONE")
    print("="*70)
    print(f" * Server running on: http://127.0.0.1:{port}")
    print(" * AI Agent: University Query Agent (Active)")
    print(" * Knowledge Base: Indexed and Ready")
    print(f" * Gemini API: {'Configured' if os.getenv('GEMINI_API_KEY') else 'Offline (Fallback RAG Active)'}")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
