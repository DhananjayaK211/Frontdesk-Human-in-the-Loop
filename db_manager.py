import sqlite3
import time
from typing import List, Dict, Optional

DB_NAME = 'frontdesk_hilit.db'
TIMEOUT_SECONDS = 3600  # 1 hour timeout for requests

class DBManager:
    """Manages the SQLite database for help requests and knowledge base."""

    def __init__(self):
        self._conn = sqlite3.connect(DB_NAME, check_same_thread=False) 
        self._conn.row_factory = sqlite3.Row
        self._setup_tables()

    def _setup_tables(self):
        """Initializes the required tables."""
        cursor = self._conn.cursor()

        # 1. Help Requests Table (Lifecycle: PENDING -> RESOLVED / UNRESOLVED)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS help_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,         -- Links to the customer for follow-up
                caller_question TEXT NOT NULL,     -- The question the AI couldn't answer
                status TEXT NOT NULL,              -- PENDING, RESOLVED, UNRESOLVED
                supervisor_answer TEXT,            -- The final answer provided by the human
                created_at REAL NOT NULL,          -- Timestamp for timeout handling
                resolved_at REAL
            )
        ''')

        # 2. Knowledge Base Table (Self-improvement/Learning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_key TEXT UNIQUE NOT NULL, -- Lowercase, stripped key for lookup
                answer TEXT NOT NULL,
                source_request_id INTEGER,         -- Link back to the request that created it
                updated_at REAL NOT NULL
            )
        ''')
        self._conn.commit()
    
    # --- Help Request Methods ---
    
    def create_request(self, customer_id: str, question: str) -> int:
        """Creates a new PENDING help request."""
        timestamp = time.time()
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO help_requests (customer_id, caller_question, status, created_at) VALUES (?, ?, ?, ?)",
            (customer_id, question, 'PENDING', timestamp)
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_pending_requests(self) -> List[Dict]:
        """Fetches all PENDING requests and marks timed-out requests as UNRESOLVED."""
        cursor = self._conn.cursor()
        
        # Timeout handling
        timeout_limit = time.time() - TIMEOUT_SECONDS
        cursor.execute(
            "UPDATE help_requests SET status = 'UNRESOLVED' WHERE status = 'PENDING' AND created_at < ?",
            (timeout_limit,)
        )
        self._conn.commit()
        
        cursor.execute("SELECT * FROM help_requests WHERE status = 'PENDING' ORDER BY created_at ASC")
        return [dict(row) for row in cursor.fetchall()]

    def resolve_request(self, request_id: int, answer: str) -> Optional[Dict]:
        """Marks a request as RESOLVED."""
        timestamp = time.time()
        cursor = self._conn.cursor()
        
        cursor.execute(
            "UPDATE help_requests SET status = 'RESOLVED', supervisor_answer = ?, resolved_at = ? WHERE id = ? AND status = 'PENDING'",
            (answer, timestamp, request_id)
        )
        self._conn.commit()

        if cursor.rowcount == 0:
            return None 
            
        cursor.execute("SELECT * FROM help_requests WHERE id = ?", (request_id,))
        return dict(cursor.fetchone())

    def get_all_requests(self) -> List[Dict]:
        """Fetches all requests for history view."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM help_requests ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    # --- Knowledge Base Methods ---

    def save_learned_answer(self, question: str, answer: str, request_id: int):
        """Saves or updates an answer in the knowledge base."""
        question_key = question.lower().strip()
        timestamp = time.time()
        cursor = self._conn.cursor()

        # Check if key exists
        cursor.execute("SELECT id FROM knowledge_base WHERE question_key = ?", (question_key,))
        existing = cursor.fetchone()

        if existing:
            # Update existing entry
            cursor.execute(
                "UPDATE knowledge_base SET answer = ?, source_request_id = ?, updated_at = ? WHERE id = ?",
                (answer, request_id, timestamp, existing['id'])
            )
        else:
            # Insert new entry
            cursor.execute(
                "INSERT INTO knowledge_base (question_key, answer, source_request_id, updated_at) VALUES (?, ?, ?, ?)",
                (question_key, answer, request_id, timestamp)
            )
        self._conn.commit()

    def get_kb_answer(self, question: str) -> Optional[str]:
        """
        Retrieves an answer from the knowledge base using the exact cleaned key.
        This provides the desired demonstration of strict self-correction.
        """
        question_key = question.lower().strip()
        cursor = self._conn.cursor()
        
        # Strict retrieval for clear demonstration of learning
        cursor.execute("SELECT answer FROM knowledge_base WHERE question_key = ?", (question_key,))
        row = cursor.fetchone()
        return row['answer'] if row else None
        
    def get_all_kb_entries(self) -> List[Dict]:
        """Fetches all knowledge base entries for the view."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM knowledge_base ORDER BY updated_at DESC")
        return [dict(row) for row in cursor.fetchall()]