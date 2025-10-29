import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import altair as alt
import varpro 
import hedge_automation
import Summary_Automation
import jainam
import usersetting_compare
import algo19
import algo8
import hedge  # Import the Hedge Manager module

# Page configuration for consistent layout across environments
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Card and Module Definitions ---
CARDS = {
    'HEDGE AUTOMATION': {
        'description': 'Automate orderbook hedge operations.',
        'roles': ['Admin', 'User'],
        'icon': '🔄'
    },
    'VAR PRO': {
        'description': 'Calculate Value at Risk.',
        'roles': ['Admin', 'User'],
        'icon': '📈'
    },
    'SUMMARY AUTOMATION': {
        'description': 'Generate automated summaries.',
        'roles': ['Admin', 'User'],
        'icon': '📋'
    },
    'STRATEGY AUTOMATION': {
        'description': 'Automate strategy execution.',
        'roles': ['Admin', 'User'],
        'icon': '🎯'
    },
    'JAINAM': {
        'description': 'Manage Jainam operations.',
        'roles': ['Admin'],
        'icon': '💼'
    },
    'USERSETTING': {
        'description': 'Configure user settings.',
        'roles': ['Admin'],
        'icon': '⚙️'
    },
    'ALGO19 REALIZED AND UNREALIZED': {
        'description': 'Analyze realized and unrealized gains for Algo19.',
        'roles': ['Admin'],
        'icon': '📊'
    },
    'ALGO 8 CALCULATOR': {
        'description': 'Calculate PNL for NIFTY/SENSEX options with Algo 8.',
        'roles': ['Admin'],
        'icon': '🧮'
    },
    'HEDGE MANAGER': {
        'description': 'Manage hedge operations.',
        'roles': ['Admin', 'User'],
        'icon': '🛡️'
    }
}

MODULES = {
    'HEDGE AUTOMATION': 'hedge_automation',
    'VAR PRO': 'varpro',
    'SUMMARY AUTOMATION': 'summary_automation',
    'JAINAM': 'jainam',
    'USERSETTING': 'usersetting',
    'ALGO19 REALIZED AND UNREALIZED': 'algo19',
    'ALGO 8 CALCULATOR': 'algo8',
    'HEDGE MANAGER': 'hedge'
}

# --- Utility functions ---
def get_avatar(name):
    if name.strip():
        initials = ''.join(n[0].upper() for n in name.split()[:2])
        return f'''
        <div class="avatar" title="User initials: {initials}">
            {initials}
        </div>
        '''
    return '<div class="avatar-placeholder">👤</div>'

