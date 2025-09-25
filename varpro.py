import streamlit as st
import pandas as pd
import numpy as np
import re

def extract_transaction_strike(symbol):
    match1 = re.search(r'(CE|PE)\s*(\d+)', symbol)
    if match1:
        return match1.group(1), match1.group(2)
    match2 = re.search(r'(\d+)(CE|PE)', symbol)
    if match2:
        return match2.group(2), match2.group(1)
    return None, None

def calculate_var(df, nfo_strike, bfo_strike, allocation):
    df["Transaction"], df["Strike"] = zip(*df["Symbol"].map(extract_transaction_strike))
    df["Strike"] = pd.to_numeric(df["Strike"], errors='coerce')
    df_nfo = df[df["Exchange"] == "NFO"].copy()
    df_bfo = df[df["Exchange"] == "BFO"].copy()
    nfo_results = {}
    if not df_nfo.empty:
        strike_nfo = df_nfo["Strike"]
        qty_nfo = df_nfo["Net Qty"]
        is_ce_nfo = df_nfo["Transaction"] == "CE"
        netpos_pos_nfo = qty_nfo > 0
        netpos_neg_nfo = qty_nfo < 0
        for perc in [10, -10, 15, -15]:
            calc_nfo = nfo_strike + (nfo_strike * perc / 100)
            colname = f"calc_{perc}%_VAR"
            if perc > 0:
                df_nfo[colname] = np.where(
                    netpos_pos_nfo & is_ce_nfo, (calc_nfo - strike_nfo) * abs(qty_nfo),
                    np.where(netpos_neg_nfo & is_ce_nfo, (calc_nfo - strike_nfo) * qty_nfo,
                    np.where(netpos_neg_nfo & ~is_ce_nfo, abs(df_nfo["Sell Avg Price"] * qty_nfo), 0))
                )
            else:
                df_nfo[colname] = np.where(
                    netpos_pos_nfo & ~is_ce_nfo, (strike_nfo - calc_nfo) * qty_nfo,
                    np.where(netpos_neg_nfo & is_ce_nfo, abs(df_nfo["Sell Avg Price"] * qty_nfo),
                    np.where(netpos_neg_nfo & ~is_ce_nfo, (calc_nfo - strike_nfo) * abs(qty_nfo), 0))
                )
            sum_var = df_nfo[colname].sum()
            perc_var = sum_var / allocation if allocation != 0 else 0
            nfo_results[perc] = (sum_var, perc_var)
    else:
        nfo_results = {perc: (0, 0) for perc in [10, -10, 15, -15]}
    bfo_results = {}
    if not df_bfo.empty:
        strike_bfo = df_bfo["Strike"]
        qty_bfo = df_bfo["Net Qty"]
        is_ce_bfo = df_bfo["Transaction"] == "CE"
        netpos_pos_bfo = qty_bfo > 0
        netpos_neg_bfo = qty_bfo < 0
        for perc in [10, -10, 15, -15]:
            calc_bfo = bfo_strike + (bfo_strike * perc / 100)
            colname = f"calc_{perc}%_VAR"
            if perc > 0:
                df_bfo[colname] = np.where(
                    netpos_pos_bfo & is_ce_bfo, (calc_bfo - strike_bfo) * abs(qty_bfo),
                    np.where(netpos_neg_bfo & is_ce_bfo, (calc_bfo - strike_bfo) * qty_bfo,
                    np.where(netpos_neg_bfo & ~is_ce_bfo, abs(df_bfo["Sell Avg Price"] * qty_bfo), 0))
                )
            else:
                df_bfo[colname] = np.where(
                    netpos_pos_bfo & ~is_ce_bfo, (strike_bfo - calc_bfo) * qty_bfo,
                    np.where(netpos_neg_bfo & is_ce_bfo, abs(df_bfo["Sell Avg Price"] * qty_bfo),
                    np.where(netpos_neg_bfo & ~is_ce_bfo, (calc_bfo - strike_bfo) * abs(qty_bfo), 0))
                )
            sum_var = df_bfo[colname].sum()
            perc_var = sum_var / allocation if allocation != 0 else 0
            bfo_results[perc] = (sum_var, perc_var)
    else:
        bfo_results = {perc: (0, 0) for perc in [10, -10, 15, -15]}
    return nfo_results, bfo_results, df_nfo, df_bfo

