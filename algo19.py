# import streamlit as st
# import pandas as pd
# import numpy as np
# import re
# import base64
# from io import BytesIO
# import logging
# import openpyxl
# from openpyxl.styles import Alignment, Border, Side, Font
# from datetime import datetime

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Check Streamlit version for compatibility
# try:
#     import streamlit
#     logger.info(f"Streamlit version: {streamlit.__version__}")
# except ImportError:
#     st.error("Streamlit is not installed. Please install it using `pip install streamlit`.")
#     st.stop()

# def run():
#     # Main title and description
#     st.markdown("# Realized PNL for 19")
#     st.write("This tool displays realized profit and loss for 19.")

#     # Enhanced Custom CSS with Tailwind CSS and Animations
#     st.markdown("""
#         <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
#         <style>
#         body {
#             font-family: 'Inter', sans-serif;
#             background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
#         }
#         .stButton>button {
#             background: linear-gradient(45deg, #3b82f6, #60a5fa);
#             color: white;
#             border: none;
#             padding: 0.75rem 1.5rem;
#             border-radius: 0.5rem;
#             font-weight: 600;
#             transition: all 0.3s ease;
#             width: 100%;
#         }
#         .stButton>button:hover {
#             background: linear-gradient(45deg, #2563eb, #3b82f6);
#             transform: translateY(-2px);
#             box-shadow: 0 4px 6px rgba(0,0,0,0.2);
#         }
#         .stDateInput input {
#             border: 2px solid #3b82f6;
#             border-radius: 0.5rem;
#             padding: 0.5rem;
#             background: #ffffff;
#             color: #1f2937;
#             font-size: 1rem;
#             transition: all 0.3s ease;
#         }
#         .stDateInput input:focus {
#             outline: none;
#             border-color: #2563eb;
#             box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
#             background: #f8fafc;
#         }
#         .stFileUploader button {
#             background: linear-gradient(45deg, #10b981, #34d399);
#             color: white;
#             border-radius: 0.5rem;
#             padding: 0.75rem;
#         }
#         .stFileUploader button:hover {
#             background: linear-gradient(45deg, #059669, #10b981);
#         }
#         .stCheckbox label {
#             font-size: 1rem;
#             color: #1f2937;
#         }
#         .metric-card {
#             background: #ffffff;
#             padding: 1.5rem;
#             border-radius: 0.75rem;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             text-align: center;
#             transition: transform 0.3s ease;
#         }
#         .metric-card:hover {
#             transform: translateY(-5px);
#             box-shadow: 0 6px 12px rgba(0,0,0,0.15);
#         }
#         .metric-label {
#             font-size: 1.1rem;
#             color: #6b7280;
#             margin-bottom: 0.5rem;
#         }
#         .metric-value {
#             font-size: 1.75rem;
#             font-weight: 700;
#         }
#         .stTabs [data-baseweb="tab"] {
#             font-size: 1.1rem;
#             font-weight: 600;
#             padding: 0.75rem 1.5rem;
#             border-radius: 0.5rem;
#             transition: all 0.3s ease;
#         }
#         .stTabs [data-baseweb="tab"]:hover {
#             background: #e5e7eb;
#         }
#         .insights-box {
#             background: #ffffff;
#             padding: 1.5rem;
#             border-radius: 0.5rem;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             margin-top: 1.5rem;
#         }
#         .chart-container {
#             background: #ffffff;
#             padding: 1.5rem;
#             border-radius: 0.75rem;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             margin-bottom: 1.5rem;
#         }
#         .header-text {
#             font-size: 2.25rem;
#             font-weight: 800;
#             color: #1f2937;
#             text-align: center;
#             margin-bottom: 1rem;
#         }
#         .subheader-text {
#             font-size: 1.25rem;
#             color: #4b5563;
#             text-align: center;
#             margin-bottom: 2rem;
#         }
#         footer { visibility: hidden; }
#         </style>
#     """, unsafe_allow_html=True)

#     # Input Section for PNL Dashboard
#     st.markdown('<h1 class="header-text">📈 Ultimate Financial PNL Dashboard</h1>', unsafe_allow_html=True)
#     st.markdown('<p class="subheader-text">Analyze your portfolio with real-time insights, interactive charts, and comprehensive data exports for smarter trading decisions.</p>', unsafe_allow_html=True)

#     st.markdown('<h2 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">📁 Upload Data</h2>', unsafe_allow_html=True)
#     with st.container():
#         positions_file = st.file_uploader("Positions CSV", type="csv", help="Upload VS20 22 AUG 2025 POSITIONS(EOD).csv", key="positions_upload")

#         # Create two columns for the checkboxes (same row)
#         checkbox_col1, checkbox_col2 = st.columns(2)

#         with checkbox_col1:
#             include_settlement_nfo = st.checkbox(
#                 "Include Settlement PNL for NFO",
#                 value=True,
#                 help="Uncheck to exclude settlement PNL for NFO",
#                 key="nfo_settlement"
#             )

#         with checkbox_col2:
#             include_settlement_bfo = st.checkbox(
#                 "Include Settlement PNL for BFO",
#                 value=True,
#                 help="Uncheck to exclude settlement PNL for BFO",
#                 key="bfo_settlement"
#             )

#         # Layout for file uploaders
#         col1, col2 = st.columns(2)

#         with col1:
#             if include_settlement_nfo:
#                 nfo_bhav_file = st.file_uploader(
#                     "📄 NFO Bhavcopy",
#                     type="csv",
#                     help="Upload op220825.csv",
#                     key="nfo_upload"
#                 )
#             else:
#                 nfo_bhav_file = None
#                 st.info("✅ NFO Bhavcopy not required when settlement PNL for NFO is disabled.")

#         with col2:
#             if include_settlement_bfo:
#                 bfo_bhav_file = st.file_uploader(
#                     "📄 BFO Bhavcopy",
#                     type="csv",
#                     help="Upload MS_20250822-01.csv",
#                     key="bfo_upload"
#                 )
#             else:
#                 bfo_bhav_file = None
#                 st.info("✅ BFO Bhavcopy not required when settlement PNL for BFO is disabled.")

#     st.markdown('<h2 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">📅 Expiry Dates</h2>', unsafe_allow_html=True)
#     with st.container():
#         col3, col4 = st.columns(2)
#         with col3:
#             expiry_nfo = st.date_input("NFO Expiry Date", value=datetime.now().date(), help="Format: YYYY-MM-DD", key="nfo_expiry", disabled=not include_settlement_nfo)
#         with col4:
#             expiry_bfo = st.date_input("BFO Expiry Date", value=datetime.now().date(), help="Format: YYYY-MM-DD", key="bfo_expiry", disabled=not include_settlement_bfo)

