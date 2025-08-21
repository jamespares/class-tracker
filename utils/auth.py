import streamlit as st
import hashlib
import secrets
from utils.database import execute_query

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def login_user(username, password):
    """Authenticate user and return user info"""
    try:
        users = execute_query(
            "SELECT id, username, password_hash, full_name, role, is_active FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        
        if users and verify_password(password, users[0][2]):
            user_info = {
                'id': users[0][0],
                'username': users[0][1],
                'full_name': users[0][3],
                'role': users[0][4],
                'is_active': users[0][5]
            }
            return user_info
        return None
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None

def create_user(username, password, full_name, role='teacher'):
    """Create a new user"""
    try:
        password_hash = hash_password(password)
        user_id = execute_query(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, full_name, role)
        )
        return user_id
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return None

def get_current_user():
    """Get current logged-in user from session state"""
    return st.session_state.get('user', None)

def is_admin():
    """Check if current user is admin"""
    user = get_current_user()
    return user and user.get('role') == 'admin'

def is_founder():
    """Check if current user is a founder (james, joe, or jake)"""
    user = get_current_user()
    return user and user.get('username') in ['james', 'joe', 'jake']

def is_james():
    """Check if current user is James (database access only)"""
    user = get_current_user()
    return user and user.get('username') == 'james'

def is_logged_in():
    """Check if user is logged in"""
    return get_current_user() is not None

def logout():
    """Log out current user"""
    if 'user' in st.session_state:
        del st.session_state.user
    st.rerun()

def require_auth():
    """Decorator function to require authentication"""
    if not is_logged_in():
        show_login_page()
        st.stop()

def require_admin():
    """Decorator function to require admin role"""
    if not is_logged_in():
        show_login_page()
        st.stop()
    if not is_admin():
        st.error("🔒 Admin access required")
        st.stop()

def show_login_page():
    """Display login form"""
    st.title("🔐 Class Tracker Login")
    
    # Demo credentials info box
    st.info("🧪 **Demo Account Available!**\n\n"
           "**Username:** demo\n\n"
           "**Password:** demo\n\n"
           "Try the demo to explore all features with sample data!")
    
    with st.form("login_form"):
        st.subheader("Please log in to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if username and password:
                user = login_user(username, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.error("❌ Please enter both username and password")

def show_user_info():
    """Display current user info in sidebar"""
    user = get_current_user()
    if user:
        st.sidebar.markdown("---")
        st.sidebar.write(f"👤 **{user['full_name']}**")
        st.sidebar.write(f"📧 {user['username']}")
        st.sidebar.write(f"🔑 {user['role'].title()}")
        
        if st.sidebar.button("🚪 Logout"):
            logout()