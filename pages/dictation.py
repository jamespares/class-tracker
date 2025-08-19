import streamlit as st
import sys
import os
import difflib
import re
from openai import OpenAI
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import execute_query

def get_openai_client():
    """Get OpenAI client with API key from Streamlit secrets or user input"""
    try:
        if "openai_api_key" in st.secrets:
            return OpenAI(api_key=st.secrets["openai_api_key"])
        else:
            # Ask user for API key
            api_key = st.text_input("Enter your OpenAI API Key:", type="password", 
                                   help="Get your API key from https://platform.openai.com/api-keys")
            if api_key:
                return OpenAI(api_key=api_key)
            else:
                st.warning("Please enter your OpenAI API key to use AI-powered scoring.")
                return None
    except Exception as e:
        st.error(f"Error setting up OpenAI client: {str(e)}")
        return None

def calculate_dictation_score_ai(correct_text, student_text, use_ai=True):
    """Calculate dictation score using AI or fallback to basic similarity"""
    try:
        if use_ai:
            client = get_openai_client()
            if client:
                return _ai_score_dictation(client, correct_text, student_text)
        
        # Fallback to basic scoring
        return _basic_dictation_score(correct_text, student_text)
    except Exception as e:
        st.error(f"Error calculating score: {str(e)}")
        return _basic_dictation_score(correct_text, student_text)