#     # Dark theme adjustments
#     if st.session_state.get("theme_select") == "Dark":
#         st.markdown("""
#             <style>
#             body {
#                 background: linear-gradient(135deg, #1f2937, #374151);
#                 color: #f3f4f6;
#             }
#             .stDateInput input {
#                 background: #4b5563;
#                 color: #f3f4f6;
#                 border: 2px solid #60a5fa;
#             }
#             .stDateInput input:focus {
#                 border-color: #3b82f6;
#                 box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
#                 background: #6b7280;
#             }
#             .metric-card, .insights-box, .chart-container {
#                 background: #4b5563;
#             }
#             .metric-label {
#                 color: #d1d5db;
#             }
#             .header-text, .subheader-text {
#                 color: #f3f4f6;
#             }
#             .stTabs [data-baseweb="tab"] {
#                 color: #f3f4f6;
#             }
#             .stTabs [data-baseweb="tab"]:hover {
#                 background: #6b7280;
#             }
#             </style>
#         """, unsafe_allow_html=True)

#     process_button = st.button("🚀 Process Data", key="process_button")

#     if process_button:
#         if positions_file:
#             if (include_settlement_nfo and nfo_bhav_file is None) or (include_settlement_bfo and bfo_bhav_file is None):
#                 st.error("⚠️ Please upload all required CSV files for enabled settlement calculations.")
#             else:
#                 try:
#                     with st.spinner("🔄 Processing your data..."):
#                         results = process_data(positions_file, nfo_bhav_file, bfo_bhav_file, expiry_nfo, expiry_bfo, include_settlement_nfo, include_settlement_bfo)

#                     # Key Metrics Section
#                     st.markdown('<h2 class="text-xl font-bold text-gray-800 dark:text-gray-200 mt-8 mb-4">🔑 Key Financial Metrics</h2>', unsafe_allow_html=True)
#                     col1, col2, col3 = st.columns(3, gap="medium")
#                     with col1:
#                         color = '#34D399' if results["overall_realized"] > 0 else '#F87171' if results["overall_realized"] < 0 else '#9CA3AF'
#                         st.markdown(f'<div class="metric-card"><p class="metric-label">Overall Realized PNL</p><p class="metric-value" style="color:{color};">₹{results["overall_realized"]:,.2f}</p></div>', unsafe_allow_html=True)
#                     if include_settlement_nfo or include_settlement_bfo:
#                         with col2:
#                             color = '#34D399' if results["overall_settlement"] > 0 else '#F87171' if results["overall_settlement"] < 0 else '#9CA3AF'
#                             st.markdown(f'<div class="metric-card"><p class="metric-label">Overall Settlement PNL</p><p class="metric-value" style="color:{color};">₹{results["overall_settlement"]:,.2f}</p></div>', unsafe_allow_html=True)
#                     with col3:
#                         color = '#34D399' if results["grand_total"] > 0 else '#F87171' if results["grand_total"] < 0 else '#9CA3AF'
#                         st.markdown(f'<div class="metric-card"><p class="metric-label">Grand Total PNL</p><p class="metric-value" style="color:{color};">₹{results["grand_total"]:,.2f}</p></div>', unsafe_allow_html=True)

#                     col4, col5, col6, col7 = st.columns(4, gap="medium")
#                     with col4:
#                         color = '#34D399' if results["total_realized_nfo"] > 0 else '#F87171' if results["total_realized_nfo"] < 0 else '#9CA3AF'
#                         st.markdown(f'<div class="metric-card"><p class="metric-label">NFO Realized PNL</p><p class="metric-value" style="color:{color};">₹{results["total_realized_nfo"]:,.2f}</p></div>', unsafe_allow_html=True)
#                     if include_settlement_nfo:
#                         with col5:
#                             color = '#34D399' if results["total_settlement_nfo"] > 0 else '#F87171' if results["total_settlement_nfo"] < 0 else '#9CA3AF'
#                             st.markdown(f'<div class="metric-card"><p class="metric-label">NFO Settlement PNL</p><p class="metric-value" style="color:{color};">₹{results["total_settlement_nfo"]:,.2f}</p></div>', unsafe_allow_html=True)
#                     with col6:
#                         color = '#34D399' if results["total_realized_bfo"] > 0 else '#F87171' if results["total_realized_bfo"] < 0 else '#9CA3AF'
#                         st.markdown(f'<div class="metric-card"><p class="metric-label">BFO Realized PNL</p><p class="metric-value" style="color:{color};">₹{results["total_realized_bfo"]:,.2f}</p></div>', unsafe_allow_html=True)
#                     if include_settlement_bfo:
#                         with col7:
#                             color = '#34D399' if results["total_settlement_bfo"] > 0 else '#F87171' if results["total_settlement_bfo"] < 0 else '#9CA3AF'
#                             st.markdown(f'<div class="metric-card"><p class="metric-label">BFO Settlement PNL</p><p class="metric-value" style="color:{color};">₹{results["total_settlement_bfo"]:,.2f}</p></div>', unsafe_allow_html=True)

#                     # Download Results
#                     st.markdown('<h2 class="text-xl font-bold text-gray-800 dark:text-gray-200 mt-8 mb-4">📥 Download Results</h2>', unsafe_allow_html=True)
#                     col_download1 = st.columns(1)[0]
#                     with col_download1:
#                         pnl_breakdown_df = pd.DataFrame({
#                             'Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
#                             'NFO Realized PNL': [results["total_realized_nfo"]],
#                             'NFO Settlement PNL': [results["total_settlement_nfo"] if include_settlement_nfo else 0],
#                             'Nfo total': [results["total_realized_nfo"] + (results["total_settlement_nfo"] if include_settlement_nfo else 0)],
#                             'BFO Realized PNL': [results["total_realized_bfo"]],
#                             'BFO Settlement PNL': [results["total_settlement_bfo"] if include_settlement_bfo else 0],
#                             'BFO total': [results["total_realized_bfo"] + (results["total_settlement_bfo"] if include_settlement_bfo else 0)],
#                             'Grand Total PNL': [results["grand_total"]]
#                         })
#                         st.markdown(get_excel_download_link(pnl_breakdown_df, "A19_data"), unsafe_allow_html=True)
#                         st.success("✅ PNL data processed successfully!")

#                 except Exception as e:
#                     logger.error(f"Error in process_data: {str(e)}")
#                     st.error(f"⚠️ Error processing data: {str(e)}")
#                     st.info("Please ensure all uploaded CSV files have the correct columns and data format. Check the log for details.")
#         else:
#             st.error("⚠️ Please upload the positions CSV file to proceed.")

#     # Portfolio Analysis Section
#     st.markdown('<hr class="my-8 border-gray-300">', unsafe_allow_html=True)
#     st.markdown('<h1 class="header-text">📊 Portfolio Analysis</h1>', unsafe_allow_html=True)
#     st.markdown('<p class="subheader-text">Upload GridLog and Summary files to analyze portfolio reasons and timestamps.</p>', unsafe_allow_html=True)
#     st.info("Upload the required files below and click 'Process Portfolio Data' to view results.")

