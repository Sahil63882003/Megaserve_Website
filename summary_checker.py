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
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2 import service_account  # New import for service account

# Configure logging
logging.basicConfig(level=logging.INFO, filename="app.log")
logger = logging.getLogger(__name__)

# ... (Keep your existing CSS markdown here - no changes)

# Handle service account credentials from Streamlit secrets
def get_service_account_credentials():
    """Load service account credentials from Streamlit secrets."""
    try:
        service_account_info = {
            "type": st.secrets["google_service_account"]["type"],
            "project_id": st.secrets["google_service_account"]["project_id"],
            "private_key_id": st.secrets["google_service_account"]["private_key_id"],
            "private_key": st.secrets["google_service_account"]["private_key"],
            "client_email": st.secrets["google_service_account"]["client_email"],
            "client_id": st.secrets["google_service_account"]["client_id"],
            "auth_uri": st.secrets["google_service_account"]["auth_uri"],
            "token_uri": st.secrets["google_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["google_service_account"]["client_x509_cert_url"],
            "universe_domain": st.secrets["google_service_account"].get("universe_domain", "googleapis.com"),
        }
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=[
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/userinfo.email'
            ]
        )
        logger.info("Service account credentials loaded successfully.")
        return credentials
    except Exception as e:
        st.error(f"Failed to load service account credentials: {e}. Check Streamlit secrets configuration.")
        logger.error(f"Service account credentials loading failed: {e}")
        return None

def authenticate_drive():
    """Authenticate with Google Drive using service account (automatic, no manual steps)."""
    credentials = get_service_account_credentials()
    if not credentials:
        st.stop()
    
    try:
        gauth = GoogleAuth()
        gauth.credentials = credentials
        drive = GoogleDrive(gauth)
        logger.info("Authenticated with Google Drive using service account.")
        # Fetch service account email for confirmation (optional)
        st.markdown(f'<div class="success-box">✅ Authenticated as service account: {credentials.service_account_email}</div>', unsafe_allow_html=True)
        return drive
    except Exception as e:
        st.error(f"Google Drive authentication failed: {e}")
        logger.error(f"Authentication failed: {e}")
        st.stop()

# ... (Keep extract_folder_id and check_summary_users functions - no changes)

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

        # Automatic authentication (no button needed; runs on load)
        if st.session_state.drive_client is None:
            with st.spinner("Authenticating with Google Drive (automatic)..."):
                drive_client = authenticate_drive()
                if drive_client:
                    st.session_state.drive_client = drive_client

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
