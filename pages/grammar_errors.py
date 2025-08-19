import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import execute_query

st.header("Grammar Error Tracking")

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

student_options = {name: student_id for student_id, name in students}

# Grammar error types
ERROR_TYPES = [
    'subject-verb agreement',
    'verb tense', 
    'articles',
    'prepositions',
    'word order',
    'plurals',
    'pronouns'
]

# Add grammar error
st.subheader("Record Grammar Error")
with st.form("grammar_error"):
    selected_student = st.selectbox("Select Student", list(student_options.keys()))
    error_type = st.selectbox("Error Type", ERROR_TYPES)
    example = st.text_area(
        "Example/Context", 
        help="Provide the specific example where this error occurred"
    )
    
    submitted = st.form_submit_button("Record Error")
    
    if submitted and example:
        student_id = student_options[selected_student]
        execute_query(
            "INSERT INTO grammar_errors (student_id, error_type, example) VALUES (?, ?, ?)",
            (student_id, error_type, example)
        )
        st.success(f"Grammar error recorded for {selected_student}")

# Analysis and visualization
st.subheader("Grammar Error Analysis")

# Get all grammar error data for the selected class
grammar_data = execute_query("""
    SELECT s.name, ge.error_type, ge.example, ge.created_at
    FROM grammar_errors ge
    JOIN students s ON ge.student_id = s.id
    WHERE s.class_name = ?
    ORDER BY ge.created_at DESC
""", (selected_class,))

if grammar_data:
    df = pd.DataFrame(grammar_data, columns=['Student', 'Error Type', 'Example', 'Date'])
    
    # Overall error distribution
    st.subheader("Most Common Grammar Errors (Class)")
    error_counts = df['Error Type'].value_counts()
    
    fig_errors = px.bar(
        x=error_counts.index,
        y=error_counts.values,
        title='Most Common Grammar Errors in Class',
        labels={'x': 'Error Type', 'y': 'Number of Occurrences'}
    )
    fig_errors.update_xaxis(tickangle=45)
    st.plotly_chart(fig_errors, use_container_width=True)
    
    # Student-specific analysis
    st.subheader("Individual Student Analysis")
    analysis_student = st.selectbox(
        "Select Student for Analysis", 
        list(student_options.keys()),
        key="analysis_student"
    )
    
    student_data = df[df['Student'] == analysis_student]
    
    if len(student_data) > 0:
        # Student's error breakdown
        student_errors = student_data['Error Type'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{analysis_student}'s Error Breakdown:**")
            fig_student = px.pie(
                values=student_errors.values,
                names=student_errors.index,
                title=f'{analysis_student} - Grammar Error Distribution'
            )
            st.plotly_chart(fig_student, use_container_width=True)
        
        with col2:
            st.write("**Most Common Errors:**")
            for i, (error_type, count) in enumerate(student_errors.head(3).items(), 1):
                st.write(f"{i}. {error_type}: {count} times")
            
            total_errors = len(student_data)
            st.metric("Total Errors Recorded", total_errors)
        
        # Recent errors for this student
        st.write("**Recent Errors:**")
        recent_errors = student_data.head(10)[['Error Type', 'Example', 'Date']]
        st.dataframe(recent_errors, use_container_width=True)
        
        # Recommendations based on errors
        st.write("**Focus Areas for Improvement:**")
        top_errors = student_errors.head(3)
        
        recommendations = {
            'subject-verb agreement': 'Practice matching subjects with correct verb forms. Focus on singular/plural distinctions.',
            'verb tense': 'Review past, present, and future tense formations. Practice timeline exercises.',
            'articles': 'Study when to use "a", "an", "the", or no article. Practice with countable/uncountable nouns.',
            'prepositions': 'Learn common preposition patterns (in/on/at for time/place). Practice with phrasal verbs.',
            'word order': 'Practice basic sentence patterns: Subject + Verb + Object. Review question formation.',
            'plurals': 'Learn regular and irregular plural forms. Practice count vs. non-count nouns.',
            'pronouns': 'Review subject, object, and possessive pronouns. Practice pronoun agreement.'
        }
        
        for error_type in top_errors.index:
            st.write(f"• **{error_type.title()}**: {recommendations.get(error_type, 'Practice this grammar area.')}")
    
    else:
        st.info(f"No grammar errors recorded for {analysis_student} yet.")
    
    # Class trends over time
    st.subheader("Error Trends Over Time")
    
    # Convert date to datetime for plotting
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.to_period('W').astype(str)
    
    weekly_errors = df.groupby(['Week', 'Error Type']).size().reset_index(name='Count')
    
    if len(weekly_errors) > 0:
        fig_trends = px.line(
            weekly_errors,
            x='Week',
            y='Count',
            color='Error Type',
            title='Grammar Error Trends Over Time'
        )
        fig_trends.update_xaxis(tickangle=45)
        st.plotly_chart(fig_trends, use_container_width=True)
    
    # Heat map of student vs error type
    st.subheader("Student Error Pattern Heatmap")
    
    heatmap_data = df.groupby(['Student', 'Error Type']).size().reset_index(name='Count')
    heatmap_pivot = heatmap_data.pivot(index='Student', columns='Error Type', values='Count').fillna(0)
    
    if not heatmap_pivot.empty:
        fig_heatmap = px.imshow(
            heatmap_pivot,
            title='Grammar Error Frequency by Student',
            labels=dict(x="Error Type", y="Student", color="Count"),
            aspect="auto"
        )
        fig_heatmap.update_xaxis(tickangle=45)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Summary statistics
    st.subheader("Class Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_errors = len(df)
        st.metric("Total Errors", total_errors)
    
    with col2:
        unique_students = df['Student'].nunique()
        st.metric("Students with Errors", unique_students)
    
    with col3:
        avg_errors_per_student = total_errors / len(students) if students else 0
        st.metric("Avg Errors/Student", f"{avg_errors_per_student:.1f}")
    
    with col4:
        most_common_error = df['Error Type'].value_counts().index[0] if len(df) > 0 else "None"
        st.metric("Most Common Error", most_common_error)
    
    # Detailed data view
    with st.expander("View All Grammar Error Records"):
        st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

else:
    st.info("No grammar errors recorded yet. Start tracking errors to see analysis and insights.")