# --- Enhanced CSS styles with improved sidebar layout ---
CSS = """
<style>
:root {
    --primary-color: #4F46E5;
    --secondary-color: #10B981;
    --accent-gradient: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
    --user-gradient: linear-gradient(135deg, #10B981 0%, #FDE047 100%);
    --bg-light: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%);
    --bg-dark: linear-gradient(135deg, #1F2937 0%, #111827 100%);
    --text-light: #111827;
    --text-dark: #F9FAFB;
    --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --border-radius: 12px;
    --transition-fast: 0.2s ease;
    --transition-slow: 0.4s ease;
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --sidebar-width: 300px;
    --sidebar-btn-height: 56px;
    --sidebar-btn-padding: 0.75rem 1rem;
    --sidebar-btn-margin: 0.25rem 0;
    --action-btn-height: 48px;
    --action-btn-bg: #EF4444;
    --action-btn-bg-hover: #DC2626;
}

body {
    font-family: var(--font-family);
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: hidden;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.container, .dash-container {
    animation: fadeIn var(--transition-slow);
}

@media (prefers-color-scheme: dark) {
    body {
        background: var(--bg-dark);
        color: var(--text-dark);
    }
    .container, .dash-container {
        background: rgba(31, 41, 55, 0.8);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: var(--shadow-lg);
    }
    input, select, .stTextInput > div > div > input, .stSelectbox > div > div > select {
        background: rgba(55, 65, 81, 0.8);
        color: var(--text-dark);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
    }
    input:focus, select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.3);
    }
    .card, .sidebar-card {
        background: rgba(31, 41, 55, 0.9);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: var(--shadow-md);
        transition: transform var(--transition-slow), box-shadow var(--transition-slow), background var(--transition-slow);
    }
    .card:hover, .sidebar-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--shadow-lg);
        background: rgba(55, 65, 81, 0.9);
    }
    .stButton > button {
        background: var(--accent-gradient);
        background-size: 200% 200%;
        animation: gradientShift 5s ease infinite;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        transition: transform var(--transition-fast), box-shadow var(--transition-fast);
        box-shadow: var(--shadow-sm);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* Enhanced Sidebar Styles */
    .stSidebar {
        width: var(--sidebar-width) !important;
        background: rgba(17, 24, 39, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stSidebar > div > div {
        padding: 1rem 0.5rem !important;
    }
    
    /* Standard Sidebar Navigation Buttons */
    .sidebar-nav-btn {
        background: var(--accent-gradient) !important;
        background-size: 200% 200% !important;
        animation: gradientShift 5s ease infinite !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: var(--sidebar-btn-padding) !important;
        margin: var(--sidebar-btn-margin) !important;
        width: 100% !important;
        height: var(--sidebar-btn-height) !important;
        transition: all var(--transition-fast) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 0.75rem !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        box-shadow: var(--shadow-sm) !important;
        text-decoration: none !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
    }
    
    .sidebar-nav-btn:hover {
        transform: translateX(4px) !important;
        box-shadow: var(--shadow-md) !important;
        background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%) !important;
    }
    
    .sidebar-nav-btn:active {
        transform: translateX(2px) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* User-specific navigation buttons */
    .user-nav-btn {
        background: var(--user-gradient) !important;
        animation: gradientShift 5s ease infinite !important;
    }
    
    .user-nav-btn:hover {
        background: linear-gradient(135deg, #FDE047 0%, #10B981 100%) !important;
    }
    
    /* Action Buttons (Back to Dashboard and Logout) */
    .action-btn {
        background: var(--action-btn-bg) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        height: var(--action-btn-height) !important;
        padding: var(--sidebar-btn-padding) !important;
        margin: var(--sidebar-btn-margin) !important;
        width: 100% !important;
        border-radius: var(--border-radius) !important;
        transition: all var(--transition-fast) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        font-size: 0.95rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .action-btn:hover {
        background: var(--action-btn-bg-hover) !important;
        transform: translateX(2px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .action-btn:active {
        transform: translateX(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Navigation title styling */
    .sidebar-title {
        color: var(--text-dark) !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        text-align: center !important;
    }
    
    .user-info {
        background: rgba(55, 65, 81, 0.5) !important;
        border-radius: var(--border-radius) !important;
        padding: 1rem !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        text-align: center !important;
    }
    
    .user-info .avatar {
        margin: 0 auto 0.75rem !important;
    }
    
    .user-name {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin: 0 !important;
    }
    
    .user-role {
        color: #9CA3AF !important;
        font-size: 0.875rem !important;
        margin: 0 !important;
    }
}

@media (prefers-color-scheme: light) {
    body {
        background: var(--bg-light);
        color: var(--text-light);
    }
    .container, .dash-container {
        background: white;
        border: 1px solid #E5E7EB;
        box-shadow: var(--shadow-md);
    }
    input, select, .stTextInput > div > div > input, .stSelectbox > div > div > select {
        background: white;
        color: var(--text-light);
        border: 1px solid #D1D5DB;
        transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
    }
    input:focus, select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
    }
    .card, .sidebar-card {
        background: white;
        border: 1px solid #E5E7EB;
        box-shadow: var(--shadow-sm);
        transition: transform var(--transition-slow), box-shadow var(--transition-slow);
    }
    .card:hover, .sidebar-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--shadow-md);
    }
    .stButton > button {
        background: var(--accent-gradient);
        background-size: 200% 200%;
        animation: gradientShift 5s ease infinite;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        transition: transform var(--transition-fast), box-shadow var(--transition-fast);
        box-shadow: var(--shadow-sm);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* Light theme sidebar styles */
    .stSidebar {
        width: var(--sidebar-width) !important;
        background: #ffffff !important;
        border-right: 1px solid #E5E7EB !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stSidebar > div > div {
        padding: 1rem 0.5rem !important;
    }
    
    .sidebar-nav-btn {
        background: var(--accent-gradient) !important;
        background-size: 200% 200% !important;
        animation: gradientShift 5s ease infinite !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: var(--sidebar-btn-padding) !important;
        margin: var(--sidebar-btn-margin) !important;
        width: 100% !important;
        height: var(--sidebar-btn-height) !important;
        transition: all var(--transition-fast) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 0.75rem !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        box-shadow: var(--shadow-sm) !important;
        text-decoration: none !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
    }
    
    .sidebar-nav-btn:hover {
        transform: translateX(4px) !important;
        box-shadow: var(--shadow-md) !important;
        background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%) !important;
    }
    
    .sidebar-nav-btn:active {
        transform: translateX(2px) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .user-nav-btn {
        background: var(--user-gradient) !important;
        animation: gradientShift 5s ease infinite !important;
    }
    
    .user-nav-btn:hover {
        background: linear-gradient(135deg, #FDE047 0%, #10B981 100%) !important;
    }
    
    .action-btn {
        background: var(--action-btn-bg) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        height: var(--action-btn-height) !important;
        padding: var(--sidebar-btn-padding) !important;
        margin: var(--sidebar-btn-margin) !important;
        width: 100% !important;
        border-radius: var(--border-radius) !important;
        transition: all var(--transition-fast) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        font-size: 0.95rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .action-btn:hover {
        background: var(--action-btn-bg-hover) !important;
        transform: translateX(2px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .action-btn:active {
        transform: translateX(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .sidebar-title {
        color: var(--text-light) !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid #E5E7EB !important;
        text-align: center !important;
    }
    
    .user-info {
        background: #F9FAFB !important;
        border-radius: var(--border-radius) !important;
        padding: 1rem !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid #E5E7EB !important;
        text-align: center !important;
    }
    
    .user-info .avatar {
        margin: 0 auto 0.75rem !important;
    }
    
    .user-name {
        color: var(--text-light) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin: 0 !important;
    }
    
    .user-role {
        color: #6B7280 !important;
        font-size: 0.875rem !important;
        margin: 0 !important;
    }
}

.container {
    max-width: 480px;
    margin: 6rem auto;
    padding: 2.5rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-md);
    animation: fadeIn var(--transition-slow);
}

.dash-container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 1.5rem;
    border-radius: var(--border-radius);
}

.dash-header {
    text-align: center;
    margin-bottom: 2rem;
}

.avatar {
    display: flex;
    width: 64px;
    height: 64px;
    margin: 0 auto 1.5rem;
    border-radius: 50%;
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    background: var(--accent-gradient);
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
    transition: transform var(--transition-slow), box-shadow var(--transition-slow);
}

.avatar:hover {
    transform: rotate(360deg);
    box-shadow: var(--shadow-md);
}

h2 {
    font-size: 1.875rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.form-error {
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 1.5rem;
    font-weight: 500;
    animation: pulse var(--transition-slow);
}

.dash-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.card {
    padding: 1.5rem;
    border-radius: var(--border-radius);
    cursor: pointer;
}

/* Ensure consistent button sizing for Streamlit buttons in sidebar */
.stSidebar [data-testid="stButton"] > button {
    height: var(--sidebar-btn-height) !important;
    min-height: var(--sidebar-btn-height) !important;
    padding: var(--sidebar-btn-padding) !important;
    margin: var(--sidebar-btn-margin) !important;
    border-radius: var(--border-radius) !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 0.75rem !important;
}

/* Specific styling for action buttons in sidebar */
.stSidebar [data-testid="stButton"][key*="back"] > button,
.stSidebar [data-testid="stButton"][key="logout_button"] > button {
    justify-content: center !important;
    gap: 0.5rem !important;
    background: var(--action-btn-bg) !important;
    color: white !important;
    height: var(--action-btn-height) !important;
}

.stSidebar [data-testid="stButton"][key*="back"] > button:hover,
.stSidebar [data-testid="stButton"][key="logout_button"] > button:hover {
    background: var(--action-btn-bg-hover) !important;
    transform: translateX(2px) !important;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# --- Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ''
    st.session_state.role = 'user'
    st.session_state.error = ''
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# --- Login page ---
def login_page():
    # ---- Header & avatar -------------------------------------------------
    st.markdown(get_avatar(st.session_state.user_name), unsafe_allow_html=True)
    st.markdown('<h2>Welcome Back</h2>', unsafe_allow_html=True)

    # ---- Error message ----------------------------------------------------
    if st.session_state.error:
        st.markdown(f'<div class="form-error">{st.session_state.error}</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 1. Use a normal (non-form) widget for the role selector
    # -----------------------------------------------------------------
    role = st.selectbox(
        "Login as:",
        ["User", "Admin"],
        index=0 if st.session_state.role == "user" else 1,
        key="role_select"
    )

    # -----------------------------------------------------------------
    # 2. Wrap ONLY the remaining inputs + submit button in a form
    # -----------------------------------------------------------------
    with st.form(key="login_form", clear_on_submit=True):
        # Name is always required
        name = st.text_input(
            "Your Name",
            max_chars=30,
            placeholder="Enter your name",
            value=st.session_state.user_name,
            key="name_input"
        )

        # Show password field **only when role == Admin**
        password = ""
        if role == "Admin":
            password = st.text_input(
                "Admin Password",
                type="password",
                placeholder="Enter admin password",
                key="password_input"
            )

        # Submit button
        submitted = st.form_submit_button("Enter Dashboard")

        # -----------------------------------------------------------------
        # 3. Validation – runs **only** when the button is pressed
        # -----------------------------------------------------------------
        if submitted:
            if not name.strip():
                st.session_state.error = "Name is required!"
                st.rerun()

            if role == "Admin" and password != "admin123":
                st.session_state.error = "Invalid admin password!"
                st.rerun()

            # ---- SUCCESS ------------------------------------------------
            st.session_state.logged_in = True
            st.session_state.user_name = name.strip()
            st.session_state.role = role.lower()
            st.session_state.error = ""
            st.session_state.current_page = "dashboard"
            st.rerun()# --- Render Sidebar Cards for Admin Role ---
            
def render_admin_sidebar_cards():
    st.markdown('<h3 class="sidebar-title">Navigation</h3>', unsafe_allow_html=True)
    for card_name, card in CARDS.items():
        if 'Admin' in card['roles']:
            if card_name == 'STRATEGY AUTOMATION':
                st.markdown(
                    f"""
                    <a href="https://strategiesautomationbysahil.streamlit.app/" target="_blank" class="sidebar-nav-btn" style="text-decoration: none;">
                        <span style="font-size: 1.1em;">{card['icon']}</span>
                        <span>{card_name}</span>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                col1, col2 = st.columns([1, 8])
                with col1:
                    st.markdown(f"<span style='font-size: 1.1em;'>{card['icon']}</span>", unsafe_allow_html=True)
                with col2:
                    if st.button(card_name, key=f"open_admin_{card_name.replace(' ', '_').lower()}", 
                               help=card['description'], use_container_width=True):
                        st.session_state.current_page = MODULES[card_name]
                        st.rerun()