#     st.markdown('<h2 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">📁 Upload Portfolio Data</h2>', unsafe_allow_html=True)
#     with st.container():
#         col_grid, col_summary = st.columns(2)
#         with col_grid:
#             gridlog_file = st.file_uploader(
#                 "GridLog File",
#                 type=["csv", "xlsx"],
#                 help="Upload VS20 24 OCT 2025 GridLog.csv or .xlsx",
#                 key="gridlog_upload"
#             )
#         with col_summary:
#             summary_file = st.file_uploader(
#                 "Summary Excel File",
#                 type="xlsx",
#                 help="Upload VS20 24 OCT 2025 SUMMARY.xlsx",
#                 key="summary_upload"
#             )

#     process_portfolio_button = st.button("🚀 Process Portfolio Data", key="process_portfolio_button")

#     if process_portfolio_button:
#         if gridlog_file and summary_file:
#             try:
#                 with st.spinner("🔄 Processing portfolio data..."):
#                     logger.info("Starting portfolio data processing")
#                     final_df = process_portfolio_data(gridlog_file, summary_file)

#                     # Display Results
#                     st.markdown('<h2 class="text-xl font-bold text-gray-800 dark:text-gray-200 mt-8 mb-4">📋 Portfolio Analysis Results</h2>', unsafe_allow_html=True)
#                     st.markdown('<div class="insights-box">', unsafe_allow_html=True)
#                     st.write(final_df)
#                     st.markdown('</div>', unsafe_allow_html=True)
#                     st.success("✅ Portfolio data processed successfully!")

#                     # Download Link
#                     st.markdown('<h2 class="text-xl font-bold text-gray-800 dark:text-gray-200 mt-8 mb-4">📥 Download Portfolio Results</h2>', unsafe_allow_html=True)
#                     output_path = "final_portfolios_with_reason_and_time_24_oct"
#                     st.markdown(get_csv_download_link(final_df, output_path), unsafe_allow_html=True)

#             except Exception as e:
#                 logger.error(f"Error in process_portfolio_data: {str(e)}")
#                 st.error(f"⚠️ Error processing portfolio data: {str(e)}")
#                 st.info("Please ensure the uploaded files have the correct format and columns (e.g., 'Message', 'Option Portfolio', 'Timestamp' for GridLog; 'Exit Type', 'Portfolio Name', 'Exit Time', 'Status' for Summary).")
#         else:
#             st.error("⚠️ Please upload both GridLog and Summary files to proceed.")

# # Function to process portfolio data
# def process_portfolio_data(gridlog_file, summary_file):
#     logger.info("Loading GridLog file")
#     if gridlog_file.name.endswith('.csv'):
#         df_grid = pd.read_csv(gridlog_file)
#     elif gridlog_file.name.endswith('.xlsx'):
#         df_grid = pd.read_excel(gridlog_file)
#     else:
#         raise ValueError("Unsupported GridLog file type. Use CSV or Excel.")

#     logger.info("Cleaning GridLog column names")
#     df_grid.columns = df_grid.columns.str.strip()

#     logger.info("Filtering GridLog for Combined SL/Trail Target messages")
#     mask = df_grid['Message'].str.contains(r'Combined SL:|Combined trail target:', case=False, na=False)
#     filtered_grid = df_grid.loc[mask, ['Message', 'Option Portfolio', 'Timestamp']].dropna(subset=['Option Portfolio'])

#     logger.info("Grouping GridLog results")
#     summary_grid = (
#         filtered_grid.groupby('Option Portfolio').agg({
#             'Message': lambda x: ', '.join(x.unique()),
#             'Timestamp': 'max'
#         }).reset_index()
#         .rename(columns={'Message': 'Reason', 'Timestamp': 'Time'})
#     )

#     logger.info("Processing Summary Excel file")
#     xl = pd.ExcelFile(summary_file)
#     summary_list = []

#     for sheet_name in xl.sheet_names:
#         if "legs" in sheet_name.lower():
#             df_leg = xl.parse(sheet_name)
#             df_leg.columns = df_leg.columns.str.strip()

#             if {'Exit Type', 'Portfolio Name', 'Exit Time'}.issubset(df_leg.columns):
#                 onsqoff_df = df_leg[df_leg['Exit Type'].astype(str).str.strip() == 'OnSqOffTime']
#                 if not onsqoff_df.empty:
#                     grouped = onsqoff_df.groupby('Portfolio Name')['Exit Time'].max().reset_index()
#                     for _, row in grouped.iterrows():
#                         summary_list.append({
#                             'Option Portfolio': row['Portfolio Name'],
#                             'Reason': 'OnSqOffTime',
#                             'Time': row['Exit Time']
#                         })

#     summary_summary = pd.DataFrame(summary_list)

#     logger.info("Combining GridLog and Summary results")
#     final_df = pd.concat([summary_grid, summary_summary], ignore_index=True)
#     final_df = (
#         final_df.groupby('Option Portfolio').agg({
#             'Reason': lambda x: ', '.join(sorted(set(x))),
#             'Time': 'last'
#         }).reset_index()
#     )

#     logger.info("Adding completed portfolios")
#     completed_list = []
#     grid_portfolios = df_grid['Option Portfolio'].dropna().unique()

#     for sheet_name in xl.sheet_names:
#         if "legs" in sheet_name.lower():
#             df_leg = xl.parse(sheet_name)
#             df_leg.columns = df_leg.columns.str.strip()

#             if 'Portfolio Name' in df_leg.columns and 'Status' in df_leg.columns:
#                 for portfolio, group in df_leg.groupby('Portfolio Name'):
#                     if portfolio not in final_df['Option Portfolio'].values and portfolio in grid_portfolios:
#                         statuses = group['Status'].astype(str).str.strip().unique()
#                         if len(statuses) == 1 and statuses[0].lower() == 'completed':
#                             reason_text = 'AllLegsCompleted'
#                             exit_time_to_use = None

#                             if 'Exit Time' in group.columns:
#                                 for exit_time, exit_type in zip(group['Exit Time'], group.get('Exit Type', [])):
#                                     if pd.isna(exit_time):
#                                         continue
#                                     normalized_exit_time = str(exit_time).replace('.', ':').strip()
#                                     matching_rows = df_grid[
#                                         (df_grid['Option Portfolio'] == portfolio) &
#                                         (df_grid['Timestamp'].astype(str).str.contains(normalized_exit_time))
#                                     ]
#                                     if not matching_rows.empty:
#                                         reason_text += f", {exit_type.strip()}"
#                                         exit_time_to_use = exit_time
#                                         break

