import streamlit as st
import pandas as pd
import numpy as np
import base64
import time

def calculate_var(df, nfo_strike, bfo_strike, allocation):
    splits = df["Symbol"].str.split()
    df["Strike"] = splits.str[-1]
    df["Transaction"] = splits.str[-2]
    df_nfo = df[df["Exchange"] == "NFO"].copy()
    df_bfo = df[df["Exchange"] == "BFO"].copy()
    nfo_results = {}
    if not df_nfo.empty:
        strike_nfo = df_nfo["Strike"].astype(float)
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
        strike_bfo = df_bfo["Strike"].astype(float)
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
        <style>
        :root {
            --bg-light: #F9FAFB;
            --bg-dark: #111827;
            --text-light: #1F2937;
            --text-dark: #F9FAFB;
            --card-bg-light: #FFFFFF;
            --card-bg-dark: #1F2937;
            --accent: #3B82F6;
            --accent-hover: #2563EB;
            --border-light: #E5E7EB;
            --border-dark: #374151;
            --shadow-light: rgba(0, 0, 0, 0.05);
            --shadow-dark: rgba(0, 0, 0, 0.3);
            --positive-color: #10B981;
            --negative-color: #EF4444;
        }
        .varpro-container {
            font-family: 'Inter', sans-serif;
            transition: background-color 0.3s ease, color 0.3s ease;
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 0.75rem;
            box-shadow: 0 4px 8px var(--shadow-light);
        }
        .light-mode .varpro-container {
            background: var(--bg-light);
            color: var(--text-light);
        }
        .dark-mode .varpro-container {
            background: var(--bg-dark);
            color: var(--text-dark);
            box-shadow: 0 4px 8px var(--shadow-dark);
        }
        .varpro-container .stApp {
            background: inherit;
            color: inherit;
        }
        .varpro-container .stButton > button {
            background: var(--accent);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            max-width: 400px;
            margin: 0.5rem auto;
        }
        .varpro-container .stButton > button:hover {
            background: var(--accent-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 6px var(--shadow-light);
        }
        .dark-mode .varpro-container .stButton > button:hover {
            box-shadow: 0 4px 6px var(--shadow-dark);
        }
        .varpro-container .metric-card {
            border-radius: 0.75rem;
            padding: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            background: var(--card-bg-light);
        }
        .dark-mode .varpro-container .metric-card {
            background: var(--card-bg-dark);
        }
        .varpro-container .header {
            font-size: 2.25rem;
            font-weight: 800;
            background: linear-gradient(to right, var(--accent), #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }
        .varpro-container .subheader {
            font-size: 1.125rem;
            color: #4B5563;
            text-align: center;
        }
        .dark-mode .varpro-container .subheader {
            color: #9CA3AF;
        }
        .varpro-container .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        .varpro-container .download-button {
            background: var(--accent);
            color: white !important;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            text-decoration: none;
            transition: background 0.3s ease;
        }
        .varpro-container .download-button:hover {
            background: var(--accent-hover);
        }
        .varpro-container .stFileUploader > div > div > input,
        .varpro-container .stNumberInput > div > div > input {
            border: 1px solid var(--border-light);
            border-radius: 0.5rem;
            padding: 0.75rem;
            width: 100%;
            max-width: 400px;
            margin: 0.5rem auto;
            display: block;
        }
        .dark-mode .varpro-container .stFileUploader > div > div > input,
        .dark-mode .varpro-container .stNumberInput > div > div > input {
            border: 1px solid var(--border-dark);
            background: var(--card-bg-dark);
            color: var(--text-dark);
        }
        .varpro-container .stCheckbox {
            text-align: center;
        }
        .centered-image {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 1.5rem auto;
            width: 100%;
            max-width: 120px;
        }
        .centered-image img {
            width: 100%;
            max-width: 96px;
            height: auto;
            transition: transform 0.3s ease;
        }
        .centered-image img:hover {
            transform: scale(1.1);
        }
        /* Metric value color styling */
        .varpro-container [data-testid="stMetricValue"] {
            font-weight: 600;
        }
        .metric-positive [data-testid="stMetricValue"] {
            color: var(--positive-color) !important;
        }
        .metric-negative [data-testid="stMetricValue"] {
            color: var(--negative-color) !important;
        }
        @media (max-width: 640px) {
            .varpro-container .header {
                font-size: 1.875rem;
            }
            .varpro-container .st-columns > div {
                margin-bottom: 1rem;
            }
            .centered-image {
                max-width: 80px;
            }
            .centered-image img {
                max-width: 80px;
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
    st.markdown('<h1 class="header fade-in">VaR Calculator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader fade-in">Interactive dashboard for Nifty and Sensex VaR analysis. View metrics and download detailed data.</p>', unsafe_allow_html=True)
    st.markdown('<div class="centered-image fade-in">', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/000000/calculator.png", width=96, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="subheader fade-in">Upload positions CSV and set parameters to compute Value at Risk (VaR).</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload POS (2).csv", type=["csv"], help="Upload your positions file in CSV format. Ensure it has columns like Symbol, Exchange, Net Qty, Sell Avg Price.")
    nfo_strike = st.number_input("Nifty Strike Price", min_value=0, value=24600, step=100, help="Current strike price for Nifty (NFO). Must be positive.")
    bfo_strike = st.number_input("Sensex Strike Price", min_value=0, value=80200, step=100, help="Current strike price for Sensex (BFO). Must be positive.")
    allocation = st.number_input("Allocation Amount", min_value=0, value=50000000, step=1000000, help="Total allocation amount. Used for percentage calculations.")

    if st.button("Calculate VaR", help="Click to process the uploaded file and calculate VaR."):
        if uploaded_file is None:
            st.error("Please upload a CSV file to proceed.")
        elif allocation <= 0:
            st.error("Allocation amount must be greater than zero.")
        elif nfo_strike <= 0 or bfo_strike <= 0:
            st.error("Strike prices must be positive.")
        else:
            with st.spinner("Analyzing positions and calculating VaR..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.005)
                    progress_bar.progress((i + 1) / 100)
                df = pd.read_csv(uploaded_file)
                if "Symbol" not in df.columns or "Exchange" not in df.columns or "Net Qty" not in df.columns or "Sell Avg Price" not in df.columns:
                    st.error("Uploaded CSV is missing required columns: Symbol, Exchange, Net Qty, Sell Avg Price.")
                else:
                    nfo_results, bfo_results, df_nfo, df_bfo = calculate_var(df, nfo_strike, bfo_strike, allocation)
                    st.session_state['nfo_results'] = nfo_results
                    st.session_state['bfo_results'] = bfo_results
                    st.session_state['df_nfo'] = df_nfo
                    st.session_state['df_bfo'] = df_bfo
                    st.success("VaR calculation completed successfully! Results are ready below.")

    if 'nfo_results' in st.session_state:
        st.markdown('<h2 class="text-lg font-semibold mt-6 mb-3 fade-in">Nifty (NFO) VaR Results</h2>', unsafe_allow_html=True)
        cols = st.columns(4)
        percs = [10, -10, 15, -15]
        for idx, perc in enumerate(percs):
            sum_var, perc_var = st.session_state['nfo_results'][perc]
            metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
            with cols[idx]:
                st.markdown(f'<div class="{metric_class}">', unsafe_allow_html=True)
                st.metric(
                    label=f"VaR at {perc}%",
                    value=f"₹{sum_var:,.2f}",
                    delta=f"{perc_var:.4%}",
                    delta_color="inverse" if perc < 0 else "normal"
                )
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<h2 class="text-lg font-semibold mt-6 mb-3 fade-in">Sensex (BFO) VaR Results</h2>', unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, perc in enumerate(percs):
            sum_var, perc_var = st.session_state['bfo_results'][perc]
            metric_class = "metric-positive" if sum_var >= 0 else "metric-negative"
            with cols[idx]:
                st.markdown(f'<div class="{metric_class}">', unsafe_allow_html=True)
                st.metric(
                    label=f"VaR at {perc}%",
                    value=f"₹{sum_var:,.2f}",
                    delta=f"{perc_var:.4%}",
                    delta_color="inverse" if perc < 0 else "normal"
                )
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<h3 class="text-md font-medium mt-6 mb-3 fade-in">Download Detailed Processed Data</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download NFO Processed CSV",
                data=st.session_state['df_nfo'].to_csv(index=False),
                file_name="nfo_processed.csv",
                mime="text/csv",
                help="Download the processed NFO data with VaR calculations.",
                key="download_nfo"
            )
        with col2:
            st.download_button(
                label="Download BFO Processed CSV",
                data=st.session_state['df_bfo'].to_csv(index=False),
                file_name="bfo_processed.csv",
                mime="text/csv",
                help="Download the processed BFO data with VaR calculations.",
                key="download_bfo"
            )

        with st.expander("Preview Processed Data", expanded=False):
            st.subheader("NFO Data Preview")
            st.dataframe(st.session_state['df_nfo'].head(10), use_container_width=True)
            st.subheader("BFO Data Preview")
            st.dataframe(st.session_state['df_bfo'].head(10), use_container_width=True)
    else:
        st.info("Upload a CSV file above and click 'Calculate VaR' to generate results. Ensure the file is correctly formatted for accurate calculations.")

    st.markdown("""
        <div class="mt-8 py-3 text-center text-sm text-gray-500 dark:text-gray-400 fade-in">
            Powered by Streamlit | Optimized for Financial Risk Analysis | Developed by Sahil
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run()
