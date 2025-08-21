import streamlit as st
import sys
import os

# Import from parent directory
try:
    from utils.database import execute_query
    from utils.auth import get_current_user
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.database import execute_query
    from utils.auth import get_current_user

st.header("Manage Classes")

# Get current user
current_user = get_current_user()
teacher_id = current_user['id']

# Create new class
st.subheader("Create New Class")
with st.form("new_class"):
    class_name = st.text_input("Class Name")
    submitted = st.form_submit_button("Create Class")
    
    if submitted and class_name:
        try:
            execute_query("INSERT INTO classes (name, teacher_id) VALUES (?, ?)", (class_name, teacher_id))
            st.success(f"Class '{class_name}' created successfully!")
        except Exception as e:
            st.error(f"Error creating class: {str(e)}")

# Add students to existing class
st.subheader("Add Students to Class")

# Get existing classes for this teacher
classes = execute_query("SELECT name FROM classes WHERE teacher_id = ? ORDER BY name", (teacher_id,))
if classes:
    class_options = [cls[0] for cls in classes]
    
    with st.form("add_students"):
        selected_class = st.selectbox("Select Class", class_options)
        student_names = st.text_area(
            "Student Names (one per line)", 
            help="Enter each student's name on a new line"
        )
        submitted = st.form_submit_button("Add Students")
        
        if submitted and student_names and selected_class:
            names = [name.strip() for name in student_names.split('\n') if name.strip()]
            added_count = 0
            
            for name in names:
                try:
                    execute_query(
                        "INSERT INTO students (name, class_name, teacher_id) VALUES (?, ?, ?)",
                        (name, selected_class, teacher_id)
                    )
                    added_count += 1
                except Exception as e:
                    st.error(f"Error adding {name}: {str(e)}")
            
            if added_count > 0:
                st.success(f"Added {added_count} students to {selected_class}")
else:
    st.info("Create a class first before adding students.")

# Display existing classes and students
st.subheader("Current Classes and Students")

classes = execute_query("SELECT name FROM classes WHERE teacher_id = ? ORDER BY name", (teacher_id,))
if classes:
    for class_row in classes:
        class_name = class_row[0]
        students = execute_query(
            "SELECT name FROM students WHERE class_name = ? AND teacher_id = ? ORDER BY name", 
            (class_name, teacher_id)
        )
        
        with st.expander(f"📚 {class_name} ({len(students)} students)"):
            if students:
                for i, student in enumerate(students, 1):
                    st.write(f"{i}. {student[0]}")
            else:
                st.write("No students in this class yet.")
else:
    st.info("No classes created yet.")