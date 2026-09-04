"""
Module 2: AI Agent-Based Query Resolution
Implements the University Query Agent that orchestrates query understanding,
action decision-making, semantic document retrieval, and LLM response generation.
"""
import time
import uuid
from services.query_processor import process_student_query
from services.document_retrieval import retrieve_relevant_document
from services.llm_service import generate_ai_response
from database.db import save_query_log

class UniversityQueryAgent:
    """
    University Query Agent:
    The central autonomous intelligence component of the Smart University Academic Assistant.
    Follows a transparent 7-stage cognitive pipeline designed for clear academic viva demonstration.
    """
    def __init__(self, name: str = "University Query Agent"):
        self.name = name
        self.agent_role = "Autonomous Academic Query Resolver"

    def execute(self, raw_query: str) -> dict:
        """
        Execute the end-to-end query resolution pipeline.
        
        Args:
            raw_query (str): The raw text submitted by the student.
            
        Returns:
            dict: Comprehensive resolution payload containing step telemetry,
                  retrieved context, relevance scores, and generated answer.
        """
        start_time = time.time()
        query_id = f"QRY-{uuid.uuid4().hex[:8].upper()}"
        steps = []

        # =========================================================================
        # STAGE 1: QUERY RECEIVED
        # =========================================================================
        steps.append({
            "step_num": 1,
            "name": "Query Received",
            "description": "Student input captured by web interface",
            "detail": f'Received raw query: "{raw_query.strip() if raw_query else ""}"',
            "status": "completed"
        })

        # =========================================================================
        # STAGE 2: UNDERSTAND & CLEAN QUERY (MODULE 1)
        # =========================================================================
        proc_result = process_student_query(raw_query)
        if not proc_result["is_valid"]:
            latency_ms = int((time.time() - start_time) * 1000)
            steps.append({
                "step_num": 2,
                "name": "Understanding Query",
                "description": "Validation failed: Empty or invalid input",
                "detail": proc_result["error_message"],
                "status": "failed"
            })
            return {
                "success": False,
                "query_id": query_id,
                "error": proc_result["error_message"],
                "steps": steps,
                "latency_ms": latency_ms
            }

        cleaned_query = proc_result["cleaned_query"]
        category = proc_result["category"]
        confidence = proc_result["confidence"]
        keywords = proc_result["keywords"]

        steps.append({
            "step_num": 2,
            "name": "Understanding Query",
            "description": "Normalized text and filtered linguistic noise",
            "detail": f'Cleaned query: "{cleaned_query}" | Extracted keywords: {", ".join(keywords[:5]) if keywords else "None"}',
            "status": "completed"
        })

        # =========================================================================
        # STAGE 3: CLASSIFYING REQUEST (MODULE 1 OUTPUT)
        # =========================================================================
        steps.append({
            "step_num": 3,
            "name": "Classifying Request",
            "description": f"Identified academic category: {category}",
            "detail": f"Category: {category} (Confidence: {int(confidence * 100)}%) — {proc_result['reason']}",
            "status": "completed",
            "category": category,
            "confidence": confidence
        })

        # =========================================================================
        # STAGE 4: DECIDING AGENT ACTION (MODULE 2 DECISION ENGINE)
        # =========================================================================
        # The agent determines whether knowledge base retrieval is required
        if category in ["Attendance", "Examination", "Fees", "Academic", "Course Information", "Admission"]:
            decision_action = "Search University Knowledge Base"
            decision_reason = f"Academic domain query detected ({category}). Triggering semantic vector retrieval."
        else:
            decision_action = "Search University Knowledge Base & General Resolution"
            decision_reason = "General student query. Checking knowledge base index for closest matching university policy."

        steps.append({
            "step_num": 4,
            "name": "Deciding Agent Action",
            "description": f"Action Selected: {decision_action}",
            "detail": decision_reason,
            "status": "completed",
            "action": decision_action
        })

        # =========================================================================
        # STAGE 5: SEARCHING KNOWLEDGE BASE & RETRIEVING CONTEXT (MODULE 3)
        # =========================================================================
        retrieval_result = retrieve_relevant_document(cleaned_query)
        retrieved_doc = retrieval_result["retrieved_document"]
        relevance_score = retrieval_result["relevance_score"]
        relevant_context = retrieval_result["relevant_context"]

        steps.append({
            "step_num": 5,
            "name": "Searching Knowledge Base",
            "description": f"Retrieved source: {retrieved_doc}",
            "detail": f"Document: {retrieved_doc} | Relevance Match: {relevance_score}%",
            "status": "completed",
            "retrieved_document": retrieved_doc,
            "relevance_score": relevance_score
        })

        # =========================================================================
        # STAGE 6: GENERATING AI RESPONSE (GENERATIVE AI / RAG)
        # =========================================================================
        llm_result = generate_ai_response(
            question=cleaned_query,
            context=relevant_context,
            source_doc=retrieved_doc,
            category=category
        )
        final_answer = llm_result["response"]
        is_fallback = llm_result["is_fallback"]
        model_name = llm_result["model_name"]

        steps.append({
            "step_num": 6,
            "name": "Generating AI Response",
            "description": f"Synthesized answer using {model_name}",
            "detail": llm_result["status"],
            "status": "completed",
            "model_name": model_name
        })

        # =========================================================================
        # STAGE 7: RESPONSE READY & TELEMETRY DELIVERY
        # =========================================================================
        latency_ms = int((time.time() - start_time) * 1000)
        steps.append({
            "step_num": 7,
            "name": "Response Ready",
            "description": "Final student-friendly response delivered",
            "detail": f"Total resolution latency: {latency_ms} ms",
            "status": "completed"
        })

        # Save to SQLite database for audit history and analytics
        save_query_log({
            "query_id": query_id,
            "student_query": raw_query.strip(),
            "query_category": category,
            "agent_decision": decision_action,
            "retrieved_document": retrieved_doc,
            "relevance_score": relevance_score,
            "retrieved_context": relevant_context,
            "generated_response": final_answer,
            "is_fallback": is_fallback,
            "latency_ms": latency_ms
        })

        return {
            "success": True,
            "query_id": query_id,
            "student_query": raw_query.strip(),
            "cleaned_query": cleaned_query,
            "category": category,
            "confidence": confidence,
            "agent_decision": decision_action,
            "retrieved_document": retrieved_doc,
            "relevance_score": relevance_score,
            "relevant_context": relevant_context,
            "generated_response": final_answer,
            "is_fallback": is_fallback,
            "model_name": model_name,
            "latency_ms": latency_ms,
            "steps": steps
        }

# Agent Singleton
_agent_instance = None

def get_university_agent() -> UniversityQueryAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = UniversityQueryAgent()
    return _agent_instance
