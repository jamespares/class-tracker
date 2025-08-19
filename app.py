import streamlit as st
from utils.database import init_database

st.set_page_config(
    page_title="Class Tracker",
    page_icon="📚",
    layout="wide"
)

# Hide file browser/navigation and other streamlit elements
hide_streamlit_style = """
<style>
/* Hide file browser */
.css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
.viewerBadge_text__1JaDK { display: none; }

/* Hide main menu, deploy button, footer */
#MainMenu {visibility: hidden;}
.stDeployButton {display:none;}
footer {visibility: hidden;}
.stApp > header {visibility: hidden;}

/* Hide file navigation panel */
[data-testid="stSidebarNav"] {display: none;}
[data-testid="stSidebarNavItems"] {display: none;}

/* Additional file browser selectors for newer Streamlit versions */
section[data-testid="stSidebarNav"] {display: none !important;}
.css-17lntkn {display: none !important;}
.css-pkbazv {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize database on app start
init_database()

st.title("📚 Class Tracker")
st.sidebar.title("Navigation")

# Navigation menu
page = st.sidebar.selectbox(
    "Choose a page:",
    [
        "Home",
        "Manage Classes",
        "Homework Tracker", 
        "Student Comments",
        "Dictation Scores",
        "Essay Marking",
        "Spelling Tests",
        "Grammar Errors",
        "My Todo List"
    ]
)

if page == "Home":
    st.header("Welcome to Class Tracker")
    st.write("""
    This tool helps you track student performance across multiple areas:
    
    - **Manage Classes**: Add students to your classes
    - **Homework Tracker**: Track daily homework submission status
    - **Student Comments**: Record observations about student performance
    - **Dictation Scores**: Upload audio and track dictation performance
    - **Spelling Tests**: Record weekly spelling test scores
    - **Grammar Errors**: Track common grammar mistakes
    - **My Todo List**: Personal task management
    
    Use the sidebar to navigate between features.
    """)
    
elif page == "Manage Classes":
    try:
        exec(open('pages/add_class.py').read())
    except Exception as e:
        st.error(f"Error loading Manage Classes page: {str(e)}")
        st.write("Please check the console for detailed error information.")
    
elif page == "Homework Tracker":
    try:
        exec(open('pages/homework_tracker.py').read())
    except Exception as e:
        st.error(f"Error loading Homework Tracker page: {str(e)}")
        st.write("Please check the console for detailed error information.")
    
elif page == "Student Comments":
    try:
        exec(open('pages/comments.py').read())
    except Exception as e:
        st.error(f"Error loading Student Comments page: {str(e)}")
        st.write("Please check the console for detailed error information.")
    
elif page == "Dictation Scores":
    try:
        exec(open('pages/dictation.py').read())
    except Exception as e:
        st.error(f"Error loading Dictation Scores page: {str(e)}")
        st.write("Please check the console for detailed error information.")
    
elif page == "Essay Marking":
    try:
        exec(open('pages/essay_marking.py').read())
    except Exception as e:
        st.error(f"Error loading Essay Marking page: {str(e)}")
        st.write("Please check the console for detailed error information.")
    
elif page == "Spelling Tests":
    try:
        exec(open('pages/spelling_tests.py').read())
    except Exception as e:
        st.error(f"Error loading Spelling Tests page: {str(e)}")
        st.write("Please check the console for detailed error information.")
    
elif page == "Grammar Errors":
    try:
        exec(open('pages/grammar_errors.py').read())
    except Exception as e:
        st.error(f"Error loading Grammar Errors page: {str(e)}")
        st.write("Please check the console for detailed error information.")
    
elif page == "My Todo List":
    try:
        exec(open('pages/todo.py').read())
    except Exception as e:
        st.error(f"Error loading My Todo List page: {str(e)}")
        st.write("Please check the console for detailed error information.")