def _ai_score_dictation(client, correct_text, student_text):
    """Use ChatGPT to score dictation and provide feedback"""
    try:
        prompt = f"""
        You are evaluating a student's DICTATION exercise. This is purely about listening accuracy - the student heard spoken text and wrote what they heard. Judge only their listening and transcription accuracy, not their writing skills or word choice.

        CORRECT TEXT (what was spoken):
        "{correct_text}"

        STUDENT'S TRANSCRIPTION (what they heard and wrote):
        "{student_text}"

        Provide your response in JSON format:
        {{
            "score": <percentage from 0-100 based on accuracy of transcription>,
            "feedback_english": "<factual feedback about what they heard correctly/incorrectly>",
            "feedback_chinese": "<same feedback in Chinese>",
            "errors": [
                {{
                    "type": "<missed_word/extra_word/misspelled_word/wrong_word>",
                    "correct": "<what was actually said>",
                    "student": "<what they wrote>",
                    "explanation": "<simple factual explanation>"
                }}
            ]
        }}

        IMPORTANT:
        - This is dictation - focus only on listening accuracy, not language skills
        - Don't comment on grammar or writing ability - only transcription accuracy
        - Be factual: "You heard X but the speaker said Y"
        - Give credit for phonetically similar attempts (e.g. "there/their")
        - Score based on percentage of words transcribed correctly
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        # Clean the content to extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        return result
        
    except Exception as e:
        st.error(f"AI scoring failed: {str(e)}")
        return _basic_dictation_score(correct_text, student_text)

def _basic_dictation_score(correct_text, student_text):
    """Fallback basic scoring method"""
    # Clean and normalize text
    correct_clean = re.sub(r'[^\w\s]', '', correct_text.lower().strip())
    student_clean = re.sub(r'[^\w\s]', '', student_text.lower().strip())
    
    # Calculate similarity using SequenceMatcher
    similarity = difflib.SequenceMatcher(None, correct_clean, student_clean).ratio()
    score = similarity * 100
    
    return {
        "score": score,
        "feedback_english": generate_feedback_en(score, correct_text, student_text),
        "feedback_chinese": generate_feedback_zh(score),
        "errors": []
    }

def show_differences(correct_text, student_text):
    """Show differences between correct and student text"""
    try:
        st.write("**Text Comparison:**")
        
        differ = difflib.unified_diff(
            correct_text.splitlines(keepends=True),
            student_text.splitlines(keepends=True),
            fromfile='Correct',
            tofile='Student',
            lineterm=''
        )
        
        diff_text = ''.join(differ)
        if diff_text:
            st.code(diff_text, language='diff')
        else:
            st.write("✅ Texts are identical!")
    except Exception as e:
        st.error(f"Error showing differences: {str(e)}")

def generate_feedback_en(score, correct_text, student_text):
    """Generate English feedback based on score - dictation focused"""
    try:
        correct_words = correct_text.split()
        student_words = student_text.split()
        total_words = len(correct_words)
        
        if score >= 90:
            return f"Excellent listening accuracy! You correctly transcribed {int(score/100 * total_words)} out of {total_words} words from the audio."
        elif score >= 80:
            return f"Good listening! You accurately heard and wrote {int(score/100 * total_words)} out of {total_words} words. Check the differences above to see what you missed."
        elif score >= 70:
            return f"Fair listening accuracy. You caught {int(score/100 * total_words)} out of {total_words} words. Practice listening more carefully to catch all the words."
        elif score >= 60:
            return f"You heard some words correctly ({int(score/100 * total_words)} out of {total_words}). Listen again to hear what you missed."
        else:
            return f"Keep practicing your listening! Try to focus on hearing each word clearly. You got {int(score/100 * total_words)} out of {total_words} words."
    except Exception as e:
        st.error(f"Error generating English feedback: {str(e)}")
        return "Feedback could not be generated."

def generate_feedback_zh(score):
    """Generate Chinese feedback based on score - dictation focused"""
    try:
        if score >= 90:
            return "听写很准确！你听懂了几乎所有的单词。"
        elif score >= 80:
            return "听力不错！大部分单词都听对了。"
        elif score >= 70:
            return "听写还可以。多练习听力，注意听清楚每个单词。"
        elif score >= 60:
            return "继续练习听力！专心听每个单词的发音。"
        else:
            return "多练习听写！仔细听，慢慢写。"
    except Exception as e:
        st.error(f"Error generating Chinese feedback: {str(e)}")
        return "无法生成反馈。"

st.header("Dictation Score Tracking")

# Create dictation task
st.subheader("Create Dictation Task")
with st.form("new_dictation_task"):
    task_name = st.text_input("Task Name")
    transcript = st.text_area("Transcript", help="The correct text for the dictation")
    audio_file = st.file_uploader("Upload Audio File (Optional)", type=['mp3', 'wav', 'ogg'])
    
    submitted = st.form_submit_button("Create Task")
    
    if submitted and task_name and transcript:
        audio_filename = None
        if audio_file:
            # Save audio file
            audio_dir = "database/audio"
            os.makedirs(audio_dir, exist_ok=True)
            audio_filename = f"{audio_dir}/{task_name}_{audio_file.name}"
            with open(audio_filename, "wb") as f:
                f.write(audio_file.getvalue())
        
        execute_query(
            "INSERT INTO dictation_tasks (name, transcript, audio_file) VALUES (?, ?, ?)",
            (task_name, transcript, audio_filename)
        )
        st.success(f"Dictation task '{task_name}' created successfully!")

# Score dictation attempts
st.subheader("Score Student Attempts")

# Get existing tasks
tasks = execute_query("SELECT id, name, transcript FROM dictation_tasks ORDER BY created_at DESC")
if tasks:
    task_options = {f"{name}": (task_id, transcript) for task_id, name, transcript in tasks}
    selected_task = st.selectbox("Select Dictation Task", list(task_options.keys()))
    
    if selected_task:
        task_id, correct_transcript = task_options[selected_task]
        
        # Display correct transcript
        with st.expander("View Correct Transcript"):
            st.write(correct_transcript)
        
        # Get classes and students
        classes = execute_query("SELECT name FROM classes ORDER BY name")
        if classes:
            class_options = [cls[0] for cls in classes]
            selected_class = st.selectbox("Select Class", class_options)
            
            students = execute_query(
                "SELECT id, name FROM students WHERE class_name = ? ORDER BY name", 
                (selected_class,)
            )
            
            if students:
                student_options = {name: student_id for student_id, name in students}
                selected_student = st.selectbox("Select Student", list(student_options.keys()))
                
                # AI vs Basic scoring toggle
                use_ai_scoring = st.checkbox("Use AI-Powered Scoring (ChatGPT)", value=True, 
                                           help="Uses ChatGPT for more accurate scoring and detailed feedback")
                
                with st.form("score_dictation"):
                    student_text = st.text_area(
                        "Student's Written Attempt", 
                        help="Enter exactly what the student wrote"
                    )
                    
                    calculate_button = st.form_submit_button("Calculate Score")
                
                if calculate_button and student_text:
                    with st.spinner("Analyzing dictation..." if use_ai_scoring else "Calculating score..."):
                        # Calculate score using AI or basic method
                        result = calculate_dictation_score_ai(correct_transcript, student_text, use_ai_scoring)
                        
                        if result:
                            score = result["score"]
                            feedback_en = result["feedback_english"]
                            feedback_zh = result["feedback_chinese"]
                            errors = result.get("errors", [])
                            
                            # Store results in session state
                            st.session_state.score_result = {
                                'score': score,
                                'feedback_en': feedback_en,
                                'feedback_zh': feedback_zh,
                                'errors': errors,
                                'student_text': student_text,
                                'student_id': student_options[selected_student],
                                'task_id': task_id
                            }
                        else:
                            st.error("Failed to calculate score. Please try again.")
                
                # Display results if they exist
                if hasattr(st.session_state, 'score_result') and st.session_state.score_result:
                    result = st.session_state.score_result
                    score = result['score']
                    feedback_en = result['feedback_en']
                    feedback_zh = result['feedback_zh']
                    errors = result['errors']
                    
                    st.write(f"**Calculated Score: {score:.1f}%**")
                    
                    # Show detailed errors if available
                    if errors:
                        st.write("**Detailed Analysis:**")
                        for error in errors:
                            with st.expander(f"❌ {error['type'].replace('_', ' ').title()} Error"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Student wrote:** {error['student']}")
                                with col2:
                                    st.write(f"**Should be:** {error['correct']}")
                                st.write(f"**Explanation:** {error['explanation']}")
                    
                    # Show text comparison (fallback)
                    if not use_ai_scoring or not errors:
                        show_differences(correct_transcript, result['student_text'])
                    
                    # Copy-pastable feedback
                    st.write("**Generated Feedback:**")
                    
                    tab1, tab2 = st.tabs(["English Feedback", "Chinese Feedback"])
                    
                    with tab1:
                        st.text_area(
                            "Copy-Pastable English Feedback:",
                            feedback_en,
                            height=100,
                            key="dictation_feedback_en",
                            help="Select all and copy this feedback to paste elsewhere"
                        )
                    
                    with tab2:
                        st.text_area(
                            "Copy-Pastable Chinese Feedback:",
                            feedback_zh,
                            height=100,
                            key="dictation_feedback_zh",
                            help="Select all and copy this feedback to paste elsewhere"
                        )
                    
                    # Allow manual adjustment and save (outside form)
                    col1, col2 = st.columns(2)
                    with col1:
                        final_score = st.number_input("Final Score (%)", 0.0, 100.0, float(score))
                    with col2:
                        if st.button("Save Score"):
                            execute_query(
                                "INSERT INTO dictation_scores (student_id, task_id, student_text, score, feedback_en, feedback_zh) VALUES (?, ?, ?, ?, ?, ?)",
                                (result['student_id'], result['task_id'], result['student_text'], final_score, feedback_en, feedback_zh)
                            )
                            st.success(f"Score saved for {selected_student}")
                            # Clear the result after saving
                            del st.session_state.score_result
            else:
                st.warning("No students found in selected class.")
        else:
            st.warning("Please create classes first.")
else:
    st.info("Create a dictation task first.")

# View scores
st.subheader("View Scores")
if tasks:
    view_task = st.selectbox("Select Task to View Scores", list(task_options.keys()), key="view_task")
    
    if view_task:
        task_id, _ = task_options[view_task]
        
        scores = execute_query("""
            SELECT s.name, ds.score, ds.feedback_en, ds.feedback_zh, ds.created_at
            FROM dictation_scores ds
            JOIN students s ON ds.student_id = s.id
            WHERE ds.task_id = ?
            ORDER BY ds.score DESC
        """, (task_id,))
        
        if scores:
            for i, (student_name, score, feedback_en, feedback_zh, created_at) in enumerate(scores):
                with st.expander(f"📊 {student_name} - {score:.1f}% ({created_at[:10]})"):
                    tab1, tab2 = st.tabs(["English Feedback", "Chinese Feedback"])
                    
                    with tab1:
                        st.text_area(
                            "Copy-Pastable English Feedback:",
                            feedback_en,
                            height=100,
                            key=f"view_feedback_en_{i}",
                            help="Select all and copy"
                        )
                    
                    with tab2:
                        st.text_area(
                            "Copy-Pastable Chinese Feedback:",
                            feedback_zh,
                            height=100,
                            key=f"view_feedback_zh_{i}",
                            help="Select all and copy"
                        )
        else:
            st.info("No scores recorded for this task yet.")