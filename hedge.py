import streamlit as st
import pandas as pd

def run():
    # Custom CSS for larger, responsive design
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --accent1: #6D28D9;
            --dash-purple: #6D28D9;
            --dash-pink: #DB2777;
            --admin-accent: linear-gradient(135deg, #6D28D9 0%, #DB2777 100%);
            --font-family: 'Inter', sans-serif;
            --border-radius: 16px;
            --transition: 0.4s ease;
            --shadow-light: 0 10px 24px rgba(0,0,0,0.1);
            --shadow-dark: 0 14px 36px rgba(0,0,0,0.2);
            --error-bg: #FEE2E2;
        }
        
        .main {
            padding: 4vw 3vw;
            width: 100%;
            max-width: 100vw;
            margin: 0 auto;
            box-sizing: border-box;
            overflow-x: hidden;
        }
        
        h1, h2, h3 {
            font-family: var(--font-family);
            font-weight: 800;
            text-align: center;
            margin: 2rem 0;
        }
        
        h1 {
            font-size: clamp(2.2rem, 7vw, 3rem);
            margin-bottom: 1.5rem;
        }
        
        h2 {
            font-size: clamp(1.6rem, 5vw, 2.2rem);
            margin-top: 2.5rem;
            margin-bottom: 1.2rem;
            letter-spacing: 1px;
        }
        
        .stFileUploader > div > div > div {
            border-radius: var(--border-radius);
            border: 2px dashed #ccc;
            padding: 2rem;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
        }
        
        .stButton > button {
            background-image: var(--admin-accent);
            border: none;
            border-radius: var(--border-radius);
            color: white;
            padding: 1.2rem 3rem;
            font-weight: 600;
            font-family: var(--font-family);
            font-size: clamp(1.1rem, 3.5vw, 1.4rem);
            transition: all var(--transition);
            width: 100%;
            box-sizing: border-box;
            margin: 2rem 0;
        }
        
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 28px rgba(109,40,217,0.4);
        }
        
        .input-section {
            background: #f8f9fa;
            padding: 3rem;
            border-radius: var(--border-radius);
            margin-bottom: 3rem;
            box-shadow: var(--shadow-light);
            width: 100%;
            box-sizing: border-box;
        }
        
        .stDataFrame {
            width: 100%;
            box-sizing: border-box;
            margin: 0 auto;
            min-height: 50vh;
        }
        
        .stSelectbox > div > div > select {
            border-radius: var(--border-radius);
            border: 1px solid #D1D5DB;
            padding: 1.2rem 1.8rem;
            font-family: var(--font-family);
            font-size: clamp(1.1rem, 3.5vw, 1.4rem);
            width: 100%;
            box-sizing: border-box;
            margin: 1.2rem 0;
        }
        
        .stInfo {
            background-color: #dbeafe;
            border-left: 5px solid var(--accent1);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 2rem;
            font-size: clamp(1rem, 3vw, 1.2rem);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(135deg, var(--dash-purple) 0%, var(--dash-pink) 100%);
            color: white;
            padding: 2rem;
        }
        
        .css-1d391kg h1, .css-1d391kg h2 {
            color: white !important;
            font-family: var(--font-family);
        }
        
        .css-1d391kg .stButton > button {
            background: white;
            color: var(--dash-purple);
            font-weight: 600;
            border-radius: var(--border-radius);
            padding: 1rem;
            margin: 0.6rem 0;
            width: 100%;
            height: 56px;
            border: none;
            transition: transform var(--transition), box-shadow var(--transition);
            font-size: 1.1rem;
        }
        
        .css-1d391kg .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.3);
            background: #f0f0f0;
        }
        
        /* Responsive adjustments */
        @media (max-width: 1024px) {
            .main {
                padding: 3vw 2vw;
            }
            h1 {
                font-size: clamp(2rem, 6vw, 2.5rem);
            }
            h2 {
                font-size: clamp(1.4rem, 4.5vw, 2rem);
            }
            .input-section {
                padding: 2rem;
                margin-bottom: 2rem;
            }
            .stDataFrame {
                min-height: 45vh;
            }
            .css-1d391kg {
                padding: 1.5rem;
            }
        }
        
        @media (max-width: 600px) {
            .main {
                padding: 2rem;
            }
            h1 {
                font-size: clamp(1.8rem, 5vw, 2.2rem);
            }
            h2 {
                font-size: clamp(1.2rem, 4vw, 1.8rem);
            }
            .stButton > button {
                padding: 1rem 2rem;
            }
            .input-section {
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            .stFileUploader > div > div > div {
                padding: 1.2rem;
            }
            .stSelectbox > div > div > select {
                padding: 1rem;
                font-size: clamp(1rem, 3vw, 1.2rem);
            }
            .stDataFrame {
                min-height: 40vh;
            }
            .css-1d391kg {
                padding: 1rem;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .main {
                background: transparent;
                color: #F3F4F6;
            }
            h1, h2, h3 {
                background: var(--admin-accent);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .input-section {
                background: rgba(255,255,255,0.1);
                box-shadow: var(--shadow-dark);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .stFileUploader > div > div > div {
                background: rgba(255,255,255,0.1);
                border: 2px dashed rgba(255,255,255,0.2);
            }
            .stButton > button {
                background-image: var(--admin-accent);
            }
            .stDataFrame {
                background: transparent;
            }
            .stInfo {
                background: rgba(255,255,255,0.1);
                border-left-color: var(--accent1);
            }
            .stSelectbox > div > div > select {
                background: rgba(255,255,255,0.08);
                color: #F3F4F6;
                border: 1px solid rgba(255,255,255,0.15);
            }
        }
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("Hedge Manager")
        st.markdown('<h2>🛡️ Options Analyzer</h2>', unsafe_allow_html=True)
        theme = st.checkbox("Enable Dark Mode", value=False, key="theme_toggle")
        if theme:
            st.markdown("""
                <style>
                    .main {
                        background: transparent;
                        color: #F3F4F6;
                    }
                    h1, h2, h3 {
                        background: var(--admin-accent);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    }
                    .input-section {
                        background: rgba(255,255,255,0.1);
                        box-shadow: var(--shadow-dark);
                        border: 1px solid rgba(255,255,255,0.2);
                    }
                    .stFileUploader > div > div > div {
                        background: rgba(255,255,255,0.1);
                        border: 2px dashed rgba(255,255,255,0.2);
                    }
                    .stButton > button {
                        background-image: var(--admin-accent);
                    }
                    .stDataFrame {
                        background: transparent;
                    }
                    .stInfo {
                        background: rgba(255,255,255,0.1);
                        border-left-color: var(--accent1);
                    }
                    .stSelectbox > div > div > select {
                        background: rgba(255,255,255,0.08);
                        color: #F3F4F6;
                        border: 1px solid rgba(255,255,255,0.15);
                    }
                </style>
            """, unsafe_allow_html=True)
        
        # Back to Dashboard button
        if st.button("🔙 Back to Dashboard", key="back_hedge_manager"):
            st.session_state.current_page = 'dashboard'
            st.rerun()

    # Main content
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown("""
        <h1>
            <span style='display: inline-flex; align-items: center;'>
                🛡️ Hedge Manager: Options Position Analyzer
                <span style='font-size: 0.5em; margin-left: 10px; color: #6D28D9;'>v1.0</span>
            </span>
        </h1>
    """, unsafe_allow_html=True)
    st.info("👇 Upload a POS CSV file to analyze options positions. Ensure columns: UserID, Symbol, Product, Buy Qty, Sell Qty.")

    # Input Section
    st.markdown("### ⚙️ Upload Data", unsafe_allow_html=True)
    with st.container():
        # st.markdown('<div class="input-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop your POS CSV file here or click to browse",
            type=["csv"],
            key="pos_file"
        )
        if uploaded_file:
            st.success("✅ File uploaded successfully")
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        # Load CSV
        with st.spinner("🔄 Processing your data..."):
            df = pd.read_csv(uploaded_file)
            df = df[df["Product"] == "MIS"]

            # Identify option type
            df['OptionType'] = df['Symbol'].apply(
                lambda x: 'Call' if 'CE' in str(x) else ('Put' if 'PE' in str(x) else 'Other')
            )

            # Assign lot size based on symbol
            def get_lot_size(symbol):
                symbol = str(symbol).upper()
                if "NIFTY" in symbol:
                    return 75
                elif "SENSEX" in symbol:
                    return 20
                else:
                    return 1  # default if neither NIFTY nor SENSEX

            df['LotSize'] = df['Symbol'].apply(get_lot_size)

            # Group and aggregate
            summary = (
                df.groupby(['UserID', 'OptionType'], as_index=False)
                  .agg({'Buy Qty': 'sum', 'Sell Qty': 'sum', 'LotSize': 'max'})
            )

            # Calculate difference and lots
            summary['difference'] = summary['Buy Qty'] - summary['Sell Qty']
            summary['lots'] = summary['difference'] / summary['LotSize']

            # Tabs for different views
            tab1, tab2 = st.tabs(["📋 Raw Data", "📊 Summary"])

            with tab1:
                st.subheader("Raw Data")
                st.dataframe(df, use_container_width=True)

            with tab2:
                st.subheader("Summary (Aggregated by User & Option Type)")
                st.dataframe(summary, use_container_width=True)

                # Download button
                csv = summary.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Summary as CSV",
                    data=csv,
                    file_name="summary.csv",
                    mime="text/csv",
                    key="download_summary",
                    use_container_width=True
                )

            # Sidebar filter
            st.sidebar.subheader("Filter Data")
            users = df['UserID'].unique().tolist()
            selected_user = st.sidebar.selectbox("Select UserID", ["All"] + users, key="user_filter")
            if selected_user != "All":
                filtered_summary = summary[summary['UserID'] == selected_user]
                st.subheader(f"Filtered Summary for User: {selected_user}")
                st.dataframe(filtered_summary, use_container_width=True)

                # Download filtered summary
                filtered_csv = filtered_summary.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"Download Filtered Summary ({selected_user})",
                    data=filtered_csv,
                    file_name=f"summary_{selected_user}.csv",
                    mime="text/csv",
                    key=f"download_filtered_{selected_user}",
                    use_container_width=True
                )

    else:
        st.info("👆 Upload a POS CSV file to start analyzing your options positions. Ensure your CSV includes UserID, Symbol, Product, Buy Qty, and Sell Qty columns.")

    # Footer
    st.markdown("""
        ---
        <div style='text-align: center; color: #888; font-size: clamp(1rem, 3vw, 1.2rem);'>
            Powered by Streamlit | Designed for 2025 UX Excellence | Developed by Sahil
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)