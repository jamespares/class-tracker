import sqlite3
import os
from datetime import datetime

DB_PATH = "database/school.db"

def init_database():
    """Initialize the SQLite database with all required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Classes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Homework tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT NOT NULL,
            status TEXT CHECK(status IN ('on_time', 'late', 'absent')) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Comments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            category TEXT CHECK(category IN ('English', 'UOI', 'General Behaviour')) NOT NULL,
            comment TEXT NOT NULL,
            evidence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Dictation tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictation_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            transcript TEXT NOT NULL,
            audio_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Dictation scores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictation_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            task_id INTEGER,
            student_text TEXT NOT NULL,
            score REAL NOT NULL,
            feedback_en TEXT,
            feedback_zh TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (task_id) REFERENCES dictation_tasks (id)
        )
    ''')
    
    # Spelling tests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spelling_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            score INTEGER NOT NULL,
            max_score INTEGER DEFAULT 20,
            week_date TEXT NOT NULL,
            percentage REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Grammar errors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grammar_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            error_type TEXT CHECK(error_type IN (
                'subject-verb agreement', 'verb tense', 'articles', 
                'prepositions', 'word order', 'plurals', 'pronouns'
            )) NOT NULL,
            example TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Todo list
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT CHECK(status IN ('pending', 'in_progress', 'done')) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Essay marking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS essay_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            essay_title TEXT NOT NULL,
            essay_type TEXT CHECK(essay_type IN ('opinion_argumentative', 'creative_narrative')) NOT NULL,
            essay_text TEXT NOT NULL,
            score INTEGER,
            feedback_en TEXT,
            feedback_zh TEXT,
            criteria_breakdown TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    if query.strip().upper().startswith('SELECT'):
        results = cursor.fetchall()
        conn.close()
        return results
    else:
        conn.commit()
        conn.close()
        return cursor.lastrowid