#!/usr/bin/env python3
"""
Script to create or update admin credentials
Run this once to set up your preferred admin login
"""

import hashlib
import sqlite3
import os

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    print("🔐 Class Tracker - Admin Setup")
    print("=" * 40)
    
    # Get admin credentials
    username = input("Enter admin username: ").strip()
    if not username:
        username = "admin"
        print(f"Using default username: {username}")
    
    password = input("Enter admin password: ").strip()
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    full_name = input("Enter admin full name: ").strip()
    if not full_name:
        full_name = "System Administrator"
        print(f"Using default name: {full_name}")
    
    # Hash the password
    password_hash = hash_password(password)
    
    # Create database directory if it doesn't exist
    os.makedirs("database", exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect("database/school.db")
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
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
    
    try:
        # Try to update existing admin user
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, full_name = ?, role = 'admin', is_active = 1 
            WHERE username = ?
        ''', (password_hash, full_name, username))
        
        if cursor.rowcount == 0:
            # No existing user, create new one
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, role) 
                VALUES (?, ?, ?, 'admin')
            ''', (username, password_hash, full_name))
            print(f"✅ Created new admin user: {username}")
        else:
            print(f"✅ Updated existing admin user: {username}")
        
        conn.commit()
        print(f"✅ Admin setup complete!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Full Name: {full_name}")
        
    except sqlite3.IntegrityError:
        print(f"❌ Username '{username}' already exists!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()