#                             completed_list.append({
#                                 'Option Portfolio': portfolio,
#                                 'Reason': reason_text,
#                                 'Time': exit_time_to_use
#                             })

#     if completed_list:
#         completed_df = pd.DataFrame(completed_list)
#         final_df = pd.concat([final_df, completed_df], ignore_index=True)

#     logger.info("Cleaning Reason texts")
#     def clean_reason(text):
#         if pd.isna(text):
#             return text
#         text = str(text)
#         match = re.search(r'(Combined SL: [^ ]+ hit|Combined Trail Target: [^ ]+ hit)', text, re.IGNORECASE)
#         if match:
#             return match.group(1)
#         if 'AllLegsCompleted' in text:
#             text = text.replace('AllLegsCompleted,', '').strip()
#             text = text.replace('AllLegsCompleted', '').strip()
#         return text.strip()

#     final_df['Reason'] = final_df['Reason'].apply(clean_reason)

#     logger.info("Cleaning Time column")
#     final_df['Time'] = final_df['Time'].astype(str).str.strip().replace('nan', None)

#     logger.info("Portfolio data processing completed successfully")
#     return final_df

# # Function to process PNL data
# def process_data(positions_file, nfo_bhav_file, bfo_bhav_file, expiry_nfo, expiry_bfo, include_settlement_nfo, include_settlement_bfo):
#     logger.info("Starting PNL data processing")
#     try:
#         df = pd.read_csv(positions_file)
#         logger.info("Positions CSV loaded successfully")

#         required_columns = ['Exchange', 'Symbol', 'Net Qty', 'Buy Avg Price', 'Sell Avg Price', 'Sell Qty', 'Buy Qty', 'Realized Profit', 'Unrealized Profit']
#         missing_columns = [col for col in required_columns if col not in df.columns]
#         if missing_columns:
#             raise ValueError(f"Missing columns in positions file: {missing_columns}")

#         mask = df["Exchange"].isin(["NFO", "BFO"])
#         if 'Symbol' in df.columns:
#             df.loc[mask, "Symbol"] = df.loc[mask, "Symbol"].astype(str).str[-5:] + df.loc[mask, "Symbol"].astype(str).str[-8:-6]
#         else:
#             raise KeyError("Symbol column not found in positions file")

#         df_nfo = df[df["Exchange"] == "NFO"].copy()
#         df_bfo = df[df["Exchange"] == "BFO"].copy()
#         logger.info("Data split into NFO and BFO")

#         total_settlement_pnl_nfo = 0
#         total_settlement_pnl_bfo = 0
#         df_bhav_nfo = pd.DataFrame()
#         df_bhav_bfo = pd.DataFrame()

#         if include_settlement_nfo:
#             if nfo_bhav_file is None:
#                 raise ValueError("NFO bhavcopy file is required when settlement PNL for NFO is enabled")
#             df_bhav_nfo = pd.read_csv(nfo_bhav_file)
#             logger.info("NFO bhavcopy loaded successfully")

#             if 'CONTRACT_D' not in df_bhav_nfo.columns:
#                 raise ValueError("CONTRACT_D column not found in NFO bhavcopy")
#             df_bhav_nfo["Date"] = df_bhav_nfo["CONTRACT_D"].str.extract(r'(\d{2}-[A-Z]{3}-\d{4})')
#             df_bhav_nfo["Symbol"] = df_bhav_nfo["CONTRACT_D"].str.extract(r'^(.*?)(\d{2}-[A-Z]{3}-\d{4})')[0]
#             df_bhav_nfo["Strike_Type"] = df_bhav_nfo["CONTRACT_D"].str.extract(r'(PE\d+|CE\d+)$')
#             df_bhav_nfo["Date"] = pd.to_datetime(df_bhav_nfo["Date"], format="%d-%b-%Y")
#             df_bhav_nfo["Strike_Type"] = df_bhav_nfo["Strike_Type"].str.replace(
#                 r'^(PE|CE)(\d+)$', r'\2\1', regex=True
#             )

#             target_symbol = "OPTIDXNIFTY"
#             df_bhav_nfo = df_bhav_nfo[
#                 (df_bhav_nfo["Date"] == pd.to_datetime(expiry_nfo)) &
#                 (df_bhav_nfo["Symbol"] == target_symbol)
#             ]

#             df_nfo["Strike_Type"] = df_nfo["Symbol"].str.extract(r'(\d+[A-Z]{2})$')
#             df_nfo['Strike'] = df_nfo['Strike_Type'].str[:-2].astype(float, errors='ignore')
#             df_nfo['Option_Type'] = df_nfo['Strike_Type'].str[-2:]

#             df_nfo = df_nfo.merge(
#                 df_bhav_nfo[["Strike_Type", "SETTLEMENT"]],
#                 on="Strike_Type",
#                 how="left"
#             )
#             logger.info("NFO data merged with bhavcopy")

#         if include_settlement_bfo:
#             if bfo_bhav_file is None:
#                 raise ValueError("BFO bhavcopy file is required when settlement PNL for BFO is enabled")
#             df_bhav_bfo = pd.read_csv(bfo_bhav_file)
#             logger.info("BFO bhavcopy loaded successfully")

#             if 'Market Summary Date' not in df_bhav_bfo.columns or 'Expiry Date' not in df_bhav_bfo.columns or 'Series Code' not in df_bhav_bfo.columns:
#                 raise ValueError("Required columns missing in BFO bhavcopy")
#             df_bhav_bfo["Date"] = pd.to_datetime(df_bhav_bfo["Market Summary Date"], format="%d %b %Y", errors="coerce")
#             df_bhav_bfo["Expiry Date"] = pd.to_datetime(df_bhav_bfo["Expiry Date"], format="%d %b %Y", errors="coerce")
#             df_bhav_bfo["Symbols"] = df_bhav_bfo["Series Code"].astype(str).str[-7:]

#             df_bhav_bfo = df_bhav_bfo[
#                 (df_bhav_bfo["Expiry Date"] == pd.to_datetime(expiry_bfo))
#             ]

#             df_bfo["Symbol"] = df_bfo["Symbol"].astype(str).str.strip()
#             df_bhav_bfo["Symbols"] = df_bhav_bfo["Symbols"].astype(str).str.strip()

#             bhav_mapping = df_bhav_bfo.drop_duplicates(subset="Symbols", keep="last").set_index("Symbols")["Close Price"]
#             df_bfo["Close Price"] = df_bfo["Symbol"].map(bhav_mapping)
#             logger.info("BFO data processed")

