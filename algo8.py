import streamlit as st
import pandas as pd
import numpy as np
from collections import deque
import io
import time
import uuid

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
    # Initialize session state to store calculated data
    if 'calculation_done' not in st.session_state:
        st.session_state.calculation_done = False
        st.session_state.df_display = None
        st.session_state.df_maxloss = None
        st.session_state.total_realized = 0
        st.session_state.total_unrealized = 0
        st.session_state.total_pnl = 0
        st.session_state.num_users = 0
        st.session_state.updated_usersetting_csv = None
        st.session_state.output_additional_excel = None
        st.session_state.expiry_str = None

    # Updated Custom CSS for modern, professional, and aligned design
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        :root {
            --primary-color: #3B82F6; /* Blue for primary actions */
            --secondary-color: #06B6D4; /* Cyan for gradients */
            --accent-color: #9333EA; /* Purple for highlights */
            --text-primary: #111827; /* Dark text */
            --text-secondary: #6B7280; /* Gray text */
            --bg-primary: #FFFFFF; /* White background */
            --bg-secondary: #F9FAFB; /* Light gray background */
            --border-color: #E5E7EB; /* Light border */
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --radius: 8px;
            --transition: 0.3s ease;
            --font-family: 'Inter', sans-serif;
        }

        html, body, [class*="css"] {
            font-family: var(--font-family);
            color: var(--text-primary);
        }

        .main-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 2rem 1rem;
            box-sizing: border-box;
        }

        h1 {
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 0.5rem;
        }

        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
        }

        .subtitle {
            text-align: center;
            color: var(--text-secondary);
            font-size: 1.125rem;
            margin-bottom: 2rem;
        }

        .section-card {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--primary-color);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .section-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        }

        .stFileUploader > div > div > div,
        .stSelectbox > div > div > select,
        .stDateInput > div > div > input {
            border-radius: var(--radius);
            border: 1px solid var(--border-color);
            padding: 0.75rem;
            font-size: 1rem;
            background-color: var(--bg-secondary);
            transition: var(--transition);
        }

        .stFileUploader > div > div > div:hover,
        .stSelectbox > div > div > select:focus,
        .stDateInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border: none;
            border-radius: var(--radius);
            color: white;
            font-weight: 500;
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
            transition: var(--transition);
            box-shadow: var(--shadow);
            height: 48px; /* Fixed height for consistency */
            line-height: 1.5; /* Align text vertically */
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .metric-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .metric-card h3 {
            margin: 0;
            font-size: 1.5rem;
            color: var(--text-primary);
        }

        .metric-card p {
            margin: 0.5rem 0 0;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .stDataFrame {
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            overflow: hidden;
        }

        .download-section {
            display: flex;
            flex-direction: row;
            gap: 1rem;
            justify-content: center;
            margin-top: 1.5rem;
            align-items: center;
        }

        .download-section .stButton {
            flex: 1;
            max-width: 250px; /* Equal width for both buttons */
        }

        .download-section .stButton > button {
            width: 100%;
            height: 48px; /* Consistent height */
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .footer {
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }

        .positive { color: #10B981; }
        .negative { color: #EF4444; }

        @media (max-width: 768px) {
            .main-container {
                padding: 1rem;
            }

            h1 {
                font-size: 1.875rem;
            }

            h2 {
                font-size: 1.25rem;
            }

            .download-section {
                flex-direction: row; /* Keep buttons in a single line */
                gap: 0.75rem;
                flex-wrap: wrap; /* Allow wrapping if screen is too narrow */
            }

            .download-section .stButton {
                max-width: 200px; /* Slightly smaller for mobile */
            }

            .download-section .stButton > button {
                font-size: 0.9rem;
                padding: 0.5rem 1rem;
            }
        }

        @media (max-width: 480px) {
            .download-section {
                flex-direction: column; /* Stack vertically on very small screens */
                align-items: center;
            }

            .download-section .stButton {
                max-width: 100%;
            }
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #60A5FA;
                --secondary-color: #22D3EE;
                --text-primary: #F9FAFB;
                --text-secondary: #9CA3AF;
                --bg-primary: #1F2937;
                --bg-secondary: #374151;
                --border-color: #4B5563;
                --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.12);
            }

            .section-card, .metric-card {
                background: var(--bg-primary);
                border-color: var(--border-color);
            }

            .stFileUploader > div > div > div,
            .stSelectbox > div > div > select,
            .stDateInput > div > div > input {
                background: var(--bg-secondary);
                color: var(--text-primary);
            }

            .stDataFrame {
                background: var(--bg-primary);
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

    # Main container for centered layout
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header with subtitle
    st.markdown("<h1>📊 Algo 8 Calculator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Calculate Realized & Unrealized PNL for NIFTY/SENSEX Options with precision.</p>", unsafe_allow_html=True)
    st.info("👇 Upload your files and configure settings below to calculate PNL. If uploads fail (403 error), check the config.toml fix in the code comments.")

    tabs = st.tabs(["💼 Full PNL Calculation", "⚙️ Noren Realized PNL Only"])

    with tabs[0]:
        # Input Section
        with st.container():
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("📁 Upload Files")
            col1, col2 = st.columns(2)
            with col1:
                uploaded_usersetting = st.file_uploader(
                    "User Settings CSV", 
                    type="csv", 
                    help="VS1 USERSETTING( EVE ).csv - Ensure file <1MB for testing. Expected columns: User ID, Broker, Telegram ID(s).",
                    key="usersetting"
                )
                if uploaded_usersetting:
                    st.success("✅ User Settings uploaded")
                uploaded_position = st.file_uploader(
                    "Position CSV", 
                    type="csv", 
                    help="VS1 Position(EOD).csv. Expected columns: UserID, Symbol, Net Qty, Sell Avg Price, Buy Avg Price, Sell Qty, Buy Qty, Realized Profit, Unrealized Profit.",
                    key="position"
                )
                if uploaded_position:
                    st.success("✅ Position uploaded")
            
            with col2:
                uploaded_orderbook = st.file_uploader(
                    "Order Book CSV", 
                    type="csv", 
                    help="VS1 ORDERBOOK.csv. Expected columns: Exchange, Symbol, Exchange Time (format: DD-MMM-YYYY HH:MM:SS), User ID, Quantity, Avg Price, Transaction.",
                    key="orderbook"
                )
                if uploaded_orderbook:
                    st.success("✅ Order Book uploaded")
                uploaded_bhav = st.file_uploader(
                    "Bhavcopy CSV", 
                    type="csv", 
                    help="opXXXXXX.csv (Bhavcopy). Expected columns for NIFTY: CONTRACT_D, SETTLEMENT. For SENSEX: Market Summary Date, Expiry Date, Series Code, Close Price.",
                    key="bhavcopy"
                )
                if uploaded_bhav:
                    st.success("✅ Bhavcopy uploaded")
            st.markdown('</div>', unsafe_allow_html=True)

        # Configuration Section
        with st.container():
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🎛️ Configuration")
            col3, col4 = st.columns(2)
            with col3:
                symbol = st.selectbox("Select Index", ["NIFTY", "SENSEX"], index=0, key="symbol")
            with col4:
                expiry = st.date_input("Select Expiry Date", value=pd.to_datetime("2025-09-23"), key="expiry")
            st.markdown('</div>', unsafe_allow_html=True)

        # Calculate Button
        if st.button("🚀 Calculate PNL", use_container_width=True, key="calculate_pnl"):
            if all([uploaded_usersetting, uploaded_orderbook, uploaded_position, uploaded_bhav]):
                with st.spinner("🔄 Processing your data... This may take a moment for large files."):
                    try:
                        # Read uploaded files safely with try-except
                        try:
                            df1 = pd.read_csv(uploaded_usersetting, skiprows=6)
                        except Exception as e:
                            st.error(f"❌ Error reading User Settings CSV: {str(e)}")
                            return
                        try:
                            df2 = pd.read_csv(uploaded_orderbook, index_col=False)
                        except Exception as e:
                            st.error(f"❌ Error reading Order Book CSV: {str(e)}")
                            return
                        try:
                            df3 = pd.read_csv(uploaded_position)
                        except Exception as e:
                            st.error(f"❌ Error reading Position CSV: {str(e)}")
                            return
                        try:
                            df_bhav = pd.read_csv(uploaded_bhav)
                        except Exception as e:
                            st.error(f"❌ Error reading Bhavcopy CSV: {str(e)}")
                            return

                        # Check required columns in df1 (User Settings)
                        required_df1_cols = ["User ID", "Broker"]
                        missing_df1_cols = [col for col in required_df1_cols if col not in df1.columns]
                        if missing_df1_cols:
                            st.error(f"❌ Missing columns in User Settings CSV: {', '.join(missing_df1_cols)}")
                            return

                        # Ensure Max Loss column exists in df1
                        if "Max Loss" not in df1.columns:
                            df1["Max Loss"] = 0  # Initialize with integer zeros

                        # Validate inputs
                        expiry_str = expiry.strftime("%d-%m-%Y")
                        if symbol not in ["NIFTY", "SENSEX"]:
                            st.error("❌ Invalid symbol. Please select 'NIFTY' or 'SENSEX'.")
                            return
                        try:
                            pd.to_datetime(expiry_str, format="%d-%m-%Y")
                        except ValueError:
                            st.error("❌ Invalid expiry date format. Use DD-MM-YYYY.")
                            return

                        # Process Symbol in df3 (Position)
                        if "Symbol" not in df3.columns:
                            st.error("❌ Missing 'Symbol' column in Position CSV.")
                            return
                        df3["Original_Symbol"] = df3["Symbol"]  # Preserve original Symbol
                        df3["Symbol"] = df3["Symbol"].astype(str).str[-5:]+df3["Symbol"].astype(str).str[-8:-6]

                        # Split users
                        temp = df1[df1["Broker"]=="MasterTrust_Noren"]
                        noren_user = temp["User ID"].to_list()
                        temp = df1[df1["Broker"]!="MasterTrust_Noren"]
                        not_noren_user = temp["User ID"].to_list()
                        df3_not = df3[df3["UserID"].isin(not_noren_user)].copy()

                        # Bhavcopy cleaning and Strike Price Details
                        if symbol=="NIFTY":
                            required_bhav_cols = ["CONTRACT_D", "SETTLEMENT"]
                            missing_bhav_cols = [col for col in required_bhav_cols if col not in df_bhav.columns]
                            if missing_bhav_cols:
                                st.error(f"❌ Missing columns in Bhavcopy CSV for NIFTY: {', '.join(missing_bhav_cols)}")
                                return
                            df_bhav["Date"] = df_bhav["CONTRACT_D"].str.extract(r'(\d{2}-[A-Z]{3}-\d{4})')
                            df_bhav["Bhav_Symbol"] = df_bhav["CONTRACT_D"].str.extract(r'^(.*?)(\d{2}-[A-Z]{3}-\d{4})')[0]
                            df_bhav["Strike_Type"] = df_bhav["CONTRACT_D"].str.extract(r'(PE\d+|CE\d+)$')
                            df_bhav["Date"] = pd.to_datetime(df_bhav["Date"], format="%d-%b-%Y", errors="coerce")
                            df_bhav["Strike_Type"] = df_bhav["Strike_Type"].str.replace(r'^(PE|CE)(\d+)$', r'\2\1', regex=True)
                            target_symbol = "OPTIDXNIFTY"
                            df_bhav = df_bhav[(df_bhav["Date"] == pd.to_datetime(expiry_str, format="%d-%m-%Y")) & (df_bhav["Bhav_Symbol"] == target_symbol)]
                            df3_not["Strike_Type"] = df3_not["Symbol"].str.extract(r'(\d+[A-Z]{2})$')
                            df3_not = df3_not.merge(df_bhav[["Bhav_Symbol", "Strike_Type", "SETTLEMENT"]], left_on="Strike_Type", right_on="Strike_Type", how="left")
                            settelment = "SETTLEMENT"
                            symbols = "Bhav_Symbol"
                            # Prepare Strike Price Details for NIFTY
                            df_strike_details = df_bhav[["Strike_Type", "SETTLEMENT"]].copy()
                            df_strike_details = df_strike_details.rename(columns={"Strike_Type": "Strike Price", "SETTLEMENT": "Settlement Price"})
                        elif symbol=="SENSEX":
                            required_bhav_cols = ["Market Summary Date", "Expiry Date", "Series Code", "Close Price"]
                            missing_bhav_cols = [col for col in required_bhav_cols if col not in df_bhav.columns]
                            if missing_bhav_cols:
                                st.error(f"❌ Missing columns in Bhavcopy CSV for SENSEX: {', '.join(missing_bhav_cols)}")
                                return
                            df_bhav["Date"] = pd.to_datetime(df_bhav["Market Summary Date"], format="%d %b %Y", errors="coerce")
                            df_bhav["Expiry Date"] = pd.to_datetime(df_bhav["Expiry Date"], format="%d %b %Y", errors="coerce")
                            df_bhav["Symbols"] = df_bhav["Series Code"].astype(str).str[-7:]
                            df_bhav = df_bhav[(df_bhav["Expiry Date"] == pd.to_datetime(expiry_str, format="%d-%m-%Y"))]
                            df_bhav["Symbols"] = df_bhav["Symbols"].astype(str).str.strip()
                            bhav_mapping = df_bhav.drop_duplicates(subset="Symbols", keep="last").set_index("Symbols")["Close Price"]
                            df3_not["Close Price"] = df3_not["Symbol"].map(bhav_mapping)
                            settelment = "Close Price"
                            symbols = "Symbols"
                            # Prepare Strike Price Details for SENSEX
                            df_strike_details = df_bhav[["Symbols", "Close Price"]].copy()
                            df_strike_details = df_strike_details.rename(columns={"Symbols": "Strike Price", "Close Price": "Settlement Price"})

                        # Remove duplicates and sort Strike Price Details
                        df_strike_details = df_strike_details.drop_duplicates(subset=["Strike Price"]).sort_values(by="Strike Price")
                        df_strike_details = df_strike_details[["Strike Price", "Settlement Price"]]

                        # Check for NaT in df_bhav dates
                        if df_bhav["Date"].isna().any():
                            st.warning("⚠️ Some dates in Bhavcopy could not be parsed and have been set to NaT.")

                        # Extract Strike Name for df3_not from Original_Symbol
                        df3_not["Strike_Name"] = df3_not["Original_Symbol"].str.extract(r'(\d+[A-Z]{2})$')

                        # Not Noren Calculation
                        not_noren_data_pos = pd.DataFrame()
                        required_df3_cols = ["UserID", "Net Qty", "Sell Avg Price", "Buy Avg Price", "Sell Qty", "Buy Qty", "Realized Profit", "Unrealized Profit"]
                        missing_df3_cols = [col for col in required_df3_cols if col not in df3_not.columns]
                        if missing_df3_cols:
                            st.error(f"❌ Missing columns in Position CSV for Non-Noren: {', '.join(missing_df3_cols)}")
                            return
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
                            not_noren_data_pos = pd.concat([not_noren_data_pos, df], ignore_index=True)
                            total_realized_pnl = df["Calculated_Realized_PNL"].fillna(0).sum()
                            total_unrealized_pnl = df["Calculated_Unrealized_PNL"].fillna(0).sum()
                            dict2[not_noren_user[i]] = total_realized_pnl
                            dict3[not_noren_user[i]] = total_unrealized_pnl
                            df3_not.loc[df3_not["UserID"] == not_noren_user[i], ["Calculated_Realized_PNL", "Calculated_Unrealized_PNL"]] = df[["Calculated_Realized_PNL", "Calculated_Unrealized_PNL"]]

                        # Noren Calculation with FIFO Logic
                        required_df2_cols = ["Exchange", "Symbol", "Exchange Time", "User ID", "Quantity", "Avg Price", "Transaction", "Status"]
                        missing_df2_cols = [col for col in required_df2_cols if col not in df2.columns]
                        if missing_df2_cols:
                            st.error(f"❌ Missing columns in Order Book CSV: {', '.join(missing_df2_cols)}")
                            return
                        dict1 = {}
                        dict4 = {}
                        df_final = pd.DataFrame()
                        x_df = pd.DataFrame()
                        df_detailed = pd.DataFrame()

                        if symbol == "NIFTY":
                            df2 = df2[(df2["Exchange"] == "NFO") & (df2["Symbol"].str.contains("NIFTY")) & (df2["Status"] == "COMPLETE")]
                        elif symbol == "SENSEX":
                            df2 = df2[(df2["Status"] == "COMPLETE")]

                        # Preprocess df2
                        df2["Symbol"] = df2["Symbol"].astype(str).str[-7:]
                        df2["Strike_Name"] = df2["Symbol"]
                        df2["Exchange Time"] = df2["Exchange Time"].replace("01-Jan-0001 00:00:00", pd.NA)
                        df2["Exchange Time"] = pd.to_datetime(df2["Exchange Time"], format="%d-%b-%Y %H:%M:%S", errors="coerce")
                        nat_count = df2["Exchange Time"].isna().sum()
                        if nat_count > 0:
                            st.warning(f"⚠️ Found {nat_count} invalid or unparsable dates in Exchange Time column. These rows have been excluded from calculations.")
                            st.dataframe(df2[df2["Exchange Time"].isna()][["Exchange Time", "User ID", "Symbol"]])
                        df2 = df2.dropna(subset=["Exchange Time"]).sort_values(by="Exchange Time")

                        for m in range(len(noren_user)):
                            df = df2[df2["User ID"] == noren_user[m]].copy()
                            sell_mask = df["Transaction"].eq("SELL")
                            df.loc[sell_mask, "Quantity"] = -df.loc[sell_mask, "Quantity"].abs()

                            if "PNL" not in df.columns:
                                df["PNL"] = 0.0
                            else:
                                df["PNL"] = df["PNL"].astype(float)
                            if "Exit_time" not in df.columns:
                                df["Exit_time"] = pd.NaT
                            else:
                                df["Exit_time"] = pd.to_datetime(df["Exit_time"], errors="coerce")
                            if "Net_Quantity" not in df.columns:
                                df["Net_Quantity"] = 0

                            lst1 = df["Symbol"].unique().tolist()
                            total_realized_pnl = 0.0
                            new_df = pd.DataFrame()
                            user_detailed = []

                            for sym in lst1:
                                test_df = (
                                    df[df["Symbol"] == sym]
                                    .sort_values(["Exchange Time"], kind="mergesort")
                                    .copy()
                                    .reset_index(drop=True)
                                )
                                if test_df.empty:
                                    continue

                                qty = test_df["Quantity"].astype(int).to_numpy(copy=True)
                                price = test_df["Avg Price"].astype(float).to_numpy(copy=True)
                                txn = test_df["Transaction"].to_numpy(copy=True)
                                t = test_df["Exchange Time"].to_numpy(copy=True)
                                idx = test_df.index.to_numpy(copy=True)

                                pnl = np.zeros(len(test_df), dtype=float)
                                net_qty = np.zeros(len(test_df), dtype=int)
                                exit_time = pd.Series([pd.NaT] * len(test_df), dtype="datetime64[ns]").to_numpy()
                                matched_with = np.array([''] * len(test_df), dtype=object)
                                matched_qty = np.zeros(len(test_df), dtype=int)
                                matched_price = np.zeros(len(test_df), dtype=float)

                                remain = np.abs(qty).astype(int)

                                if len(txn) > 0 and txn[0] == "SELL":
                                    sell_q = deque()
                                    for i in range(len(test_df)):
                                        if txn[i] == "SELL":
                                            sell_q.append([i, remain[i], price[i]])
                                        else:  # BUY
                                            need = remain[i]
                                            total_matched = 0
                                            matched_indices = []
                                            matched_prices = []
                                            while need > 0 and sell_q:
                                                s_idx, s_rem, s_px = sell_q[0]
                                                matched = min(need, s_rem)
                                                pnl[i] += (s_px - price[i]) * matched
                                                matched_indices.append(str(s_idx))
                                                matched_prices.append(s_px)
                                                total_matched += matched
                                                need -= matched
                                                s_rem -= matched
                                                if s_rem == 0:
                                                    sell_q.popleft()
                                                else:
                                                    sell_q[0][1] = s_rem
                                            net_qty[i] = need
                                            if need == 0:
                                                exit_time[i] = t[i]
                                            matched_with[i] = ";".join(matched_indices)
                                            matched_qty[i] = total_matched
                                            if matched_prices:
                                                matched_price[i] = np.mean(matched_prices)
                                    for s_idx, s_rem, _ in sell_q:
                                        net_qty[s_idx] = -s_rem
                                else:
                                    buy_q = deque()
                                    for i in range(len(test_df)):
                                        if txn[i] == "BUY":
                                            buy_q.append([i, remain[i], price[i]])
                                        else:  # SELL
                                            need = remain[i]
                                            total_matched = 0
                                            matched_indices = []
                                            matched_prices = []
                                            while need > 0 and buy_q:
                                                b_idx, b_rem, b_px = buy_q[0]
                                                matched = min(need, b_rem)
                                                pnl[i] += (price[i] - b_px) * matched
                                                matched_indices.append(str(b_idx))
                                                matched_prices.append(b_px)
                                                total_matched += matched
                                                need -= matched
                                                b_rem -= matched
                                                if b_rem == 0:
                                                    exit_time[b_idx] = t[i]
                                                    buy_q.popleft()
                                                else:
                                                    buy_q[0][1] = b_rem
                                            net_qty[i] = -need
                                            matched_with[i] = ";".join(matched_indices)
                                            matched_qty[i] = total_matched
                                            if matched_prices:
                                                matched_price[i] = np.mean(matched_prices)
                                    for b_idx, b_rem, _ in buy_q:
                                        net_qty[b_idx] = b_rem

                                test_df["PNL"] = pnl
                                test_df["Net_Quantity"] = net_qty
                                test_df["Exit_time"] = exit_time
                                test_df["Matched_With"] = matched_with
                                test_df["Matched_Quantity"] = matched_qty
                                test_df["Matched_Price"] = matched_price

                                user_detailed.append(test_df[["User ID", "Symbol", "Strike_Name", "Exchange Time", "Transaction", "Quantity", "Avg Price", "PNL", "Net_Quantity", "Exit_time", "Matched_With", "Matched_Quantity", "Matched_Price"]])
                                new_df = pd.concat([new_df, test_df], ignore_index=True)
                                total_realized_pnl += float(pnl.sum())

                            carry_fwd_pos_df_nfo = new_df[new_df["Net_Quantity"] != 0].copy()
                            x_df = pd.concat([x_df, new_df], ignore_index=True)
                            carry_fwd_pos_df_nfo["Value"] = carry_fwd_pos_df_nfo["Avg Price"] * carry_fwd_pos_df_nfo["Quantity"]
                            df_grouped = (
                                carry_fwd_pos_df_nfo.groupby("Symbol")
                                .apply(lambda x: pd.Series({
                                    "Total_Quantity": x["Quantity"].sum(),
                                    "Weighted_Avg_Price": (x["Avg Price"] * x["Quantity"]).sum() / x["Quantity"].sum()
                                    if x["Quantity"].sum() != 0 else 0,
                                    "Strike_Name": x["Strike_Name"].iloc[0]  # Add Strike_Name
                                }))
                                .reset_index()
                            )
                            fil_name = f"carry_fwd_pos_df_{noren_user[m]}.csv"
                            carry_fwd_pos_df_nfo.to_csv(fil_name)
                            df_grouped["User ID"] = noren_user[m]
                            df_grouped["Calculated_Realized_PNL"] = total_realized_pnl  # Add total realized PNL for the user
                            df_final = pd.concat([df_final, df_grouped], ignore_index=True)
                            dict1[noren_user[m]] = total_realized_pnl
                            if user_detailed:
                                df_detailed = pd.concat([df_detailed] + user_detailed, ignore_index=True)

                        # Calculate Unrealized PNL for Noren Users
                        df_final[settelment] = df_final['Symbol'].map(
                            df_bhav.set_index('Strike_Type' if symbol == "NIFTY" else 'Symbols')[settelment]
                        )
                        df_final["Calculated_Unrealized_PNL"] = np.select(
                            [
                                df_final["Total_Quantity"] > 0,
                                df_final["Total_Quantity"] < 0
                            ],
                            [
                                (df_final[settelment] - df_final["Weighted_Avg_Price"]) * abs(df_final["Total_Quantity"]),
                                (df_final["Weighted_Avg_Price"] - df_final[settelment]) * abs(df_final["Total_Quantity"])
                            ],
                            default=0
                        )
                        # Initialize missing columns in df_final
                        for col in ["Sell Avg Price", "Sell Qty", "Buy Qty", "Realized Profit", "Unrealized Profit", "Matching_Realized", "Matching_Unrealized"]:
                            if col not in df_final:
                                df_final[col] = np.nan
                        df_final["Net settlement value"] = df_final["Calculated_Unrealized_PNL"]
                        df_final["Calculated PNL"] = df_final["Calculated_Unrealized_PNL"] + df_final["Calculated_Realized_PNL"]

                        for user in noren_user:
                            dict4[user] = df_final[df_final["User ID"] == user]["Calculated_Unrealized_PNL"].fillna(0).sum()

                        # Formatting
                        dict1_fmt = {k: f"{v:.1f}" for k, v in dict1.items()}
                        dict4_fmt = {k: f"{v:.1f}" for k, v in dict4.items()}
                        dict2_fmt = {k: f"{v:.2f}" for k, v in dict2.items()}
                        dict3_fmt = {k: f"{v:.2f}" for k, v in dict3.items()}

                        # Convert dictionaries to DataFrames for Excel export
                        df_dict1 = pd.DataFrame(list(dict1.items()), columns=['User ID', 'Realized PNL'])
                        df_dict2 = pd.DataFrame(list(dict2.items()), columns=['User ID', 'Realized PNL'])
                        df_dict3 = pd.DataFrame(list(dict3.items()), columns=['User ID', 'Unrealized PNL'])
                        df_dict4 = pd.DataFrame(list(dict4.items()), columns=['User ID', 'Unrealized PNL'])

                        # Prepare data for metrics
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

                        # Prepare detailed position DataFrame for Excel
                        df3_not["Net settlement value"] = np.nan
                        positive_mask = df3_not["Net Qty"] > 0
                        negative_mask = df3_not["Net Qty"] < 0
                        df3_not.loc[positive_mask, "Net settlement value"] = (df3_not.loc[positive_mask, settelment] - df3_not.loc[positive_mask, "Buy Avg Price"]) * abs(df3_not.loc[positive_mask, "Net Qty"])
                        df3_not.loc[negative_mask, "Net settlement value"] = (df3_not.loc[negative_mask, "Sell Avg Price"] - df3_not.loc[negative_mask, settelment]) * abs(df3_not.loc[negative_mask, "Net Qty"])
                        df3_not["Calculated PNL"] = df3_not["Calculated_Realized_PNL"] + df3_not["Calculated_Unrealized_PNL"]

                        # Ensure all required columns are present
                        required_columns = ["UserID", "Original_Symbol", "Strike_Name", "Net Qty", "Sell Avg Price", "Buy Avg Price", "Sell Qty", "Buy Qty", "Realized Profit", "Unrealized Profit", settelment, "Calculated_Realized_PNL", "Calculated_Unrealized_PNL", "Net settlement value", "Calculated PNL"]
                        missing_cols = [col for col in required_columns if col not in df3_not.columns]
                        if missing_cols:
                            for col in missing_cols:
                                if col not in [settelment, "Calculated_Realized_PNL", "Calculated_Unrealized_PNL", "Net settlement value", "Calculated PNL", "Strike_Name"]:
                                    st.error(f"❌ Missing column in df3_not: {col}")
                                    return
                                df3_not[col] = np.nan

                        # For Noren users, merge with df_final
                        if not df_final.empty:
                            df_position_detailed = pd.concat([
                                df3_not[["UserID", "Original_Symbol", "Strike_Name", "Net Qty", "Sell Avg Price", "Buy Avg Price", "Sell Qty", "Buy Qty", "Realized Profit", "Unrealized Profit", settelment, "Calculated_Realized_PNL", "Calculated_Unrealized_PNL", "Net settlement value", "Calculated PNL"]].rename(columns={"Original_Symbol": "Symbol"}),
                                df_final[["User ID", "Symbol", "Strike_Name", "Total_Quantity", "Sell Avg Price", "Weighted_Avg_Price", "Sell Qty", "Buy Qty", "Realized Profit", "Unrealized Profit", settelment, "Calculated_Realized_PNL", "Calculated_Unrealized_PNL", "Net settlement value", "Calculated PNL"]].rename(columns={"User ID": "UserID", "Total_Quantity": "Net Qty", "Weighted_Avg_Price": "Buy Avg Price"})
                            ], ignore_index=True)
                        else:
                            df_position_detailed = df3_not[["UserID", "Original_Symbol", "Strike_Name", "Net Qty", "Sell Avg Price", "Buy Avg Price", "Sell Qty", "Buy Qty", "Realized Profit", "Unrealized Profit", settelment, "Calculated_Realized_PNL", "Calculated_Unrealized_PNL", "Net settlement value", "Calculated PNL"]].rename(columns={"Original_Symbol": "Symbol"})

                        # Prepare Pivot from df_position_detailed
                        df_pivot = df_position_detailed.groupby("UserID")["Net settlement value"].sum().reset_index()
                        df_pivot.columns = ["Row Labels", "Sum of Net settlement value"]
                        grand_total = pd.DataFrame({"Row Labels": ["Grand Total"], "Sum of Net settlement value": [df_pivot["Sum of Net settlement value"].sum()]})
                        df_pivot = pd.concat([df_pivot, grand_total], ignore_index=True)

                        # Update Max Loss in usersetting df (df1) and create df_maxloss
                        telegram_col = "Telegram ID(s)"
                        if telegram_col not in df1.columns:
                            st.warning(f"⚠️ '{telegram_col}' column not found in User Settings CSV. Max Loss calculation skipped.")
                        else:
                            maxloss_rows = []
                            # Combine all PNL data into a single DataFrame for easier mapping
                            df_pnl_combined = pd.DataFrame()
                            
                            # Add Noren users' PNL
                            if not df_dict1.empty:
                                df_pnl_combined = pd.concat([df_pnl_combined, df_dict1.rename(columns={'Realized PNL': 'Noren_Realized_PNL'})], ignore_index=True)
                            if not df_dict4.empty:
                                df_pnl_combined = df_pnl_combined.merge(df_dict4.rename(columns={'Unrealized PNL': 'Noren_Unrealized_PNL'}), on='User ID', how='outer')
                            
                            # Add Non-Noren users' PNL
                            if not df_dict2.empty:
                                df_pnl_combined = df_pnl_combined.merge(df_dict2.rename(columns={'Realized PNL': 'Not_Noren_Realized_PNL'}), on='User ID', how='outer')
                            if not df_dict3.empty:
                                df_pnl_combined = df_pnl_combined.merge(df_dict3.rename(columns={'Unrealized PNL': 'Not_Noren_Unrealized_PNL'}), on='User ID', how='outer')
                            
                            # Add Pivot data
                            if not df_pivot.empty:
                                df_pnl_combined = df_pnl_combined.merge(df_pivot[['Row Labels', 'Sum of Net settlement value']].rename(columns={'Row Labels': 'User ID'}), on='User ID', how='outer')
                            
                            # Process all users from df1
                            for user in df1["User ID"]:
                                telegram_id = df1.loc[df1["User ID"] == user, telegram_col].iloc[0] if not df1.loc[df1["User ID"] == user, telegram_col].empty else 0
                                user_type = "Noren" if user in noren_user else "Non-Noren"
                                
                                # Initialize PNL values
                                realized_pnl = 0.0
                                unrealized_pnl = 0.0
                                net_settlement = 0.0
                                
                                # Fetch PNL based on user type
                                if user_type == "Noren" and user in df_pnl_combined['User ID'].values:
                                    realized_pnl = df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Noren_Realized_PNL'].iloc[0] if pd.notna(df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Noren_Realized_PNL']).any() else 0.0
                                    unrealized_pnl = df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Noren_Unrealized_PNL'].iloc[0] if pd.notna(df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Noren_Unrealized_PNL']).any() else 0.0
                                elif user_type == "Non-Noren" and user in df_pnl_combined['User ID'].values:
                                    realized_pnl = df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Not_Noren_Realized_PNL'].iloc[0] if pd.notna(df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Not_Noren_Realized_PNL']).any() else 0.0
                                    unrealized_pnl = df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Not_Noren_Unrealized_PNL'].iloc[0] if pd.notna(df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Not_Noren_Unrealized_PNL']).any() else 0.0
                                
                                # Fetch Net Settlement Value
                                if user in df_pnl_combined['User ID'].values:
                                    net_settlement = df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Sum of Net settlement value'].iloc[0] if pd.notna(df_pnl_combined.loc[df_pnl_combined['User ID'] == user, 'Sum of Net settlement value']).any() else 0.0
                                
                                # Calculate Max Loss
                                max_loss = (telegram_id * 0.7) + realized_pnl + (unrealized_pnl if user_type == "Non-Noren" else 0)
                                df1.loc[df1["User ID"] == user, "Max Loss"] = int(max_loss)
                                
                                # Append to maxloss_rows
                                maxloss_rows.append({
                                    "User ID": user,
                                    "User Type": user_type,
                                    "Telegram ID": telegram_id,
                                    "Realized PNL": realized_pnl,
                                    "Unrealized PNL": unrealized_pnl,
                                    "Net Settlement Value": net_settlement,
                                    "Max Loss": int(max_loss)
                                })

                            # Create df_maxloss
                            df_maxloss = pd.DataFrame(maxloss_rows)
                            
                            # Calculate metrics
                            total_realized = df_display["REALIZED_PNL"].sum()
                            total_unrealized = df_display["UNREALIZED_PNL"].sum()
                            total_pnl = total_realized + total_unrealized
                            num_users = len(df_display)

                            # Prepare download files
                            output = io.StringIO()
                            output.write(comment_lines)
                            df1["Max Loss"] = df1["Max Loss"].astype(int)
                            df1.to_csv(output, index=False)
                            updated_usersetting_csv = output.getvalue().encode('utf-8')

                            output_additional_excel = io.BytesIO()
                            with pd.ExcelWriter(output_additional_excel, engine='xlsxwriter') as writer:
                                df_pivot.to_excel(writer, sheet_name="Pivot", index=False)
                                df_maxloss.to_excel(writer, sheet_name="Calculation", index=False)
                                x_df.to_excel(writer, sheet_name="Noren Realized Data", index=False)
                                df_final.to_excel(writer, sheet_name="Noren UnRealized Data", index=False)
                                not_noren_data_pos.to_excel(writer, sheet_name="Not Noren Data Pos", index=False)
                                df_bhav.to_excel(writer, sheet_name="BhavCopy", index=False)
                                df_strike_details.to_excel(writer, sheet_name="Strike Price Details", index=False)
                                df_dict1.to_excel(writer, sheet_name="Dict1 Realized PNL", index=False)
                            output_additional_excel.seek(0)

                            # Store results in session state
                            st.session_state.calculation_done = True
                            st.session_state.df_display = df_display
                            st.session_state.df_maxloss = df_maxloss
                            st.session_state.total_realized = total_realized
                            st.session_state.total_unrealized = total_unrealized
                            st.session_state.total_pnl = total_pnl
                            st.session_state.num_users = num_users
                            st.session_state.updated_usersetting_csv = updated_usersetting_csv
                            st.session_state.output_additional_excel = output_additional_excel
                            st.session_state.expiry_str = expiry_str

                            st.success("✅ Calculation completed! Explore the insights below.")

                    except Exception as e:
                        st.error(f"❌ An error occurred during calculation: {str(e)}")
                        st.exception(e)
            else:
                st.warning("⚠️ Please upload all four files to proceed. If uploads fail, ensure config.toml is set as per code comments.")

        # Display results if calculation is done
        if st.session_state.calculation_done:
            # Key Metrics Section
            with st.container():
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("📊 Key Metrics")
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>₹{st.session_state.total_realized:,.2f}</h3>
                        <p>Total Realized PNL</p>
                        <span class="{'positive' if st.session_state.total_realized >= 0 else 'negative'}">●</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>₹{st.session_state.total_unrealized:,.2f}</h3>
                        <p>Total Unrealized PNL</p>
                        <span class="{'positive' if st.session_state.total_unrealized >= 0 else 'negative'}">●</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>₹{st.session_state.total_pnl:,.2f}</h3>
                        <p>Grand Total PNL</p>
                        <span class="{'positive' if st.session_state.total_pnl >= 0 else 'negative'}">●</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{st.session_state.num_users}</h3>
                        <p>Active Users</p>
                        <span class="positive">●</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Max Loss Summary Section
            with st.container():
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("💰 Max Loss Summary")
                st.dataframe(
                    st.session_state.df_maxloss.style.format({
                        "Telegram ID": "{:.2f}",
                        "Realized PNL": "{:.2f}",
                        "Unrealized PNL": "{:.2f}",
                        "Net Settlement Value": "{:.2f}",
                        "Max Loss": "{:d}"
                    }).map(
                        lambda x: "color: #EF4444" if isinstance(x, (int, float)) and x < 0 else "color: #10B981",
                        subset=["Realized PNL", "Unrealized PNL", "Net Settlement Value", "Max Loss"]
                    ),
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # Download Section
            with st.container():
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("💾 Download Results")
                st.markdown('<div class="download-section">', unsafe_allow_html=True)
                col_download1, col_download2 = st.columns(2)  # Use columns for precise control
                with col_download1:
                    st.download_button(
                        label="Download Updated Usersetting CSV",
                        data=st.session_state.updated_usersetting_csv,
                        file_name=f'updated_usersetting_{st.session_state.expiry_str}.csv',
                        mime='text/csv',
                        key="download_usersetting"
                    )
                with col_download2:
                    st.download_button(
                        label="Download Additional Data XLSX",
                        data=st.session_state.output_additional_excel,
                        file_name=f"A8 {pd.to_datetime(st.session_state.expiry_str, format='%d-%m-%Y').strftime('%d %b %y').upper()} Additional Data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_additional_excel"
                    )
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]:
        # Noren Realized PNL Section
        with st.container():
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("📁 Upload Files for Realized PNL")
            col1, col2 = st.columns(2)
            with col1:
                uploaded_usersetting_r = st.file_uploader(
                    "User Settings CSV", 
                    type="csv", 
                    help="VS1 USERSETTING( EVE ).csv - Ensure file <1MB for testing. Expected columns: User ID, Broker.",
                    key="usersetting_r"
                )
                if uploaded_usersetting_r:
                    st.success("✅ User Settings uploaded")
            with col2:
                uploaded_orderbook_r = st.file_uploader(
                    "Order Book CSV", 
                    type="csv", 
                    help="VS1 ORDERBOOK.csv. Expected columns: Exchange, Symbol, Exchange Time (format: DD-MMM-YYYY HH:MM:SS), User ID, Quantity, Avg Price, Transaction.",
                    key="orderbook_r"
                )
                if uploaded_orderbook_r:
                    st.success("✅ Order Book uploaded")
            st.markdown('</div>', unsafe_allow_html=True)

        # Configuration Section
        with st.container():
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🎛️ Configuration")
            col3, _ = st.columns(2)
            with col3:
                symbol_r = st.selectbox("Select Index", ["NIFTY", "SENSEX"], index=0, key="symbol_r")
            st.markdown('</div>', unsafe_allow_html=True)

        # Calculate Button
        if st.button("🚀 Calculate Realized PNL", use_container_width=True, key="calculate_realized_pnl"):
            if uploaded_usersetting_r and uploaded_orderbook_r:
                with st.spinner("🔄 Processing your data... This may take a moment."):
                    try:
                        # Read uploaded files
                        df1_r = pd.read_csv(uploaded_usersetting_r, skiprows=6)
                        df2_r = pd.read_csv(uploaded_orderbook_r, index_col=False)

                        # Get Noren users
                        temp_r = df1_r[df1_r["Broker"] == "MasterTrust_Noren"]
                        noren_user_r = temp_r["User ID"].to_list()

                        # Validate inputs
                        if symbol_r not in ["NIFTY", "SENSEX"]:
                            st.error("❌ Invalid symbol. Please select 'NIFTY' or 'SENSEX'.")
                            return

                        # Noren Calculation with FIFO Logic (only realized)
                        required_df2_cols_r = ["Exchange", "Symbol", "Exchange Time", "User ID", "Quantity", "Avg Price", "Transaction", "Status"]
                        missing_df2_cols_r = [col for col in required_df2_cols_r if col not in df2_r.columns]
                        if missing_df2_cols_r:
                            st.error(f"❌ Missing columns in Order Book CSV: {', '.join(missing_df2_cols_r)}")
                            return

                        dict1_r = {}

                        if symbol_r == "NIFTY":
                            df2_r = df2_r[(df2_r["Exchange"] == "NFO") & (df2_r["Symbol"].str.contains("NIFTY")) & (df2_r["Status"] == "COMPLETE")]
                        elif symbol_r == "SENSEX":
                            df2_r = df2_r[(df2_r["Status"] == "COMPLETE")]

                        # Preprocess df2_r
                        df2_r["Symbol"] = df2_r["Symbol"].astype(str).str[-7:]
                        df2_r["Strike_Name"] = df2_r["Symbol"]
                        df2_r["Exchange Time"] = df2_r["Exchange Time"].replace("01-Jan-0001 00:00:00", pd.NA)
                        df2_r["Exchange Time"] = pd.to_datetime(df2_r["Exchange Time"], format="%d-%b-%Y %H:%M:%S", errors="coerce")
                        nat_count_r = df2_r["Exchange Time"].isna().sum()
                        if nat_count_r > 0:
                            st.warning(f"⚠️ Found {nat_count_r} invalid or unparsable dates in Exchange Time column. These rows have been excluded from calculations.")
                            st.dataframe(df2_r[df2_r["Exchange Time"].isna()][["Exchange Time", "User ID", "Symbol"]])
                        df2_r = df2_r.dropna(subset=["Exchange Time"]).sort_values(by="Exchange Time")

                        for m in range(len(noren_user_r)):
                            df_r = df2_r[df2_r["User ID"] == noren_user_r[m]].copy()
                            sell_mask_r = df_r["Transaction"].eq("SELL")
                            df_r.loc[sell_mask_r, "Quantity"] = -df_r.loc[sell_mask_r, "Quantity"].abs()

                            if "PNL" not in df_r.columns:
                                df_r["PNL"] = 0.0
                            else:
                                df_r["PNL"] = df_r["PNL"].astype(float)
                            if "Exit_time" not in df_r.columns:
                                df_r["Exit_time"] = pd.NaT
                            else:
                                df_r["Exit_time"] = pd.to_datetime(df_r["Exit_time"], errors="coerce")
                            if "Net_Quantity" not in df_r.columns:
                                df_r["Net_Quantity"] = 0

                            lst1_r = df_r["Symbol"].unique().tolist()
                            total_realized_pnl_r = 0.0

                            for sym_r in lst1_r:
                                test_df_r = (
                                    df_r[df_r["Symbol"] == sym_r]
                                    .sort_values(["Exchange Time"], kind="mergesort")
                                    .copy()
                                    .reset_index(drop=True)
                                )
                                if test_df_r.empty:
                                    continue

                                qty_r = test_df_r["Quantity"].astype(int).to_numpy(copy=True)
                                price_r = test_df_r["Avg Price"].astype(float).to_numpy(copy=True)
                                txn_r = test_df_r["Transaction"].to_numpy(copy=True)
                                t_r = test_df_r["Exchange Time"].to_numpy(copy=True)

                                pnl_r = np.zeros(len(test_df_r), dtype=float)
                                net_qty_r = np.zeros(len(test_df_r), dtype=int)
                                exit_time_r = pd.Series([pd.NaT] * len(test_df_r), dtype="datetime64[ns]").to_numpy()
                                matched_with_r = np.array([''] * len(test_df_r), dtype=object)
                                matched_qty_r = np.zeros(len(test_df_r), dtype=int)
                                matched_price_r = np.zeros(len(test_df_r), dtype=float)

                                remain_r = np.abs(qty_r).astype(int)

                                if len(txn_r) > 0 and txn_r[0] == "SELL":
                                    sell_q_r = deque()
                                    for i in range(len(test_df_r)):
                                        if txn_r[i] == "SELL":
                                            sell_q_r.append([i, remain_r[i], price_r[i]])
                                        else:  # BUY
                                            need = remain_r[i]
                                            total_matched = 0
                                            matched_indices = []
                                            matched_prices = []
                                            while need > 0 and sell_q_r:
                                                s_idx, s_rem, s_px = sell_q_r[0]
                                                matched = min(need, s_rem)
                                                pnl_r[i] += (s_px - price_r[i]) * matched
                                                matched_indices.append(str(s_idx))
                                                matched_prices.append(s_px)
                                                total_matched += matched
                                                need -= matched
                                                s_rem -= matched
                                                if s_rem == 0:
                                                    sell_q_r.popleft()
                                                else:
                                                    sell_q_r[0][1] = s_rem
                                            net_qty_r[i] = need
                                            if need == 0:
                                                exit_time_r[i] = t_r[i]
                                            matched_with_r[i] = ";".join(matched_indices)
                                            matched_qty_r[i] = total_matched
                                            if matched_prices:
                                                matched_price_r[i] = np.mean(matched_prices)
                                    for s_idx, s_rem, _ in sell_q_r:
                                        net_qty_r[s_idx] = -s_rem
                                else:
                                    buy_q_r = deque()
                                    for i in range(len(test_df_r)):
                                        if txn_r[i] == "BUY":
                                            buy_q_r.append([i, remain_r[i], price_r[i]])
                                        else:  # SELL
                                            need = remain_r[i]
                                            total_matched = 0
                                            matched_indices = []
                                            matched_prices = []
                                            while need > 0 and buy_q_r:
                                                b_idx, b_rem, b_px = buy_q_r[0]
                                                matched = min(need, b_rem)
                                                pnl_r[i] += (price_r[i] - b_px) * matched
                                                matched_indices.append(str(b_idx))
                                                matched_prices.append(b_px)
                                                total_matched += matched
                                                need -= matched
                                                b_rem -= matched
                                                if b_rem == 0:
                                                    exit_time_r[b_idx] = t_r[i]
                                                    buy_q_r.popleft()
                                                else:
                                                    buy_q_r[0][1] = b_rem
                                            net_qty_r[i] = -need
                                            matched_with_r[i] = ";".join(matched_indices)
                                            matched_qty_r[i] = total_matched
                                            if matched_prices:
                                                matched_price_r[i] = np.mean(matched_prices)
                                    for b_idx, b_rem, _ in buy_q_r:
                                        net_qty_r[b_idx] = b_rem

                                total_realized_pnl_r += float(pnl_r.sum())

                            dict1_r[noren_user_r[m]] = total_realized_pnl_r

                        # Display results
                        rows_r = []
                        for user, pnl in dict1_r.items():
                            rows_r.append({
                                "User ID": user,
                                "Realized PNL": pnl
                            })
                        df_realized = pd.DataFrame(rows_r)
                        with st.container():
                            st.markdown('<div class="section-card">', unsafe_allow_html=True)
                            st.subheader("📊 Noren Realized PNL")
                            st.dataframe(
                                df_realized.style.format({
                                    "Realized PNL": "{:.2f}"
                                }).map(
                                    lambda x: "color: #EF4444" if isinstance(x, (int, float)) and x < 0 else "color: #10B981",
                                    subset=["Realized PNL"]
                                ),
                                use_container_width=True,
                                hide_index=True
                            )
                            # Download
                            output_r = io.BytesIO()
                            with pd.ExcelWriter(output_r, engine='xlsxwriter') as writer_r:
                                df_realized.to_excel(writer_r, sheet_name="Noren Realized PNL", index=False)
                            output_r.seek(0)
                            st.download_button(
                                label="Download Noren Realized PNL XLSX",
                                data=output_r,
                                file_name="noren_realized_pnl.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True,
                                key="download_realized"
                            )
                            st.markdown('</div>', unsafe_allow_html=True)

                        st.success("✅ Realized PNL calculation completed!")

                    except Exception as e:
                        st.error(f"❌ An error occurred during realized PNL calculation: {str(e)}")
                        st.exception(e)
            else:
                st.warning("⚠️ Please upload User Settings and Order Book files to proceed.")

    # Footer
    st.markdown('<div class="footer">Powered by Streamlit | Designed for 2025 UX Excellence | Developed by Sahil</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run()
