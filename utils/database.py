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
    
    # Demo User (password: demo)
    demo_password = hashlib.sha256("demo".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, full_name, role) 
        VALUES ('demo', ?, 'Demo Teacher', 'teacher')
    ''', (demo_password,))
    

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

def insert_demo_data():
    """Insert comprehensive test data for demo purposes"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get the demo user's ID
        cursor.execute("SELECT id FROM users WHERE username = 'demo'")
        demo_user_result = cursor.fetchone()
        if not demo_user_result:
            return False, "Demo user not found"
            
        demo_user_id = demo_user_result[0]
        
        # Clear existing demo data first
        cursor.execute("DELETE FROM homework WHERE student_id IN (SELECT id FROM students WHERE teacher_id = ?)", (demo_user_id,))
        cursor.execute("DELETE FROM comments WHERE student_id IN (SELECT id FROM students WHERE teacher_id = ?)", (demo_user_id,))
        cursor.execute("DELETE FROM spelling_tests WHERE student_id IN (SELECT id FROM students WHERE teacher_id = ?)", (demo_user_id,))
        cursor.execute("DELETE FROM grammar_errors WHERE student_id IN (SELECT id FROM students WHERE teacher_id = ?)", (demo_user_id,))
        cursor.execute("DELETE FROM dictation_scores WHERE student_id IN (SELECT id FROM students WHERE teacher_id = ?)", (demo_user_id,))
        cursor.execute("DELETE FROM essay_marks WHERE student_id IN (SELECT id FROM students WHERE teacher_id = ?)", (demo_user_id,))
        cursor.execute("DELETE FROM students WHERE teacher_id = ?", (demo_user_id,))
        cursor.execute("DELETE FROM classes WHERE teacher_id = ?", (demo_user_id,))
        
        # Create demo classes
        demo_classes = [
            ("5A Math", demo_user_id),
            ("5B English", demo_user_id),
            ("6A Science", demo_user_id)
        ]
        
        class_ids = []
        for class_name, teacher_id in demo_classes:
            cursor.execute("INSERT INTO classes (name, teacher_id) VALUES (?, ?)", (class_name, teacher_id))
            class_ids.append(cursor.lastrowid)
        
        # Create demo students
        demo_students = [
            ("Emma Thompson", "5A Math", demo_user_id),
            ("Lucas Chen", "5A Math", demo_user_id),
            ("Sophia Rodriguez", "5A Math", demo_user_id),
            ("Oliver Kim", "5B English", demo_user_id),
            ("Ava Patel", "5B English", demo_user_id),
            ("Noah Johnson", "5B English", demo_user_id),
            ("Isabella Brown", "6A Science", demo_user_id),
            ("Ethan Davis", "6A Science", demo_user_id),
            ("Mia Wilson", "6A Science", demo_user_id),
            ("Benjamin Garcia", "6A Science", demo_user_id)
        ]
        
        student_ids = []
        for name, class_name, teacher_id in demo_students:
            cursor.execute("INSERT INTO students (name, class_name, teacher_id) VALUES (?, ?, ?)", (name, class_name, teacher_id))
            student_ids.append(cursor.lastrowid)
        
        # Create demo homework records (last 10 days)
        import datetime
        homework_statuses = ['on_time', 'late', 'absent']
        
        for student_id in student_ids[:6]:  # First 6 students
            for days_ago in range(10):
                date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
                import random
                status = random.choices(homework_statuses, weights=[70, 20, 10])[0]  # Most homework on time
                cursor.execute("INSERT INTO homework (student_id, date, status) VALUES (?, ?, ?)", 
                             (student_id, date, status))
        
        # Create demo comments
        demo_comments = [
            (student_ids[0], "English", "Excellent reading comprehension and vocabulary usage", "Participated actively in class discussion"),
            (student_ids[1], "UOI", "Shows great curiosity about science topics", "Asked thoughtful questions during experiment"),
            (student_ids[2], "General Behaviour", "Very helpful with classmates", "Assisted struggling peer with math problem"),
            (student_ids[3], "English", "Improving writing structure", "Last essay showed better paragraph organization"),
            (student_ids[4], "UOI", "Creative problem solving approach", "Found innovative solution to group project challenge"),
            (student_ids[5], "General Behaviour", "Excellent leadership skills", "Led group project effectively")
        ]
        
        for student_id, category, comment, evidence in demo_comments:
            cursor.execute("INSERT INTO comments (student_id, category, comment, evidence) VALUES (?, ?, ?, ?)",
                         (student_id, category, comment, evidence))
        
        # Create demo spelling test scores
        for i, student_id in enumerate(student_ids[:8]):
            for week in range(4):  # 4 weeks of data
                import random
                score = random.randint(14, 20)  # Scores between 14-20 out of 20
                percentage = (score / 20) * 100
                week_date = (datetime.datetime.now() - datetime.timedelta(weeks=week)).strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO spelling_tests (student_id, score, max_score, week_date, percentage) VALUES (?, ?, ?, ?, ?)",
                             (student_id, score, 20, week_date, percentage))
        
        # Create demo grammar errors
        grammar_types = ['subject-verb agreement', 'verb tense', 'articles', 'prepositions', 'word order', 'plurals', 'pronouns']
        grammar_examples = {
            'subject-verb agreement': 'She don\'t like apples',
            'verb tense': 'Yesterday I go to the store',
            'articles': 'I saw a elephant at zoo',
            'prepositions': 'I am good in math',
            'word order': 'Always I do my homework',
            'plurals': 'I have two childs',
            'pronouns': 'Me and him went to school'
        }
        
        for student_id in student_ids[:6]:
            import random
            error_type = random.choice(grammar_types)
            example = grammar_examples[error_type]
            cursor.execute("INSERT INTO grammar_errors (student_id, error_type, example) VALUES (?, ?, ?)",
                         (student_id, error_type, example))
        
        # Create demo dictation task
        cursor.execute("""INSERT INTO dictation_tasks (name, transcript, audio_file) VALUES (?, ?, ?)""",
                      ("Sample Dictation", "The quick brown fox jumps over the lazy dog. This sentence contains many common English words.", None))
        task_id = cursor.lastrowid
        
        # Create demo dictation scores
        for student_id in student_ids[:5]:
            import random
            student_text = "The quick brown fox jumps over the lazy dog. This sentence contains many common English words."
            # Add some intentional errors for realism
            if random.random() < 0.3:
                student_text = student_text.replace("jumps", "jump")
            score = random.uniform(75, 95)
            feedback_en = "Good listening skills, minor spelling errors"
            feedback_zh = "听力技能良好，拼写错误较少"
            
            cursor.execute("""INSERT INTO dictation_scores (student_id, task_id, student_text, score, feedback_en, feedback_zh) 
                           VALUES (?, ?, ?, ?, ?, ?)""",
                         (student_id, task_id, student_text, score, feedback_en, feedback_zh))
        
        # Create demo essay marks
        essay_types = ['opinion_argumentative', 'creative_narrative']
        for i, student_id in enumerate(student_ids[:4]):
            essay_type = essay_types[i % 2]
            essay_title = "My Favorite Season" if essay_type == 'opinion_argumentative' else "Adventure in the Forest"
            essay_text = "This is a sample essay text for demonstration purposes. The student wrote about their thoughts and experiences..."
            import random
            score = random.randint(75, 95)
            feedback_en = "Well-structured essay with clear ideas"
            feedback_zh = "结构清晰的文章，观点明确"
            criteria_breakdown = "Organization: 18/20, Content: 17/20, Language: 16/20, Mechanics: 15/20"
            
            cursor.execute("""INSERT INTO essay_marks (student_id, essay_title, essay_type, essay_text, score, feedback_en, feedback_zh, criteria_breakdown) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         (student_id, essay_title, essay_type, essay_text, score, feedback_en, feedback_zh, criteria_breakdown))
        
        # Create some demo todos
        demo_todos = [
            ("Review student essays from last week", "pending"),
            ("Prepare math worksheets for next unit", "in_progress"),
            ("Contact parent about Emma's progress", "done"),
            ("Order new classroom supplies", "pending"),
            ("Plan science experiment for Friday", "pending")
        ]
        
        for task, status in demo_todos:
            cursor.execute("INSERT INTO todos (task, status) VALUES (?, ?)", (task, status))
        
        conn.commit()
        conn.close()
        
        return True, f"Successfully inserted demo data with {len(demo_students)} students across {len(demo_classes)} classes"
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, f"Error inserting demo data: {str(e)}"