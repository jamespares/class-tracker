import streamlit as st
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import execute_query

st.header("My Todo List")

# Add new todo
st.subheader("Add New Task")
with st.form("new_todo"):
    task = st.text_input("Task Description")
    submitted = st.form_submit_button("Add Task")
    
    if submitted and task:
        execute_query(
            "INSERT INTO todos (task) VALUES (?)",
            (task,)
        )
        st.success("Task added successfully!")

# Display todos by status
st.subheader("My Tasks")

# Get all todos
todos = execute_query("""
    SELECT id, task, status, created_at, updated_at
    FROM todos
    ORDER BY 
        CASE status 
            WHEN 'in_progress' THEN 1 
            WHEN 'pending' THEN 2 
            WHEN 'done' THEN 3 
        END, 
        created_at DESC
""")

if todos:
    # Group todos by status
    pending_todos = [todo for todo in todos if todo[2] == 'pending']
    in_progress_todos = [todo for todo in todos if todo[2] == 'in_progress']
    done_todos = [todo for todo in todos if todo[2] == 'done']
    
    # Display in progress tasks
    if in_progress_todos:
        st.write("### 🔄 In Progress")
        for todo_id, task, status, created_at, updated_at in in_progress_todos:
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                st.write(f"• {task}")
            with col2:
                if st.button("✅", key=f"done_{todo_id}", help="Mark as done"):
                    execute_query(
                        "UPDATE todos SET status = 'done', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (todo_id,)
                    )
                    st.rerun()
            with col3:
                if st.button("⏸️", key=f"pause_{todo_id}", help="Move to pending"):
                    execute_query(
                        "UPDATE todos SET status = 'pending', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (todo_id,)
                    )
                    st.rerun()
    
    # Display pending tasks
    if pending_todos:
        st.write("### 📋 Pending")
        for todo_id, task, status, created_at, updated_at in pending_todos:
            col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
            with col1:
                st.write(f"• {task}")
            with col2:
                if st.button("▶️", key=f"start_{todo_id}", help="Start working"):
                    execute_query(
                        "UPDATE todos SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (todo_id,)
                    )
                    st.rerun()
            with col3:
                if st.button("✅", key=f"complete_{todo_id}", help="Mark as done"):
                    execute_query(
                        "UPDATE todos SET status = 'done', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (todo_id,)
                    )
                    st.rerun()
            with col4:
                if st.button("🗑️", key=f"delete_{todo_id}", help="Delete task"):
                    execute_query("DELETE FROM todos WHERE id = ?", (todo_id,))
                    st.rerun()
    
    # Display completed tasks (collapsible)
    if done_todos:
        with st.expander(f"✅ Completed Tasks ({len(done_todos)})"):
            for todo_id, task, status, created_at, updated_at in done_todos:
                col1, col2, col3 = st.columns([6, 1, 1])
                with col1:
                    st.write(f"~~{task}~~")
                    st.caption(f"Completed: {updated_at[:10]}")
                with col2:
                    if st.button("🔄", key=f"reopen_{todo_id}", help="Move back to pending"):
                        execute_query(
                            "UPDATE todos SET status = 'pending', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                            (todo_id,)
                        )
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"delete_done_{todo_id}", help="Delete task"):
                        execute_query("DELETE FROM todos WHERE id = ?", (todo_id,))
                        st.rerun()
    
    # Summary statistics
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", len(todos))
    with col2:
        st.metric("Pending", len(pending_todos))
    with col3:
        st.metric("In Progress", len(in_progress_todos))
    with col4:
        st.metric("Completed", len(done_todos))

else:
    st.info("No tasks yet. Add your first task above!")

# Bulk actions
if todos:
    st.subheader("Bulk Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Mark All Pending as Done"):
            execute_query(
                "UPDATE todos SET status = 'done', updated_at = CURRENT_TIMESTAMP WHERE status = 'pending'"
            )
            st.success("All pending tasks marked as done!")
            st.rerun()
    
    with col2:
        if st.button("Delete All Completed Tasks"):
            execute_query("DELETE FROM todos WHERE status = 'done'")
            st.success("All completed tasks deleted!")
            st.rerun()