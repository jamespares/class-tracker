#!/usr/bin/env python3
"""
Script to remove all users except James, Joe, and Jake
"""

import sqlite3
import os

def cleanup_users():
    print("🧹 Cleaning up users - keeping only James, Joe, and Jake...")
    
    # Connect to database
    db_path = "database/school.db"
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current users
    cursor.execute("SELECT id, username, full_name FROM users")
    current_users = cursor.fetchall()
    
    print("Current users:")
    for user in current_users:
        print(f"  - {user[1]} ({user[2]})")
    
    # Delete users except james, joe, jake
    cursor.execute("""
        DELETE FROM users 
        WHERE username NOT IN ('james', 'joe', 'jake')
    """)
    
    deleted_count = cursor.rowcount
    print(f"\n✅ Deleted {deleted_count} users")
    
    # Show remaining users
    cursor.execute("SELECT id, username, full_name, role FROM users ORDER BY username")
    remaining_users = cursor.fetchall()
    
    print("\nRemaining users:")
    for user in remaining_users:
        print(f"  - {user[1]} ({user[2]}) - {user[3]}")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 User cleanup complete!")

if __name__ == "__main__":
    cleanup_users()