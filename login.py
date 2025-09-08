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
import algo19  # Placeholder for the new Algo19 module

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
    }
}

MODULES = {
    'HEDGE AUTOMATION': 'hedge_automation',
    'VAR PRO': 'varpro',
    'SUMMARY AUTOMATION': 'summary_automation',
    'JAINAM': 'jainam',
    'USERSETTING': 'usersetting',
    'ALGO19 REALIZED AND UNREALIZED': 'algo19'
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

# --- Enhanced CSS styles with centralization and symmetry ---
CSS = """
<style>
:root {
    --accent1: #6D28D9;
    --accent2: #059669;
    --dash-purple: #6D28D9;
    --dash-pink: #DB2777;
    --dash-yellow: #EAB308;
    --admin-accent: linear-gradient(135deg, #6D28D9 0%, #DB2777 100%);
    --user-accent: linear-gradient(135deg, #059669 0%, #EAB308 100%);
    --error-bg: #FEE2E2;
    --success-bg: #D1FAE5;
    --font-family: 'Inter', sans-serif;
    --border-radius: 16px;
    --transition: 0.4s ease;
    --shadow-light: 0 10px 24px rgba(0,0,0,0.1);
    --shadow-dark: 0 14px 36px rgba(0,0,0,0.2);
    --bg-gradient-light: linear-gradient(135deg, #F3F4F6, #FFFFFF);
    --bg-gradient-dark: linear-gradient(135deg, #4C1D95, #831843 70%, #92400E 100%);
    --sidebar-button-width: 100%;
    --sidebar-button-height: 48px;
}
body {
    font-family: var(--font-family);
    margin: 0; padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
}
@media (prefers-color-scheme: dark) {
    body {
        background: var(--bg-gradient-dark);
        color: #F3F4F6;
    }
    .container {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: var(--shadow-dark);
        backdrop-filter: blur(20px);
    }
    input, select {
        background: rgba(255,255,255,0.08);
        color: #F3F4F6;
        border: 1px solid rgba(255,255,255,0.15);
    }
    input:focus, select:focus {
        box-shadow: 0 0 12px var(--accent1);
        border-color: var(--accent1);
        background: rgba(255,255,255,0.15);
    }
    h2, h3 {
        background: var(--admin-accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .card, .sidebar-card {
        background: rgba(255,255,255,0.1);
        box-shadow: var(--shadow-dark);
        border-color: rgba(255,255,255,0.2);
        transition: transform var(--transition), box-shadow var(--transition);
    }
    .card:hover, .sidebar-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 40px rgba(0,0,0,0.3);
    }
    .stButton > button {
        background-image: var(--admin-accent);
        box-shadow: 0 8px 32px rgba(109,40,217,0.6);
        color: white;
        font-weight: 700;
        border-radius: var(--border-radius);
        padding: 1rem 2rem;
        font-size: 1.2rem;
        transition: transform var(--transition), filter var(--transition);
        width: 100%;
        max-width: 600px;
        margin: 0.8rem auto;
        display: block;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        filter: brightness(1.2);
    }
    .sidebar-nav-btn, .stSidebar .stButton > button {
        background: linear-gradient(135deg, var(--accent1) 0%, var(--dash-pink) 100%);
        color: white;
        font-weight: 600;
        border-radius: var(--border-radius);
        padding: 0.8rem;
        margin: 0.5rem 0;
        width: var(--sidebar-button-width);
        height: var(--sidebar-button-height);
        border: none;
        transition: transform var(--transition), box-shadow var(--transition);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        box-sizing: border-box;
        text-decoration: none;
    }
    .sidebar-nav-btn:hover, .stSidebar .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(109,40,217,0.4);
    }
    .user-nav-btn {
        background: linear-gradient(135deg, var(--accent2) 0%, var(--dash-yellow) 100%);
    }
    .logout-btn, .stSidebar .stButton > button[key="logout_button"] {
        color: #DDA0DD;
        text-decoration: underline;
        background: none;
        box-shadow: none;
        width: var(--sidebar-button-width);
        height: var(--sidebar-button-height);
        font-size: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logout-btn:hover, .stSidebar .stButton > button[key="logout_button"]:hover {
        color: #FF69B4;
        transform: translateY(-2px);
    }
}
@media (prefers-color-scheme: light) {
    body {
        background: var(--bg-gradient-light);
        color: #1F2937;
    }
    .container {
        background: white;
        border: 1px solid #E5E7EB;
        box-shadow: var(--shadow-light);
    }
    input, select {
        background: white;
        color: #1F2937;
        border: 1px solid #D1D5DB;
        border-radius: var(--border-radius);
        padding: 0.8rem 1.2rem;
        font-size: 1.1rem;
    }
    input:focus, select:focus {
        border-color: var(--accent1);
        box-shadow: 0 0 12px rgba(109,40,217,0.5);
    }
    h2, h3 {
        color: var(--dash-purple);
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 1.5rem;
    }
    .card, .sidebar-card {
        background: white;
        box-shadow: var(--shadow-light);
        border: 1px solid #E0E7FF;
        border-radius: var(--border-radius);
        padding: 2rem 1.8rem;
        transition: transform var(--transition), box-shadow var(--transition);
    }
    .card:hover, .sidebar-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 40px rgba(109,40,217,0.2);
    }
    .stButton > button {
        background-image: var(--admin-accent);
        box-shadow: 0 6px 28px rgba(109,40,217,0.4);
        border-radius: var(--border-radius);
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 700;
        color: white;
        width: 100%;
        max-width: 600px;
        margin: 0.8rem auto;
        display: block;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        filter: brightness(1.1);
    }
    .sidebar-nav-btn, .stSidebar .stButton > button {
        background: linear-gradient(135deg, var(--accent1) 0%, var(--dash-pink) 100%);
        color: white;
        font-weight: 600;
        border-radius: var(--border-radius);
        padding: 0.8rem;
        margin: 0.5rem 0;
        width: var(--sidebar-button-width);
        height: var(--sidebar-button-height);
        border: none;
        transition: transform var(--transition), box-shadow var(--transition);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        box-sizing: border-box;
        text-decoration: none;
    }
    .sidebar-nav-btn:hover, .stSidebar .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(109,40,217,0.3);
    }
    .user-nav-btn {
        background: linear-gradient(135deg, var(--accent2) 0%, var(--dash-yellow) 100%);
    }
    .logout-btn, .stSidebar .stButton > button[key="logout_button"] {
        color: #4C1D95;
        font-weight: 700;
        text-decoration: underline;
        background: none;
        box-shadow: none;
        width: var(--sidebar-button-width);
        height: var(--sidebar-button-height);
        font-size: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logout-btn:hover, .stSidebar .stButton > button[key="logout_button"]:hover {
        color: #7C3AED;
    }
}
.container {
    max-width: 600px;
    margin: 3rem auto;
    border-radius: var(--border-radius);
    padding: 2rem 2.5rem 3rem;
    text-align: center;
}
.avatar {
    display: inline-flex;
    width: 80px;
    height: 80px;
    margin: 0 auto 2rem;
    border-radius: 50%;
    font-size: 2.8rem;
    font-weight: 800;
    color: #fff;
    background: var(--admin-accent);
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 16px rgba(109,40,217,0.7);
    transition: transform var(--transition);
}
.avatar:hover {
    transform: scale(1.08) rotate(5deg);
    box-shadow: 0 10px 24px rgba(109,40,217,0.9);
}
.avatar-placeholder {
    font-size: 52px;
    color: #9CA3AF;
    margin-bottom: 2rem;
}
h2 {
    margin-bottom: 1rem;
    font-size: 2.2rem;
}
h3 {
    margin-bottom: 0.8rem;
    font-size: 1.4rem;
    letter-spacing: 1px;
}
input[type=text], input[type=password] {
    border-radius: var(--border-radius);
    margin-bottom: 1.2rem;
    width: 100%;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    display: block;
}
.stSelectbox > div > div > select {
    border-radius: var(--border-radius);
    padding: 0.8rem 1.2rem;
    font-size: 1.1rem;
    width: 100%;
    max-width: 600px;
    margin: 0.8rem auto;
    display: block;
}
.form-error {
    background: var(--error-bg);
    color: #B91C1C;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.5rem;
    border-radius: var(--border-radius);
    font-weight: 600;
    box-shadow: 0 0 8px #FCA5A5;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
}
.dash-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 0 1.5rem;
    text-align: center;
}
.dash-header {
    text-align: center;
    margin-bottom: 2rem;
}
.dash-metrics {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 2rem;
    gap: 1rem;
}
.dash-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2.5rem;
    margin-top: 2rem;
    justify-items: center;
}
.card {
    cursor: pointer;
    width: 100%;
    max-width: 400px;
}
.card.user {
    border-left: 8px solid var(--accent2);
}
.card.admin {
    border-left: 8px solid var(--accent1);
}
.card-accent {
    color: white !important;
    border: none !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.25);
}
.card-accent.user {
    background: var(--user-accent);
}
.card-accent.admin {
    background: var(--admin-accent);
}
.stMetric {
    margin: 0 auto;
}
.stExpander {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}
.sidebar-card {
    width: 100%;
    max-width: 200px;
    margin: 1rem auto;
    border-radius: var(--border-radius);
    padding: 1rem;
    cursor: pointer;
    transition: transform var(--transition), box-shadow var(--transition);
}
.sidebar-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
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
    st.session_state.current_page = 'dashboard'  # Default page

# --- Login page ---
def login_page():
    with st.container():
        st.markdown(get_avatar(st.session_state.user_name), unsafe_allow_html=True)
        st.markdown('<h2>Welcome Back</h2>', unsafe_allow_html=True)
        if st.session_state.error:
            st.markdown(f'<div class="form-error">{st.session_state.error}</div>', unsafe_allow_html=True)

        # Role select
        role = st.selectbox('Login as:', ['User', 'Admin'],
                            index=0 if st.session_state.role == 'user' else 1, key='role_select')
        st.session_state.role = role.lower()

        # Name input
        name = st.text_input('Your Name', max_chars=30, placeholder='Enter your name',
                             value=st.session_state.user_name, key='name_input')

        # Password for admin
        password = ''
        if role.lower() == 'admin':
            password = st.text_input('Admin Password', type='password', placeholder='Enter admin password', key='password_input')

        with st.form(key='login_form', clear_on_submit=True):
            submit = st.form_submit_button('Enter Dashboard →')
            if submit:
                if not name.strip():
                    st.session_state.error = 'Name is required!'
                    st.rerun()
                if role.lower() == 'admin':
                    if password != 'admin123':
                        st.session_state.error = 'Invalid admin password!'
                        st.rerun()
                st.session_state.logged_in = True
                st.session_state.user_name = name.strip()
                st.session_state.role = role.lower()
                st.session_state.error = ''
                st.session_state.current_page = 'dashboard'
                st.rerun()

# --- Render Sidebar Cards for Admin Role ---
def render_admin_sidebar_cards():
    st.markdown("### Navigation")
    for card_name, card in CARDS.items():
        if 'Admin' in card['roles']:
            if card_name == 'STRATEGY AUTOMATION':
                # Use an <a> tag styled as a button to open the link in a new tab
                st.markdown(
                    f"""
                    <a href="https://strategiesautomationbysahil.streamlit.app/" target="_blank" class="sidebar-nav-btn" style="width: 100%; height: 48px; margin: 0.5rem 0; display: flex; align-items: center; justify-content: center;">
                        {card['icon']} {card_name}
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                if st.button(f"{card['icon']} {card_name}", key=f"open_admin_{card_name.replace(' ', '_')}", help=card['description']):
                    st.session_state.current_page = MODULES[card_name]
                    st.rerun()

# --- Render Sidebar Cards for User Role ---
def render_user_sidebar_cards():
    st.markdown("### Navigation")
    for card_name, card in CARDS.items():
        if 'User' in card['roles']:
            if card_name == 'STRATEGY AUTOMATION':
                # Use an <a> tag styled as a button to open the link in a new tab
                st.markdown(
                    f"""
                    <a href="https://strategiesautomationbysahil.streamlit.app/" target="_blank" class="sidebar-nav-btn user-nav-btn" style="width: 100%; height: 48px; margin: 0.5rem 0; display: flex; align-items: center; justify-content: center;">
                        {card['icon']} {card_name}
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                if st.button(f"{card['icon']} {card_name}", key=f"open_user_{card_name.replace(' ', '_')}", help=card['description']):
                    st.session_state.current_page = MODULES[card_name]
                    st.rerun()

# --- User Dashboard Pages ---
def user_dashboard():
    st.markdown('<div class="dash-container">', unsafe_allow_html=True)
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

    st.markdown('</div>', unsafe_allow_html=True)

# --- Admin Dashboard ---
def admin_dashboard():
    st.markdown('<div class="dash-container">', unsafe_allow_html=True)
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

    st.markdown('</div>', unsafe_allow_html=True)

# --- Main app control ---
if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar for navigation and logout
    with st.sidebar:
        st.title(f"{st.session_state.role.capitalize()} Panel")
        st.markdown(get_avatar(st.session_state.user_name), unsafe_allow_html=True)
        st.write(f"Logged in as: {st.session_state.user_name}")

        if st.session_state.role == 'user':
            render_user_sidebar_cards()
        elif st.session_state.role == 'admin':
            render_admin_sidebar_cards()

        if st.button("🔙 Back to Dashboard", key="back_dashboard"):
            st.session_state.current_page = 'dashboard'
            st.rerun()

        if st.button("Logout", key='logout_button'):
            st.session_state.logged_in = False
            st.session_state.user_name = ''
            st.session_state.role = 'user'
            st.session_state.error = ''
            st.session_state.current_page = 'dashboard'
            st.rerun()

    if st.session_state.role == 'admin':
        admin_dashboard()
    else:
        user_dashboard()
