import streamlit as st
import pandas as pd
import numpy as np

def run():
    # ──────────────────────────────────────────────────────────────
    # 1. CSS (unchanged – copy-paste from your original)
    # ──────────────────────────────────────────────────────────────
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        :root{--accent1:#6D28D9;--dash-purple:#6D28D9;--dash-pink:#DB2777;
              --admin-accent:linear-gradient(135deg,#6D28D9 0%,#DB2777 100%);
              --font-family:'Inter',sans-serif;--border-radius:12px;
              --transition:0.3s ease;--shadow-light:0 8px 20px rgba(0,0,0,0.1);
              --shadow-dark:0 12px 30px rgba(0,0,0,0.15);
              --success-bg:#D1FAE5;--success-border:#10B981}
        .main{padding:2vw;width:100%;max-width:100vw;margin:0 auto;
              box-sizing:border-box;overflow-x:hidden;background:#F9FAFB}
        h1{font-family:var(--font-family);font-weight:800;text-align:center;
           font-size:clamp(2rem,6vw,2.8rem);margin:1.5rem 0;
           background:var(--admin-accent);-webkit-background-clip:text;
           -webkit-text-fill-color:transparent}
        .stFileUploader > div > div > div{border-radius:var(--border-radius);
           border:2px dashed #ccc;padding:1.5rem;width:100%;box-sizing:border-box;
           text-align:center;background:#FFF;transition:all var(--transition)}
        .stFileUploader > div > div > div:hover{border-color:var(--dash-purple);
           background:#F8F9FA}
        .stButton > button{background-image:var(--admin-accent);border:none;
           border-radius:var(--border-radius);color:white;padding:1rem 2rem;
           font-weight:600;font-family:var(--font-family);
           font-size:clamp(1rem,3vw,1.2rem);transition:all var(--transition);
           width:100%;box-sizing:border-box;margin:1.5rem 0}
        .stButton > button:hover{transform:translateY(-2px);
           box-shadow:0 6px 20px rgba(109,40,217,.3)}
        .stInfo{background-color:#dbeafe;border-left:5px solid var(--accent1);
           padding:1rem;border-radius:var(--border-radius);margin-bottom:1.5rem;
           font-size:clamp(.9rem,2.5vw,1.1rem);font-family:var(--font-family)}
        .dashboard-card{background:#FFF;padding:1.5rem;border-radius:var(--border-radius);
           box-shadow:var(--shadow-light);margin-bottom:1rem;display:flex;
           justify-content:space-between;align-items:center;transition:all var(--transition)}
        .dashboard-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-dark)}
        .dashboard-card .user-info{font-family:var(--font-family);
           font-size:clamp(1rem,3vw,1.2rem);font-weight:600}
        .dashboard-card .action-buy{background:var(--success-bg);color:var(--success-border);
           padding:.5rem 1rem;border-radius:8px;font-weight:500}
        .dashboard-card .action-sell{background:#FEE2E2;color:#EF4444;
           padding:.5rem 1rem;border-radius:8px;font-weight:500}
        .dashboard-card .lots{font-family:var(--font-family);
           font-size:clamp(1rem,3vw,1.2rem);font-weight:600;color:var(--dash-purple)}
        @media(max-width:1024px){.main{padding:1.5vw}h1{font-size:clamp(1.8rem,5vw,2.5rem)}
           .dashboard-card{padding:1.2rem}}
        @media(max-width:600px){.main{padding:1rem}h1{font-size:clamp(1.6rem,4vw,2rem)}
           .dashboard-card{flex-direction:column;gap:.5rem;padding:1rem}
           .dashboard-card .user-info,.dashboard-card .lots{font-size:clamp(.9rem,2.5vw,1.1rem)}}
        @media(prefers-color-scheme:dark){.main{background:#1F2937;color:#F3F4F6}
           .stFileUploader > div > div > div{background:rgba(255,255,255,.1);
           border:2px dashed rgba(255,255,255,.2)}
           .stFileUploader > div > div > div:hover{border-color:var(--dash-pink)}
           .stInfo{background:rgba(255,255,255,.1);border-left-color:var(--accent1)}
           .dashboard-card{background:rgba(255,255,255,.05);box-shadow:var(--shadow-dark)}
           .dashboard-card .user-info,.dashboard-card .lots{color:#F3F4F6}}
        </style>
        <meta name="viewport" content="width=device-width,initial-scale=1">
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────
    # 2. PAGE LAYOUT
    # ──────────────────────────────────────────────────────────────
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown("<h1>Hedge Manager Dashboard</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your POS CSV file here or click to browse",
        type=["csv"],
        key="pos_file",
        label_visibility="collapsed"
    )

    # ──────────────────────────────────────────────────────────────
    # 3. ADVANCED SETTINGS (optional)
    # ──────────────────────────────────────────────────────────────
    with st.expander("Advanced Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            product_options = st.multiselect(
                "Product type(s) to include",
                options=["MIS", "NRML"],
                default=["MIS"],
                help="Leave empty to include **all** products."
            )
        with col2:
            manual_lot = st.number_input(
                "Manual lot size (override auto-detect)",
                min_value=0,
                value=0,
                step=1,
                help="Enter >0 to use this lot size for **every** symbol."
            )

    # ──────────────────────────────────────────────────────────────
    # 4. PROCESS FILE
    # ──────────────────────────────────────────────────────────────
    if uploaded_file is not None:
        try:
            with st.spinner("Processing your data..."):
                df = pd.read_csv(uploaded_file)

                # ---- Clean column names ----
                df.columns = [c.strip() for c in df.columns]

                # ---- Required columns ----
                required = ['UserID', 'Symbol', 'Product', 'Buy Qty', 'Sell Qty']
                missing = [c for c in required if c not in df.columns]
                if missing:
                    st.error(f"Missing columns: {', '.join(missing)}")
                    st.stop()

                # ---- 1. PRODUCT FILTER ----
                if product_options:
                    df = df[df["Product"].isin(product_options)].copy()
                # else: keep everything

                if df.empty:
                    st.warning("No rows match the selected product filter.")
                    st.stop()

                # ---- 2. QUANTITY CLEANUP ----
                for col in ['Buy Qty', 'Sell Qty']:
                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace(r'[^\d\.]', '', regex=True)
                        .replace('', '0')
                    )
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                # ---- 3. OPTION TYPE ----
                df['OptionType'] = df['Symbol'].apply(
                    lambda x: 'Call' if 'CE' in str(x).upper()
                    else ('Put' if 'PE' in str(x).upper() else 'Other')
                )

                # ---- 4. LOT SIZE (auto or manual) ----
                def auto_lot(symbol):
                    s = str(symbol).upper()
                    if "NIFTY" in s:   return 75
                    if "SENSEX" in s or "BANKEX" in s: return 20
                    return 1

                if manual_lot > 0:
                    df['LotSize'] = int(manual_lot)
                else:
                    df['LotSize'] = df['Symbol'].apply(auto_lot).astype(int)

                # ---- 5. AGGREGATE ----
                summary = (
                    df.groupby(['UserID', 'OptionType'], as_index=False)
                      .agg({'Buy Qty': 'sum', 'Sell Qty': 'sum', 'LotSize': 'max'})
                )

                summary['difference'] = summary['Buy Qty'] - summary['Sell Qty']
                summary['lots']       = summary['difference'] / summary['LotSize']

                # ---- 6. FILTER NON-ZERO ----
                summary = summary[summary['difference'] != 0].copy()

                if summary.empty:
                    st.success("All positions are perfectly hedged!")
                else:
                    # ---- 7. ACTION & FINAL COLUMNS ----
                    summary['ActionToHedge'] = summary['difference'].apply(
                        lambda x: 'Sell' if x > 0 else 'Buy'
                    )
                    summary['LotsToHedge'] = summary['lots'].abs().round(2)
                    summary = summary[['UserID', 'OptionType', 'ActionToHedge', 'LotsToHedge']]

                    # ---- 8. DISPLAY ----
                    st.markdown("### Hedge Actions Required")
                    for _, row in summary.iterrows():
                        cls = 'action-buy' if row['ActionToHedge'] == 'Buy' else 'action-sell'
                        st.markdown(f"""
                            <div class="dashboard-card">
                                <span class="user-info">{row['UserID']} ({row['OptionType']})</span>
                                <span class="{cls}">{row['ActionToHedge']}</span>
                                <span class="lots">{row['LotsToHedge']} Lots</span>
                            </div>
                        """, unsafe_allow_html=True)

                    # ---- 9. DOWNLOAD ----
                    csv = summary.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Hedge Actions as CSV",
                        data=csv,
                        file_name="hedge_actions.csv",
                        mime="text/csv",
                        key="download_summary"
                    )

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("CSV must contain: `UserID`, `Symbol`, `Product`, `Buy Qty`, `Sell Qty`")
    else:
        st.info("Upload a POS CSV file to start.")

    # ──────────────────────────────────────────────────────────────
    # 5. FOOTER
    # ──────────────────────────────────────────────────────────────
    st.markdown("""
        ---
        <div style='text-align:center;color:#888;font-size:clamp(.9rem,2.5vw,1rem);'>
            Powered by Streamlit | Designed for 2025 UX Excellence | Developed by Saksham
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    run()
