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
    st.set_page_config(page_title="VaR Calculator Pro", layout="wide")
    st.markdown("""
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
            --blur: blur(8px);
        }
        .varpro-container {
            font-family: 'Inter', sans-serif;
            max-width: 1400px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 1rem;
            background: var(--bg-light);
            box-shadow: 0 8px 16px var(--shadow-light);
            transition: all 0.3s ease;
        }
        .dark-mode .varpro-container {
            background: var(--bg-dark);
            color: var(--text-dark);
            box-shadow: 0 8px 16px var(--shadow-dark);
        }
        .varpro-container * {
            text-align: center;
        }
        .varpro-container .stApp {
            background: inherit;
            color: inherit;
        }
        .header {
            font-size: 2.5rem;
            font-weight: 800;
            background: var(--header-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subheader {
            font-size: 1.1rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .dark-mode .subheader {
            color: #D1D5DB;
        }
        .input-container, .results-container, .manage-var-container {
            background: var(--card-bg-light);
            border: 1px solid var(--border-accent);
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 8px var(--shadow-light);
        }
        .dark-mode .input-container, .dark-mode .results-container, .dark-mode .manage-var-container {
            background: var(--card-bg-dark);
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .stButton > button {
            background: var(--header-gradient);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 0.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            min-width: 200px;
            margin: 0.5rem;
            box-shadow: 0 4px 8px var(--shadow-light);
        }
        .stButton > button:hover {
            background: linear-gradient(90deg, #2563EB, #9333EA, #DB2777);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px var(--shadow-light);
        }
        .dark-mode .stButton > button:hover {
            box-shadow: 0 6px 12px var(--shadow-dark);
        }
        .metric-card {
            border-radius: 0.75rem;
            padding: 1rem;
            background: var(--card-bg-light);
            border: 1px solid var(--border-accent);
            margin: 0.5rem;
            box-shadow: 0 4px 8px var(--shadow-light);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            border-color: var(--accent);
            box-shadow: 0 6px 12px var(--shadow-light);
        }
        .dark-mode .metric-card {
            background: var(--card-bg-dark);
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .metric-positive [data-testid="stMetricValue"], .metric-positive [data-testid="stMetricDelta"] {
            color: var(--positive-color) !important;
        }
        .metric-negative [data-testid="stMetricValue"], .metric-negative [data-testid="stMetricDelta"] {
            color: var(--negative-color) !important;
        }
        .stFileUploader > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > select {
            border: 1px solid var(--border-accent);
            border-radius: 0.5rem;
            padding: 0.5rem;
            width: 100%;
            max-width: 500px;
            margin: 0.5rem auto;
            background: var(--card-bg-light);
            box-shadow: 0 2px 4px var(--shadow-light);
            transition: all 0.3s ease;
        }
        .dark-mode .stFileUploader > div > div > input, .dark-mode .stNumberInput > div > div > input, 
        .dark-mode .stSelectbox > div > div > select {
            background: var(--card-bg-dark);
            color: var(--text-dark);
            box-shadow: 0 2px 4px var(--shadow-dark);
        }
        .stForm {
            border: 1px solid var(--border-accent);
            border-radius: 1rem;
            padding: 1.5rem;
            background: var(--card-bg-light);
            box-shadow: 0 4px 8px var(--shadow-light);
        }
        .dark-mode .stForm {
            background: var(--card-bg-dark);
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .stExpander {
            border: 1px solid var(--border-accent);
            border-radius: 0.75rem;
            background: var(--card-bg-light);
            margin: 1rem 0;
            box-shadow: 0 4px 8px var(--shadow-light);
        }
        .dark-mode .stExpander {
            background: var(--card-bg-dark);
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .download-button {
            background: var(--header-gradient);
            color: white !important;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-weight: 500;
            margin: 0.5rem;
            box-shadow: 0 4px 8px var(--shadow-light);
            display: inline-block;
        }
        .download-button:hover {
            background: linear-gradient(90deg, #2563EB, #9333EA, #DB2777);
            transform: translateY(-2px);
        }
        .centered-image img {
            width: 100px;
            height: auto;
            border-radius: 0.5rem;
            box-shadow: 0 4px 8px var(--shadow-light);
            transition: transform 0.3s ease;
        }
        .centered-image img:hover {
            transform: scale(1.1);
        }
        .dark-mode .centered-image img {
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .stColumns {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
        }
        @media (max-width: 768px) {
            .varpro-container {
                padding: 1rem;
                margin: 1rem;
            }
            .header {
                font-size: 2rem;
            }
            .subheader {
                font-size: 1rem;
            }
            .stButton > button, .download-button {
                min-width: 160px;
                padding: 0.5rem 1.5rem;
            }
            .metric-card {
                max-width: 100%;
                padding: 0.75rem;
            }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
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
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('varpro-theme') || 
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            applyVarproTheme(savedTheme);
        });
        </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="varpro-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="header">VaR Calculator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Precision Risk Analysis for Nifty & Sensex Options</p>', unsafe_allow_html=True)
    st.markdown('<div class="centered-image"><img src="https://img.icons8.com/fluency/96/000000/calculator.png"></div>', unsafe_allow_html=True)

    # Input Section
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="text-lg font-semibold mb-4">Input Parameters</h3>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Positions CSV", type=["csv"], help="Upload a CSV with columns: UserID, Symbol, Exchange, Net Qty, Sell Avg Price")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            nfo_strike = st.number_input("Nifty Strike Price", min_value=0, value=24600, step=100, help="Current Nifty (NFO) strike price")
        with col2:
            bfo_strike = st.number_input("Sensex Strike Price", min_value=0, value=80200, step=100, help="Current Sensex (BFO) strike price")
        with col3:
            allocation = st.number_input("Allocation Amount", min_value=0, value=50000000, step=1000000, help="Total allocation for VaR calculations")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            required_columns = ["UserID", "Symbol", "Exchange", "Net Qty", "Sell Avg Price"]
            if not all(col in df.columns for col in required_columns):
                st.error(f"Missing required columns: {', '.join(required_columns)}")
            else:
                unique_users = ["Select a User"] + df["UserID"].unique().tolist()
                selected_user = st.selectbox("Select User", unique_users, help="Select a user to calculate VaR")
                if st.button("Calculate VaR", key="calc_var"):
                    if selected_user == "Select a User":
                        st.error("Please select a valid user")
                    elif allocation <= 0:
                        st.error("Allocation amount must be greater than zero")
                    elif nfo_strike <= 0 or bfo_strike <= 0:
                        st.error("Strike prices must be positive")
                    else:
                        with st.spinner(f"Calculating VaR for {selected_user}..."):
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
                            st.success(f"VaR calculated for {selected_user}!")
        st.markdown('</div>', unsafe_allow_html=True)

    # Results Section
    if 'results' in st.session_state and st.session_state.get('selected_user') != "Select a User":
        user_id = st.session_state['selected_user']
        user_results = st.session_state['results'][user_id]
        percs = [10, -10, 15, -15]

        with st.container():
            st.markdown('<div class="results-container">', unsafe_allow_html=True)
            st.markdown(f'<h2 class="text-xl font-semibold mb-4">Results for User: {user_id}</h2>', unsafe_allow_html=True)
            
            st.markdown('<h3 class="text-lg font-semibold mb-3">Nifty (NFO) VaR</h3>', unsafe_allow_html=True)
            cols = st.columns(4)
            for idx, perc in enumerate(percs):
                sum_var, perc_var = user_results['nfo_results'][perc]
                metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
                with cols[idx]:
                    st.markdown(f'<div class="metric-card {metric_class}">', unsafe_allow_html=True)
                    st.metric(label=f"VaR at {perc}%", value=f"₹{sum_var:,.2f}", delta=f"{perc_var:.4%}")
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<h3 class="text-lg font-semibold mt-6 mb-3">Sensex (BFO) VaR</h3>', unsafe_allow_html=True)
            cols = st.columns(4)
            for idx, perc in enumerate(percs):
                sum_var, perc_var = user_results['bfo_results'][perc]
                metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
                with cols[idx]:
                    st.markdown(f'<div class="metric-card {metric_class}">', unsafe_allow_html=True)
                    st.metric(label=f"VaR at {perc}%", value=f"₹{sum_var:,.2f}", delta=f"{perc_var:.4%}")
                    st.markdown('</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label=f"Download NFO CSV",
                    data=user_results['df_nfo'].to_csv(index=False),
                    file_name=f"nfo_processed_{user_id}.csv",
                    mime="text/csv",
                    key=f"download_nfo_{user_id}",
                    help="Download processed NFO data"
                )
            with col2:
                st.download_button(
                    label=f"Download BFO CSV",
                    data=user_results['df_bfo'].to_csv(index=False),
                    file_name=f"bfo_processed_{user_id}.csv",
                    mime="text/csv",
                    key=f"download_bfo_{user_id}",
                    help="Download processed BFO data"
                )

            with st.expander("Preview Processed Data", expanded=False):
                st.subheader("NFO Data Preview")
                st.dataframe(user_results['df_nfo'].head(10), use_container_width=True)
                st.subheader("BFO Data Preview")
                st.dataframe(user_results['df_bfo'].head(10), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Manage VaR Section
        with st.container():
            st.markdown('<div class="manage-var-container">', unsafe_allow_html=True)
            if st.button(f"Add Hypothetical Position", key=f"manage_var_btn_{user_id}"):
                st.session_state[f'manage_var_{user_id}'] = True
                for key in [f'manage_index_{user_id}', f'manage_trans_{user_id}', f'manage_strike_{user_id}', 
                           f'manage_price_{user_id}', f'manage_qty_{user_id}']:
                    if key in st.session_state:
                        del st.session_state[key]
            
            if st.session_state.get(f'manage_var_{user_id}'):
                st.markdown('<h3 class="text-lg font-semibold mb-3">Add Hypothetical Position</h3>', unsafe_allow_html=True)
                with st.form(key=f"manage_var_form_{user_id}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        index = st.selectbox("Index", ["NFO", "BFO"], help="Select NFO (Nifty) or BFO (Sensex)")
                    with col2:
                        trans = st.selectbox("Transaction", ["CE", "PE"], help="Select CE (Call) or PE (Put)")
                    with col3:
                        strike_step = 50 if index == "NFO" else 100
                        strike_input = st.number_input("Strike Price", min_value=0, value=0, step=strike_step, 
                                                    help=f"Strike price (increments by {strike_step})")
                    col4, col5 = st.columns(2)
                    with col4:
                        price = st.number_input("Price", min_value=0.0, value=0.0, step=0.1, help="Average price")
                    with col5:
                        qty = st.number_input("Quantity", value=0, step=1, help="Quantity (positive for long, negative for short)")
                    if st.form_submit_button("Recalculate VaR"):
                        if strike_input <= 0 or price <= 0 or qty == 0:
                            st.error("Strike price, price, and quantity must be non-zero")
                        elif (index == "NFO" and qty % 75 != 0) or (index == "BFO" and qty % 20 != 0):
                            st.error(f"Quantity must be a multiple of {'75' if index == 'NFO' else '20'} for {index}")
                        else:
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
                            st.success("VaR recalculated with new position!")

                if f'nfo_results_recal_{user_id}' in st.session_state:
                    index_selected = st.session_state[f'index_selected_{user_id}']
                    st.markdown(f'<h3 class="text-lg font-semibold mb-3">Recalculated {"Nifty (NFO)" if index_selected == "NFO" else "Sensex (BFO)"} VaR</h3>', unsafe_allow_html=True)
                    cols = st.columns(4)
                    for idx, perc in enumerate(percs):
                        sum_var, perc_var = st.session_state[f'nfo_results_recal_{user_id}' if index_selected == "NFO" else f'bfo_results_recal_{user_id}'][perc]
                        metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
                        with cols[idx]:
                            st.markdown(f'<div class="metric-card {metric_class}">', unsafe_allow_html=True)
                            st.metric(label=f"VaR at {perc}%", value=f"₹{sum_var:,.2f}", delta=f"{perc_var:.4%}")
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.download_button(
                        label=f"Download Recalculated {'NFO' if index_selected == 'NFO' else 'BFO'} CSV",
                        data=st.session_state[f'df_nfo_recal_{user_id}' if index_selected == "NFO" else f'df_bfo_recal_{user_id}'].to_csv(index=False),
                        file_name=f"{'nfo' if index_selected == 'NFO' else 'bfo'}_recal_processed_{user_id}.csv",
                        mime="text/csv",
                        key=f"download_recal_{user_id}"
                    )
                    
                    with st.expander("Preview Recalculated Data", expanded=False):
                        st.subheader(f"{'NFO' if index_selected == 'NFO' else 'BFO'} Data Preview")
                        st.dataframe(st.session_state[f'df_nfo_recal_{user_id}' if index_selected == "NFO" else f'df_bfo_recal_{user_id}'].tail(10), use_container_width=True)
                
                if st.button("Reset Hypothetical Position", key=f"reset_manage_var_{user_id}"):
                    for key in [f'index_selected_{user_id}', f'nfo_results_recal_{user_id}', f'bfo_results_recal_{user_id}', 
                               f'df_nfo_recal_{user_id}', f'df_bfo_recal_{user_id}']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.success("Hypothetical position reset!")
            st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is None:
        st.info("Please upload a CSV file to begin")
    
    st.markdown('<div class="text-sm text-gray-500 dark:text-gray-400 mt-6">Powered by Streamlit | Developed by Sahil</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run()
