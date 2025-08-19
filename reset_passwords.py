#!/usr/bin/env python3
"""
Script to reset founder passwords
Run this to update the passwords in the database
"""

import hashlib
import sqlite3
import os

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_founder_passwords():
    print("🔐 Resetting Founder Passwords...")
    
    # Connect to database
    db_path = "database/school.db"
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Reset founder passwords
    founders = [
        ('james', 'rx9K2p', 'James Pares'),
        ('joe', 'mL7Ht3', 'Joe (Founder)'),
        ('jake', 'qN4Xv8', 'Jake (Founder)')
    ]
    
    for username, password, full_name in founders:
        password_hash = hash_password(password)
        
        # Update or insert the user
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, password_hash, full_name, role, is_active) 
            VALUES (?, ?, ?, 'admin', 1)
        ''', (username, password_hash, full_name))
        
        print(f"✅ Updated {username} with password: {password}")
    
    conn.commit()
    conn.close()
    
    print("🎉 All founder passwords updated!")
    print("\nLogin credentials:")
    print("james / rx9K2p")
    print("joe / mL7Ht3") 
    print("jake / qN4Xv8")

if __name__ == "__main__":
    reset_founder_passwords()