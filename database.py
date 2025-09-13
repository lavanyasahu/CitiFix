import sqlite3
import uuid
from datetime import datetime
import threading
import os

class Database:
    def __init__(self, db_path='civic_issues.db'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.lock = threading.Lock()
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    phone TEXT,
                    role TEXT DEFAULT 'citizen',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    image_data TEXT,
                    user_id TEXT,
                    status TEXT DEFAULT 'pending',
                    admin_notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TEXT,
                    resolved_by TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS authority_signatures (
                    id TEXT PRIMARY KEY,
                    issue_id TEXT NOT NULL,
                    authority_id TEXT NOT NULL,
                    note TEXT,
                    signed_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()

    # user methods
    def create_user(self, username, email, password_hash, phone=None, role='citizen'):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            user_id = str(uuid.uuid4())[:8]
            try:
                cursor.execute('''
                    INSERT INTO users (id, username, email, password_hash, phone, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, username, email, password_hash, phone, role))
                conn.commit()
                return user_id
            except sqlite3.IntegrityError:
                return None
            finally:
                conn.close()

    def get_user_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # issue methods
    def create_issue(self, issue_data):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            issue_id = str(uuid.uuid4())[:8]
            cursor.execute('''
                INSERT INTO issues (id, title, description, category, latitude, longitude, image_data, user_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                issue_id, issue_data.get('title'), issue_data.get('description'),
                issue_data.get('category'), issue_data.get('latitude'),
                issue_data.get('longitude'), issue_data.get('image_data'),
                issue_data.get('user_id'), issue_data.get('status','pending')
            ))
            conn.commit()
            conn.close()
            return issue_id

    def get_all_issues(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM issues ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_issue_by_id(self, issue_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_issue_status(self, issue_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE issues SET status = ? WHERE id = ?', (status, issue_id))
        conn.commit()
        conn.close()
        return True

    # authority signatures and resolve flow
    def add_authority_signature(self, issue_id, authority_id, note=''):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            sig_id = str(uuid.uuid4())[:8]
            cursor.execute('''
                INSERT INTO authority_signatures (id, issue_id, authority_id, note)
                VALUES (?, ?, ?, ?)
            ''', (sig_id, issue_id, authority_id, note))
            conn.commit()
            conn.close()
            return sig_id

    def get_signatures_for_issue(self, issue_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM authority_signatures WHERE issue_id = ? ORDER BY signed_at ASC', (issue_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_issue_resolved(self, issue_id, authority_id, note=''):
        # record signature then mark resolved
        self.add_authority_signature(issue_id, authority_id, note)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE issues SET status = ?, resolved_at = ?, resolved_by = ? WHERE id = ?',
                       ('resolved', datetime.utcnow().isoformat(), authority_id, issue_id))
        conn.commit()
        conn.close()
        return True
