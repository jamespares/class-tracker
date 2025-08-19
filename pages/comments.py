import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import execute_query

st.header("Student Comments")

# Get existing classes
classes = execute_query("SELECT name FROM classes ORDER BY name")
if not classes:
    st.warning("Please create classes and add students first.")
    st.stop()

class_options = [cls[0] for cls in classes]
selected_class = st.selectbox("Select Class", class_options)

# Get students in selected class
students = execute_query(
    "SELECT id, name FROM students WHERE class_name = ? ORDER BY name", 
    (selected_class,)
)

if not students:
    st.warning(f"No students found in {selected_class}. Please add students first.")
    st.stop()

student_options = {name: student_id for student_id, name in students}

# Add new comment
st.subheader("Add New Comment")
with st.form("new_comment"):
    selected_student = st.selectbox("Select Student", list(student_options.keys()))
    category = st.selectbox("Category", ["English", "UOI", "General Behaviour"])
    comment = st.text_area("Comment", help="Describe the student's performance")
    evidence = st.text_area("Evidence", help="Supporting evidence or examples")
    
    submitted = st.form_submit_button("Add Comment")
    
    if submitted and comment:
        student_id = student_options[selected_student]
        execute_query(
            "INSERT INTO comments (student_id, category, comment, evidence) VALUES (?, ?, ?, ?)",
            (student_id, category, comment, evidence)
        )
        st.success(f"Comment added for {selected_student}")

# View comments
st.subheader("View Comments")

# Filter options
col1, col2 = st.columns(2)
with col1:
    filter_student = st.selectbox(
        "Filter by Student", 
        ["All Students"] + list(student_options.keys())
    )
with col2:
    filter_category = st.selectbox(
        "Filter by Category",
        ["All Categories", "English", "UOI", "General Behaviour"]
    )

# Build query based on filters
query = """
    SELECT s.name, c.category, c.comment, c.evidence, c.created_at
    FROM comments c
    JOIN students s ON c.student_id = s.id
    WHERE s.class_name = ?
"""
params = [selected_class]

if filter_student != "All Students":
    query += " AND s.name = ?"
    params.append(filter_student)

if filter_category != "All Categories":
    query += " AND c.category = ?"
    params.append(filter_category)

query += " ORDER BY c.created_at DESC"

comments = execute_query(query, tuple(params))

if comments:
    for comment in comments:
        student_name, category, comment_text, evidence, created_at = comment
        
        with st.expander(f"📝 {student_name} - {category} ({created_at[:10]})"):
            st.write("**Comment:**")
            st.write(comment_text)
            if evidence:
                st.write("**Evidence:**")
                st.write(evidence)
else:
    st.info("No comments found for the selected filters.")

# Generate student report
st.subheader("Generate Student Report")
report_student = st.selectbox(
    "Select Student for Report", 
    list(student_options.keys()),
    key="report_student"
)

if st.button("Generate Report"):
    student_id = student_options[report_student]
    
    # Get all comments for this student
    student_comments = execute_query("""
        SELECT category, comment, evidence, created_at
        FROM comments
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (student_id,))
    
    if student_comments:
        st.subheader(f"Report for {report_student}")
        
        # Group by category
        categories = {"English": [], "UOI": [], "General Behaviour": []}
        
        for category, comment, evidence, created_at in student_comments:
            categories[category].append({
                'comment': comment,
                'evidence': evidence,
                'date': created_at[:10]
            })
        
        for category, comments_list in categories.items():
            if comments_list:
                st.write(f"**{category}** ({len(comments_list)} comments)")
                for i, comment_data in enumerate(comments_list, 1):
                    st.write(f"{i}. ({comment_data['date']}) {comment_data['comment']}")
                    if comment_data['evidence']:
                        st.write(f"   *Evidence: {comment_data['evidence']}*")
                st.write("")
    else:
        st.info(f"No comments found for {report_student}")