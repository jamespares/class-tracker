import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import execute_query

st.header("Spelling Tests")

# Get existing classes
classes = execute_query("SELECT name FROM classes ORDER BY name")
if not classes:
    st.warning("Please create classes and add students first.")
    st.stop()

class_options = [cls[0] for cls in classes]
selected_class = st.selectbox("Select Class", class_options)

students = execute_query(
    "SELECT id, name FROM students WHERE class_name = ? ORDER BY name", 
    (selected_class,)
)

if not students:
    st.warning(f"No students found in {selected_class}. Please add students first.")
    st.stop()

# Add spelling test scores
st.subheader("Add Weekly Spelling Test Scores")

with st.form("spelling_scores"):
    week_date = st.date_input("Week Date", datetime.now().date())
    max_score = st.number_input("Maximum Score", min_value=1, value=20)
    
    st.write("**Enter scores for each student:**")
    
    scores_data = {}
    for student_id, student_name in students:
        score = st.number_input(
            f"{student_name}",
            min_value=0,
            max_value=max_score,
            value=0,
            key=f"score_{student_id}"
        )
        scores_data[student_id] = score
    
    submitted = st.form_submit_button("Save Scores")
    
    if submitted:
        for student_id, score in scores_data.items():
            if score > 0:  # Only save non-zero scores
                percentage = (score / max_score) * 100
                
                # Check if score already exists for this week
                existing = execute_query(
                    "SELECT id FROM spelling_tests WHERE student_id = ? AND week_date = ?",
                    (student_id, str(week_date))
                )
                
                if existing:
                    # Update existing score
                    execute_query(
                        "UPDATE spelling_tests SET score = ?, max_score = ?, percentage = ? WHERE student_id = ? AND week_date = ?",
                        (score, max_score, percentage, student_id, str(week_date))
                    )
                else:
                    # Insert new score
                    execute_query(
                        "INSERT INTO spelling_tests (student_id, score, max_score, week_date, percentage) VALUES (?, ?, ?, ?, ?)",
                        (student_id, score, max_score, str(week_date), percentage)
                    )
        
        st.success(f"Spelling test scores saved for week of {week_date}")

# View and analyze scores
st.subheader("Spelling Test Analysis")

# Get all spelling test data for the selected class
spelling_data = execute_query("""
    SELECT s.name, st.score, st.max_score, st.percentage, st.week_date
    FROM spelling_tests st
    JOIN students s ON st.student_id = s.id
    WHERE s.class_name = ?
    ORDER BY st.week_date DESC, s.name
""", (selected_class,))

if spelling_data:
    df = pd.DataFrame(spelling_data, columns=['Student', 'Score', 'Max Score', 'Percentage', 'Week Date'])
    
    # Weekly class averages
    st.subheader("Weekly Class Averages")
    weekly_avg = df.groupby('Week Date')['Percentage'].mean().reset_index()
    weekly_avg = weekly_avg.sort_values('Week Date')
    
    fig_weekly = px.line(
        weekly_avg, 
        x='Week Date', 
        y='Percentage',
        title='Weekly Class Average Spelling Scores',
        markers=True
    )
    fig_weekly.update_yaxis(range=[0, 100])
    st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Individual student progress
    st.subheader("Individual Student Progress")
    selected_student = st.selectbox("Select Student for Individual Analysis", df['Student'].unique())
    
    student_data = df[df['Student'] == selected_student].sort_values('Week Date')
    
    if len(student_data) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Student's average
            student_avg = student_data['Percentage'].mean()
            st.metric("Student Average", f"{student_avg:.1f}%")
        
        with col2:
            # Class average for comparison
            class_avg = df['Percentage'].mean()
            st.metric("Class Average", f"{class_avg:.1f}%")
        
        # Student progress chart
        fig_student = px.line(
            student_data,
            x='Week Date',
            y='Percentage',
            title=f'{selected_student} - Spelling Test Progress',
            markers=True
        )
        fig_student.update_yaxis(range=[0, 100])
        st.plotly_chart(fig_student, use_container_width=True)
        
        # Recent scores table
        st.write("**Recent Scores:**")
        st.dataframe(
            student_data[['Week Date', 'Score', 'Max Score', 'Percentage']].tail(10),
            use_container_width=True
        )
    
    # Class performance summary
    st.subheader("Class Performance Summary")
    
    # Current week statistics
    latest_week = df['Week Date'].max()
    latest_week_data = df[df['Week Date'] == latest_week]
    
    if len(latest_week_data) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_score = latest_week_data['Percentage'].mean()
            st.metric("Latest Week Average", f"{avg_score:.1f}%")
        
        with col2:
            high_score = latest_week_data['Percentage'].max()
            st.metric("Highest Score", f"{high_score:.1f}%")
        
        with col3:
            low_score = latest_week_data['Percentage'].min()
            st.metric("Lowest Score", f"{low_score:.1f}%")
        
        with col4:
            students_above_80 = len(latest_week_data[latest_week_data['Percentage'] >= 80])
            st.metric("Students ≥80%", students_above_80)
    
    # Term averages for each student
    st.subheader("Term Averages by Student")
    student_averages = df.groupby('Student')['Percentage'].mean().reset_index()
    student_averages = student_averages.sort_values('Percentage', ascending=False)
    
    fig_averages = px.bar(
        student_averages,
        x='Student',
        y='Percentage',
        title='Term Average Spelling Scores by Student'
    )
    fig_averages.update_xaxis(tickangle=45)
    fig_averages.update_yaxis(range=[0, 100])
    st.plotly_chart(fig_averages, use_container_width=True)
    
    # Raw data table
    with st.expander("View All Data"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("No spelling test data found. Add some scores to see analysis.")