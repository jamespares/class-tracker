import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import execute_query
from utils.auth import is_james, create_user, hash_password

# SECURITY: Only James can access admin panel
if not is_james():
    st.error("🔒 Access Denied - James Only")
    st.stop()

st.header("🔧 Admin Panel")

tab1, tab2, tab3, tab4 = st.tabs(["User Management", "System Overview", "Data Export", "Settings"])

with tab1:
    st.subheader("👥 User Management")
    
    # Add new teacher
    st.write("**Add New Teacher**")
    with st.form("add_teacher"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
        with col2:
            new_full_name = st.text_input("Full Name")
            new_role = st.selectbox("Role", ["teacher", "admin"])
        
        if st.form_submit_button("Add Teacher"):
            if new_username and new_password and new_full_name:
                user_id = create_user(new_username, new_password, new_full_name, new_role)
                if user_id:
                    st.success(f"✅ Teacher '{new_full_name}' added successfully!")
            else:
                st.error("❌ Please fill in all fields")
    
    # List existing users
    st.write("**Current Users**")
    users = execute_query("""
        SELECT id, username, full_name, role, is_active, created_at 
        FROM users 
        ORDER BY created_at DESC
    """)
    
    if users:
        df = pd.DataFrame(users, columns=['ID', 'Username', 'Full Name', 'Role', 'Active', 'Created'])
        st.dataframe(df, use_container_width=True)
        
        # Deactivate user
        st.write("**Deactivate User**")
        active_users = execute_query("SELECT id, full_name FROM users WHERE is_active = 1 AND username != 'admin'")
        if active_users:
            user_to_deactivate = st.selectbox(
                "Select user to deactivate:",
                options=[f"{user[0]} - {user[1]}" for user in active_users]
            )
            
            if st.button("🚫 Deactivate User"):
                user_id = int(user_to_deactivate.split(" - ")[0])
                execute_query("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
                st.success("✅ User deactivated")
                st.rerun()

with tab2:
    st.subheader("📊 System Overview")
    
    # System stats
    stats = {
        "Total Teachers": execute_query("SELECT COUNT(*) FROM users WHERE role = 'teacher' AND is_active = 1")[0][0],
        "Total Classes": execute_query("SELECT COUNT(*) FROM classes")[0][0],
        "Total Students": execute_query("SELECT COUNT(*) FROM students")[0][0],
        "Total Essay Marks": execute_query("SELECT COUNT(*) FROM essay_marks")[0][0],
        "Total Dictation Scores": execute_query("SELECT COUNT(*) FROM dictation_scores")[0][0],
        "Total Comments": execute_query("SELECT COUNT(*) FROM comments")[0][0]
    }
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Teachers", stats["Total Teachers"])
        st.metric("📚 Classes", stats["Total Classes"])
    with col2:
        st.metric("👨‍🎓 Students", stats["Total Students"])
        st.metric("📝 Essays", stats["Total Essay Marks"])
    with col3:
        st.metric("🎧 Dictations", stats["Total Dictation Scores"])
        st.metric("💬 Comments", stats["Total Comments"])
    
    # Teacher activity
    st.write("**Teacher Activity Summary**")
    try:
        teacher_activity = execute_query("""
            SELECT 
                u.full_name,
                COALESCE(COUNT(DISTINCT c.id), 0) as classes,
                COALESCE(COUNT(DISTINCT s.id), 0) as students,
                COALESCE(COUNT(DISTINCT em.id), 0) as essays,
                COALESCE(COUNT(DISTINCT ds.id), 0) as dictations
            FROM users u
            LEFT JOIN classes c ON u.id = COALESCE(c.teacher_id, 1)
            LEFT JOIN students s ON u.id = COALESCE(s.teacher_id, 1)
            LEFT JOIN essay_marks em ON s.id = em.student_id
            LEFT JOIN dictation_scores ds ON s.id = ds.student_id
            WHERE u.role = 'teacher' AND u.is_active = 1
            GROUP BY u.id, u.full_name
            ORDER BY u.full_name
        """)
    except Exception as e:
        st.error(f"Error loading teacher activity: {str(e)}")
        teacher_activity = []
    
    if teacher_activity:
        activity_df = pd.DataFrame(teacher_activity, 
                                 columns=['Teacher', 'Classes', 'Students', 'Essays', 'Dictations'])
        st.dataframe(activity_df, use_container_width=True)

with tab3:
    st.subheader("📤 Data Export")
    
    # Export options
    export_type = st.selectbox("Select data to export:", [
        "All Students",
        "All Essay Marks", 
        "All Dictation Scores",
        "All Comments",
        "Teacher Summary"
    ])
    
    if st.button("📋 Generate Export"):
        if export_type == "All Students":
            data = execute_query("""
                SELECT s.name, s.class_name, u.full_name as teacher
                FROM students s
                JOIN users u ON s.teacher_id = u.id
                ORDER BY u.full_name, s.class_name, s.name
            """)
            df = pd.DataFrame(data, columns=['Student', 'Class', 'Teacher'])
            
        elif export_type == "All Essay Marks":
            data = execute_query("""
                SELECT s.name, em.essay_title, em.essay_type, em.score, 
                       em.created_at, u.full_name as teacher
                FROM essay_marks em
                JOIN students s ON em.student_id = s.id
                JOIN users u ON s.teacher_id = u.id
                ORDER BY em.created_at DESC
            """)
            df = pd.DataFrame(data, columns=['Student', 'Essay Title', 'Type', 'Score', 'Date', 'Teacher'])
            
        elif export_type == "All Dictation Scores":
            data = execute_query("""
                SELECT s.name, dt.name as task, ds.score, ds.created_at, u.full_name as teacher
                FROM dictation_scores ds
                JOIN students s ON ds.student_id = s.id
                JOIN dictation_tasks dt ON ds.task_id = dt.id
                JOIN users u ON s.teacher_id = u.id
                ORDER BY ds.created_at DESC
            """)
            df = pd.DataFrame(data, columns=['Student', 'Task', 'Score', 'Date', 'Teacher'])
            
        elif export_type == "All Comments":
            data = execute_query("""
                SELECT s.name, c.category, c.comment, c.created_at, u.full_name as teacher
                FROM comments c
                JOIN students s ON c.student_id = s.id
                JOIN users u ON s.teacher_id = u.id
                ORDER BY c.created_at DESC
            """)
            df = pd.DataFrame(data, columns=['Student', 'Category', 'Comment', 'Date', 'Teacher'])
            
        elif export_type == "Teacher Summary":
            df = activity_df if 'activity_df' in locals() else pd.DataFrame()
        
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"{export_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data available for export")

with tab4:
    st.subheader("⚙️ System Settings")
    
    st.write("**Change Admin Password**")
    with st.form("change_admin_password"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔐 Change Password"):
            if current_password and new_password and confirm_password:
                # Verify current password
                admin_user = execute_query("SELECT password_hash FROM users WHERE username = 'admin'")[0][0]
                if hash_password(current_password) == admin_user:
                    if new_password == confirm_password:
                        new_hash = hash_password(new_password)
                        execute_query("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
                        st.success("✅ Admin password updated successfully!")
                    else:
                        st.error("❌ New passwords don't match")
                else:
                    st.error("❌ Current password is incorrect")
            else:
                st.error("❌ Please fill in all fields")
    
    st.write("**Database Information**")
    st.info(f"""
    📂 **Database Location:** `database/school.db`
    📊 **Total Records:** {sum(stats.values())} entries
    💾 **Last Modified:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    
    st.write("**System Health**")
    try:
        test_query = execute_query("SELECT 1")
        if test_query:
            st.success("✅ Database connection healthy")
        else:
            st.error("❌ Database connection issues")
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")
    
    # Danger zone
    st.write("**⚠️ Danger Zone**")
    with st.expander("🗑️ Reset System Data"):
        st.warning("This will delete ALL data except user accounts!")
        if st.text_input("Type 'DELETE ALL DATA' to confirm") == "DELETE ALL DATA":
            if st.button("🗑️ Reset All Data"):
                tables_to_clear = [
                    "homework", "comments", "dictation_tasks", "dictation_scores",
                    "spelling_tests", "grammar_errors", "essay_marks", "students", "classes"
                ]
                for table in tables_to_clear:
                    execute_query(f"DELETE FROM {table}")
                st.success("✅ All data cleared (users preserved)")
                st.rerun()