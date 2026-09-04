"""
End-to-End Route and API Verification Script for Smart University Academic Assistant
Validates all Flask endpoints, JSON schemas, HTML responses, and student query workflows.
"""
import urllib.request
import urllib.parse
import json
import sys

# Configure UTF-8 encoding for console
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "TestClient/1.0"})
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status, response.read().decode('utf-8')

def post_json(path, data):
    url = f"{BASE_URL}{path}"
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "TestClient/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.status, json.loads(response.read().decode('utf-8'))

def test_routes():
    print("=" * 65)
    print("[HTTP TEST] VERIFYING ALL FLASK APPLICATION ENDPOINTS")
    print("=" * 65)

    # 1. Test Dashboard Route GET /
    print("\n[Route 1] Testing GET / (Dashboard)...")
    status, html = get("/")
    assert status == 200, f"Expected status 200, got {status}"
    assert "Smart University" in html, "Missing Brand in HTML"
    assert "Your academic questions" in html, "Missing Hero title"
    assert "NEW ACADEMIC QUERY" in html, "Missing Query Section"
    assert "What is the minimum attendance requirement?" in html, "Missing Suggestion Chips"
    print("[OK] GET / rendered successfully with Hero, Sidebar, and Query Card.")

    # 2. Test AJAX Query Resolution POST /ask (Attendance Query)
    print("\n[Route 2] Testing POST /ask (JSON Attendance Query)...")
    status, data = post_json("/ask", {"query": "What is the minimum attendance requirement?"})
    assert status == 200, f"Expected 200, got {status}"
    assert data["success"], f"Query failed: {data}"
    assert data["category"] == "Attendance", f"Expected Attendance, got {data['category']}"
    assert data["retrieved_document"] == "attendance_policy.txt", f"Wrong doc: {data['retrieved_document']}"
    assert data["relevance_score"] >= 75.0, f"Low relevance score: {data['relevance_score']}"
    assert len(data["steps"]) == 7, f"Expected 7 steps, got {len(data['steps'])}"
    print(f"[OK] Category: [{data['category']}] | Doc: [{data['retrieved_document']}] | Score: {data['relevance_score']}%")
    print(f"[OK] Response: {data['generated_response'][:100]}...")

    # 3. Test AJAX Query Resolution POST /ask (Exam Query)
    print("\n[Route 3] Testing POST /ask (JSON Exam Rules Query)...")
    status, data = post_json("/ask", {"query": "What are the rules for semester examinations and hall ticket?"})
    assert status == 200 and data["success"]
    assert data["category"] in ["Examination", "Academic"]
    assert data["retrieved_document"] == "exam_rules.txt"
    print(f"[OK] Category: [{data['category']}] | Doc: [{data['retrieved_document']}] | Score: {data['relevance_score']}%")

    # 4. Test Knowledge Base Page GET /knowledge-base
    print("\n[Route 4] Testing GET /knowledge-base...")
    status, html = get("/knowledge-base")
    assert status == 200
    assert "University Knowledge Base" in html
    assert "ADD NEW KNOWLEDGE" in html
    assert "attendance_policy.txt" in html
    assert "exam_rules.txt" in html
    print("[OK] GET /knowledge-base rendered with all documents and Add Knowledge form.")

    # 5. Test Query History Page GET /history
    print("\n[Route 5] Testing GET /history...")
    status, html = get("/history")
    assert status == 200
    assert "Student Query History" in html
    assert "attendance_policy.txt" in html or "exam_rules.txt" in html
    print("[OK] GET /history rendered past queries from SQLite.")

    # 6. Test About & Architecture Page GET /about
    print("\n[Route 6] Testing GET /about...")
    status, html = get("/about")
    assert status == 200
    assert "End-to-End System Workflow" in html
    assert "Student Query Processing" in html
    assert "AI Agent-Based Query Resolution" in html
    assert "Academic Document Retrieval" in html
    assert "Knowledge Base Management" in html
    assert "User Interface and Response Delivery" in html
    print("[OK] GET /about rendered 5 modules breakdown and RAG diagram.")

    # 7. Test Document API GET /api/document/attendance_policy.txt
    print("\n[Route 7] Testing GET /api/document/attendance_policy.txt...")
    status, doc_json_str = get("/api/document/attendance_policy.txt")
    doc_data = json.loads(doc_json_str)
    assert status == 200
    assert doc_data["category"] == "Attendance"
    assert "75 percent" in doc_data["content"]
    print(f"[OK] Document API returned '{doc_data['title']}' ({doc_data['word_count']} words).")

    # 8. Test Stats API GET /api/stats
    print("\n[Route 8] Testing GET /api/stats...")
    status, stats_json_str = get("/api/stats")
    stats_data = json.loads(stats_json_str)
    assert status == 200
    assert stats_data["total_queries"] >= 2
    assert stats_data["total_documents"] >= 6
    print(f"[OK] Stats API: Total Queries: {stats_data['total_queries']} | Total Docs: {stats_data['total_documents']} | Avg Score: {stats_data['avg_relevance_score']}%")

    print("\n" + "=" * 65)
    print("[SUCCESS] ALL HTTP ENDPOINTS & API WORKFLOWS VERIFIED (8/8)!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    test_routes()
