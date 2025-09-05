import sqlite3
import json
import os
from datetime import datetime
import pandas as pd
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.environ.get('DATABASE_PATH', 'eda_agent.db')
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create analysis_results table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            df_context TEXT,
            analysis_plan TEXT,
            statistical_summary TEXT,
            anomalies TEXT,
            cleaning_suggestions TEXT,
            final_analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create visualizations table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS visualizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            type TEXT,
            title TEXT,
            image_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
        )
        ''')

        # Create chat_sessions table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create chat_messages table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
        ''')

        conn.commit()
        conn.close()

    def save_analysis(self, filename, df_context, analysis_plan, statistical_summary, 
                     anomalies, cleaning_suggestions, visualizations, final_analysis):
        """Save analysis results and visualizations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Save analysis results
            cursor.execute('''
            INSERT INTO analysis_results 
            (filename, df_context, analysis_plan, statistical_summary, anomalies, cleaning_suggestions, final_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename,
                json.dumps(df_context),
                analysis_plan,
                json.dumps(statistical_summary),
                json.dumps(anomalies),
                json.dumps(cleaning_suggestions),
                final_analysis
            ))
            
            analysis_id = cursor.lastrowid

            # Save visualizations with base64 encoded image data
            for viz in visualizations:
                cursor.execute('''
                INSERT INTO visualizations (analysis_id, type, title, image_data)
                VALUES (?, ?, ?, ?)
                ''', (
                    analysis_id,
                    viz[0],  # type
                    viz[1],  # title
                    viz[3]   # base64 encoded image data
                ))

            conn.commit()
            return analysis_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in save_analysis: {str(e)}")
            raise e
        finally:
            conn.close()

    def get_analysis(self, analysis_id):
        """Retrieve analysis results by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get analysis results
            cursor.execute('''
            SELECT * FROM analysis_results WHERE id = ?
            ''', (analysis_id,))
            analysis = cursor.fetchone()

            if not analysis:
                return None

            # Get visualizations with image data
            cursor.execute('''
            SELECT id, type, title, image_data FROM visualizations 
            WHERE analysis_id = ?
            ''', (analysis_id,))
            visualizations = cursor.fetchall()

            return {
                'id': analysis[0],
                'filename': analysis[1],
                'df_context': json.loads(analysis[2]),
                'analysis_plan': analysis[3],
                'statistical_summary': json.loads(analysis[4]),
                'anomalies': json.loads(analysis[5]),
                'cleaning_suggestions': json.loads(analysis[6]),
                'final_analysis': analysis[7],
                'created_at': analysis[8],
                'visualizations': [
                    {
                        'id': v[0],
                        'type': v[1],
                        'title': v[2],
                        'image_data': v[3] if v[3] else None
                    } for v in visualizations
                ]
            }
        except Exception as e:
            logger.error(f"Error in get_analysis: {str(e)}")
            raise
        finally:
            conn.close()

    def get_recent_analyses(self, limit=5):
        """Get most recent analyses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT id, filename, created_at FROM analysis_results 
            ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        finally:
            conn.close()

    def create_chat_session(self, session_name=None):
        """Create a new chat session and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO chat_sessions (session_name)
            VALUES (?)
            ''', (session_name or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",))
            
            session_id = cursor.lastrowid
            conn.commit()
            return session_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in create_chat_session: {str(e)}")
            raise e
        finally:
            conn.close()

    def save_chat_message(self, session_id, role, content):
        """Save a chat message to a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO chat_messages (session_id, role, content)
            VALUES (?, ?, ?)
            ''', (session_id, role, content))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in save_chat_message: {str(e)}")
            raise e
        finally:
            conn.close()

    def get_chat_history(self, session_id):
        """Get chat history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT role, content, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            ''', (session_id,))
            
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error in get_chat_history: {str(e)}")
            raise e
        finally:
            conn.close()

    def get_all_chat_sessions(self):
        """Get all chat sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, session_name, created_at
            FROM chat_sessions
            ORDER BY created_at DESC
            ''')
            
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error in get_all_chat_sessions: {str(e)}")
            raise e
        finally:
            conn.close()

    def delete_chat_session(self, session_id):
        """Delete a chat session and all its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete all messages in the session
            cursor.execute('''
            DELETE FROM chat_messages
            WHERE session_id = ?
            ''', (session_id,))
            
            # Delete the session
            cursor.execute('''
            DELETE FROM chat_sessions
            WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting chat session: {str(e)}")
            return False
        finally:
            conn.close()

    def cleanup_old_files(self, days=7):
        """Clean up old analysis files and database entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get old visualizations
            cursor.execute('''
            SELECT v.image_data 
            FROM visualizations v
            JOIN analysis_results a ON v.analysis_id = a.id
            WHERE a.created_at < datetime('now', ?)
            ''', (f'-{days} days',))
            
            old_files = cursor.fetchall()

            # Delete old files
            for file_data in old_files:
                try:
                    if os.path.exists(file_data[0]):
                        os.remove(file_data[0])
                except Exception as e:
                    logger.error(f"Error deleting file {file_data[0]}: {str(e)}")

            # Delete old chat messages
            cursor.execute('''
            DELETE FROM chat_messages 
            WHERE session_id IN (
                SELECT id FROM chat_sessions 
                WHERE created_at < datetime('now', ?)
            )
            ''', (f'-{days} days',))

            # Delete old chat sessions
            cursor.execute('''
            DELETE FROM chat_sessions 
            WHERE created_at < datetime('now', ?)
            ''', (f'-{days} days',))

            # Delete old visualizations
            cursor.execute('''
            DELETE FROM visualizations 
            WHERE analysis_id IN (
                SELECT id FROM analysis_results 
                WHERE created_at < datetime('now', ?)
            )
            ''', (f'-{days} days',))

            # Delete old analysis results
            cursor.execute('''
            DELETE FROM analysis_results 
            WHERE created_at < datetime('now', ?)
            ''', (f'-{days} days',))

            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in cleanup_old_files: {str(e)}")
            raise e
        finally:
            conn.close()

    def delete_analysis(self, analysis_id):
        """Delete an analysis and its associated files"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # First, get the visualization paths
            cursor.execute('''
            SELECT image_data FROM visualizations 
            WHERE analysis_id = ?
            ''', (analysis_id,))
            
            visualization_paths = cursor.fetchall()
            
            # Delete the files
            for path in visualization_paths:
                try:
                    if os.path.exists(path[0]):
                        os.remove(path[0])
                except Exception as e:
                    logger.error(f"Error deleting file {path[0]}: {str(e)}")
            
            # Delete from visualizations
            cursor.execute('''
            DELETE FROM visualizations 
            WHERE analysis_id = ?
            ''', (analysis_id,))
            
            # Delete from analysis_results
            cursor.execute('''
            DELETE FROM analysis_results 
            WHERE id = ?
            ''', (analysis_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting analysis: {str(e)}")
            return False
        finally:
            conn.close()

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.conn.close()

    def execute_query(self, query, params=None):
        """Execute a query with optional parameters."""
        try:
            with self as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise