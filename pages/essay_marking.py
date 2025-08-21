import streamlit as st
import sys
import os
import json
from openai import OpenAI

# Import from parent directory
try:
    from utils.database import execute_query
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.database import execute_query

def get_openai_client():
    """Get OpenAI client with API key from Streamlit secrets"""
    try:
        if "openai_api_key" in st.secrets:
            return OpenAI(api_key=st.secrets["openai_api_key"])
        else:
            st.error("OpenAI API key not found in secrets. Please configure your API key.")
            return None
    except Exception as e:
        st.error(f"Error setting up OpenAI client: {str(e)}")
        return None

def mark_essay_with_ai(essay_text, essay_type, student_name):
    """Use ChatGPT to mark essay according to ISA Year 4 criteria"""
    try:
        client = get_openai_client()
        if not client:
            return None
            
        if essay_type == "opinion_argumentative":
            criteria_prompt = """
            ISA Year 4 Opinion/Argumentative Writing Criteria:
            
            1. CONTENT & IDEAS (25 points):
            - Clear opinion/position statement
            - Relevant supporting reasons and evidence
            - Understanding of topic
            - Development of ideas
            
            2. ORGANIZATION (25 points):
            - Clear introduction with thesis
            - Logical sequence of ideas
            - Appropriate transitions
            - Strong conclusion
            
            3. LANGUAGE USE (25 points):
            - Appropriate vocabulary for purpose
            - Varied sentence structure
            - Clear expression of ideas
            - Academic tone
            
            4. CONVENTIONS (25 points):
            - Grammar and usage
            - Spelling accuracy
            - Punctuation
            - Capitalization
            """
        else:  # creative_narrative
            criteria_prompt = """
            ISA Year 4 Creative/Narrative Writing Criteria:
            
            1. CONTENT & CREATIVITY (25 points):
            - Original and engaging ideas
            - Character development
            - Plot development
            - Descriptive details
            
            2. ORGANIZATION (25 points):
            - Clear beginning, middle, end
            - Logical sequence of events
            - Smooth transitions
            - Satisfying conclusion
            
            3. LANGUAGE USE (25 points):
            - Rich, descriptive vocabulary
            - Varied sentence structure
            - Voice and style
            - Figurative language use
            
            4. CONVENTIONS (25 points):
            - Grammar and usage
            - Spelling accuracy
            - Punctuation
            - Capitalization
            """
        
        prompt = f"""
        You are marking a Year 4 student's {essay_type.replace('_', '/')} essay according to ISA (International Schools Assessment) criteria.

        {criteria_prompt}

        STUDENT: {student_name}
        ESSAY TYPE: {essay_type.replace('_', ' ').title()}

        STUDENT'S ESSAY:
        "{essay_text}"

        Provide detailed marking in JSON format:
        {{
            "total_score": <score out of 100>,
            "content_ideas": {{"score": <out of 25>, "comments": "<specific feedback>"}},
            "organization": {{"score": <out of 25>, "comments": "<specific feedback>"}},
            "language_use": {{"score": <out of 25>, "comments": "<specific feedback>"}},
            "conventions": {{"score": <out of 25>, "comments": "<specific feedback>"}},
            "feedback_english": "<comprehensive, copy-pastable feedback for student in English>",
            "feedback_chinese": "<same feedback translated to Chinese>",
            "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
            "areas_for_improvement": ["<area 1>", "<area 2>", "<area 3>"],
            "next_steps": "<specific suggestions for improvement>"
        }}

        Make feedback encouraging but honest. Focus on specific examples from the text.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
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
        st.error(f"AI essay marking failed: {str(e)}")
        return None

st.header("Essay Marking")

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

# Essay submission form
st.subheader("Mark New Essay")

with st.form("essay_submission"):
    selected_student = st.selectbox("Select Student", list(student_options.keys()))
    essay_title = st.text_input("Essay Title/Prompt")
    essay_type = st.selectbox(
        "Essay Type",
        ["opinion_argumentative", "creative_narrative"],
        format_func=lambda x: "Opinion/Argumentative Writing" if x == "opinion_argumentative" else "Creative/Narrative Writing"
    )
    essay_text = st.text_area(
        "Student's Essay", 
        height=300,
        help="Copy and paste the student's complete essay here"
    )
    
    submit_for_marking = st.form_submit_button("Mark Essay with AI")

if submit_for_marking and essay_text and essay_title:
    with st.spinner("Marking essay with AI... This may take a moment..."):
        result = mark_essay_with_ai(essay_text, essay_type, selected_student)
        
        if result:
            # Store in session state
            st.session_state.essay_result = {
                'result': result,
                'student_name': selected_student,
                'student_id': student_options[selected_student],
                'essay_title': essay_title,
                'essay_type': essay_type,
                'essay_text': essay_text
            }

# Display marking results
if hasattr(st.session_state, 'essay_result') and st.session_state.essay_result:
    data = st.session_state.essay_result
    result = data['result']
    
    st.subheader(f"Essay Marking Results: {data['student_name']}")
    st.write(f"**Essay:** {data['essay_title']}")
    st.write(f"**Type:** {data['essay_type'].replace('_', ' ').title()}")
    
    # Overall score
    total_score = result['total_score']
    st.metric("Total Score", f"{total_score}/100")
    
    # Breakdown by criteria
    st.subheader("Detailed Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Content & Ideas", f"{result['content_ideas']['score']}/25")
        with st.expander("Content Feedback"):
            st.write(result['content_ideas']['comments'])
    
    with col2:
        st.metric("Organization", f"{result['organization']['score']}/25")
        with st.expander("Organization Feedback"):
            st.write(result['organization']['comments'])
    
    with col3:
        st.metric("Language Use", f"{result['language_use']['score']}/25")
        with st.expander("Language Feedback"):
            st.write(result['language_use']['comments'])
    
    with col4:
        st.metric("Conventions", f"{result['conventions']['score']}/25")
        with st.expander("Conventions Feedback"):
            st.write(result['conventions']['comments'])
    
    # Strengths and areas for improvement
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Strengths")
        for strength in result['strengths']:
            st.write(f"✅ {strength}")
    
    with col2:
        st.subheader("Areas for Improvement")
        for area in result['areas_for_improvement']:
            st.write(f"📈 {area}")
    
    # Copy-pastable feedback
    st.subheader("Student Feedback")
    
    tab1, tab2 = st.tabs(["English Feedback", "Chinese Feedback"])
    
    with tab1:
        st.text_area(
            "Copy-Pastable English Feedback:",
            result['feedback_english'],
            height=200,
            help="Select all and copy this feedback to paste elsewhere"
        )
    
    with tab2:
        st.text_area(
            "Copy-Pastable Chinese Feedback:",
            result['feedback_chinese'],
            height=200,
            help="Select all and copy this feedback to paste elsewhere"
        )
    
    # Next steps
    st.subheader("Next Steps for Student")
    st.info(result['next_steps'])
    
    # Save button (outside form)
    col1, col2 = st.columns(2)
    with col1:
        final_score = st.number_input("Final Score (if adjusting)", 0, 100, total_score)
    with col2:
        if st.button("Save Essay Mark"):
            criteria_breakdown = json.dumps({
                'content_ideas': result['content_ideas']['score'],
                'organization': result['organization']['score'], 
                'language_use': result['language_use']['score'],
                'conventions': result['conventions']['score']
            })
            
            execute_query(
                "INSERT INTO essay_marks (student_id, essay_title, essay_type, essay_text, score, feedback_en, feedback_zh, criteria_breakdown) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (data['student_id'], data['essay_title'], data['essay_type'], data['essay_text'], 
                 final_score, result['feedback_english'], result['feedback_chinese'], criteria_breakdown)
            )
            st.success(f"Essay mark saved for {data['student_name']}")
            # Clear results after saving
            del st.session_state.essay_result

# View previous essay marks
st.subheader("Previous Essay Marks")

essay_history = execute_query("""
    SELECT s.name, em.essay_title, em.essay_type, em.score, em.created_at, em.id
    FROM essay_marks em
    JOIN students s ON em.student_id = s.id
    WHERE s.class_name = ?
    ORDER BY em.created_at DESC
""", (selected_class,))

if essay_history:
    for student_name, essay_title, essay_type, score, created_at, essay_id in essay_history:
        with st.expander(f"📝 {student_name} - {essay_title} ({score}/100) - {created_at[:10]}"):
            st.write(f"**Type:** {essay_type.replace('_', ' ').title()}")
            
            # Get full essay details
            essay_details = execute_query(
                "SELECT feedback_en, feedback_zh, criteria_breakdown FROM essay_marks WHERE id = ?",
                (essay_id,)
            )
            
            if essay_details:
                feedback_en, feedback_zh, criteria_breakdown = essay_details[0]
                
                if criteria_breakdown:
                    breakdown = json.loads(criteria_breakdown)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"Content: {breakdown['content_ideas']}/25")
                    with col2:
                        st.write(f"Organization: {breakdown['organization']}/25")
                    with col3:
                        st.write(f"Language: {breakdown['language_use']}/25")
                    with col4:
                        st.write(f"Conventions: {breakdown['conventions']}/25")
                
                # Copy-pastable feedback tabs
                tab1, tab2 = st.tabs(["English Feedback", "Chinese Feedback"])
                
                with tab1:
                    st.text_area(
                        "English Feedback:",
                        feedback_en,
                        height=150,
                        key=f"en_feedback_{essay_id}",
                        help="Select all and copy"
                    )
                
                with tab2:
                    st.text_area(
                        "Chinese Feedback:",
                        feedback_zh,
                        height=150,
                        key=f"zh_feedback_{essay_id}",
                        help="Select all and copy"
                    )
else:
    st.info("No essays marked yet.")