#         logger.info("Calculating Realized PNL for NFO")
#         conditions = [
#             df_nfo["Net Qty"] == 0,
#             df_nfo["Net Qty"] > 0,
#             df_nfo["Net Qty"] < 0
#         ]
#         choices = [
#             (df_nfo["Sell Avg Price"] - df_nfo["Buy Avg Price"]) * df_nfo["Sell Qty"],
#             (df_nfo["Sell Avg Price"] - df_nfo["Buy Avg Price"]) * df_nfo["Sell Qty"],
#             (df_nfo["Sell Avg Price"] - df_nfo["Buy Avg Price"]) * df_nfo["Buy Qty"]
#         ]
#         df_nfo["Calculated_Realized_PNL"] = np.select(conditions, choices, default=0)
#         df_nfo["Matching_Realized"] = df_nfo["Realized Profit"] == df_nfo["Calculated_Realized_PNL"]
#         df_nfo["Matching_Realized"] = df_nfo["Matching_Realized"].replace({True: "TRUE", False: ""})

#         if include_settlement_nfo:
#             logger.info("Calculating Settlement PNL for NFO")
#             df_nfo["Calculated_Settlement_PNL"] = np.select(
#                 [
#                     df_nfo["Net Qty"] > 0,
#                     df_nfo["Net Qty"] < 0
#                 ],
#                 [
#                     (df_nfo["SETTLEMENT"] - df_nfo["Buy Avg Price"]) * abs(df_nfo["Net Qty"]),
#                     (df_nfo["Sell Avg Price"] - df_nfo["SETTLEMENT"]) * abs(df_nfo["Net Qty"])
#                 ],
#                 default=0
#             )
#             df_nfo["Matching_Settlement"] = df_nfo["Unrealized Profit"] == df_nfo["Calculated_Settlement_PNL"]
#             df_nfo["Matching_Settlement"] = df_nfo["Matching_Settlement"].replace({True: "TRUE", False: ""})
#             total_settlement_pnl_nfo = df_nfo["Calculated_Settlement_PNL"].fillna(0).sum()
#         else:
#             df_nfo["Calculated_Settlement_PNL"] = 0
#             df_nfo["Matching_Settlement"] = ""

#         total_realized_pnl_nfo = df_nfo["Calculated_Realized_PNL"].fillna(0).sum()

#         logger.info("Calculating Realized PNL for BFO")
#         conditions_bfo = [
#             df_bfo["Net Qty"] == 0,
#             df_bfo["Net Qty"] > 0,
#             df_bfo["Net Qty"] < 0
#         ]
#         choices_bfo = [
#             (df_bfo["Sell Avg Price"] - df_bfo["Buy Avg Price"]) * df_bfo["Sell Qty"],
#             (df_bfo["Sell Avg Price"] - df_bfo["Buy Avg Price"]) * df_bfo["Sell Qty"],
#             (df_bfo["Sell Avg Price"] - df_bfo["Buy Avg Price"]) * df_bfo["Buy Qty"]
#         ]
#         df_bfo["Calculated_Realized_PNL"] = np.select(conditions_bfo, choices_bfo, default=0)
#         df_bfo["Matching_Realized"] = df_bfo["Realized Profit"] == df_bfo["Calculated_Realized_PNL"]
#         df_bfo["Matching_Realized"] = df_bfo["Matching_Realized"].replace({True: "TRUE", False: ""})

#         if include_settlement_bfo:
#             logger.info("Calculating Settlement PNL for BFO")
#             long_condition = df_bfo["Net Qty"] > 0
#             df_bfo.loc[long_condition, "Calculated_Settlement_PNL"] = (
#                 (df_bfo["Close Price"] - df_bfo["Buy Avg Price"]) * abs(df_bfo["Net Qty"])
#             )
#             short_condition = df_bfo["Net Qty"] < 0
#             df_bfo.loc[short_condition, "Calculated_Settlement_PNL"] = (
#                 (df_bfo["Sell Avg Price"] - df_bfo["Close Price"]) * abs(df_bfo["Net Qty"])
#             )
#             df_bfo.loc[df_bfo["Net Qty"] == 0, "Calculated_Settlement_PNL"] = 0
#             df_bfo["Matching_Settlement"] = df_bfo["Unrealized Profit"] == df_bfo["Calculated_Settlement_PNL"]
#             df_bfo["Matching_Settlement"] = df_bfo["Matching_Settlement"].replace({True: "TRUE", False: ""})
#             total_settlement_pnl_bfo = df_bfo["Calculated_Settlement_PNL"].fillna(0).sum()
#         else:
#             df_bfo["Calculated_Settlement_PNL"] = 0
#             df_bfo["Matching_Settlement"] = ""

#         total_realized_pnl_bfo = df_bfo["Calculated_Realized_PNL"].fillna(0).sum()

#         overall_realized = total_realized_pnl_nfo + total_realized_pnl_bfo
#         overall_settlement = total_settlement_pnl_nfo + total_settlement_pnl_bfo
#         grand_total = overall_realized + overall_settlement

#         logger.info("PNL data processing completed successfully")
#         return {
#             "df_nfo": df_nfo,
#             "df_bfo": df_bfo,
#             "total_realized_nfo": total_realized_pnl_nfo,
#             "total_settlement_nfo": total_settlement_pnl_nfo,
#             "total_realized_bfo": total_realized_pnl_bfo,
#             "total_settlement_bfo": total_settlement_pnl_bfo,
#             "overall_realized": overall_realized,
#             "overall_settlement": overall_settlement,
#             "grand_total": grand_total
#         }
#     except Exception as e:
#         logger.error(f"Error in process_data: {str(e)}")
#         raise

# # Function to get Excel download link
# def get_excel_download_link(df, filename):
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='PNL Data')
#         worksheet = writer.sheets['PNL Data']
#         for row in worksheet.rows:
#             for cell in row:
#                 cell.alignment = Alignment(horizontal='center')
#         for cell in worksheet[1]:
#             cell.font = Font(bold=True, color="FFFFFF")
#             cell.fill = openpyxl.styles.PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
#         for row in worksheet.rows:
#             for cell in row:
#                 cell.border = Border(left=Side(style='thin'),
#                                     right=Side(style='thin'),
#                                     top=Side(style='thin'),
#                                     bottom=Side(style='thin'))
#     excel_data = output.getvalue()
#     b64 = base64.b64encode(excel_data).decode()
#     return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx" class="text-blue-600 hover:text-blue-800 font-semibold">Download {filename}.xlsx</a>'

# # Function to get CSV download link
# def get_csv_download_link(df, filename):
#     output = BytesIO()
#     df.to_csv(output, index=False)
#     csv_data = output.getvalue()
#     b64 = base64.b64encode(csv_data).decode()
#     return f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv" class="text-blue-600 hover:text-blue-800 font-semibold">Download {filename}.csv</a>'

# # Run the app
# if __name__ == "__main__":
#     st.write(f"DEBUG: Starting Streamlit app at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     run()

