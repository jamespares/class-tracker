import streamlit as st
from utils.database import init_database
from utils.auth import is_logged_in, show_login_page, show_user_info, is_admin, is_founder, is_james

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

# Check authentication
if not is_logged_in():
    show_login_page()
    st.stop()

st.title("📚 Class Tracker")
st.sidebar.title("Navigation")

# Show user info in sidebar
show_user_info()

# Navigation menu
# Build navigation menu based on user role
nav_options = [
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

# Add admin panel for James only
if is_james():
    nav_options.append("Admin Panel")

# Add database viewer for James only
if is_james():
    nav_options.append("🗄️ Database Viewer")

page = st.sidebar.selectbox("Choose a page:", nav_options)

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
    
    # Demo data section
    from utils.auth import get_current_user
    from utils.database import insert_demo_data
    
    user = get_current_user()
    if user and user.get('username') == 'demo':
        st.markdown("---")
        st.subheader("🧪 Demo Data")
        st.write("Welcome to the demo! Click the button below to populate the app with sample data to explore all features.")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🗂️ Insert Test Data", type="primary"):
                with st.spinner("Inserting demo data..."):
                    success, message = insert_demo_data()
                    if success:
                        st.success(f"✅ {message}")
                        st.info("🔄 Please refresh the page or navigate to different sections to see the demo data!")
                    else:
                        st.error(f"❌ {message}")
        
        with col2:
            st.info("💡 **Tip**: This will create sample students, classes, homework records, comments, and test scores for you to explore!")
    
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

elif page == "Admin Panel":
    try:
        exec(open('pages/admin_panel.py').read())
    except Exception as e:
        st.error(f"Error loading Admin Panel page: {str(e)}")
        st.write("Please check the console for detailed error information.")

elif page == "🗄️ Database Viewer":
    try:
        exec(open('pages/database_viewer.py').read())
    except Exception as e:
        st.error(f"Error loading Database Viewer page: {str(e)}")
        st.write("Please check the console for detailed error information.")