# --- Render Sidebar Cards for User Role ---
def render_user_sidebar_cards():
    st.markdown('<h3 class="sidebar-title">Navigation</h3>', unsafe_allow_html=True)
    for card_name, card in CARDS.items():
        if 'User' in card['roles']:
            if card_name == 'STRATEGY AUTOMATION':
                st.markdown(
                    f"""
                    <a href="https://strategiesautomationbysahil.streamlit.app/" target="_blank" class="sidebar-nav-btn user-nav-btn" style="text-decoration: none;">
                        <span style="font-size: 1.1em;">{card['icon']}</span>
                        <span>{card_name}</span>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                col1, col2 = st.columns([1, 8])
                with col1:
                    st.markdown(f"<span style='font-size: 1.1em;'>{card['icon']}</span>", unsafe_allow_html=True)
                with col2:
                    if st.button(card_name, key=f"open_user_{card_name.replace(' ', '_').lower()}", 
                               help=card['description'], use_container_width=True):
                        st.session_state.current_page = MODULES[card_name]
                        st.rerun()

# --- User Dashboard Pages ---
def user_dashboard():
    st.markdown('<div class="dash-header">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;">{get_avatar(st.session_state.user_name)}</div>', unsafe_allow_html=True)
    st.markdown(f'<h2>Welcome, {st.session_state.user_name}!</h2>', unsafe_allow_html=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'<p style="text-align:center; font-weight:600; font-style:italic;">Last updated at {now}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Page content based on selection
    if st.session_state.current_page == 'dashboard':
        st.subheader("Your Activity Trend User")
    elif st.session_state.current_page == 'hedge_automation':
        try:
            hedge_automation.run()
        except Exception as e:
            st.error(f"Error in Hedge Automation: {e}")
    elif st.session_state.current_page == 'varpro':
        try:
            varpro.run()
        except Exception as e:
            st.error(f"Error in VAR Pro: {e}")
    elif st.session_state.current_page == 'summary_automation':
        try:
            Summary_Automation.run()
        except Exception as e:
            st.error(f"Error in Summary Automation: {e}")
    elif st.session_state.current_page == 'hedge':
        try:
            hedge.run()
        except Exception as e:
            st.error(f"Error in Hedge Manager: {e}")

# --- Admin Dashboard ---
def admin_dashboard():
    st.markdown('<div class="dash-header">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;">{get_avatar(st.session_state.user_name)}</div>', unsafe_allow_html=True)
    st.markdown(f'<h2>Welcome, Admin {st.session_state.user_name}!</h2>', unsafe_allow_html=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'<p style="text-align:center; font-weight:600; font-style:italic;">Last updated at {now}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Page content based on selection
    if st.session_state.current_page == 'dashboard':
        st.subheader("Your Activity Trend Admin")
    elif st.session_state.current_page == 'hedge_automation':
        try:
            hedge_automation.run()
        except Exception as e:
            st.error(f"Error in Hedge Automation: {e}")
    elif st.session_state.current_page == 'varpro':
        try:
            varpro.run()
        except Exception as e:
            st.error(f"Error in VAR Pro: {e}")
    elif st.session_state.current_page == 'summary_automation':
        try:
            Summary_Automation.run()
        except Exception as e:
            st.error(f"Error in Summary Automation: {e}")
    elif st.session_state.current_page == 'jainam':
        try:
            jainam.run()
        except Exception as e:
            st.error(f"Error in Jainam: {e}")
    elif st.session_state.current_page == 'usersetting':
        try:
            usersetting_compare.run()
        except Exception as e:
            st.error(f"Error in User Settings: {e}")
    elif st.session_state.current_page == 'algo19':
        try:
            algo19.run()
        except Exception as e:
            st.error(f"Error in Algo19: {e}")
    elif st.session_state.current_page == 'algo8':
        try:
            algo8.run()
        except Exception as e:
            st.error(f"Error in Algo 8 Calculator: {e}")
    elif st.session_state.current_page == 'hedge':
        try:
            hedge.run()
        except Exception as e:
            st.error(f"Error in Hedge Manager: {e}")

# --- Main app control ---
if not st.session_state.logged_in:
    login_page()
else:
    # Enhanced Sidebar with consistent layout
    with st.sidebar:
        # Panel title
        st.markdown(f'<h3 class="sidebar-title">{st.session_state.role.capitalize()} Panel</h3>', unsafe_allow_html=True)
        
        # User info section
        st.markdown('<div class="user-info">', unsafe_allow_html=True)
        st.markdown(get_avatar(st.session_state.user_name), unsafe_allow_html=True)
        st.markdown(f'<p class="user-name">Logged in as: {st.session_state.user_name}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="user-role">Role: {st.session_state.role.capitalize()}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Navigation cards
        if st.session_state.role == 'user':
            render_user_sidebar_cards()
        elif st.session_state.role == 'admin':
            render_admin_sidebar_cards()

        # Action buttons with distinct styling
        st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)  # Spacer
        if st.button("🔙 Back to Dashboard", key=f"back_dashboard_{st.session_state.current_page}", 
                    help="Return to main dashboard", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()

        if st.button("🚪 Logout", key='logout_button', help="Log out of the system"):
            st.session_state.logged_in = False
            st.session_state.user_name = ''
            st.session_state.role = 'user'
            st.session_state.error = ''
            st.session_state.current_page = 'dashboard'
            st.rerun()

    # Main content area
    if st.session_state.role == 'admin':
        admin_dashboard()
    else:
        user_dashboard()
