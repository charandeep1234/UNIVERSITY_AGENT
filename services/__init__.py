"""
Services package for Smart University Academic Assistant.
"""
from .query_processor import process_student_query, classify_query
from .document_retrieval import retrieve_relevant_document, DocumentRetrievalEngine
from .knowledge_base import (
    get_all_documents,
    get_document_by_name,
    add_document,
    refresh_knowledge_base,
    get_knowledge_base_stats
)
from .llm_service import generate_ai_response

__all__ = [
    'process_student_query',
    'classify_query',
    'retrieve_relevant_document',
    'DocumentRetrievalEngine',
    'get_all_documents',
    'get_document_by_name',
    'add_document',
    'refresh_knowledge_base',
    'get_knowledge_base_stats',
    'generate_ai_response'
]
