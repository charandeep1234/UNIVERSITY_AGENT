"""
Automated Test Verification Script for Smart University Academic Assistant
Tests all 5 modules, database, query agent, and document retrieval.
"""
import os
import sys

# Configure UTF-8 encoding for Windows standard output
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure current directory is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.query_processor import process_student_query
from services.document_retrieval import retrieve_relevant_document, get_retrieval_engine
from services.knowledge_base import get_all_documents, add_document, refresh_knowledge_base
from agents.query_agent import get_university_agent
from database.db import init_db, get_query_history, get_analytics_stats

def test_all():
    print("=" * 60)
    print("[TEST] RUNNING AUTOMATED CAPSTONE SYSTEM VERIFICATION")
    print("=" * 60)

    # 1. Test Database Initialization
    print("\n[Test 1] Initializing SQLite Database...")
    init_db()
    stats = get_analytics_stats()
    print(f"[OK] SQLite Database ready. Current total queries: {stats['total_queries']}")

    # 2. Test Knowledge Base & Document Ingestion
    print("\n[Test 2] Testing Knowledge Base Ingestion...")
    docs = get_all_documents()
    print(f"[OK] Found {len(docs)} documents in knowledge base.")
    assert len(docs) >= 6, "Expected at least 6 initial knowledge base documents!"
    for d in docs:
        print(f"  - {d['filename']} ({d['category']}): {d['word_count']} words")

    # 3. Test Retrieval Engine Indexing
    print("\n[Test 3] Testing Semantic Vector Retrieval Engine...")
    engine = get_retrieval_engine()
    print(f"[OK] Indexed {len(engine.chunks)} semantic chunks.")
    assert len(engine.chunks) > 0, "Expected chunks to be indexed!"

    # 4. Test Sample Queries on Query Processor (Module 1) and Retrieval (Module 3)
    sample_test_cases = [
        ("What is the minimum attendance requirement?", "Attendance", "attendance_policy.txt"),
        ("When are semester examinations conducted?", ["Examination", "Academic"], ["academic_calendar.txt", "exam_rules.txt"]),
        ("How can I pay my tuition fees?", "Fees", "fees_information.txt"),
        ("What are the examination rules?", "Examination", "exam_rules.txt"),
        ("Tell me about the AI course.", "Course Information", "course_information.txt"),
        ("What documents are required for admission?", "Admission", "admission_information.txt")
    ]

    print("\n[Test 4] Testing Query Processor & Semantic Retrieval on All Sample Queries...")
    for query, expected_cat, expected_doc in sample_test_cases:
        proc = process_student_query(query)
        assert proc["is_valid"], f"Query should be valid: {query}"
        
        # Verify category
        if isinstance(expected_cat, list):
            cat_ok = proc["category"] in expected_cat
        else:
            cat_ok = proc["category"] == expected_cat
        assert cat_ok, f"Category mismatch for '{query}': got {proc['category']}, expected {expected_cat}"

        # Test retrieval
        ret = retrieve_relevant_document(proc["cleaned_query"])
        assert ret["found"], f"Retrieval failed for: {query}"
        
        if isinstance(expected_doc, list):
            doc_ok = ret["retrieved_document"] in expected_doc
        else:
            doc_ok = ret["retrieved_document"] == expected_doc
        assert doc_ok, f"Document match mismatch for '{query}': got {ret['retrieved_document']}, expected {expected_doc}"
        
        print(f"[OK] Query: '{query}' -> Category: [{proc['category']}] -> Doc: [{ret['retrieved_document']}] (Score: {ret['relevance_score']}%)")

    # 5. Test Empty Query Validation
    print("\n[Test 5] Testing Empty Query Error Handling...")
    empty_proc = process_student_query("")
    assert not empty_proc["is_valid"], "Empty query should be marked invalid!"
    print(f"[OK] Correctly handled empty query with message: '{empty_proc['error_message']}'")

    # 6. Test University Query Agent End-to-End (Module 2)
    print("\n[Test 6] Testing University Query Agent (End-to-End Pipeline)...")
    agent = get_university_agent()
    result = agent.execute("What is the minimum attendance requirement?")
    assert result["success"], "Agent execution should succeed!"
    assert len(result["steps"]) == 7, f"Expected 7 telemetry steps, got {len(result['steps'])}"
    assert result["relevance_score"] > 70, f"Expected high relevance score, got {result['relevance_score']}"
    assert result["retrieved_document"] == "attendance_policy.txt"
    assert "75" in result["generated_response"] or "attendance" in result["generated_response"].lower()
    print(f"[OK] Agent successfully executed 7 steps in {result['latency_ms']} ms.")
    print(f"[OK] Model used: {result['model_name']}")
    print(f"[OK] Generated answer snippet: {result['generated_response'][:120]}...")

    # 7. Test Adding New Knowledge (Module 4) & Searching it
    print("\n[Test 7] Testing Dynamic Knowledge Ingestion...")
    test_title = "Hostel Regulations and Gate Timings"
    test_content = "All residential students must return to the university hostel campus before the curfew time of 9:30 PM on weekdays. Gate passes must be signed by the chief warden."
    
    success, fname, msg = add_document(test_title, test_content, "General")
    assert success, f"Failed to add test document: {msg}"
    print(f"[OK] Added test document: {fname}")
    
    # Query newly added document
    new_query = "What is the hostel gate curfew time?"
    new_ret = retrieve_relevant_document(new_query)
    print(f"[OK] Retrieval for newly added knowledge: Doc: [{new_ret['retrieved_document']}] (Score: {new_ret['relevance_score']}%)")
    assert new_ret["found"] and new_ret["retrieved_document"] == fname, "Failed to retrieve newly added document!"

    # 8. Test Database Logging
    print("\n[Test 8] Testing SQLite History Logging...")
    hist = get_query_history(limit=5)
    assert len(hist) > 0, "Expected at least one logged query in history!"
    print(f"[OK] Successfully retrieved {len(hist)} query records from SQLite history.")
    print(f"  Latest Log: [{hist[0]['query_id']}] Category: {hist[0]['query_category']} | Doc: {hist[0]['retrieved_document']}")

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL AUTOMATED CAPSTONE TESTS PASSED SUCCESSFULLY (8/8)!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_all()
