#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tempfile
import io
import logging
from typing import Dict, List, Set
import streamlit as st
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

# Configure logging
logging.basicConfig(level=logging.INFO, filename="app.log")
logger = logging.getLogger(__name__)

# Ultra-modern UI with 2025 trends: centered content, professional design, clear section separation
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #0A2540;
    --accent: #00D2FF;
    --success: #10B981;
    --warning: #FBBF24;
    --error: #EF4444;
    --body-bg: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
    --body-text: #1E293B;
    --header-bg: linear-gradient(90deg, #1D4ED8 0%, #10B981 100%);
    --header-text: #FFFFFF;
    --metric-bg: rgba(255, 255, 255, 0.9);
    --metric-glass: rgba(255, 255, 255, 0.6);
    --metric-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    --metric-border: 1px solid rgba(203, 213, 225, 0.5);
    --success-bg: linear-gradient(90deg, #10B981 0%, #34D399 100%);
    --success-text: #064E3B;
    --success-border: #10B981;
    --warning-bg: linear-gradient(90deg, #FBBF24 0%, #F59E0B 100%);
    --warning-text: #713F12;
    --warning-border: #FBBF24;
    --error-bg: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
    --error-text: #7F1D1D;
    --error-border: #EF4444;
    --expander-bg: rgba(255, 255, 255, 0.75);
    --footer-bg: rgba(255, 255, 255, 0.95);
    --footer-text: #475569;
    --table-border: #E2E8F0;
    --hover-row-bg: rgba(59, 130, 246, 0.05);
    --divider-bg: linear-gradient(90deg, #3B82F6, #10B981);
    --font-family: 'Poppins', sans-serif;
    --border-radius: 12px;
    --transition: 0.3s ease-in-out;
    --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.06);
    --shadow-dark: 0 4px 12px rgba(0, 0, 0, 0.1);
}

@media (prefers-color-scheme: dark) {
    :root {
        --body-bg: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        --body-text: #E2E8F0;
        --header-bg: linear-gradient(90deg, #1D4ED8 0%, #047857 100%);
        --header-text: #F1F5F9;
        --metric-bg: rgba(30, 41, 59, 0.9);
        --metric-glass: rgba(30, 41, 59, 0.7);
        --metric-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        --metric-border: 1px solid rgba(51, 65, 85, 0.5);
        --success-bg: linear-gradient(90deg, #047857 0%, #065F46 100%);
        --warning-bg: linear-gradient(90deg, #92400E 0%, #78350F 100%);
        --error-bg: linear-gradient(90deg, #B91C1C 0%, #991B1B 100%);
        --footer-bg: rgba(15, 23, 42, 0.95);
        --footer-text: #CBD5E1;
        --hover-row-bg: rgba(59, 130, 246, 0.1);
        --table-border: #475569;
        --divider-bg: linear-gradient(90deg, #1D4ED8, #047857);
    }
}

body, .main, [data-testid="stAppViewContainer"] {
    background: var(--body-bg) !important;
    color: var(--body-text) !important;
    min-height: 100vh;
    font-family: var(--font-family);
    font-size: 16px;
    line-height: 1.5;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
}

.main-header {
    font-size: 2.5rem;
    font-weight: 600;
    background: var(--header-bg);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    padding: 0.5rem 0;
    margin-bottom: 1rem;
    text-align: center;
    animation: fadein 0.5s ease-out;
    max-width: 800px;
}

@keyframes fadein {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

.section-container {
    max-width: 800px;
    width: 100%;
    margin: 0 auto 2rem auto;
    padding: 1.5rem;
    background: var(--metric-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-light);
    backdrop-filter: blur(8px);
    border: var(--metric-border);
}

.section-divider {
    height: 3px;
    background: var(--divider-bg);
    border: none;
    border-radius: 2px;
    margin: 1.5rem 0;
}

.metric-card {
    background: var(--metric-bg);
    border-radius: var(--border-radius);
    color: var(--body-text);
    padding: 1rem;
    margin-bottom: 1rem;
    text-align: center;
    box-shadow: var(--shadow-light);
    backdrop-filter: blur(8px);
    border: var(--metric-border);
    transition: transform var(--transition), box-shadow var(--transition);
    font-size: 0.95rem;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-dark);
}

@keyframes popcard {
    0% { transform: scale(0.98); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

.stButton > button {
    background: var(--header-bg) !important;
    color: var(--header-text) !important;
    border: none;
    border-radius: var(--border-radius) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    box-shadow: var(--shadow-light) !important;
    transition: all var(--transition) !important;
    width: 100%;
    max-width: 400px;
    margin: 0.5rem auto;
    display: block;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-dark) !important;
}

.stButton > button:focus {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

.success-box, .warning-box, .error-box {
    padding: 0.75rem 1rem;
    border-radius: var(--border-radius);
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 0.75rem;
    box-shadow: var(--shadow-light);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-align: left;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.success-box {
    background: var(--success-bg);
    color: var(--success-text);
    border-left: 4px solid var(--success-border);
}
.warning-box {
    background: var(--warning-bg);
    color: var(--warning-text);
    border-left: 4px solid var(--warning-border);
}
.error-box {
    background: var(--error-bg);
    color: var(--error-text);
    border-left: 4px solid var(--error-border);
}

.stExpander {
    border: 1px solid var(--table-border);
    border-radius: var(--border-radius);
    background: var(--expander-bg);
    margin-bottom: 1rem;
    backdrop-filter: blur(6px);
    box-shadow: var(--shadow-light);
    transition: all var(--transition);
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.stExpander:hover {
    box-shadow: var(--shadow-dark);
}

.stExpander > div > div > button {
    background: var(--header-bg) !important;
    color: var(--header-text) !important;
    border-radius: var(--border-radius) !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem !important;
}

.stTextInput > div > div > input {
    border-radius: var(--border-radius);
    border: 1px solid var(--table-border);
    padding: 0.75rem;
    font-size: 0.95rem;
    transition: border-color var(--transition);
    max-width: 800px;
    width: 100%;
    margin: 0 auto;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(0, 210, 255, 0.2);
}

.stFileUploader > div > button {
    background: var(--header-bg) !important;
    color: var(--header-text) !important;
    border-radius: var(--border-radius) !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    max-width: 400px;
    width: 100%;
    margin: 0 auto;
}

/* Enhanced Table Formatting */
[data-testid="stDataFrameResizable"] {
    background: var(--metric-bg) !important;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-light) !important;
    overflow: hidden !important;
    margin-top: 0.75rem !important;
    border: 1px solid var(--table-border);
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.stDataFrame {
    width: 100%;
    border-collapse: separate !important;
    border-spacing: 0;
    table-layout: fixed;
}

th {
    background: var(--header-bg) !important;
    color: var(--header-text) !important;
    font-weight: 500;
    font-size: 0.95rem;
    padding: 0.75rem 1rem !important;
    text-align: left !important;
    border-bottom: 1px solid var(--table-border) !important;
    position: sticky;
    top: 0;
    z-index: 1;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}

td {
    padding: 0.75rem 1rem !important;
    font-size: 0.9rem !important;
    color: var(--body-text) !important;
    border-bottom: 1px solid var(--table-border) !important;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    transition: background-color var(--transition);
}

tr:last-child td {
    border-bottom: none !important;
}

tr:nth-child(even) {
    background: rgba(243, 244, 246, 0.3) !important;
}

tr:hover {
    background: var(--hover-row-bg) !important;
    cursor: pointer;
}

/* Progress bar */
.stProgress > div > div > div > div {
    background: var(--header-bg) !important;
    border-radius: 6px !important;
    transition: width 0.4s ease-in-out;
}

/* Footer */
.footer {
    background: var(--footer-bg) !important;
    padding: 1rem;
    border-top: 1px solid var(--table-border) !important;
    text-align: center;
    font-size: 0.9rem;
    color: var(--footer-text) !important;
    margin-top: 2rem !important;
    border-radius: var(--border-radius) var(--border-radius) 0 0;
    box-shadow: var(--shadow-light) !important;
    max-width: 800px;
    width: 100%;
    margin-left: auto;
    margin-right: auto;
}

/* Animations */
tr, .stExpander, .metric-card {
    animation: fadein 0.5s ease-out;
}

@keyframes fadein {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-thumb {
    background: var(--header-bg);
    border-radius: 3px;
}

::-webkit-scrollbar-track {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# Handle client secrets securely
def get_client_secrets():
    """Load client secrets from Streamlit secrets."""
    try:
        client_config = {
            "installed": {
                "client_id": st.secrets["google"]["client_id"],
                "project_id": st.secrets["google"]["project_id"],
                "auth_uri": st.secrets["google"]["auth_uri"],
                "token_uri": st.secrets["google"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
                "client_secret": st.secrets["google"]["client_secret"],
                "redirect_uris": st.secrets["google"]["redirect_uris"]
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(client_config, f)
            temp_path = f.name
        logger.info(f"Created temporary client secrets file: {temp_path}")
        return temp_path
    except Exception as e:
        st.error(f"Client secrets loading failed: {e}. Please configure in Streamlit secrets.")
        logger.error(f"Client secrets loading failed: {e}")
        return None

def extract_folder_id(drive_link: str) -> str:
    """Extract folder ID from Google Drive link."""
    m = re.search(r"(?:folders/|id=)([a-zA-Z0-9_-]+)", drive_link)
    if not m:
        st.markdown('<div class="error-box">❌ Invalid Google Drive folder link.</div>', unsafe_allow_html=True)
        logger.error(f"Invalid Google Drive folder link: {drive_link}")
        st.stop()
    return m.group(1)

def check_summary_users(drive: GoogleDrive, folder_id: str, ref_lookup: Dict[str, Dict[str, List[str]]], results_container) -> None:
    logger.info(f"Starting validation for folder ID: {folder_id}")
    progress_bar = results_container.progress(0.0)
    status_text = results_container.empty()
    try:
        root_folder = drive.CreateFile({"id": folder_id})
        root_folder.FetchMetadata(fields="title,permissions")
        logger.info(f"Processing folder: {root_folder['title']}")
        permissions = root_folder.get("permissions", [])
        logger.info(f"Folder Permissions: {permissions}")
        with results_container.expander("🔍 Debug: Folder Permissions"):
            st.json(permissions)
        status_text.text("Fetching folder structure...")
        progress_bar.progress(0.1)
    except Exception as e:
        error_msg = f"Failed to access folder: {str(e)}"
        if "insufficient permissions" in str(e).lower():
            error_msg += " Ensure the folder is shared with the authenticated account."
        results_container.markdown(f'<div class="error-box">❌ {error_msg}</div>', unsafe_allow_html=True)
        logger.error(f"Failed to access folder {folder_id}: {e}")
        return

    children = drive.ListFile({"q": f"'{folder_id}' in parents and trashed=false"}).GetList()
    folder_map = {f["title"].lower(): f["id"] for f in children if f["mimeType"] == "application/vnd.google-apps.folder"}
    if "summary" not in folder_map:
        results_container.markdown('<div class="warning-box">⚠️ No "summary" sub-folder found.</div>', unsafe_allow_html=True)
        logger.warning(f"No 'summary' sub-folder found in folder {folder_id}")
        return

    summary_id = folder_map["summary"]
    summary_files = drive.ListFile({"q": f"'{summary_id}' in parents and trashed=false"}).GetList()
    excel_files = [f for f in summary_files if f["title"].lower().endswith((".xlsx", ".xls"))]
    if not excel_files:
        results_container.markdown('<div class="warning-box">⚠️ No Excel files found in "summary" folder.</div>', unsafe_allow_html=True)
        logger.warning(f"No Excel files found in 'summary' folder {summary_id}")
        return
    results_container.markdown(f'<div class="success-box">Found {len(excel_files)} Excel files to analyze.</div>', unsafe_allow_html=True)

    all_results = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        for idx, file_meta in enumerate(excel_files):
            title = file_meta["title"]
            status_text.text(f"Processing {title} ({idx+1}/{len(excel_files)})...")
            progress_value = 0.15 + (0.85 * (idx / max(len(excel_files), 1)))
            progress_bar.progress(min(progress_value, 1.0))
            local_path = os.path.join(tmp_dir, title)
            try:
                file_meta.GetContentFile(local_path)
                logger.info(f"Downloaded file: {title}")
            except Exception as e:
                results_container.markdown(f'<div class="error-box">❌ Download failed for {title}: {e}</div>', unsafe_allow_html=True)
                logger.error(f"Download failed for {title}: {e}")
                continue
            try:
                xl = pd.read_excel(local_path, sheet_name=None, engine="openpyxl")
            except Exception as e:
                results_container.markdown(f'<div class="error-box">❌ Could not read {title}: {e}</div>', unsafe_allow_html=True)
                logger.error(f"Could not read {title}: {e}")
                continue
            users_sheet_name = next((name for name in xl if name.strip().lower() == "users"), None)
            if not users_sheet_name:
                logger.warning(f"No 'Users' sheet found in {title}")
                continue
            users_df = xl[users_sheet_name]
            users_df_columns = [col.lower() for col in users_df.columns]
            if "userid" not in users_df_columns:
                logger.warning(f"No 'UserID' column found in 'Users' sheet of {title}")
                continue
            userid_col = users_df.columns[users_df_columns.index("userid")]
            algo_col = users_df.columns[users_df_columns.index("algo")] if "algo" in users_df_columns else None
            server_col = users_df.columns[users_df_columns.index("server")] if "server" in users_df_columns else None
            algos = users_df[algo_col].unique() if algo_col else []
            servers = users_df[server_col].unique() if server_col else []
            algo_ok = len(algos) == 1
            server_ok = len(servers) == 1
            multiple_algo_msg = f"File contains {len(algos)} different ALGO values – expected 1." if len(algos) > 1 else None
            multiple_server_msg = f"File contains {len(servers)} different SERVER values – expected 1." if len(servers) > 1 else None
            all_users_set: Set[str] = {str(uid).strip() for uid in users_df[userid_col].dropna()}
            users_count_msg = f"Found {len(all_users_set)} distinct users in '{users_sheet_name}'."
            reference_match = None
            reference_msg = None
            reference_type = None
            ref_algo = None
            ref_server = None
            if len(algos) > 0 and len(servers) > 0:
                ref_algo = str(algos[0])
                ref_server = str(servers[0])
                ref_user_list = ref_lookup.get(ref_algo, {}).get(ref_server, [])
                ref_user_set = set(ref_user_list)
                reference_match = ref_user_set == all_users_set
                match_text = "match" if reference_match else "DO NOT match"
                reference_msg = f"**Reference check (algo={ref_algo}, server={ref_server}):** user lists {match_text}."
                reference_type = 'markdown'
            else:
                reference_msg = "ALGO or SERVER column empty – skipping reference comparison."
                reference_type = 'info'
            file_issues = []
            if not algo_ok:
                file_issues.append("Algo mismatch")
            if not server_ok:
                file_issues.append("Server mismatch")
            if reference_match is not None and not reference_match:
                file_issues.append("Reference mismatch")
            skipped_sheets = []
            sheet_results = {}
            sheet_issue_count = 0
            for sheet_name, sheet_df in xl.items():
                if sheet_name == users_sheet_name:
                    continue
                sheet_df_columns = [col.lower() for col in sheet_df.columns]
                if "user id" not in sheet_df_columns:
                    skipped_sheets.append(sheet_name)
                    continue
                user_id_col = sheet_df.columns[sheet_df_columns.index("user id")]
                present_set: Set[str] = {str(uid).strip() for uid in sheet_df[user_id_col].dropna()}
                missing = sorted(all_users_set - present_set)
                extra = sorted(present_set - all_users_set)
                if missing or extra:
                    sheet_issue_count += 1
                    file_issues.append(f"{sheet_name}: missing {', '.join(missing)}; extra {', '.join(extra)}")
                status = "✅ All match" if not (missing or extra) else "❌ Issue"
                sheet_results[sheet_name] = {"status": status, "missing": missing, "extra": extra}
            total_issues = len(file_issues)
            algo_str = ref_algo if algo_ok else ", ".join(map(str, algos))
            server_str = ref_server if server_ok else ", ".join(map(str, servers))
            all_results.append({
                "File": title,
                "Algo": algo_str,
                "Server": server_str,
                "Algo OK": algo_ok,
                "Server OK": server_ok,
                "Reference Match": reference_match if reference_match is not None else "N/A",
                "Sheet Issues": sheet_issue_count,
                "Total Issues": total_issues,
                "Issues Details": ", ".join(file_issues) if file_issues else "None",
                "multiple_algo_msg": multiple_algo_msg,
                "multiple_server_msg": multiple_server_msg,
                "users_count_msg": users_count_msg,
                "reference_msg": reference_msg,
                "reference_type": reference_type,
                "skipped_sheets": skipped_sheets,
                "sheet_results": sheet_results
            })
            logger.info(f"Processed file {title}: {total_issues} issues found")

        # Final progress
        progress_bar.progress(1.0)
        status_text.text("Analysis complete!")
        logger.info("Analysis completed")

        # Summary Table with dynamic glass style
        with results_container.container():
            st.markdown("""
            <div style='font-size:1.5rem;padding-bottom:0.5rem;background:linear-gradient(90deg,#1D4ED8,#10B981);background-clip:text;-webkit-background-clip:text;color:transparent;font-weight:600;letter-spacing:0.02em;text-align:center;'>
            📈 Summary Report
            </div>
            """, unsafe_allow_html=True)
            summary_df = pd.DataFrame(all_results)
            def highlight_errors(row):
                styles = [''] * len(row)
                if not row['Algo OK']:
                    styles[summary_df.columns.get_loc('Algo OK')] = 'background: var(--error-bg);color:var(--error-text);font-weight:500;'
                if not row['Server OK']:
                    styles[summary_df.columns.get_loc('Server OK')] = 'background: var(--error-bg);color:var(--error-text);font-weight:500;'
                if row['Reference Match'] == False:
                    styles[summary_df.columns.get_loc('Reference Match')] = 'background: var(--error-bg);color:var(--error-text);font-weight:500;'
                if row['Sheet Issues'] > 0:
                    styles[summary_df.columns.get_loc('Sheet Issues')] = 'background: var(--warning-bg);color:var(--warning-text);font-weight:500;'
                if row['Total Issues'] > 0:
                    styles[summary_df.columns.get_loc('Total Issues')] = 'background: var(--error-bg);color:var(--error-text);font-weight:500;'
                return styles

            styled_df = summary_df.style.apply(highlight_errors, axis=1).set_table_styles(
                [
                    {'selector': 'th', 'props': [
                        ('background', 'var(--header-bg)'),
                        ('color', 'var(--header-text)'),
                        ('font-weight', '500'),
                        ('padding', '0.75rem 1rem'),
                        ('text-align', 'left'),
                        ('font-size', '0.95rem'),
                        ('position', 'sticky'),
                        ('top', '0'),
                        ('z-index', '1'),
                        ('white-space', 'nowrap'),
                        ('text-overflow', 'ellipsis'),
                        ('overflow', 'hidden')
                    ]},
                    {'selector': 'td', 'props': [
                        ('padding', '0.75rem 1rem'),
                        ('font-size', '0.9rem'),
                        ('border-bottom', '1px solid var(--table-border)'),
                        ('white-space', 'nowrap'),
                        ('text-overflow', 'ellipsis'),
                        ('overflow', 'hidden')
                    ]},
                    {'selector': 'tr:nth-child(even)', 'props': [('background-color', 'rgba(243,244,246,0.3)')]},
                    {'selector': 'tr:hover', 'props': [('background', 'var(--hover-row-bg)')]},
                ]
            ).set_properties(**{
                'border': '1px solid var(--table-border)',
                'border-radius': 'var(--border-radius)',
                'background': 'var(--metric-bg)'
            })
            
            st.dataframe(styled_df, use_container_width=True, height=400)

            total_files = len(all_results)
            ok_files = sum(1 for r in all_results if r["Total Issues"] == 0)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="metric-card"><span style="font-size:1.25rem;"><b>Files Processed</b></span><br>{total_files}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><span style="font-size:1.25rem;"><b>Files OK</b></span><br>{ok_files}<br><span style="font-size:0.9rem;color:var(--success-text);">{(ok_files/total_files)*100:.1f}%</span></div>', unsafe_allow_html=True)

            csv_buffer = io.StringIO()
            summary_df.to_csv(csv_buffer, index=False)
            st.download_button(
                "📥 Download Summary CSV",
                csv_buffer.getvalue(),
                file_name="summary_check_report.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Detailed Reports
        with results_container.container():
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("""
            <div style='font-size:1.5rem;padding-bottom:0.5rem;background:linear-gradient(90deg,#10B981,#1D4ED8);background-clip:text;-webkit-background-clip:text;color:transparent;font-weight:600;letter-spacing:0.02em;text-align:center;'>
            🗂 Detailed Reports
            </div>
            """, unsafe_allow_html=True)
            for result in all_results:
                with st.expander(f"Details for {result['File']} ({result['Total Issues']} issues)"):
                    if result['multiple_algo_msg']:
                        st.markdown(f'<div class="warning-box">⚠️ {result["multiple_algo_msg"]}</div>', unsafe_allow_html=True)
                    if result['multiple_server_msg']:
                        st.markdown(f'<div class="warning-box">⚠️ {result["multiple_server_msg"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="success-box">✅ {result["users_count_msg"]}</div>', unsafe_allow_html=True)
                    if result['reference_type'] == 'info':
                        st.markdown(f'<div class="success-box">ℹ️ {result["reference_msg"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="success-box">{result["reference_msg"]}</div>', unsafe_allow_html=True)
                    for s in result['skipped_sheets']:
                        st.markdown(f'<div class="success-box">ℹ️ Skipping sheet "{s}" – no "User ID" column.</div>', unsafe_allow_html=True)
                    for sheet_name, data in result['sheet_results'].items():
                        if data['missing'] or data['extra']:
                            st.markdown(f'<div class="error-box">❌ {sheet_name}: Issue detected</div>', unsafe_allow_html=True)
                            for uid in data['missing']:
                                st.markdown(f'<div class="error-box">🔍 User {uid} missing in sheet "{sheet_name}".</div>', unsafe_allow_html=True)
                            for uid in data['extra']:
                                st.markdown(f'<div class="warning-box">⚠️ User {uid} present in sheet "{sheet_name}" but not in Users sheet.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="success-box">✅ All users match in sheet "{sheet_name}".</div>', unsafe_allow_html=True)

def main_app():
    # Main header
    st.markdown('<h1 class="main-header">🔍 Google Drive Summary Checker</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;font-family:var(--font-family);font-size:1rem;color:var(--body-text);margin-bottom:1.5rem;max-width:800px;">
        Upload your <b>reference CSV</b>, provide a <b>Google Drive folder link</b>, and validate user mappings with a sleek, modern interface.
    </div>
    """, unsafe_allow_html=True)

    # Configuration Section
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:1.5rem;padding-bottom:0.5rem;background:linear-gradient(90deg,#1D4ED8,#10B981);background-clip:text;-webkit-background-clip:text;color:transparent;font-weight:600;letter-spacing:0.02em;text-align:center;'>
        🚀 Configuration
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="font-family:var(--font-family);font-size:0.95rem;color:var(--body-text);text-align:center;">Set up your CSV and Google Drive details below.</div>', unsafe_allow_html=True)

        # Step 1: Upload CSV
        uploaded_csv = st.file_uploader(
            "📁 Upload Reference CSV (e.g., running-users)",
            type="csv",
            help="Upload a CSV file containing algo, server, and userid columns.",
            key="csv_upload"
        )

        if uploaded_csv is None:
            st.markdown('<div class="warning-box">⚠️ Please upload the reference CSV to proceed.</div>', unsafe_allow_html=True)
            st.stop()

        # Read CSV and build lookup
        with st.spinner("Processing CSV..."):
            try:
                df = pd.read_csv(uploaded_csv)
                if df.empty:
                    st.error("Uploaded CSV is empty.")
                    logger.error("Uploaded CSV is empty")
                    st.stop()
                df_columns = [col.lower() for col in df.columns]
                required_columns = ["algo", "server", "userid"]
                if not all(col in df_columns for col in required_columns):
                    st.error(f"Reference CSV must contain {', '.join(required_columns)} columns (case-insensitive).")
                    logger.error(f"Reference CSV missing required columns: {required_columns}")
                    st.stop()
            except Exception as e:
                st.error(f"Failed to process CSV: {e}")
                logger.error(f"CSV processing failed: {e}")
                st.stop()
        st.markdown('<div class="success-box">✅ CSV uploaded successfully!</div>', unsafe_allow_html=True)

        ref_lookup: Dict[str, Dict[str, List[str]]] = {
            algo: {
                srv: grp[df.columns[df_columns.index("userid")]].astype(str).str.strip().tolist()
                for srv, grp in algo_grp.groupby(df.columns[df_columns.index("server")])
            }
            for algo, algo_grp in df.groupby(df.columns[df_columns.index("algo")])
        }

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Data Overview Section
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:1.5rem;padding-bottom:0.5rem;background:linear-gradient(90deg,#10B981,#1D4ED8);background-clip:text;-webkit-background-clip:text;color:transparent;font-weight:600;letter-spacing:0.02em;text-align:center;'>
        📊 Data Overview
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><span style="font-size:1.25rem;"><b>Total Algos</b></span><br>{len(ref_lookup)}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><span style="font-size:1.25rem;"><b>Total Servers</b></span><br>{sum(len(s) for s in ref_lookup.values())}</div>', unsafe_allow_html=True)
        with col3:
            total_users = sum(len(u) for s in ref_lookup.values() for u in s.values())
            st.markdown(f'<div class="metric-card"><span style="font-size:1.25rem;"><b>Total Users</b></span><br>{total_users}</div>', unsafe_allow_html=True)

        with st.expander("👁 Preview Reference Data"):
            st.dataframe(df.head(10), use_container_width=True, height=300)

        # Step 2: Drive Folder Link
        folder_link = st.text_input(
            "🔗 Google Drive Folder Link",
            placeholder="https://drive.google.com/drive/folders/ABC123...",
            help="Paste the shareable link to your Google Drive folder.",
            key="folder_link"
        )

        if not folder_link:
            st.markdown('<div class="warning-box">⚠️ Please enter the Drive folder link.</div>', unsafe_allow_html=True)
            st.stop()

        fid = extract_folder_id(folder_link)
        st.markdown(f'<div class="success-box">✅ Folder ID extracted: {fid}</div>', unsafe_allow_html=True)

        # Initialize session state for auth
        if "drive_client" not in st.session_state:
            st.session_state.drive_client = None
        if "auth_step" not in st.session_state:
            st.session_state.auth_step = "initial"
        if "gauth" not in st.session_state:
            st.session_state.gauth = None
        if "client_json" not in st.session_state:
            st.session_state.client_json = None

        # Authenticate logic
        if st.session_state.drive_client is None:
            if st.session_state.auth_step == "initial":
                if st.button("🔑 Authenticate Google Drive", type="primary"):
                    client_json = get_client_secrets()
                    if not client_json or not os.path.isfile(client_json):
                        st.error("Client secrets file not found. Check configuration.")
                        logger.error("Client secrets file not found.")
                        st.stop()
                    st.session_state.client_json = client_json
                    gauth = GoogleAuth()
                    gauth.settings['client_config_file'] = client_json
                    gauth.settings['oauth_scope'] = [
                        'https://www.googleapis.com/auth/drive.readonly',
                        'https://www.googleapis.com/auth/userinfo.email'
                    ]
                    gauth.LoadClientConfigFile(client_json)
                    gauth.flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    auth_url = gauth.GetAuthUrl()
                    st.session_state.gauth = gauth
                    st.markdown(f'<div class="success-box">Please visit this URL to authorize the app: <a href="{auth_url}" target="_blank">{auth_url}</a></div>', unsafe_allow_html=True)
                    st.session_state.auth_step = "waiting_for_code"
            elif st.session_state.auth_step == "waiting_for_code":
                code = st.text_input("Enter the authorization code here:")
                if st.button("Submit Code", type="primary"):
                    try:
                        gauth = st.session_state.gauth
                        gauth.Auth(code)
                        drive = GoogleDrive(gauth)
                        st.session_state.drive_client = drive
                        # Fetch authenticated user's email
                        credentials = Credentials(
                            token=gauth.credentials.access_token,
                            refresh_token=gauth.credentials.refresh_token,
                            token_uri=gauth.credentials.token_uri,
                            client_id=gauth.credentials.client_id,
                            client_secret=gauth.credentials.client_secret
                        )
                        service = build('oauth2', 'v2', credentials=credentials)
                        user_info = service.userinfo().get().execute()
                        email = user_info.get('email', 'Unknown')
                        logger.info(f"Authenticated as: {email}")
                        st.markdown(f'<div class="success-box">✅ Authenticated as: {email}</div>', unsafe_allow_html=True)
                        os.unlink(st.session_state.client_json)
                        logger.info(f"Deleted temporary client secrets file: {st.session_state.client_json}")
                        st.session_state.auth_step = "complete"
                    except Exception as e:
                        st.error(f"Google Drive authentication failed: {e}")
                        logger.error(f"Authentication failed: {e}")
            st.markdown('<div class="warning-box">⚠️ Complete authentication to proceed.</div>', unsafe_allow_html=True)
            st.stop()

        drive = st.session_state.drive_client

        # Run validation
        if st.button("🚀 Run Validation", type="primary", use_container_width=True):
            with st.container():
                st.markdown('<div class="section-container">', unsafe_allow_html=True)
                check_summary_users(drive, fid, ref_lookup, st)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Stylish Footer
    st.markdown("""
    <div class="footer">
        Developed by <b>Sahil</b> | Designed by <b>Saksham</b> | Built with ❤️ using Streamlit<br>
        <span style="font-size:0.85rem;color:var(--footer-text);">2025 &copy; All Rights Reserved</span>
    </div>
    """, unsafe_allow_html=True)

def run():
    """Main function to run the Google Drive Summary Checker module."""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("❌ Please log in to access this module.")
        logger.error("Access denied: User not logged in")
        st.stop()
    if st.session_state.get('role') != 'admin':
        st.error("❌ Admin access required for this module.")
        logger.error("Access denied: User is not admin")
        st.stop()
    main_app()

if __name__ == "__main__":
    run()
