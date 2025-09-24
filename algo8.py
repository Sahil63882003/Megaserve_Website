import streamlit as st
import pandas as pd
import numpy as np
from collections import deque
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# IMPORTANT: To fix "AxiosError: Request failed with status code 403" for file uploads:
# 1. Create a '.streamlit' folder in your project root (if not exists).
# 2. Inside it, create 'config.toml' with:
#    [server]
#    enableXsrfProtection = false
#    enableCORS = false
# 3. Restart the app. For production, use secure alternatives (e.g., auth middleware).
# 4. If deployed, run with: streamlit run dashboard.py --server.enableXsrfProtection=false --server.enableCORS=false
# 5. Test with small files (<1MB) first. Update Streamlit: pip install --upgrade streamlit

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
            padding: 3vw 2vw;
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
            margin: 1.5rem 0;
        }
        
        h1 {
            font-size: clamp(2rem, 6vw, 2.5rem);
            margin-bottom: 1.2rem;
        }
        
        h2 {
            font-size: clamp(1.4rem, 4vw, 1.8rem);
            margin-top: 2rem;
            margin-bottom: 1rem;
            letter-spacing: 1px;
        }
        
        .stTextInput > div > div > input, .stDateInput > div > div > input {
            border-radius: var(--border-radius);
            border: 1px solid #D1D5DB;
            padding: 1rem 1.5rem;
            font-family: var(--font-family);
            font-size: clamp(1rem, 3vw, 1.2rem);
            width: 100%;
            box-sizing: border-box;
            margin: 1rem 0;
        }
        
        .stSelectbox > div > div > select {
            border-radius: var(--border-radius);
            border: 1px solid #D1D5DB;
            padding: 1rem 1.5rem;
            font-family: var(--font-family);
            font-size: clamp(1rem, 3vw, 1.2rem);
            width: 100%;
            box-sizing: border-box;
            margin: 1rem 0;
        }
        
        .stFileUploader > div > div > div {
            border-radius: var(--border-radius);
            border: 2px dashed #ccc;
            padding: 1.5rem;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
        }
        
        .stButton > button {
            background-image: var(--admin-accent);
            border: none;
            border-radius: var(--border-radius);
            color: white;
            padding: 1rem 2.5rem;
            font-weight: 600;
            font-family: var(--font-family);
            font-size: clamp(1rem, 3vw, 1.2rem);
            transition: all var(--transition);
            width: 100%;
            box-sizing: border-box;
            margin: 1.5rem 0;
        }
        
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 28px rgba(109,40,217,0.4);
        }
        
        .metric-card {
            background: white;
            padding: 2rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-light);
            text-align: center;
            border-left: 4px solid var(--accent1);
            margin-bottom: 2rem;
            width: 100%;
            box-sizing: border-box;
        }
        
        .input-section {
            background: #f8f9fa;
            padding: 2.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 2.5rem;
            box-shadow: var(--shadow-light);
            width: 100%;
            box-sizing: border-box;
        }
        
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        
        .stDataFrame, .stPlotlyChart {
            width: 100%;
            box-sizing: border-box;
            margin: 0 auto;
            min-height: 50vh;
        }
        
        /* Responsive adjustments */
        @media (max-width: 1024px) {
            .main {
                padding: 2vw 1.5vw;
            }
            h1 {
                font-size: clamp(1.8rem, 5vw, 2.2rem);
            }
            h2 {
                font-size: clamp(1.2rem, 3.5vw, 1.6rem);
            }
            .input-section, .metric-card {
                padding: 1.5rem;
            }
        }
        
        @media (max-width: 600px) {
            .main {
                padding: 1.5rem;
            }
            h1 {
                font-size: clamp(1.6rem, 4.5vw, 2rem);
            }
            h2 {
                font-size: clamp(1rem, 3vw, 1.4rem);
            }
            .stButton > button {
                padding: 0.8rem 1.5rem;
            }
            .metric-card {
                padding: 1.2rem;
                margin-bottom: 1.2rem;
            }
            .input-section {
                padding: 1.2rem;
            }
            .stTextInput > div > div > input, .stDateInput > div > div > input, .stSelectbox > div > div > select {
                padding: 0.8rem;
                font-size: clamp(0.9rem, 2.5vw, 1rem);
            }
            .stPlotlyChart, .stDataFrame {
                min-height: 40vh;
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
            .metric-card {
                background: rgba(255,255,255,0.1);
                box-shadow: var(--shadow-dark);
                border-left: 4px solid var(--accent1);
            }
            .stTextInput > div > div > input, .stDateInput > div > div > input {
                background: rgba(255,255,255,0.08);
                color: #F3F4F6;
                border: 1px solid rgba(255,255,255,0.15);
            }
            .stSelectbox > div > div > select {
                background: rgba(255,255,255,0.08);
                color: #F3F4F6;
                border: 1px solid rgba(255,255,255,0.15);
            }
            .stFileUploader > div > div > div {
                background: rgba(255,255,255,0.1);
                border: 2px dashed rgba(255,255,255,0.2);
            }
            .stButton > button {
                background-image: var(--admin-accent);
            }
            .stDataFrame, .stPlotlyChart {
                background: transparent;
            }
        }
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """, unsafe_allow_html=True)

    # Define the comment lines to prepend to the updated usersetting CSV
    comment_lines = """# Please fill all values carefully. ANY VALUE WHICH IS NOT REQUIRED CAN BE LEFT BLANK.
# For Boolean, True / False OR Yes / No can be used.
# For NRML SqOff, 0 = None, 1 = All, 2 = Today
# For Time, enter like 15:15:00.
# Password & PIN: These are only required if you have selected for Auto Login. Auto login internally fills user details in browser for easy login. It is totally optional feature.
# Broker: Zerodha, AliceBlue etc.
"""

    # Main header
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<h1>📊 Algo 8 Calculator</h1>', unsafe_allow_html=True)
    st.markdown("**Calculate Realized & Unrealized PNL for NIFTY/SENSEX Options**", unsafe_allow_html=True)
    st.info("👇 Upload your files and configure settings below to calculate PNL. If uploads fail (403 error), check the config.toml fix in the code comments.")

    # Input Section
    # st.markdown("### ⚙️ Input Settings", unsafe_allow_html=True)
    with st.container():
        # st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        # File Uploaders in a 2-column grid
        st.subheader("📁 Upload Files")
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            uploaded_usersetting = st.file_uploader(
                "User Settings CSV", 
                type="csv", 
                help="VS1 USERSETTING( EVE ).csv - Ensure file <1MB for testing",
                key="usersetting"
            )
            if uploaded_usersetting:
                st.success("✅ User Settings uploaded")
            uploaded_position = st.file_uploader(
                "Position CSV", 
                type="csv", 
                help="VS1 Position(EOD).csv",
                key="position"
            )
            if uploaded_position:
                st.success("✅ Position uploaded")
        
        with col2:
            uploaded_orderbook = st.file_uploader(
                "Order Book CSV", 
                type="csv", 
                help="VS1 ORDERBOOK.csv",
                key="orderbook"
            )
            if uploaded_orderbook:
                st.success("✅ Order Book uploaded")
            uploaded_bhav = st.file_uploader(
                "Bhavcopy CSV", 
                type="csv", 
                help="opXXXXXX.csv (Bhavcopy)",
                key="bhavcopy"
            )
            if uploaded_bhav:
                st.success("✅ Bhavcopy uploaded")
        
        st.divider()
        
        # Settings and Features
        st.subheader("🎛️ Configuration")
        col3, col4 = st.columns(2, gap="medium")
        with col3:
            symbol = st.selectbox("Select Index", ["NIFTY", "SENSEX"], index=0, key="symbol")
            expiry = st.date_input("Select Expiry Date", value=pd.to_datetime("2025-09-23"), key="expiry")
        with col4:
            show_charts = st.checkbox("📊 Show Visual Charts", value=True, key="show_charts")
            show_details = st.checkbox("🔍 Show Detailed Breakdown", value=False, key="show_details")
            auto_refresh = st.checkbox("🔄 Auto-refresh Results", value=False, key="auto_refresh")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if auto_refresh:
            time.sleep(5)  # Simulate auto-refresh (remove in production for real-time)

    # Calculate button
    if st.button("🚀 Calculate PNL", use_container_width=True, key="calculate_pnl"):
        if all([uploaded_usersetting, uploaded_orderbook, uploaded_position, uploaded_bhav]):
            with st.spinner("🔄 Processing your data... This may take a moment for large files."):
                try:
                    # Read uploaded files safely
                    df1 = pd.read_csv(uploaded_usersetting, skiprows=6)
                    df2 = pd.read_csv(uploaded_orderbook, index_col=False)
                    df3 = pd.read_csv(uploaded_position)
                    df_bhav = pd.read_csv(uploaded_bhav)

                    # Ensure Max Loss column exists in df1
                    if "Max Loss" not in df1.columns:
                        df1["Max Loss"] = 0.0  # Initialize with zeros if column is missing

                    # Validate inputs
                    expiry_str = expiry.strftime("%d-%m-%Y")
                    if symbol not in ["NIFTY", "SENSEX"]:
                        st.error("Invalid symbol. Please select 'NIFTY' or 'SENSEX'.")
                        st.stop()
                    try:
                        pd.to_datetime(expiry_str, format="%d-%m-%Y")
                    except ValueError:
                        st.error("Invalid expiry date format.")
                        st.stop()

                    # Process Symbol in df3
                    df3["Symbol"] = df3["Symbol"].astype(str).str[-5:]+df3["Symbol"].astype(str).str[-8:-6]

                    # Split users
                    temp = df1[df1["Broker"]=="MasterTrust_Noren"]
                    noren_user = temp["User ID"].to_list()
                    temp = df1[df1["Broker"]!="MasterTrust_Noren"]
                    not_noren_user = temp["User ID"].to_list()
                    df3_not = df3[df3["UserID"].isin(not_noren_user)].copy()

                    # Bhavcopy cleaning
                    if symbol=="NIFTY":
                        df_bhav["Date"] = df_bhav["CONTRACT_D"].str.extract(r'(\d{2}-[A-Z]{3}-\d{4})')
                        df_bhav["Symbol"] = df_bhav["CONTRACT_D"].str.extract(r'^(.*?)(\d{2}-[A-Z]{3}-\d{4})')[0]
                        df_bhav["Strike_Type"] = df_bhav["CONTRACT_D"].str.extract(r'(PE\d+|CE\d+)$')
                        df_bhav["Date"] = pd.to_datetime(df_bhav["Date"], format="%d-%b-%Y")
                        df_bhav["Strike_Type"] = df_bhav["Strike_Type"].str.replace(r'^(PE|CE)(\d+)$', r'\2\1', regex=True)
                        target_symbol = "OPTIDXNIFTY"
                        df_bhav = df_bhav[(df_bhav["Date"] == pd.to_datetime(expiry_str, format="%d-%m-%Y")) & (df_bhav["Symbol"] == target_symbol)]
                        df3_not["Strike_Type"] = df3_not["Symbol"].str.extract(r'(\d+[A-Z]{2})$')
                        df3_not = df3_not.merge(df_bhav[["Symbol", "Strike_Type", "SETTLEMENT"]], left_on="Strike_Type", right_on="Strike_Type", how="left")
                        settelment = "SETTLEMENT"
                        symbols = "Symbol"
                    elif symbol=="SENSEX":
                        df_bhav["Date"] = pd.to_datetime(df_bhav["Market Summary Date"], format="%d %b %Y", errors="coerce")
                        df_bhav["Expiry Date"] = pd.to_datetime(df_bhav["Expiry Date"], format="%d %b %Y", errors="coerce")
                        df_bhav["Symbols"] = df_bhav["Series Code"].astype(str).str[-7:]
                        df_bhav = df_bhav[(df_bhav["Expiry Date"] == pd.to_datetime(expiry_str, format="%d-%m-%Y"))]
                        df_bhav["Symbols"] = df_bhav["Symbols"].astype(str).str.strip()
                        bhav_mapping = df_bhav.drop_duplicates(subset="Symbols", keep="last").set_index("Symbols")["Close Price"]
                        df3_not["Close Price"] = df3_not["Symbol"].map(bhav_mapping)
                        settelment = "Close Price"
                        symbols = "Symbols"

                    # Not Noren Calculation
                    dict2 = {}
                    dict3 = {}
                    for i in range(len(not_noren_user)):
                        df = df3_not[df3_not["UserID"]==not_noren_user[i]].copy()
                        conditions = [
                            df["Net Qty"] == 0,
                            df["Net Qty"] > 0,
                            df["Net Qty"] < 0
                        ]
                        choices = [
                            (df["Sell Avg Price"] - df["Buy Avg Price"]) * df["Sell Qty"],
                            (df["Sell Avg Price"] - df["Buy Avg Price"]) * df["Sell Qty"],
                            (df["Sell Avg Price"] - df["Buy Avg Price"]) * df["Buy Qty"]
                        ]
                        df.loc[:, "Calculated_Realized_PNL"] = np.select(conditions, choices, default=0)
                        df.loc[:, "Calculated_Unrealized_PNL"] = np.select(
                            [
                                df["Net Qty"] > 0,
                                df["Net Qty"] < 0
                            ],
                            [
                                (df[settelment] - df["Buy Avg Price"]) * abs(df["Net Qty"]),
                                (df["Sell Avg Price"] - df[settelment]) * abs(df["Net Qty"])
                            ],
                            default=0
                        )
                        df.loc[:, "Matching_Realized"] = df["Realized Profit"] == df["Calculated_Realized_PNL"]
                        df.loc[:, "Matching_Realized"] = df["Matching_Realized"].replace({True: "TRUE", False: ""})
                        df.loc[:, "Matching_Unrealized"] = df["Unrealized Profit"] == df["Calculated_Unrealized_PNL"]
                        df.loc[:, "Matching_Unrealized"] = df["Matching_Unrealized"].replace({True: "TRUE", False: ""})
                        total_realized_pnl = df["Calculated_Realized_PNL"].fillna(0).sum()
                        total_unrealized_pnl = df["Calculated_Unrealized_PNL"].fillna(0).sum()
                        dict2[not_noren_user[i]] = total_realized_pnl
                        dict3[not_noren_user[i]] = total_unrealized_pnl

                    # Noren Calculation
                    dict1 = {}
                    dict4 = {}
                    if symbol == "NIFTY":
                        df2 = df2[(df2["Exchange"] == "NFO") & (df2["Symbol"].str.contains("NIFTY"))]
                    df2["Symbol"] = df2["Symbol"].astype(str).str[-7:]
                    df2["Exchange Time"] = pd.to_datetime(df2["Exchange Time"], format="%d-%b-%Y %H:%M:%S")
                    df2 = df2.sort_values(by="Exchange Time")
                    for i in range(len(noren_user)):
                        df_user = df2[df2["User ID"] == noren_user[i]].copy()
                        grouped = df_user.groupby("Symbol")
                        total_realized_pnl = 0.0
                        carry_forward = []
                        for name, group in grouped:
                            buy_queue = deque()
                            sell_queue = deque()
                            net_qty = 0
                            total_value = 0.0
                            group = group.sort_values(by="Exchange Time")
                            for _, row in group.iterrows():
                                qty = row["Quantity"]
                                price = row["Avg Price"]
                                time = row["Exchange Time"]
                                trans = row["Transaction"]
                                if trans == "BUY":
                                    total_value += price * qty
                                    net_qty += qty
                                    buy_queue.append((time, price, qty))
                                elif trans == "SELL":
                                    total_value -= price * qty
                                    net_qty -= qty
                                    sell_queue.append((time, price, qty))
                                while buy_queue and sell_queue:
                                    buy_time, buy_price, buy_qty = buy_queue[0]
                                    sell_time, sell_price, sell_qty = sell_queue[0]
                                    matched = min(buy_qty, sell_qty)
                                    pnl = (sell_price - buy_price) * matched
                                    total_realized_pnl += pnl
                                    if buy_qty - matched > 0:
                                        buy_queue[0] = (buy_time, buy_price, buy_qty - matched)
                                    else:
                                        buy_queue.popleft()
                                    if sell_qty - matched > 0:
                                        sell_queue[0] = (sell_time, sell_price, sell_qty - matched)
                                    else:
                                        sell_queue.popleft()
                            if net_qty != 0:
                                weighted_avg = total_value / net_qty if net_qty > 0 else -total_value / abs(net_qty)
                                carry_forward.append({"Symbol": name, "Net_Quantity": net_qty, "Weighted_Avg_Price": weighted_avg, "UserID": noren_user[i]})
                        dict1[noren_user[i]] = total_realized_pnl
                        if carry_forward:
                            df_carry = pd.DataFrame(carry_forward)
                            if symbol == "NIFTY":
                                df_carry["Strike_Type"] = df_carry["Symbol"].str.extract(r'(\d+[A-Z]{2})$')
                                df_carry = df_carry.merge(df_bhav[["Strike_Type", "SETTLEMENT"]], on="Strike_Type", how="left")
                                settelment_col = "SETTLEMENT"
                            elif symbol == "SENSEX":
                                df_carry["Symbols"] = df_carry["Symbol"]
                                df_carry = df_carry.merge(df_bhav[["Symbols", "Close Price"]], on="Symbols", how="left")
                                settelment_col = "Close Price"
                            df_carry.loc[:, "Calculated_Unrealized_PNL"] = np.select(
                                [
                                    df_carry["Net_Quantity"] > 0,
                                    df_carry["Net_Quantity"] < 0
                                ],
                                [
                                    (df_carry[settelment_col] - df_carry["Weighted_Avg_Price"]) * abs(df_carry["Net_Quantity"]),
                                    (df_carry["Weighted_Avg_Price"] - df_carry[settelment_col]) * abs(df_carry["Net_Quantity"])
                                ],
                                default=0
                            )
                            total_unrealized_pnl = df_carry["Calculated_Unrealized_PNL"].fillna(0).sum()
                        else:
                            total_unrealized_pnl = 0.0
                        dict4[noren_user[i]] = total_unrealized_pnl

                    # Formatting
                    dict1_fmt = {k: f"{v:.1f}" for k, v in dict1.items()}
                    dict4_fmt = {k: f"{v:.1f}" for k, v in dict4.items()}
                    dict2_fmt = {k: f"{v:.2f}" for k, v in dict2.items()}
                    dict3_fmt = {k: f"{v:.2f}" for k, v in dict3.items()}

                    # Prepare data for display
                    rows = []
                    for user in sorted(dict1_fmt.keys()):
                        rows.append({
                            "User & PnL Type": f"NOREN_USER - {user}",
                            "REALIZED_PNL": float(dict1_fmt[user]),
                            "UNREALIZED_PNL": float(dict4_fmt[user])
                        })
                    for user in sorted(dict2_fmt.keys()):
                        rows.append({
                            "User & PnL Type": f"NOT_NOREN_USER - {user}",
                            "REALIZED_PNL": float(dict2_fmt[user]),
                            "UNREALIZED_PNL": float(dict3_fmt[user])
                        })
                    df_display = pd.DataFrame(rows)

                    # Update Max Loss in usersetting df (df1)
                    telegram_col = "Telegram ID(s)"
                    if telegram_col not in df1.columns:
                        st.warning(f"⚠️ '{telegram_col}' column not found in User Settings CSV. Max Loss calculation skipped.")
                    else:
                        maxloss_rows = []
                        for user in noren_user:
                            if user in dict1:
                                x = df1.loc[df1["User ID"] == user, telegram_col].iloc[0]
                                realized_pnl = dict1[user]
                                max_loss = (x * 0.7) + realized_pnl
                                df1.loc[df1["User ID"] == user, "Max Loss"] = max_loss
                                maxloss_rows.append({
                                    "User ID": user,
                                    "User Type": "Noren",
                                    "Telegram ID": x,
                                    "Max Loss": max_loss
                                })

                        for user in not_noren_user:
                            if user in dict2:
                                x = df1.loc[df1["User ID"] == user, telegram_col].iloc[0]
                                realized_pnl = dict2[user]
                                unrealized_pnl = dict3[user]
                                max_loss = (x * 0.7) + realized_pnl + unrealized_pnl
                                df1.loc[df1["User ID"] == user, "Max Loss"] = max_loss
                                maxloss_rows.append({
                                    "User ID": user,
                                    "User Type": "Non-Noren",
                                    "Telegram ID": x,
                                    "Max Loss": max_loss
                                })

                        # Display Max Loss Table
                        st.subheader("💰 Max Loss Summary")
                        df_maxloss = pd.DataFrame(maxloss_rows)
                        st.dataframe(
                            df_maxloss.style.format({"Telegram ID": "{:.2f}", "Max Loss": "{:.2f}"}).map(
                                lambda x: "color: red" if isinstance(x, (int, float)) and x < 0 else "color: black",
                                subset=["Max Loss"]
                            ),
                            use_container_width=True,
                            hide_index=True
                        )

                    # Key Metrics Section
                    st.markdown("### 📊 Key Metrics", unsafe_allow_html=True)
                    col1, col2, col3, col4 = st.columns(4, gap="medium")
                    total_realized = df_display["REALIZED_PNL"].sum()
                    total_unrealized = df_display["UNREALIZED_PNL"].sum()
                    total_pnl = total_realized + total_unrealized
                    num_users = len(df_display)

                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="margin: 0; font-size: clamp(1.4rem, 4vw, 2rem);">₹{total_realized:,.2f}</h3>
                            <p style="margin: 0; color: #666; font-size: clamp(0.8rem, 2.5vw, 1rem);">Total Realized PNL</p>
                            <span class="{'positive' if total_realized >= 0 else 'negative'}">●</span>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="margin: 0; font-size: clamp(1.4rem, 4vw, 2rem);">₹{total_unrealized:,.2f}</h3>
                            <p style="margin: 0; color: #666; font-size: clamp(0.8rem, 2.5vw, 1rem);">Total Unrealized PNL</p>
                            <span class="{'positive' if total_unrealized >= 0 else 'negative'}">●</span>
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="margin: 0; font-size: clamp(1.4rem, 4vw, 2rem);">₹{total_pnl:,.2f}</h3>
                            <p style="margin: 0; color: #666; font-size: clamp(0.8rem, 2.5vw, 1rem);">Grand Total PNL</p>
                            <span class="{'positive' if total_pnl >= 0 else 'negative'}">●</span>
                        </div>
                        """, unsafe_allow_html=True)

                    with col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="margin: 0; font-size: clamp(1.4rem, 4vw, 2rem);">{num_users}</h3>
                            <p style="margin: 0; color: #666; font-size: clamp(0.8rem, 2.5vw, 1rem);">Active Users</p>
                            <span style="color: #10b981;">●</span>
                        </div>
                        """, unsafe_allow_html=True)

                    # Charts Section
                    if show_charts:
                        st.subheader("📈 Visual Insights")
                        col_a, col_b = st.columns(2, gap="medium")

                        with col_a:
                            # Bar chart for PNL by user type
                            df_summary = df_display.copy()
                            df_summary['User_Type'] = df_summary["User & PnL Type"].str.contains("NOREN_USER").map({True: "Noren Users", False: "Non-Noren Users"})
                            fig_bar = px.bar(df_summary, x="User_Type", y=["REALIZED_PNL", "UNREALIZED_PNL"],
                                             barmode="group", title="PNL Breakdown by User Type",
                                             color_discrete_map={"REALIZED_PNL": "#ef4444", "UNREALIZED_PNL": "#10b981"})
                            fig_bar.update_layout(showlegend=True, font=dict(size=clamp(12, 16)), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                            st.plotly_chart(fig_bar, use_container_width=True)

                        with col_b:
                            # Pie chart for Total PNL Distribution
                            fig_pie = px.pie(values=[abs(total_realized), abs(total_unrealized)], names=["Realized", "Unrealized"],
                                             title="PNL Distribution", color_discrete_sequence=["#ef4444", "#10b981"])
                            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                            st.plotly_chart(fig_pie, use_container_width=True)

                        # Scatter plot for users
                        st.markdown("### User PNL Scatter Plot")
                        fig_scatter = px.scatter(df_display, x="REALIZED_PNL", y="UNREALIZED_PNL",
                                                 text="User & PnL Type", size=np.sqrt(np.abs(df_display["REALIZED_PNL"] + df_display["UNREALIZED_PNL"] + 1)),  # +1 to avoid zero
                                                 color="REALIZED_PNL", hover_name="User & PnL Type",
                                                 title="User PNL Scatter: Realized vs Unrealized",
                                                 color_continuous_scale="RdYlGn")
                        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_scatter, use_container_width=True)

                    # Table Section
                    st.subheader("📋 Calculation Summary")
                    st.dataframe(
                        df_display.style.format({
                            "REALIZED_PNL": "{:.2f}",
                            "UNREALIZED_PNL": "{:.2f}"
                        }).map(lambda x: "color: green" if x >= 0 else "color: red",
                               subset=["REALIZED_PNL", "UNREALIZED_PNL"]),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Download Section
                    st.subheader("💾 Download Results")
                    col_dl1, col_dl2 = st.columns(2, gap="medium")
                    with col_dl1:
                        csv = df_display.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download PNL Summary as CSV",
                            data=csv,
                            file_name=f'pnl_summary_{symbol}_{expiry_str}.csv',
                            mime='text/csv',
                            use_container_width=True,
                            key="download_pnl"
                        )
                    with col_dl2:
                        output = io.StringIO()
                        output.write(comment_lines)
                        df1.to_csv(output, index=False)
                        updated_usersetting_csv = output.getvalue().encode('utf-8')
                        st.download_button(
                            label="Download Updated Usersetting CSV",
                            data=updated_usersetting_csv,
                            file_name=f'updated_usersetting_{expiry_str}.csv',
                            mime='text/csv',
                            use_container_width=True,
                            key="download_usersetting"
                        )

                    # Detailed Breakdown
                    if show_details:
                        st.subheader("🔍 Detailed Position Breakdown")
                        if 'df3_not' in locals() and not df3_not.empty:
                            st.dataframe(df3_not.head(100), use_container_width=True)
                        else:
                            st.info("No detailed position data available.")

                    # Success message
                    st.success("✅ Calculation completed! Explore the insights above.")

                except Exception as e:
                    st.error(f"❌ An error occurred during calculation: {str(e)}")
                    st.exception(e)
        else:
            st.warning("⚠️ Please upload all four files to proceed. If uploads fail, ensure config.toml is set as per code comments.")

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888; font-size: clamp(0.9rem, 2.5vw, 1rem);'>Powered by Streamlit | Designed for 2025 UX Excellence | Developed by Sahil</p>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)