"""
Database package for Smart University Academic Assistant.
"""
from .db import init_db, save_query_log, get_query_history, get_query_by_id, get_analytics_stats, clear_history

__all__ = [
    'init_db',
    'save_query_log',
    'get_query_history',
    'get_query_by_id',
    'get_analytics_stats',
    'clear_history',
]