import streamlit as st
import pandas as pd
import numpy as np
import re
import base64
from io import BytesIO
import logging
import openpyxl
from openpyxl.styles import Alignment, Border, Side, Font
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== PROFESSIONAL CENTERED UI SETUP ======================
def set_professional_ui():
    st.set_page_config(page_title="Algo 19 Pro", page_icon="📈", layout="centered")

    # Premium CSS with perfect centering, light/dark support, glassmorphism
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
        
        .main {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 2rem 1rem;
        }
        
        /* Light mode support */
        @media (prefers-color-scheme: light) {
            .main { 
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.85) !important;
                border: 1px solid rgba(0, 0, 0, 0.1) !important;
                color: #1e293b !important;
            }
            .header-title { 
                background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
            .header-subtitle, .upload-text, .metric-label { color: #475569 !important; }
            .metric-value { 
                background: linear-gradient(90deg, #10b981, #34d399) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
            .metric-value.red {
                background: linear-gradient(90deg, #ef4444, #f87171) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
        }

        .block-container {
            padding-top: 2rem;
            max-width: 1000px;
            margin: 0 auto;
        }

        .header-title {
            font-size: 4.8rem;
            font-weight: 900;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin: 2rem 0 0.5rem;
            letter-spacing: -3px;
            line-height: 1;
        }

        .header-subtitle {
            font-size: 1.6rem;
            color: #94a3b8;
            text-align: center;
            font-weight: 500;
            margin-bottom: 3rem;
            opacity: 0.9;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 2.5rem;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
            transition: all 0.4s ease;
            margin: 2rem auto;
            max-width: 900px;
        }

        .glass-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(139, 92, 246, 0.4);
        }

        .metric-container {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            transition: all 0.3s ease;
            height: 100%;
        }

        .metric-container:hover {
            background: rgba(255, 255, 255, 0.22);
            transform: translateY(-5px) scale(1.03);
        }

        .metric-label {
            color: #cbd5e1;
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(90deg, #10b981, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metric-value.red {
            background: linear-gradient(90deg, #ef4444, #f87171);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white !important;
            border: none;
            border-radius: 16px;
            padding: 1rem 2.5rem;
            font-weight: 700;
            font-size: 1.2rem;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
            transition: all 0.3s ease;
            width: 100%;
            height: 70px;
            margin: 1rem 0;
        }

        .stButton > button:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 35px rgba(99, 102, 241, 0.6);
            background: linear-gradient(135deg, #7c3aed, #a855f7);
        }

        /* File Uploaders */
        .stFileUploader > div > div {
            background: rgba(255, 255, 255, 0.1);
            border: 2px dashed rgba(255, 255, 255, 0.35);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            transition: all 0.4s;
        }

        .stFileUploader > div > div:hover {
            border-color: #a78bfa;
            background: rgba(167, 139, 250, 0.15);
            transform: scale(1.02);
        }

        .upload-text {
            color: #e2e8f0;
            font-size: 1.15rem;
            font-weight: 500;
            margin-top: 0.5rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
            gap: 1.5rem;
            padding: 0 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            font-size: 1.2rem;
            font-weight: 600;
            padding: 1rem 2rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.1);
            transition: all 0.3s;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            color: white;
        }

        /* Download Link */
        .download-link {
            display: inline-block;
            background: linear-gradient(135deg, #10b981, #34d399);
            color: white;
            padding: 1.2rem 3rem;
            border-radius: 16px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.3rem;
            box-shadow: 0 12px 30px rgba(16, 185, 129, 0.4);
            transition: all 0.3s;
            text-align: center;
        }

        .download-link:hover {
            transform: translateY(-6px);
            box-shadow: 0 20px 40px rgba(16, 185, 129, 0.6);
        }

        /* Center everything */
        .center { text-align: center; }
        .full-center { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            flex-direction: column;
            width: 100%;
        }

        .footer {
            text-align: center;
            color: #64748b;
            font-size: 1rem;
            margin-top: 5rem;
            padding: 2rem;
            opacity: 0.8;
        }

        h3, h4 { text-align: center; color: #e2e8f0; }
        </style>
    """, unsafe_allow_html=True)

def run():
    set_professional_ui()

    # Centered Header
    st.markdown('<div class="full-center">', unsafe_allow_html=True)
    st.markdown('<h1 class="header-title">Algo 19 Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Institutional-Grade Multi-User PNL & Portfolio Exit Intelligence</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["PNL Calculator (Multi-User)", "Portfolio Exit Analyzer"])

    # ==================== TAB 1: PNL ====================
    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Upload Positions File (Must contain `UserID` column)</h3>", unsafe_allow_html=True)
        
        st.markdown("<div class='full-center'>", unsafe_allow_html=True)
        positions_file = st.file_uploader(
            "", 
            type="csv", 
            key="pos",
            label_visibility="collapsed"
        )
        if positions_file:
            st.markdown(f"<p class='upload-text'>Uploaded: <strong>{positions_file.name}</strong></p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='upload-text'>Drag & drop POSITIONS CSV here</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### Settlement Options")
        col1, col2 = st.columns(2)
        with col1:
            include_nfo = st.checkbox("Include NFO Settlement", value=True)
            include_bfo = st.checkbox("Include BFO Settlement", value=True)
        with col2:
            nfo_bhav = st.file_uploader("NFO Bhavcopy", type="csv", key="nfo_bhav") if include_nfo else None
            bfo_bhav = st.file_uploader("BFO Bhavcopy", type="csv", key="bfo_bhav") if include_bfo else None

        col3, col4 = st.columns(2)
        with col3:
            expiry_nfo = st.date_input("NFO Expiry Date", value=datetime(2025, 11, 11), disabled=not include_nfo)
        with col4:
            expiry_bfo = st.date_input("BFO Expiry Date", value=datetime(2025, 11, 13), disabled=not include_bfo)

        st.markdown("<div class='full-center'>", unsafe_allow_html=True)
        if st.button("Process Multi-User PNL", type="primary", use_container_width=True):
            if not positions_file:
                st.error("Please upload POSITIONS file.")
            elif (include_nfo and not nfo_bhav) or (include_bfo and not bfo_bhav):
                st.error("Please upload required bhavcopy files.")
            else:
                with st.spinner("Processing millions of records..."):
                    try:
                        results = process_pnl_multi_user(
                            positions_file, nfo_bhav, bfo_bhav,
                            expiry_nfo, expiry_bfo, include_nfo, include_bfo
                        )
                        display_pnl_results(results)
                    except Exception as e:
                        st.error(f"Error: {e}")
                        logger.error(e)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==================== TAB 2: PORTFOLIO ====================
    with tab2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Upload GridLog & Summary Files</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='full-center'>", unsafe_allow_html=True)
            gridlog_file = st.file_uploader("", type=["csv", "xlsx"], key="grid", label_visibility="collapsed")
            if gridlog_file:
                st.markdown(f"<p class='upload-text'>GridLog: <strong>{gridlog_file.name}</strong></p>", unsafe_allow_html=True)
            else:
                st.markdown("<p class='upload-text'>Upload GridLog (CSV/XLSX)</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='full-center'>", unsafe_allow_html=True)
            summary_file = st.file_uploader("", type="xlsx", key="sum", label_visibility="collapsed")
            if summary_file:
                st.markdown(f"<p class='upload-text'>Summary: <strong>{summary_file.name}</strong></p>", unsafe_allow_html=True)
            else:
                st.markdown("<p class='upload-text'>Upload Summary Excel</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='full-center'>", unsafe_allow_html=True)
        if st.button("Analyze Portfolio Exits", type="primary", use_container_width=True):
            if not gridlog_file or not summary_file:
                st.error("Please upload both files.")
            else:
                with st.spinner("Deep analysis in progress..."):
                    try:
                        final_df = process_portfolio_data(gridlog_file, summary_file)
                        st.success("Analysis Complete!")
                        st.markdown("### Exit Reasons & Timestamps")
                        st.dataframe(final_df, use_container_width=True)
                        st.markdown(get_csv_download_link(final_df, "Portfolio_Exit_Analysis"), unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div class='footer'>
            <p>Algo 19 Pro
     © 2025 | Institutional Trading Intelligence Platform</p>
            <p>Powered by Precision • Trusted by Elite Traders</p>
        </div>
    """, unsafe_allow_html=True)

# ====================== PNL PROCESSING (UNCHANGED) ======================
def process_pnl_multi_user(pos_file, nfo_bhav_file, bfo_bhav_file, expiry_nfo, expiry_bfo, inc_nfo, inc_bfo):
    df = pd.read_csv(pos_file)
    if 'UserID' not in df.columns:
        raise ValueError("UserID column missing!")

    mask = df["Exchange"].isin(["NFO", "BFO"])
    df.loc[mask, "Symbol"] = df.loc[mask, "Symbol"].astype(str).str.extract(r'(\d{5}[CP]\d*)')[0]

    df_bhav_nfo = pd.DataFrame()
    df_bhav_bfo = pd.DataFrame()
    bhav_map = {}

    if inc_nfo and nfo_bhav_file:
        df_bhav_nfo = pd.read_csv(nfo_bhav_file)
        df_bhav_nfo["Date"] = pd.to_datetime(df_bhav_nfo["CONTRACT_D"].str.extract(r'(\d{2}-[A-Z]{3}-\d{4})')[0], format="%d-%b-%Y")
        df_bhav_nfo["Strike_Type"] = df_bhav_nfo["CONTRACT_D"].str.extract(r'(PE\d+|CE\d+)$')[0].str.replace(r'^(PE|CE)(\d+)$', r'\2\1', regex=True)
        df_bhav_nfo = df_bhav_nfo[(df_bhav_nfo["Date"] == pd.to_datetime(expiry_nfo)) & (df_bhav_nfo["CONTRACT_D"].str.contains("NIFTY"))]

    if inc_bfo and bfo_bhav_file:
        df_bhav_bfo = pd.read_csv(bfo_bhav_file)
        df_bhav_bfo["Expiry Date"] = pd.to_datetime(df_bhav_bfo["Expiry Date"], format="%d %b %Y", errors='coerce')
        df_bhav_bfo = df_bhav_bfo[df_bhav_bfo["Expiry Date"] == pd.to_datetime(expiry_bfo)]
        bhav_map = df_bhav_bfo.drop_duplicates("Series Code").set_index("Series Code")["Close Price"]

    all_results = {}
    summary_rows = []

    for user in df['UserID'].unique():
        user_df = df[df['UserID'] == user].copy()
        nfo_df = user_df[user_df["Exchange"] == "NFO"].copy()
        bfo_df = user_df[user_df["Exchange"] == "BFO"].copy()

        realized_nfo = realized_bfo = settlement_nfo = settlement_bfo = 0

        if not nfo_df.empty:
            nfo_df["Strike_Type"] = nfo_df["Symbol"].str.extract(r'(\d+[A-Z]{2})$')[0]
            conditions = [nfo_df["Net Qty"] == 0, nfo_df["Net Qty"] > 0, nfo_df["Net Qty"] < 0]
            choices = [
                (nfo_df["Sell Avg Price"] - nfo_df["Buy Avg Price"]) * nfo_df["Sell Qty"],
                (nfo_df["Sell Avg Price"] - nfo_df["Buy Avg Price"]) * nfo_df["Sell Qty"],
                (nfo_df["Sell Avg Price"] - nfo_df["Buy Avg Price"]) * nfo_df["Buy Qty"]
            ]
            nfo_df["Calc_Realized"] = np.select(conditions, choices, 0)
            realized_nfo = nfo_df["Calc_Realized"].sum()

            if inc_nfo and not df_bhav_nfo.empty:
                nfo_df = nfo_df.merge(df_bhav_nfo[["Strike_Type", "SETTLEMENT"]], on="Strike_Type", how="left")
                nfo_df["Calc_Settlement"] = np.where(
                    nfo_df["Net Qty"] > 0,
                    (nfo_df["SETTLEMENT"] - nfo_df["Buy Avg Price"]) * nfo_df["Net Qty"],
                    np.where(nfo_df["Net Qty"] < 0,
                             (nfo_df["Sell Avg Price"] - nfo_df["SETTLEMENT"]) * (-nfo_df["Net Qty"]), 0)
                )
                settlement_nfo = nfo_df["Calc_Settlement"].fillna(0).sum()
            else:
                nfo_df["Calc_Settlement"] = 0

        if not bfo_df.empty:
            conditions_b = [bfo_df["Net Qty"] == 0, bfo_df["Net Qty"] > 0, bfo_df["Net Qty"] < 0]
            choices_b = [
                (bfo_df["Sell Avg Price"] - bfo_df["Buy Avg Price"]) * bfo_df["Sell Qty"],
                (bfo_df["Sell Avg Price"] - bfo_df["Buy Avg Price"]) * bfo_df["Sell Qty"],
                (bfo_df["Sell Avg Price"] - bfo_df["Buy Avg Price"]) * bfo_df["Buy Qty"]
            ]
            bfo_df["Calc_Realized"] = np.select(conditions_b, choices_b, 0)
            realized_bfo = bfo_df["Calc_Realized"].sum()

            if inc_bfo and not df_bhav_bfo.empty:
                bfo_df["Close"] = bfo_df["Symbol"].map(bhav_map)
                bfo_df["Calc_Settlement"] = 0
                long = bfo_df["Net Qty"] > 0
                short = bfo_df["Net Qty"] < 0
                bfo_df.loc[long, "Calc_Settlement"] = (bfo_df["Close"] - bfo_df["Buy Avg Price"]) * bfo_df["Net Qty"]
                bfo_df.loc[short, "Calc_Settlement"] = (bfo_df["Sell Avg Price"] - bfo_df["Close"]) * (-bfo_df["Net Qty"])
                settlement_bfo = bfo_df["Calc_Settlement"].fillna(0).sum()
            else:
                bfo_df["Calc_Settlement"] = 0

        total = realized_nfo + realized_bfo + settlement_nfo + settlement_bfo
        summary_rows.append({
            "UserID": user,
            "Realized PNL": realized_nfo + realized_bfo,
            "Settlement PNL": settlement_nfo + settlement_bfo,
            "Total PNL": total
        })

        all_results[user] = {
            "nfo": nfo_df.assign(UserID=user),
            "bfo": bfo_df.assign(UserID=user)
        }

    summary_df = pd.DataFrame(summary_rows)
    return {
        "detailed": all_results,
        "summary": summary_df,
        "total_realized": summary_df["Realized PNL"].sum(),
        "total_settlement": summary_df["Settlement PNL"].sum(),
        "grand_total": summary_df["Total PNL"].sum()
    }

# ====================== DISPLAY RESULTS (CENTERED) ======================
def display_pnl_results(results):
    st.success("Processing Complete – All Users Analyzed!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Total Realized</div>
                <div class="metric-value {'red' if results["total_realized"] < 0 else ''}">₹{results["total_realized"]:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Settlement PNL</div>
                <div class="metric-value {'red' if results["total_settlement"] < 0 else ''}">₹{results["total_settlement"]:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Grand Total</div>
                <div class="metric-value {'red' if results["grand_total"] < 0 else ''}">₹{results["grand_total"]:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### Per-User PNL Breakdown")
    st.dataframe(
        results["summary"].style.format({
            "Realized PNL": "₹{:,.2f}",
            "Settlement PNL": "₹{:,.2f}",
            "Total PNL": "₹{:,.2f}"
        }).bar(subset=["Total PNL"], color='#8b5cf6'),
        use_container_width=True
    )

    st.markdown("<div class='full-center'>", unsafe_allow_html=True)
    st.markdown(get_multi_user_excel(results["detailed"], results["summary"], "Multi_User_PNL"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ====================== EXCEL & CSV EXPORT ======================
def get_multi_user_excel(detailed, summary, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary.to_excel(writer, sheet_name="SUMMARY", index=False)
        for user, data in detailed.items():
            combined = pd.concat([data["nfo"], data["bfo"]], ignore_index=True)
            export_cols = ['UserID', 'Symbol', 'Net Qty', 'Realized Profit', 'Calc_Realized', 'Unrealized Profit']
            if 'Calc_Settlement' in combined.columns:
                export_cols.append('Calc_Settlement')
            combined = combined[export_cols]
            safe_name = str(user)[:31]
            combined.to_excel(writer, sheet_name=safe_name, index=False)

        for ws_name, ws in writer.sheets.items():
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = openpyxl.styles.PatternFill(start_color="1e40af", fill_type="solid")
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(horizontal='center')
                    cell.border = Border(left=Side('thin'), right=Side('thin'), top=Side('thin'), bottom=Side('thin'))

    b64 = base64.b64encode(output.getvalue()).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx" class="download-link">Download Full Excel Report</a>'

def get_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv" class="download-link">Download {filename}.csv</a>'

# ====================== PORTFOLIO ANALYSIS (UNCHANGED) ======================
def process_portfolio_data(gridlog_file, summary_file):
    if gridlog_file.name.endswith('.csv'):
        df_grid = pd.read_csv(gridlog_file)
    else:
        df_grid = pd.read_excel(gridlog_file)

    df_grid.columns = df_grid.columns.str.strip()
    mask = df_grid['Message'].str.contains(r'Combined SL:|Combined trail target:', case=False, na=False)
    filtered = df_grid.loc[mask, ['Message', 'Option Portfolio', 'Timestamp']].dropna(subset=['Option Portfolio'])

    summary_grid = (
        filtered.groupby('Option Portfolio')
        .agg({'Message': lambda x: ', '.join(x.unique()), 'Timestamp': 'max'})
        .reset_index()
        .rename(columns={'Message': 'Reason', 'Timestamp': 'Time'})
    )

    xl = pd.ExcelFile(summary_file)
    onsqoff_list = []
    for sheet in xl.sheet_names:
        if "legs" in sheet.lower():
            df_leg = xl.parse(sheet)
            df_leg.columns = df_leg.columns.str.strip()
            if {'Exit Type', 'Portfolio Name', 'Exit Time'}.issubset(df_leg.columns):
                onsqoff = df_leg[df_leg['Exit Type'].astype(str).str.strip() == 'OnSqOffTime']
                if not onsqoff.empty:
                    grouped = onsqoff.groupby('Portfolio Name')['Exit Time'].max().reset_index()
                    for _, row in grouped.iterrows():
                        onsqoff_list.append({
                            'Option Portfolio': row['Portfolio Name'],
                            'Reason': 'OnSqOffTime',
                            'Time': row['Exit Time']
                        })

    summary_summary = pd.DataFrame(onsqoff_list)
    final_df = pd.concat([summary_grid, summary_summary], ignore_index=True)
    final_df = final_df.groupby('Option Portfolio').agg({
        'Reason': lambda x: ', '.join(sorted(set(x))),
        'Time': 'last'
    }).reset_index()

    completed = []
    grid_ports = df_grid['Option Portfolio'].dropna().unique()
    for sheet in xl.sheet_names:
        if "legs" in sheet.lower():
            df_leg = xl.parse(sheet)
            df_leg.columns = df_leg.columns.str.strip()
            if 'Portfolio Name' in df_leg.columns and 'Status' in df_leg.columns:
                for port, group in df_leg.groupby('Portfolio Name'):
                    if port not in final_df['Option Portfolio'].values and port in grid_ports:
                        if (group['Status'].astype(str).str.strip() == 'completed').all():
                            reason = 'AllLegsCompleted'
                            time = group['Exit Time'].dropna().iloc[-1] if 'Exit Time' in group.columns and not group['Exit Time'].dropna().empty else None
                            completed.append({'Option Portfolio': port, 'Reason': reason, 'Time': time})

    if completed:
        final_df = pd.concat([final_df, pd.DataFrame(completed)], ignore_index=True)

    def clean(r):
        if pd.isna(r): return r
        m = re.search(r'(Combined SL: [^ ]+ hit|Combined Trail Target: [^ ]+ hit)', r, re.I)
        if m: return m.group(1)
        return r.replace('AllLegsCompleted,', '').replace('AllLegsCompleted', '').strip()

    final_df['Reason'] = final_df['Reason'].apply(clean)
    final_df['Time'] = final_df['Time'].astype(str).str.strip().replace('nan', None)
    return final_df

if __name__ == "__main__":
    run()

