import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Import from parent directory
try:
    from utils.database import execute_query
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.database import execute_query

st.header("Homework Tracker")

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

# Date selection
st.subheader("Track Homework Submission")
selected_date = st.date_input("Select Date", datetime.now().date())

# Create a form for homework tracking
with st.form("homework_tracker"):
    st.write(f"**Homework status for {selected_date}**")
    
    homework_data = {}
    
    for student_id, student_name in students:
        # Check if there's existing data for this student and date
        existing = execute_query(
            "SELECT status FROM homework WHERE student_id = ? AND date = ?",
            (student_id, str(selected_date))
        )
        current_status = existing[0][0] if existing else "on_time"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(student_name)
        with col2:
            status = st.selectbox(
                "Status",
                ["on_time", "late", "absent"],
                key=f"status_{student_id}",
                index=["on_time", "late", "absent"].index(current_status),
                label_visibility="collapsed"
            )
            homework_data[student_id] = status
    
    submitted = st.form_submit_button("Save Homework Status")
    
    if submitted:
        for student_id, status in homework_data.items():
            # Check if record exists
            existing = execute_query(
                "SELECT id FROM homework WHERE student_id = ? AND date = ?",
                (student_id, str(selected_date))
            )
            
            if existing:
                # Update existing record
                execute_query(
                    "UPDATE homework SET status = ? WHERE student_id = ? AND date = ?",
                    (status, student_id, str(selected_date))
                )
            else:
                # Insert new record
                execute_query(
                    "INSERT INTO homework (student_id, date, status) VALUES (?, ?, ?)",
                    (student_id, str(selected_date), status)
                )
        
        st.success(f"Homework status saved for {selected_date}")

# Display homework history
st.subheader("Homework History")

# Date range selection
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("From Date", datetime.now().date() - timedelta(days=7))
with col2:
    end_date = st.date_input("To Date", datetime.now().date())

# Get homework data for the selected class and date range
homework_history = execute_query("""
    SELECT s.name, h.date, h.status 
    FROM homework h
    JOIN students s ON h.student_id = s.id
    WHERE s.class_name = ? AND h.date BETWEEN ? AND ?
    ORDER BY h.date, s.name
""", (selected_class, str(start_date), str(end_date)))

if homework_history:
    # Create a DataFrame for better display
    df = pd.DataFrame(homework_history, columns=['Student', 'Date', 'Status'])
    
    # Pivot table for calendar view
    pivot_df = df.pivot(index='Student', columns='Date', values='Status')
    
    # Style the dataframe
    def color_status(val):
        if pd.isna(val):
            return ''
        elif val == 'on_time':
            return 'background-color: lightgreen'
        elif val == 'late':
            return 'background-color: lightcoral'
        elif val == 'absent':
            return 'background-color: lightgray'
        return ''
    
    styled_df = pivot_df.style.applymap(color_status)
    st.dataframe(styled_df, use_container_width=True)
    
    # Summary statistics
    st.subheader("Summary")
    status_counts = df['Status'].value_counts()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("On Time", status_counts.get('on_time', 0))
    with col2:
        st.metric("Late", status_counts.get('late', 0))
    with col3:
        st.metric("Absent", status_counts.get('absent', 0))
        
else:
    st.info("No homework data found for the selected date range.")