def run():
    st.markdown("""
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
        :root {
            --bg-light: #F9FAFB;
            --bg-dark: #1F2937;
            --text-light: #1E3A8A;
            --text-dark: #F3F4F6;
            --card-bg-light: #FFFFFF;
            --card-bg-dark: #374151;
            --accent: #3B82F6;
            --accent-hover: #1D4ED8;
            --border-accent: #93C5FD;
            --shadow-light: rgba(0, 0, 0, 0.08);
            --shadow-dark: rgba(0, 0, 0, 0.4);
            --positive-color: #10B981;
            --negative-color: #EF4444;
            --header-gradient: linear-gradient(90deg, #3B82F6, #A855F7, #EC4899);
            --blur: blur(10px);
        }
        .varpro-container {
            font-family: 'Poppins', sans-serif;
            max-width: 1200px;
            margin: 3rem auto;
            padding: 2rem;
            border-radius: 1.5rem;
            background: var(--bg-light);
            text-align: center;
            backdrop-filter: var(--blur);
            box-shadow: 0 10px 20px var(--shadow-light);
            transition: all 0.3s ease;
        }
        .dark-mode .varpro-container {
            background: var(--bg-dark);
            color: var(--text-dark);
            box-shadow: 0 10px 20px var(--shadow-dark);
        }
        .varpro-container, .varpro-container * {
            text-align: center !important;
        }
        .varpro-container .stApp {
            background: inherit;
            color: inherit;
        }
        .varpro-container .stButton > button {
            background: var(--header-gradient);
            color: white;
            border: none;
            padding: 0.75rem 2.5rem;
            border-radius: 0.75rem;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            min-width: 240px;
            margin: 1.5rem auto;
            display: block;
            box-shadow: 0 6px 12px var(--shadow-light), inset 0 2px 4px rgba(255, 255, 255, 0.3);
            position: relative;
            overflow: hidden;
        }
        .varpro-container .stButton > button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s ease, height 0.6s ease;
        }
        .varpro-container .stButton > button:hover::after {
            width: 400px;
            height: 400px;
        }
        .varpro-container .stButton > button:hover {
            background: linear-gradient(90deg, #2563EB, #9333EA, #DB2777);
            transform: translateY(-2px);
            box-shadow: 0 8px 16px var(--shadow-light);
        }
        .dark-mode .varpro-container .stButton > button:hover {
            box-shadow: 0 8px 16px var(--shadow-dark);
        }
        .varpro-container .metric-card {
            border-radius: 1rem;
            padding: 1.5rem;
            background: var(--card-bg-light);
            border: 2px solid var(--border-accent);
            backdrop-filter: var(--blur);
            transition: all 0.3s ease;
            margin: 1rem auto;
            max-width: 300px;
            box-shadow: 0 6px 12px var(--shadow-light);
            transform: translateY(0);
        }
        .varpro-container .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px var(--shadow-light);
            border-color: var(--accent);
        }
        .dark-mode .varpro-container .metric-card {
            background: var(--card-bg-dark);
            box-shadow: 0 6px 12px var(--shadow-dark);
        }
        .dark-mode .varpro-container .metric-card:hover {
            box-shadow: 0 8px 16px var(--shadow-dark);
        }
        .varpro-container .header {
            font-size: 3.5rem;
            font-weight: 700;
            background: var(--header-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            animation: slideIn 0.8s ease-out;
        }
        .varpro-container .subheader {
            font-size: 1.25rem;
            color: #4B5563;
            margin-bottom: 2rem;
            animation: fadeInUp 1s ease-out;
        }
        .dark-mode .varpro-container .subheader {
            color: #D1D5DB;
        }
        .varpro-container .fade-in {
            animation: fadeIn 1s ease-out;
        }
        .varpro-container .slide-in {
            animation: slideIn 0.8s ease-out;
        }
        .varpro-container .download-button {
            background: var(--header-gradient);
            color: white !important;
            padding: 0.75rem 2rem;
            border-radius: 0.75rem;
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 500;
            display: inline-block;
            margin: 1rem;
            box-shadow: 0 4px 8px var(--shadow-light);
            position: relative;
            overflow: hidden;
        }
        .varpro-container .download-button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s ease, height 0.6s ease;
        }
        .varpro-container .download-button:hover::after {
            width: 300px;
            height: 300px;
        }
        .varpro-container .download-button:hover {
            background: linear-gradient(90deg, #2563EB, #9333EA, #DB2777);
            transform: translateY(-2px);
        }
        .varpro-container .stFileUploader > div > div > input,
        .varpro-container .stNumberInput > div > div > input,
        .varpro-container .stSelectbox > div > div > select {
            border: 2px solid var(--border-accent);
            border-radius: 0.75rem;
            padding: 0.75rem;
            width: 100%;
            max-width: 600px;
            margin: 1rem auto;
            display: block;
            box-sizing: border-box;
            font-size: 1rem;
            background: var(--card-bg-light);
            backdrop-filter: var(--blur);
            box-shadow: 0 4px 8px var(--shadow-light);
            transition: all 0.3s ease;
        }
        .varpro-container .stFileUploader > div > div > input:hover,
        .varpro-container .stNumberInput > div > div > input:hover,
        .varpro-container .stSelectbox > div > div > select:hover {
            border-color: var(--accent);
            box-shadow: 0 4px 8px var(--shadow-light);
            transform: translateY(-2px);
        }
        .dark-mode .varpro-container .stFileUploader > div > div > input,
        .dark-mode .varpro-container .stNumberInput > div > div > input,
        .dark-mode .varpro-container .stSelectbox > div > div > select {
            border: 2px solid var(--border-accent);
            background: var(--card-bg-dark);
            color: var(--text-dark);
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .varpro-container .input-container {
            background: var(--card-bg-light);
            border: 2px solid var(--border-accent);
            border-radius: 1.25rem;
            padding: 2rem;
            max-width: 800px;
            margin: 2rem auto;
            box-shadow: 0 8px 16px var(--shadow-light);
            backdrop-filter: var(--blur);
            animation: slideIn 0.8s ease-out;
        }
        .dark-mode .varpro-container .input-container {
            background: var(--card-bg-dark);
            box-shadow: 0 8px 16px var(--shadow-dark);
        }
        .varpro-container .stForm {
            border: 2px solid var(--border-accent);
            border-radius: 1.25rem;
            padding: 2rem;
            background: var(--card-bg-light);
            max-width: 800px;
            margin: 2rem auto;
            box-shadow: 0 8px 16px var(--shadow-light);
            backdrop-filter: var(--blur);
            animation: slideIn 0.8s ease-out;
        }
        .dark-mode .varpro-container .stForm {
            background: var(--card-bg-dark);
            box-shadow: 0 8px 16px var(--shadow-dark);
        }
        .varpro-container .stColumns {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            justify-content: center;
            margin: 1.5rem 0;
        }
        .varpro-container .stExpander {
            border: 2px solid var(--border-accent);
            border-radius: 1rem;
            background: var(--card-bg-light);
            margin: 2rem auto;
            max-width: 1000px;
            box-shadow: 0 6px 12px var(--shadow-light);
            backdrop-filter: var(--blur);
            animation: fadeIn 1s ease-out;
        }
        .dark-mode .varpro-container .stExpander {
            background: var(--card-bg-dark);
            box-shadow: 0 6px 12px var(--shadow-dark);
        }
        .centered-image {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 2rem auto;
            width: 100%;
            max-width: 140px;
        }
        .centered-image img {
            width: 100%;
            max-width: 120px;
            height: auto;
            transition: transform 0.4s ease, opacity 0.4s ease;
            border-radius: 1rem;
            box-shadow: 0 4px 8px var(--shadow-light);
        }
        .centered-image img:hover {
            transform: scale(1.15);
            opacity: 0.9;
        }
        .dark-mode .centered-image img {
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .varpro-container [data-testid="stMetricLabel"],
        .varpro-container [data-testid="stMetricValue"],
        .varpro-container [data-testid="stMetricDelta"],
        .varpro-container [data-testid="stForm"] label,
        .varpro-container [data-testid="stExpander"] summary,
        .varpro-container [data-testid="stMarkdown"],
        .varpro-container .stSpinner > div > div,
        .varpro-container .stSuccess > div > div,
        .varpro-container .stError > div > div {
            text-align: center !important;
        }
        .varpro-container [data-testid="stMetricValue"] {
            font-weight: 700;
            font-size: 1.5rem;
            white-space: nowrap;
            overflow: visible;
            text-overflow: unset;
        }
        .varpro-container [data-testid="stMetricDelta"] {
            font-size: 1.25rem;
            white-space: nowrap;
            overflow: visible;
            text-overflow: unset;
        }
        .metric-positive [data-testid="stMetricValue"],
        .metric-positive [data-testid="stMetricDelta"] {
            color: var(--positive-color) !important;
        }
        .metric-negative [data-testid="stMetricValue"],
        .metric-negative [data-testid="stMetricDelta"] {
            color: var(--negative-color) !important;
        }
        .varpro-container .stAlert > div {
            text-align: center !important;
            max-width: 800px;
            margin: 1.5rem auto;
            border-radius: 1rem;
            border: 2px solid var(--border-accent);
            background: var(--card-bg-light);
            backdrop-filter: var(--blur);
            box-shadow: 0 6px 12px var(--shadow-light);
            animation: fadeIn 1s ease-out;
        }
        .dark-mode .varpro-container .stAlert > div {
            background: var(--card-bg-dark);
            box-shadow: 0 6px 12px var(--shadow-dark);
        }
        @media (max-width: 768px) {
            .varpro-container {
                padding: 1.5rem;
                margin: 1rem;
            }
            .varpro-container .header {
                font-size: 2.5rem;
            }
            .varpro-container .subheader {
                font-size: 1.1rem;
            }
            .varpro-container .stButton > button {
                min-width: 200px;
                padding: 0.6rem 2rem;
                font-size: 1rem;
            }
            .varpro-container .stFileUploader > div > div > input,
            .varpro-container .stNumberInput > div > div > input,
            .varpro-container .stSelectbox > div > div > select {
                max-width: 100%;
                margin: 0.75rem auto;
            }
            .varpro-container .input-container,
            .varpro-container .stForm {
                max-width: 100%;
                padding: 1.5rem;
            }
            .varpro-container .metric-card {
                max-width: 100%;
                padding: 1rem;
                margin: 0.5rem 0;
            }
            .varpro-container .stExpander {
                max-width: 100%;
            }
            .centered-image {
                max-width: 100px;
            }
            .centered-image img {
                max-width: 80px;
            }
        }
        @media (max-width: 480px) {
            .varpro-container .header {
                font-size: 2rem;
            }
            .varpro-container .subheader {
                font-size: 1rem;
            }
            .varpro-container .stButton > button {
                min-width: 180px;
                padding: 0.5rem 1.5rem;
                font-size: 0.9rem;
            }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px var(--accent); }
            50% { box-shadow: 0 0 20px var(--accent); }
            100% { box-shadow: 0 0 5px var(--accent); }
        }
        </style>
        <script>
        function applyVarproTheme(theme) {
            const container = document.querySelector('.varpro-container');
            if (container) {
                container.classList.remove('light-mode', 'dark-mode');
                container.classList.add(theme + '-mode');
                localStorage.setItem('varpro-theme', theme);
            }
        }
        function toggleVarproTheme() {
            const currentTheme = localStorage.getItem('varpro-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyVarproTheme(newTheme);
        }
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('varpro-theme');
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            applyVarproTheme(savedTheme || systemTheme);
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
                if (!localStorage.getItem('varpro-theme')) {
                    applyVarproTheme(e.matches ? 'dark' : 'light');
                }
            });
        });
        </script>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="varpro-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="header slide-in">VaR Calculator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader fade-in-up">Precision Risk Analysis for Nifty & Sensex</p>', unsafe_allow_html=True)
    st.markdown('<div class="centered-image fade-in">', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/000000/calculator.png", width=120)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-container slide-in">', unsafe_allow_html=True)
    st.markdown('<h3 class="text-xl font-semibold mb-6">Input Parameters</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Positions CSV", type=["csv"], help="Upload a CSV file with columns: UserID, Symbol, Exchange, Net Qty, Sell Avg Price.")
    col1, col2 = st.columns([1, 1])
    with col1:
        nfo_strike = st.number_input("Nifty Strike Price", min_value=0, value=24600, step=100, help="Current Nifty (NFO) strike price. Must be positive.")
    with col2:
        bfo_strike = st.number_input("Sensex Strike Price", min_value=0, value=80200, step=100, help="Current Sensex (BFO) strike price. Must be positive.")
    allocation = st.number_input("Allocation Amount", min_value=0, value=50000000, step=1000000, help="Total allocation for VaR calculations.")
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        required_columns = ["UserID", "Symbol", "Exchange", "Net Qty", "Sell Avg Price"]
        if not all(col in df.columns for col in required_columns):
            st.error(f"Uploaded CSV is missing required columns: {', '.join(required_columns)}.")
        else:
            unique_users = df["UserID"].unique().tolist()
            unique_users.insert(0, "Select a User")  # Add placeholder
            selected_user = st.selectbox("Select User to View VaR Results", unique_users, help="Select a user to calculate and display their VaR results.")

            st.markdown('<div class="fade-in">', unsafe_allow_html=True)
            if st.button("Calculate VaR", help="Process the selected user and calculate VaR."):
                if selected_user == "Select a User":
                    st.error("Please select a valid user to proceed.")
                elif allocation <= 0:
                    st.error("Allocation amount must be greater than zero.")
                elif nfo_strike <= 0 or bfo_strike <= 0:
                    st.error("Strike prices must be positive.")
                else:
                    with st.spinner(f"Analyzing positions and calculating VaR for {selected_user}..."):
                        user_df = df[df["UserID"] == selected_user]
                        nfo_results, bfo_results, df_nfo, df_bfo = calculate_var(user_df, nfo_strike, bfo_strike, allocation)
                        st.session_state['results'] = {
                            selected_user: {
                                'nfo_results': nfo_results,
                                'bfo_results': bfo_results,
                                'df_nfo': df_nfo,
                                'df_bfo': df_bfo
                            }
                        }
                        st.session_state['nfo_strike'] = nfo_strike
                        st.session_state['bfo_strike'] = bfo_strike
                        st.session_state['allocation'] = allocation
                        st.session_state['df'] = df
                        st.session_state['selected_user'] = selected_user
                        st.success(f"VaR calculation completed for {selected_user}! Results are ready below.")
            st.markdown('</div>', unsafe_allow_html=True)

            if 'results' in st.session_state and selected_user != "Select a User" and selected_user in st.session_state['results']:
                user_id = selected_user
                user_results = st.session_state['results'][user_id]
                percs = [10, -10, 15, -15]
                
                st.markdown(f'<h2 class="text-2xl font-semibold mt-12 mb-6 slide-in">Results for User: {user_id}</h2>', unsafe_allow_html=True)
                
                st.markdown('<h3 class="text-xl font-semibold mb-6 slide-in">Nifty (NFO) VaR Results</h3>', unsafe_allow_html=True)
                cols = st.columns(4)
                for idx, perc in enumerate(percs):
                    sum_var, perc_var = user_results['nfo_results'][perc]
                    metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
                    with cols[idx]:
                        st.markdown(f'<div class="metric-card fade-in {metric_class}">', unsafe_allow_html=True)
                        st.metric(
                            label=f"VaR at {perc}%",
                            value=f"₹{sum_var:,.2f}",
                            delta=f"{perc_var:.4%}",
                            delta_color="normal"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<h3 class="text-xl font-semibold mt-8 mb-6 slide-in">Sensex (BFO) VaR Results</h3>', unsafe_allow_html=True)
                cols = st.columns(4)
                for idx, perc in enumerate(percs):
                    sum_var, perc_var = user_results['bfo_results'][perc]
                    metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
                    with cols[idx]:
                        st.markdown(f'<div class="metric-card fade-in {metric_class}">', unsafe_allow_html=True)
                        st.metric(
                            label=f"VaR at {perc}%",
                            value=f"₹{sum_var:,.2f}",
                            delta=f"{perc_var:.4%}",
                            delta_color="normal"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                st.markdown(f'<h4 class="text-lg font-semibold mt-8 mb-6 slide-in">Download Processed Data for {user_id}</h4>', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label=f"Download NFO CSV for {user_id}",
                        data=user_results['df_nfo'].to_csv(index=False),
                        file_name=f"nfo_processed_{user_id}.csv",
                        mime="text/csv",
                        help="Download the processed NFO data with VaR calculations.",
                        key=f"download_nfo_{user_id}"
                    )
                with col2:
                    st.download_button(
                        label=f"Download BFO CSV for {user_id}",
                        data=user_results['df_bfo'].to_csv(index=False),
                        file_name=f"bfo_processed_{user_id}.csv",
                        mime="text/csv",
                        help="Download the processed BFO data with VaR calculations.",
                        key=f"download_bfo_{user_id}"
                    )

                with st.expander(f"Preview Processed Data for {user_id}", expanded=False):
                    st.subheader("NFO Data Preview")
                    st.dataframe(user_results['df_nfo'].head(10), use_container_width=True)
                    st.subheader("BFO Data Preview")
                    st.dataframe(user_results['df_bfo'].head(10), use_container_width=True)

                st.markdown('<div class="fade-in">', unsafe_allow_html=True)
                if st.button(f"Manage VaR for {user_id}", help="Add a hypothetical position to recalculate VaR.", key=f"manage_var_btn_{user_id}"):
                    st.session_state[f'manage_var_{user_id}'] = True
                    if f'manage_index_{user_id}' in st.session_state:
                        del st.session_state[f'manage_index_{user_id}']
                    if f'manage_trans_{user_id}' in st.session_state:
                        del st.session_state[f'manage_trans_{user_id}']
                    if f'manage_strike_{user_id}' in st.session_state:
                        del st.session_state[f'manage_strike_{user_id}']
                    if f'manage_price_{user_id}' in st.session_state:
                        del st.session_state[f'manage_price_{user_id}']
                    if f'manage_qty_{user_id}' in st.session_state:
                        del st.session_state[f'manage_qty_{user_id}']
                st.markdown('</div>', unsafe_allow_html=True)

                if f'manage_var_{user_id}' in st.session_state and st.session_state[f'manage_var_{user_id}']:
                    st.markdown(f'<h3 class="text-xl font-semibold mt-12 mb-6 slide-in">Manage VaR for {user_id} - Add Hypothetical Position</h3>', unsafe_allow_html=True)
                    st.markdown('<p class="subheader fade-in-up">Simulate the impact of a new position on VaR</p>', unsafe_allow_html=True)
                    
                    with st.form(key=f"manage_var_form_{user_id}"):
                        index_options = ["NFO", "BFO"]
                        index = st.selectbox("Index", index_options, index=0, help="Select the exchange: NFO (Nifty) or BFO (Sensex).")
                        trans_options = ["CE", "PE"]
                        trans = st.selectbox("Transaction", trans_options, index=0, help="Select CE (Call) or PE (Put).")
                        strike_step = 50 if index == "NFO" else 100
                        strike_input = st.number_input("Strike Price", min_value=0, value=0, step=strike_step, help=f"Strike price for the new position (increments by {strike_step}).")
                        price = st.number_input("Price", min_value=0.0, value=0.0, step=0.1, help="Average price for the position.")
                        qty = st.number_input("Quantity", value=0, step=1, help="Quantity (positive for long, negative for short). Must be a multiple of 75 (NFO) or 20 (BFO).")
                        submit_button = st.form_submit_button(label="Recalculate VaR with Added Position")

                        if submit_button:
                            if 'results' not in st.session_state or user_id not in st.session_state['results']:
                                st.error("Please calculate the original VaR first.")
                            elif strike_input <= 0 or price <= 0 or qty == 0:
                                st.error("Strike price, price, and quantity must be non-zero positive/negative values as appropriate.")
                            elif (index == "NFO" and qty % 75 != 0) or (index == "BFO" and qty % 20 != 0):
                                st.error(f"Quantity must be a multiple of {'75' if index == 'NFO' else '20'} for {index}.")
                            else:
                                st.session_state[f'manage_index_{user_id}'] = index
                                st.session_state[f'manage_trans_{user_id}'] = trans
                                st.session_state[f'manage_strike_{user_id}'] = strike_input
                                st.session_state[f'manage_price_{user_id}'] = price
                                st.session_state[f'manage_qty_{user_id}'] = qty
                                with st.spinner("Recalculating VaR with new position..."):
                                    user_df = st.session_state['df'][st.session_state['df']["UserID"] == user_id].copy()
                                    new_row_data = {col: '' if pd.api.types.is_string_dtype(user_df[col]) else 0 for col in user_df.columns}
                                    buy_price = price if qty > 0 else 0
                                    sell_price = price if qty < 0 else 0
                                    new_row_data.update({
                                        'UserID': user_id,
                                        'Exchange': index,
                                        'Symbol': f"DUMMY {trans} {strike_input}",
                                        'Net Qty': qty,
                                        'Buy Avg Price': buy_price,
                                        'Sell Avg Price': sell_price,
                                    })
                                    new_row_df = pd.DataFrame([new_row_data])
                                    recal_df = pd.concat([user_df, new_row_df], ignore_index=True)
                                    nfo_results_recal, bfo_results_recal, df_nfo_recal, df_bfo_recal = calculate_var(
                                        recal_df, st.session_state['nfo_strike'], st.session_state['bfo_strike'], st.session_state['allocation']
                                    )
                                    st.session_state[f'index_selected_{user_id}'] = index
                                    st.session_state[f'nfo_results_recal_{user_id}'] = nfo_results_recal
                                    st.session_state[f'bfo_results_recal_{user_id}'] = bfo_results_recal
                                    st.session_state[f'df_nfo_recal_{user_id}'] = df_nfo_recal
                                    st.session_state[f'df_bfo_recal_{user_id}'] = df_bfo_recal
                                    st.success("Recalculation completed! Check the updated VaR below.")

                    if f'nfo_results_recal_{user_id}' in st.session_state:
                        index_selected = st.session_state.get(f'index_selected_{user_id}', 'NFO')
                        st.markdown(f'<h3 class="text-xl font-semibold mt-12 mb-6 slide-in">Recalculated {"Nifty (NFO)" if index_selected == "NFO" else "Sensex (BFO)"} VaR Results for {user_id}</h3>', unsafe_allow_html=True)
                        cols = st.columns(4)
                        for idx, perc in enumerate(percs):
                            sum_var, perc_var = st.session_state[f'nfo_results_recal_{user_id}' if index_selected == "NFO" else f'bfo_results_recal_{user_id}'][perc]
                            metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
                            with cols[idx]:
                                st.markdown(f'<div class="metric-card fade-in {metric_class}">', unsafe_allow_html=True)
                                st.metric(
                                    label=f"VaR at {perc}%",
                                    value=f"₹{sum_var:,.2f}",
                                    delta=f"{perc_var:.4%}",
                                    delta_color="normal"
                                )
                                st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown(f'<h4 class="text-lg font-semibold mt-12 mb-6 slide-in">Download Recalculated Data for {user_id}</h4>', unsafe_allow_html=True)
                        st.download_button(
                            label=f"Download Recal {'NFO' if index_selected == 'NFO' else 'BFO'} CSV for {user_id}",
                            data=st.session_state[f'df_nfo_recal_{user_id}'].to_csv(index=False) if index_selected == "NFO" else st.session_state[f'df_bfo_recal_{user_id}'].to_csv(index=False),
                            file_name=f"{'nfo' if index_selected == 'NFO' else 'bfo'}_recal_processed_{user_id}.csv",
                            mime="text/csv",
                            help="Download the recalculated data.",
                            key=f"download_recal_{user_id}"
                        )

                        with st.expander(f"Preview Recalculated Data for {user_id}", expanded=False):
                            st.subheader(f"Recal {'NFO' if index_selected == 'NFO' else 'BFO'} Data Preview")
                            st.dataframe(st.session_state[f'df_nfo_recal_{user_id}' if index_selected == 'NFO' else f'df_bfo_recal_{user_id}'].tail(10), use_container_width=True)

                    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
                    if st.button(f"Reset Manage VaR for {user_id}", help="Reset and start a new hypothetical position calculation.", key=f"reset_manage_var_{user_id}"):
                        if f'index_selected_{user_id}' in st.session_state:
                            del st.session_state[f'index_selected_{user_id}']
                        if f'nfo_results_recal_{user_id}' in st.session_state:
                            del st.session_state[f'nfo_results_recal_{user_id}']
                        if f'bfo_results_recal_{user_id}' in st.session_state:
                            del st.session_state[f'bfo_results_recal_{user_id}']
                        if f'df_nfo_recal_{user_id}' in st.session_state:
                            del st.session_state[f'df_nfo_recal_{user_id}']
                        if f'df_bfo_recal_{user_id}' in st.session_state:
                            del st.session_state[f'df_bfo_recal_{user_id}']
                        st.success("Manage VaR reset successfully! You can now add a new position.")
                    st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Upload a CSV file to proceed. Ensure the file is correctly formatted with UserID column.")

    st.markdown("""
        <div class="mt-12 py-6 text-sm text-gray-500 dark:text-gray-400 fade-in">
            Powered by Streamlit | Optimized for Financial Risk Analysis | Developed by Sahil
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run()
