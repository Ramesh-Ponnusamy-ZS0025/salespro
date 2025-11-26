# GTM Conversation Database - SQLite Storage
# Stores conversation history per user for context-aware AI interactions

import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class GTMConversationDB:
    """
    SQLite-based conversation storage for GTM Generator
    Fast, local storage for conversation history and extracted context
    """
    
    def __init__(self, db_path: str = "gtm_conversations.db"):
        """Initialize SQLite database"""
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # Conversations table - stores each message
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                extraction_data TEXT,
                section_updates TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Sessions table - stores session metadata and accumulated context
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                form_data TEXT,
                validation_result TEXT,
                accumulated_context TEXT,
                section_states TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Extracted entities table - stores structured extractions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_entities (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_data TEXT NOT NULL,
                source_message_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_session ON extracted_entities(session_id)")
        
        conn.commit()
        conn.close()
        
        logger.info(f"GTM Conversation DB initialized at {self.db_path}")
    
    def get_connection(self):
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def create_session(self, user_id: str, form_data: Dict) -> str:
        """Create new conversation session"""
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (session_id, user_id, form_data, accumulated_context, 
                                 section_states, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            user_id,
            json.dumps(form_data),
            json.dumps({}),  # Empty context initially
            json.dumps({}),  # Empty sections initially
            'active',
            now,
            now
        ))
        
        conn.commit()
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_or_create_active_session(self, user_id: str, form_data: Dict) -> str:
        """Get active session or create new one"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Try to find active session for this user
        cursor.execute("""
            SELECT session_id FROM sessions 
            WHERE user_id = ? AND status = 'active'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            session_id = row['session_id']
            # Update form data
            self.update_session_form_data(session_id, form_data)
            return session_id
        else:
            return self.create_session(user_id, form_data)
    
    def update_session_form_data(self, session_id: str, form_data: Dict):
        """Update session form data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions 
            SET form_data = ?, updated_at = ?
            WHERE session_id = ?
        """, (json.dumps(form_data), datetime.now(timezone.utc).isoformat(), session_id))
        
        conn.commit()
    
    def add_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        extraction_data: Optional[Dict] = None,
        section_updates: Optional[Dict] = None
    ) -> str:
        """Add message to conversation"""
        message_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (id, user_id, session_id, role, content, timestamp,
                                      extraction_data, section_updates, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message_id,
            user_id,
            session_id,
            role,
            content,
            now,
            json.dumps(extraction_data) if extraction_data else None,
            json.dumps(section_updates) if section_updates else None,
            now
        ))
        
        conn.commit()
        return message_id
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history for session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM conversations 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            msg = dict(row)
            # Parse JSON fields
            if msg.get('extraction_data'):
                msg['extraction_data'] = json.loads(msg['extraction_data'])
            if msg.get('section_updates'):
                msg['section_updates'] = json.loads(msg['section_updates'])
            messages.append(msg)
        
        return messages
    
    def update_accumulated_context(self, session_id: str, context: Dict):
        """Update accumulated context for session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions 
            SET accumulated_context = ?, updated_at = ?
            WHERE session_id = ?
        """, (json.dumps(context), datetime.now(timezone.utc).isoformat(), session_id))
        
        conn.commit()
    
    def update_section_states(self, session_id: str, sections: Dict):
        """Update section states for session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions 
            SET section_states = ?, updated_at = ?
            WHERE session_id = ?
        """, (json.dumps(sections), datetime.now(timezone.utc).isoformat(), session_id))
        
        conn.commit()
    
    def add_extracted_entity(
        self,
        session_id: str,
        user_id: str,
        entity_type: str,
        entity_data: Dict,
        source_message_id: Optional[str] = None
    ):
        """Add extracted entity"""
        entity_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO extracted_entities (id, session_id, user_id, entity_type,
                                           entity_data, source_message_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entity_id,
            session_id,
            user_id,
            entity_type,
            json.dumps(entity_data),
            source_message_id,
            now
        ))
        
        conn.commit()
    
    def get_extracted_entities(self, session_id: str, entity_type: Optional[str] = None) -> List[Dict]:
        """Get extracted entities for session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if entity_type:
            cursor.execute("""
                SELECT * FROM extracted_entities 
                WHERE session_id = ? AND entity_type = ?
                ORDER BY created_at ASC
            """, (session_id, entity_type))
        else:
            cursor.execute("""
                SELECT * FROM extracted_entities 
                WHERE session_id = ?
                ORDER BY created_at ASC
            """, (session_id,))
        
        rows = cursor.fetchall()
        
        entities = []
        for row in rows:
            entity = dict(row)
            entity['entity_data'] = json.loads(entity['entity_data'])
            entities.append(entity)
        
        return entities
    
    def close_session(self, session_id: str):
        """Mark session as completed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions 
            SET status = 'completed', updated_at = ?
            WHERE session_id = ?
        """, (datetime.now(timezone.utc).isoformat(), session_id))
        
        conn.commit()
    
    def get_full_context(self, session_id: str) -> Dict:
        """Get complete context for session including all history"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        conversation_history = self.get_conversation_history(session_id)
        extracted_entities = self.get_extracted_entities(session_id)
        
        # Parse JSON fields from session
        form_data = json.loads(session['form_data']) if session.get('form_data') else {}
        accumulated_context = json.loads(session['accumulated_context']) if session.get('accumulated_context') else {}
        section_states = json.loads(session['section_states']) if session.get('section_states') else {}
        
        return {
            'session_id': session_id,
            'user_id': session['user_id'],
            'form_data': form_data,
            'conversation_history': conversation_history,
            'accumulated_context': accumulated_context,
            'section_states': section_states,
            'extracted_entities': extracted_entities,
            'message_count': len(conversation_history),
            'status': session['status']
        }
    
    def clear_user_sessions(self, user_id: str):
        """Clear all sessions for user (for testing/reset)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get session IDs first
        cursor.execute("SELECT session_id FROM sessions WHERE user_id = ?", (user_id,))
        session_ids = [row['session_id'] for row in cursor.fetchall()]
        
        # Delete related data
        for session_id in session_ids:
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM extracted_entities WHERE session_id = ?", (session_id,))
        
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        
        conn.commit()
        logger.info(f"Cleared {len(session_ids)} sessions for user {user_id}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Global instance
_gtm_conv_db = None

def get_conversation_db() -> GTMConversationDB:
    """Get or create global conversation DB instance"""
    global _gtm_conv_db
    if _gtm_conv_db is None:
        _gtm_conv_db = GTMConversationDB()
    return _gtm_conv_db
