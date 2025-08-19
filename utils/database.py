import sqlite3
import os
from datetime import datetime

DB_PATH = "database/school.db"

def init_database():
    """Initialize the SQLite database with all required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users/Teachers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT CHECK(role IN ('teacher', 'admin')) DEFAULT 'teacher',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create founding team accounts only
    import hashlib
    
    # Founding team accounts with random passwords
    
    # James - Founder (password: rx9K2p)
    james_password = hashlib.sha256("rx9K2p".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, full_name, role) 
        VALUES ('james', ?, 'James Pares', 'admin')
    ''', (james_password,))
    
    # Joe - Founder (password: mL7Ht3)  
    joe_password = hashlib.sha256("mL7Ht3".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, full_name, role) 
        VALUES ('joe', ?, 'Joe (Founder)', 'admin')
    ''', (joe_password,))
    
    # Jake - Founder (password: qN4Xv8)
    jake_password = hashlib.sha256("qN4Xv8".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, full_name, role) 
        VALUES ('jake', ?, 'Jake (Founder)', 'admin')
    ''', (jake_password,))
    

    # Students table (now linked to teachers)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Classes table (now linked to teachers)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id),
            UNIQUE(name, teacher_id)
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
    
    # Migrate existing database to add teacher_id columns if they don't exist
    try:
        # Check if classes table has teacher_id column
        cursor.execute("PRAGMA table_info(classes)")
        classes_columns = [col[1] for col in cursor.fetchall()]
        if 'teacher_id' not in classes_columns:
            cursor.execute("ALTER TABLE classes ADD COLUMN teacher_id INTEGER DEFAULT 1")
            cursor.execute("UPDATE classes SET teacher_id = 1 WHERE teacher_id IS NULL")
        
        # Check if students table has teacher_id column
        cursor.execute("PRAGMA table_info(students)")
        students_columns = [col[1] for col in cursor.fetchall()]
        if 'teacher_id' not in students_columns:
            cursor.execute("ALTER TABLE students ADD COLUMN teacher_id INTEGER DEFAULT 1")
            cursor.execute("UPDATE students SET teacher_id = 1 WHERE teacher_id IS NULL")
            
    except Exception as e:
        print(f"Migration warning: {e}")
    
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