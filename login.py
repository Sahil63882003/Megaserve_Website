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
CSS =  """
<style>
/* ========================================================
   HyperGlass 2025 v3 – ULTRA-CENTERED NEON STREAMLIT THEME
   -------------------------------------------------------
   • 100% CENTERED LAYOUT (Login, Dashboard, Cards, Messages)
   • Neon Glass Panels + Animated Gradient Borders
   • Smart Collapsible Sidebar
   • 60 FPS Micro-interactions + Ripple + Pulse
   • Mobile-First + Auto Dark/Light
   • AA/AAA Accessible
   ======================================================== */

:root {
  /* Core Palette – Neon 2025 */
  --primary: #00FF9C;        /* Neon Green */
  --primary-glow: #B6FFA1;
  --secondary: #D2FF72;      /* Electric Lime */
  --accent: #E0185A;         /* Neon Pink */
  --success: #15B392;        /* Emerald */
  --danger: #FCF927;         /* Neon Yellow */
  --warning: #F61981;        /* Hot Pink */

  /* Gradients */
  --grad-primary: linear-gradient(135deg, var(--primary) 0%, var(--primary-glow) 100%);
  --grad-secondary: linear-gradient(135deg, var(--secondary) 0%, var(--success) 100%);
  --grad-accent: linear-gradient(135deg, var(--accent) 0%, var(--primary-glow) 100%);
  --grad-border: linear-gradient(45deg, #00FF9C, #E0185A, #D2FF72, #15B392, #00FF9C);

  /* Glass & Backgrounds */
  --glass: rgba(255, 255, 255, 0.12);
  --glass-hover: rgba(255, 255, 255, 0.22);
  --glass-dark: rgba(15, 23, 42, 0.75);
  --glass-dark-hover: rgba(30, 41, 59, 0.95);
  --bg-light: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
  --bg-dark: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);

  /* Layout */
  --radius: 24px;
  --radius-sm: 16px;
  --transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  --transition-fast: all 0.2s ease-out;
  --shadow-sm: 0 8px 20px rgba(0,0,0,0.12);
  --shadow-md: 0 16px 32px rgba(0,0,0,0.18);
  --shadow-lg: 0 24px 48px rgba(0,0,0,0.22);
  --sidebar-width: 320px;
  --sidebar-collapsed: 80px;
  --gap: 2.5rem;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
}

/* Global Reset */
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-light);
  color: #1e293b;
  line-height: 1.7;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem 1rem;
  transition: background 0.6s ease;
}
@media (prefers-color-scheme: dark) {
  body { background: var(--bg-dark); color: #e2e8f0; }
}

/* ========================================
   100% CENTERED LAYOUT (Login + Dashboard)
   ======================================== */
.main-container {
  width: 100%;
  max-width: 600px;
  margin: 3rem auto;
  animation: floatIn 1s ease-out;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.dash-container {
  width: 100%;
  max-width: 1440px;
  margin: 2rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--gap);
  animation: floatIn 0.8s ease-out;
}

/* Floating Glass Panel – Centered */
.glass-panel {
  width: 100%;
  max-width: 520px;
  background: var(--glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius);
  border: 2px solid rgba(255, 255, 255, 0.2);
  padding: 2.8rem;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  transition: var(--transition);
  text-align: center;
}
.glass-panel:hover {
  transform: translateY(-10px) scale(1.01);
  box-shadow: 0 36px 72px rgba(0, 255, 156, 0.28);
  background: var(--glass-hover);
}
@media (prefers-color-scheme: dark) {
  .glass-panel { background: var(--glass-dark); }
  .glass-panel:hover { background: var(--glass-dark-hover); }
}

/* Animated Gradient Border */
.glass-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--radius);
  padding: 2px;
  background: var(--grad-border);
  background-size: 300% 300%;
  animation: borderFlow 8s linear infinite;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.7;
  transition: opacity 0.4s ease;
}
.glass-panel:hover::before { opacity: 1; }

/* ========================================
   SIDEBAR – Smart & Collapsible
   ======================================== */
.stSidebar {
  width: var(--sidebar-width) !important;
  background: var(--glass-dark);
  backdrop-filter: blur(28px);
  border-right: 1px solid rgba(255,255,255,0.15);
  transition: width 0.4s var(--transition);
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 100;
}
@media (prefers-color-scheme: light) {
  .stSidebar { background: var(--glass); }
}

/* Sticky Header */
.sidebar-header {
  position: sticky;
  top: 0;
  background: inherit;
  padding: 2rem 1.4rem 1.4rem;
  border-bottom: 1px solid rgba(255,255,255,0.12);
  z-index: 10;
  text-align: center;
}
.sidebar-title {
  font-size: 1.6rem;
  font-weight: 900;
  background: var(--grad-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

/* Collapse Toggle */
.sidebar-toggle {
  position: absolute;
  top: 1.8rem;
  right: -16px;
  width: 40px; height: 40px;
  background: var(--grad-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: var(--shadow-md);
  color: white;
  font-weight: bold;
  font-size: 1rem;
  transition: var(--transition-fast);
  z-index: 11;
}
.sidebar-toggle:hover { transform: scale(1.2); }

/* Collapsed State */
.stSidebar[data-collapsed="true"] {
  width: var(--sidebar-collapsed) !important;
}
.stSidebar[data-collapsed="true"] .sidebar-nav-btn span,
.stSidebar[data-collapsed="true"] .sidebar-title { display: none; }
.stSidebar[data-collapsed="true"] .sidebar-nav-btn { justify-content: center; padding: 0; }

/* Sidebar Nav Buttons */
.sidebar-nav-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 1.2rem;
  height: 62px;
  margin: 0.5rem 0.9rem;
  padding: 0 1.4rem;
  border-radius: var(--radius-sm);
  background: var(--grad-primary);
  background-size: 220% 220%;
  color: #fff;
  font-weight: 600;
  font-size: 1rem;
  overflow: hidden;
  cursor: pointer;
  transition: var(--transition);
  animation: gradientFlow 7s ease infinite;
  box-shadow: var(--shadow-sm);
}
.sidebar-nav-btn::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 2px;
  background: var(--grad-border);
  background-size: 300% 300%;
  animation: borderFlow 6s linear infinite;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.sidebar-nav-btn:hover::before { opacity: 0.8; }
.sidebar-nav-btn:hover {
  transform: translateX(10px) scale(1.05);
  box-shadow: var(--shadow-md);
}
.user-nav-btn { background: var(--grad-secondary); }

/* Action Buttons */
.action-btn {
  height: 54px;
  background: var(--danger);
  color: white;
  font-weight: 700;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  margin: 0.5rem 0.9rem;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}
.action-btn:hover {
  background: #e62626;
  transform: translateY(-4px);
  animation: pulseGlow 1.6s infinite;
}
.action-btn:active::after {
  content: ""; position: absolute; width: 28px; height: 28px;
  background: rgba(255,255,255,0.4); border-radius: 50%;
  animation: ripple 0.7s ease-out;
}

/* ========================================
   ANIMATIONS
   ======================================== */
@keyframes floatIn { from { opacity: 0; transform: translateY(30px) scale(0.95); } to { opacity: 1; transform: none; } }
@keyframes gradientFlow { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
@keyframes borderFlow { 0% { background-position: 0% 50%; } 100% { background-position: 300% 50%; } }
@keyframes ripple { to { transform: scale(3); opacity: 0; } }
@keyframes pulseGlow { 0%,100% { box-shadow: 0 0 18px rgba(224,24,90,0.5); } 50% { box-shadow: 0 0 40px rgba(0,255,156,0.8); } }

/* ========================================
   DASHBOARD CARDS – CENTERED GRID
   ======================================== */
.dash-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: var(--gap);
  width: 100%;
  max-width: 1200px;
  justify-content: center;
}
.card {
  background: var(--glass);
  backdrop-filter: blur(14px);
  border-radius: var(--radius);
  padding: 2.2rem;
  border: 2px solid rgba(255,255,255,0.18);
  box-shadow: var(--shadow-md);
  transition: var(--transition);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  text-align: center;
}
.card:hover {
  transform: translateY(-12px) scale(1.04);
  box-shadow: var(--shadow-lg);
  background: var(--glass-hover);
}
.card::before {
  content: ""; position: absolute; inset: 0; border-radius: inherit;
  padding: 2px; background: var(--grad-border); background-size: 300% 300%;
  animation: borderFlow 9s linear infinite;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; opacity: 0.4; transition: opacity 0.4s;
}
.card:hover::before { opacity: 0.9; }
@media (prefers-color-scheme: dark) {
  .card { background: var(--glass-dark); }
  .card:hover { background: var(--glass-dark-hover); }
}

/* ========================================
   FORM & INPUTS – CENTERED
   ======================================== */
.glass-panel .stTextInput,
.glass-panel .stSelectbox,
.glass-panel .stButton {
  width: 100%;
  max-width: 420px;
  margin: 1rem auto;
  display: block;
}

input, select, textarea,
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
  width: 100%;
  background: rgba(255,255,255,0.92);
  border: 2px solid rgba(0,255,156,0.3);
  border-radius: var(--radius-sm);
  padding: 0.9rem 1.4rem;
  font-size: 1.05rem;
  transition: var(--transition);
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  text-align: center;
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(0,255,156,0.3), 0 8px 22px rgba(0,255,156,0.2);
  transform: scale(1.03);
}
@media (prefers-color-scheme: dark) {
  input, select, textarea,
  .stTextInput > div > div > input,
  .stSelectbox > div > div > select {
    background: rgba(30,41,59,0.97);
    border-color: rgba(182,255,161,0.4);
    color: #f1f5f9;
  }
}

/* Buttons – Centered */
.stButton > button {
  width: 100%;
  max-width: 420px;
  margin: 1.5rem auto;
  display: block;
  background: var(--grad-primary);
  background-size: 220% 220%;
  animation: gradientFlow 6s ease infinite;
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: 1rem 2.2rem;
  font-weight: 700;
  font-size: 1.05rem;
  box-shadow: var(--shadow-md);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}
.stButton > button:hover {
  transform: translateY(-5px) scale(1.06);
  box-shadow: 0 22px 44px rgba(0,255,156,0.4);
}
.stButton > button:active::after {
  content: ""; position: absolute; inset: 0;
  background: rgba(255,255,255,0.3);
  animation: ripple 0.6s ease-out;
}

/* Messages – Centered */
.stAlert, .stSuccess, .stInfo, .stWarning, .stError {
  max-width: 520px;
  margin: 1.5rem auto;
  text-align: center;
  border-radius: var(--radius-sm);
}

/* Avatar – Centered */
.avatar {
  width: 88px; height: 88px;
  border-radius: 50%;
  background: var(--grad-primary);
  color: white;
  font-weight: 900;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.8rem;
  box-shadow: var(--shadow-md);
  transition: var(--transition);
}
.avatar:hover { transform: rotate(360deg) scale(1.2); }

/* Headings – Centered */
h1, h2, h3, h4 {
  background: var(--grad-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: -0.03em;
  text-align: center;
}
h2 { font-size: 2.4rem; margin-bottom: 1.8rem; }

/* Responsive */
@media (max-width: 768px) {
  .main-container, .dash-container { padding: 1.8rem; margin: 1.2rem auto; }
  .glass-panel, .card { padding: 2rem; }
  .dash-cards { grid-template-columns: 1fr; }
  .stSidebar { width: var(--sidebar-collapsed) !important; }
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

