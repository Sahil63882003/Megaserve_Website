import streamlit as st
import pandas as pd
import io
import re
import time
import os
from typing import List, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# Config
APP_TITLE = "User Settings — Compile from Drive & Compare"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_PATH = "token.json"
CLIENT_SECRETS_FILE = "client_secrets.json"
CANONICAL_NAMES = {
    "user alias": "User Alias", "alias": "User Alias", "useralias": "User Alias", "user_alias": "User Alias",
    "user-alias": "User Alias", "user name alias": "User Alias", "name alias": "User Alias", "alisa": "User Alias",
    "user alisa": "User Alias", "user id": "User ID", "userid": "User ID", "user_id": "User ID", "broker": "Broker",
    "max loss": "Max Loss", "maxloss": "Max Loss", "server": "Server", "telegram id(s)": "Telegram ID(s)",
    "telegram ids": "Telegram ID(s)", "telegram id": "Telegram ID(s)", "allocation": "Telegram ID(s)", "algo": "Algo",
    "operator": "Operator"
}
SPECIFIED_ORDER = ["User Alias", "User ID", "Broker", "Max Loss", "Server", "Telegram ID(s)", "Algo"]
COMPARE_COLS = ["User ID", "Max Loss", "Server", "Telegram ID(s)", "Algo"]
SHEET_TO_COMPARE = "Specified_Compiled"
SHEET1_NAME = "Sheet1"

def _norm_header(s: str) -> str:
    s = str(s).replace("\n", " ").replace("\r", " ")
    return " ".join(s.split()).strip()

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        key = _norm_header(col).lower()
        key_compact = key.replace("_", " ").replace("-", " ")
        if key in CANONICAL_NAMES:
            rename_map[col] = CANONICAL_NAMES[key]
        elif key_compact in CANONICAL_NAMES:
            rename_map[col] = CANONICAL_NAMES[key_compact]
        else:
            tight = "".join(key_compact.split())
            if tight in CANONICAL_NAMES:
                rename_map[col] = CANONICAL_NAMES[tight]
    return df.rename(columns=rename_map)

def ensure_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for c in columns:
        if c not in df.columns:
            df[c] = ""
    return df

def to_excel_bytes(sheet_map: dict) -> bytes:
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in sheet_map.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    bio.seek(0)
    return bio.read()

def to_int(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")

def extract_folder_id(link: str) -> str:
    link = link.strip()
    m = re.search(r"/folders/([A-Za-z0-9_\-]+)", link)
    if m: return m.group(1)
    m = re.search(r"[?&]id=([A-Za-z0-9_\-]+)", link)
    if m: return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_\-]{20,}", link): return link
    raise ValueError("Could not extract folder id from the provided link/id.")

def _normalize_column_names(cols: List[str]) -> List[str]:
    return [_norm_header(c) for c in cols]

def authenticate_drive():
    if 'drive_service' in st.session_state:
        return st.session_state['drive_service']
    if "google_token" in st.secrets:
        token_info = dict(st.secrets["google_token"])
        token_info["scopes"] = token_info.get("scopes", SCOPES)
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        if not creds.valid:
            if creds.refresh_token:
                creds.refresh(Request())
            else:
                st.error("google_token has no refresh_token. Recreate token.json with offline access and update Secrets.")
                st.stop()
        service = build('drive', 'v3', credentials=creds)
        st.session_state['drive_service'] = service
        return service
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if not os.path.exists(CLIENT_SECRETS_FILE):
            raise FileNotFoundError(f"Missing '{CLIENT_SECRETS_FILE}'. Provide OAuth client or set [google_token] in Secrets.")
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    st.session_state['drive_service'] = service
    return service

def list_files_in_folder(service, folder_id: str) -> List[dict]:
    files, page_token = [], None
    while True:
        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)",
            pageSize=1000, pageToken=page_token
        ).execute()
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files

def download_csv_as_df(service, file_id: str, skiprows: int = 6) -> pd.DataFrame:
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_csv(fh, skiprows=skiprows)

def read_server_mapping(upload) -> dict:
    if upload is None:
        st.error("Please upload a ServerMapping file (.xlsx or .csv) with columns Server, Operator, Algo.")
        st.stop()
    name = upload.name.lower()
    try:
        if name.endswith(".csv"):
            mdf = pd.read_csv(upload)
        else:
            mdf = pd.read_excel(upload)
    except Exception as e:
        st.error(f"Failed to read mapping file: {e}")
        st.stop()
    mdf.columns = [_norm_header(c) for c in mdf.columns]
    lower = {c.lower(): c for c in mdf.columns}
    required = {"server", "operator", "algo"}
    if not required.issubset(lower.keys()):
        st.error(f"Mapping must contain columns: Server, Operator, Algo. Found: {list(mdf.columns)}")
        st.stop()
    server_col = lower["server"]
    operator_col = lower["operator"]
    algo_col = lower["algo"]
    mdf = mdf[[server_col, operator_col, algo_col]].copy()
    mdf[server_col] = mdf[server_col].astype(str).str.strip()
    mdf[operator_col] = mdf[operator_col].astype(str).str.strip()
    mdf = mdf[mdf[server_col] != ""]
    mapping = {}
    for _, r in mdf.iterrows():
        mapping[r[server_col]] = {"Operator": r[operator_col], "Algo": r[algo_col]}
    if not mapping:
        st.error("Mapping file produced an empty mapping. Please check contents.")
        st.stop()
    return mapping

def process_csv_files(service, files: List[dict], server_map: dict, skiprows: int = 6) -> pd.DataFrame:
    all_data = []
    for f in files:
        if not str(f.get("name", "")).lower().endswith(".csv"):
            continue
        try:
            df = download_csv_as_df(service, f["id"], skiprows=skiprows)
            df = normalize_columns(df)
            server = str(f["name"]).split()[0].strip()
            op = server_map.get(server, {}).get("Operator", "")
            algo = server_map.get(server, {}).get("Algo", "")
            df["Server"] = server
            df["Operator"] = op
            df["Algo"] = str(algo)
            df = ensure_columns(df, ["User Alias", "User ID", "Broker", "Max Loss", "Server", "Telegram ID(s)", "Algo", "Operator"])
            df["Telegram ID(s)"] = to_int(df["Telegram ID(s)"])
            df["Max Loss"] = to_int(df["Max Loss"])
            mask = df["User Alias"].astype(str).str.contains("DEAL|FEED", case=False, na=False)
            df = df[~mask]
            all_data.append(df)
        except Exception as e:
            st.warning(f"Skipping '{f.get('name','?')}' due to error: {e}")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    required = {"User ID", "Server", "Algo", "Operator"}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    summary = df.groupby(['Algo', 'Server', 'Operator'], dropna=False)['User ID'].count().reset_index()
    summary.columns = ['Algo', 'Server', 'Operator', 'Count of User ID']
    grand_total = pd.DataFrame([{
        'Algo': 'Grand Total', 'Server': '', 'Operator': '',
        'Count of User ID': summary['Count of User ID'].sum()
    }])
    return pd.concat([summary, grand_total], ignore_index=True)

def clean_for_compare(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = _normalize_column_names(df.columns)
    missing = [c for c in COMPARE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Sheet '{SHEET_TO_COMPARE}' is missing columns: {missing}")
    df = df[COMPARE_COLS].copy()
    df["User ID"] = df["User ID"].astype(str)
    df["Server"] = df["Server"].astype(str)
    df["Algo"] = df["Algo"].astype(str)
    df["Telegram ID(s)"] = to_int(df["Telegram ID(s)"])
    df["Max Loss"] = to_int(df["Max Loss"])
    df = df.sort_index().drop_duplicates(subset=["User ID"], keep="last").reset_index(drop=True)
    return df

def read_specified_compiled(xlsx_bytes: bytes) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=SHEET_TO_COMPARE, engine="openpyxl")

def read_sheet1_last(xlsx_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=SHEET1_NAME, engine="openpyxl")
    norm_map = {c: _norm_header(c) for c in df.columns}
    df.rename(columns=norm_map, inplace=True)
    lower_to_real = {_norm_header(c).lower(): c for c in df.columns}
    def pick(*names):
        for n in names:
            key = _norm_header(n).lower()
            if key in lower_to_real:
                return lower_to_real[key]
        raise ValueError(f"Missing column in {SHEET1_NAME}: one of {names}")
    col_user = pick("UserID", "User ID", "userid", "user_id")
    col_alloc = pick("ALLOCATION", "Telegram ID(s)", "Telegram IDs", "Telegram ID")
    col_mloss = pick("MAX LOSS", "Max Loss", "maxloss")
    col_server = pick("SERVER", "Server")
    col_algo = pick("ALGO", "Algo")
    out = pd.DataFrame({
        "User ID": df[col_user].astype(str),
        "Max Loss": to_int(df[col_mloss]),
        "Server": df[col_server].astype(str),
        "Telegram ID(s)": to_int(df[col_alloc]),
        "Algo": df[col_algo].astype(str),
    })
    return clean_for_compare(out)

def compare_frames(last_df: pd.DataFrame, latest_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    last_idx = last_df.set_index("User ID")
    latest_idx = latest_df.set_index("User ID")
    last_ids, latest_ids = set(last_idx.index), set(latest_idx.index)
    added_ids = sorted(list(latest_ids - last_ids))
    removed_ids = sorted(list(last_ids - latest_ids))
    common_ids = sorted(list(latest_ids & last_ids))
    cols_out = [
        "User ID", "Change Type",
        "Max Loss (Last)", "Max Loss (Latest)",
        "Server (Last)", "Server (Latest)",
        "Telegram ID(s) (Last)", "Telegram ID(s) (Latest)",
        "Algo (Last)", "Algo (Latest)",
        "Diff Columns",
    ]
    rows = []
    def fmt(v, integer=False):
        if pd.isna(v):
            return ""
        return int(v) if integer else str(v)
    def neq(x, y):
        if pd.isna(x) and pd.isna(y):
            return False
        return x != y
    for uid in added_ids:
        r = latest_idx.loc[uid]
        rows.append([
            uid, "ADDED",
            "", fmt(r["Max Loss"], integer=True),
            "", fmt(r["Server"]),
            "", fmt(r["Telegram ID(s)"], integer=True),
            "", fmt(r["Algo"]),
            "ALL"
        ])
    for uid in removed_ids:
        r = last_idx.loc[uid]
        rows.append([
            uid, "REMOVED",
            fmt(r["Max Loss"], integer=True), "",
            fmt(r["Server"]), "",
            fmt(r["Telegram ID(s)"], integer=True), "",
            fmt(r["Algo"]), "",
            "ALL"
        ])
    for uid in common_ids:
        a, b = last_idx.loc[uid], latest_idx.loc[uid]
        diffs = []
        if neq(a["Max Loss"], b["Max Loss"]):
            diffs.append("Max Loss")
        if neq(a["Server"], b["Server"]):
            diffs.append("Server")
        if neq(a["Telegram ID(s)"], b["Telegram ID(s)"]):
            diffs.append("Telegram ID(s)")
        if neq(a["Algo"], b["Algo"]):
            diffs.append("Algo")
        if diffs:
            rows.append([
                uid, "MODIFIED",
                fmt(a["Max Loss"], integer=True), fmt(b["Max Loss"], integer=True),
                fmt(a["Server"]), fmt(b["Server"]),
                fmt(a["Telegram ID(s)"], integer=True), fmt(b["Telegram ID(s)"], integer=True),
                fmt(a["Algo"]), fmt(b["Algo"]),
                ", ".join(diffs),
            ])
    all_diffs = pd.DataFrame(rows, columns=cols_out)
    return (
        all_diffs[all_diffs["Change Type"] == "ADDED"].reset_index(drop=True),
        all_diffs[all_diffs["Change Type"] == "REMOVED"].reset_index(drop=True),
        all_diffs[all_diffs["Change Type"] == "MODIFIED"].reset_index(drop=True),
        all_diffs.reset_index(drop=True)
    )

def render_modified_with_filters(modified_df: pd.DataFrame):
    st.caption("Use filters to narrow down the Modified rows.")
    if modified_df.empty:
        st.info("No modified rows.")
        return
    diff_tokens = sorted({t.strip() for s in modified_df["Diff Columns"].dropna().astype(str) for t in s.split(",") if t.strip()})
    if not diff_tokens:
        diff_tokens = ["Max Loss", "Server", "Telegram ID(s)", "Algo"]
    servers = sorted(set(modified_df["Server (Last)"].astype(str)) | set(modified_df["Server (Latest)"].astype(str)))
    algos = sorted(set(modified_df["Algo (Last)"].astype(str)) | set(modified_df["Algo (Latest)"].astype(str)))
    def _nan_to_series(col):
        s = pd.to_numeric(modified_df[col], errors="coerce")
        return s.dropna()
    maxloss_last_vals = _nan_to_series("Max Loss (Last)")
    maxloss_latest_vals = _nan_to_series("Max Loss (Latest)")
    tel_last_vals = _nan_to_series("Telegram ID(s) (Last)")
    tel_latest_vals = _nan_to_series("Telegram ID(s) (Latest)")
    with st.expander("Filters", expanded=True):
        fcol1, fcol2, fcol3 = st.columns([1.2, 1, 1])
        with fcol1:
            selected_tokens = st.multiselect("Changed columns include…", diff_tokens, default=diff_tokens)
            user_query = st.text_input("User ID contains", value="")
        with fcol2:
            sel_servers = st.multiselect("Server (Last/Latest)", servers, default=servers)
            sel_algos = st.multiselect("Algo (Last/Latest)", algos, default=algos)
        with fcol3:
            if not maxloss_latest_vals.empty:
                ml_min, ml_max = int(maxloss_latest_vals.min()), int(maxloss_latest_vals.max())
            else:
                ml_min, ml_max = 0, 0
            ml_range = st.slider("Max Loss (Latest) range", min_value=int(ml_min), max_value=int(ml_max) if ml_max >= ml_min else int(ml_min), value=(int(ml_min), int(ml_max)) if ml_max>=ml_min else (int(ml_min), int(ml_min)))
            if not tel_latest_vals.empty:
                tl_min, tl_max = int(tel_latest_vals.min()), int(tel_latest_vals.max())
            else:
                tl_min, tl_max = 0, 0
            tl_range = st.slider("Telegram ID(s) (Latest) range", min_value=int(tl_min), max_value=int(tl_max) if tl_max >= tl_min else int(tl_min), value=(int(tl_min), int(tl_max)) if tl_max>=tl_min else (int(tl_min), int(tl_min)))
    filt = modified_df.copy()
    if selected_tokens and len(selected_tokens) < len(diff_tokens):
        mask = filt["Diff Columns"].apply(lambda s: any(tok in str(s) for tok in selected_tokens))
        filt = filt[mask]
    if user_query.strip():
        q = user_query.strip().lower()
        filt = filt[filt["User ID"].astype(str).str.lower().str.contains(q)]
    if sel_servers and len(sel_servers) < len(servers):
        filt = filt[
            filt["Server (Last)"].astype(str).isin(sel_servers) |
            filt["Server (Latest)"].astype(str).isin(sel_servers)
        ]
    if sel_algos and len(sel_algos) < len(algos):
        filt = filt[
            filt["Algo (Last)"].astype(str).isin(sel_algos) |
            filt["Algo (Latest)"].astype(str).isin(sel_algos)
        ]
    if not filt.empty and (ml_max >= ml_min):
        ml_num = pd.to_numeric(filt["Max Loss (Latest)"], errors="coerce")
        filt = filt[(ml_num.isna()) | ((ml_num >= ml_range[0]) & (ml_num <= ml_range[1]))]
    if not filt.empty and (tl_max >= tl_min):
        tl_num = pd.to_numeric(filt["Telegram ID(s) (Latest)"], errors="coerce")
        filt = filt[(tl_num.isna()) | ((tl_num >= tl_range[0]) & (tl_num <= tl_range[1]))]
    m1, m2 = st.columns(2)
    with m1: st.metric("Rows after filters", len(filt))
    with m2:
        st.caption("Changed columns legend:")
        st.markdown("".join([f"<span class='pill'>{t}</span>" for t in diff_tokens]), unsafe_allow_html=True)
    st.dataframe(filt, use_container_width=True, height=480)
    dl1, dl2 = st.columns(2)
    with dl1:
        xbytes = to_excel_bytes({"Modified_Filtered": filt})
        st.download_button(
            "⬇️ Download filtered Modified (Excel)",
            data=xbytes,
            file_name="modified_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with dl2:
        st.download_button(
            "⬇️ Download filtered Modified (CSV)",
            data=filt.to_csv(index=False).encode(),
            file_name="modified_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )

def run():
    # if st.button("🔙 Back to Dashboard", key="back_dashboard"):
    #     st.session_state.current_page = 'dashboard'
    #     st.rerun()
    # Apply theme-based CSS with system preference detection
    st.markdown("""
        <style>
        .usersetting-container {
            font-family: 'Inter', sans-serif;
            transition: background-color 0.3s ease, color 0.3s ease;
            max-width: 550px;
            margin: 0 auto;
            padding: 2rem;
        }
        .usersetting-container.light-mode {
            background: #F9FAFB;
            color: #1F2937;
        }
        .usersetting-container.dark-mode {
            background: #111827;
            color: #F9FAFB;
        }
        .usersetting-container .app-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: .25rem;
            text-align: center;
        }
        .usersetting-container .app-subtle {
            color: #64748b;
            margin-bottom: 1rem;
            text-align: center;
        }
        .usersetting-container.dark-mode .app-subtle {
            color: #9CA3AF;
        }
        .usersetting-container .stMetric {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 8px 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,.06);
        }
        .usersetting-container.dark-mode .stMetric {
            background: #1F2937;
        }
        .usersetting-container .block-gap {
            margin-top: 12px;
            margin-bottom: 12px;
        }
        .usersetting-container .pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            background: #eef2ff;
            color: #3730a3;
            font-size: 12px;
            margin-right: 6px;
        }
        .usersetting-container.dark-mode .pill {
            background: #4b5563;
            color: #e0e7ff;
        }
        .usersetting-container .bordered-container {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 10px;
            background: #FFFFFF;
            max-width: 510px;
            margin: 0 auto;
        }
        .usersetting-container.dark-mode .bordered-container {
            border: 1px solid #374151;
            background: #1F2937;
        }
        .standard-button, .stButton>button {
            background: linear-gradient(90deg, #10B981, #3B82F6);
            border: none;
            border-radius: 12px;
            padding: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            color: #1F2937;
            width: 100%;
            max-width: 200px;
            margin: 0.5rem auto;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .standard-button:hover, .stButton>button:hover {
            background: linear-gradient(90deg, #047857, #1E40AF);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .stFileUploader, .stTextInput, .stNumberInput {
            background: #F9FAFB;
            border-radius: 12px;
            padding: 0.75rem;
            margin: 0.5rem auto;
            border: 1px solid #D1D5DB;
            max-width: 510px;
            width: 100%;
            transition: all 0.3s ease;
        }
        .usersetting-container.dark-mode .stFileUploader,
        .usersetting-container.dark-mode .stTextInput,
        .usersetting-container.dark-mode .stNumberInput {
            background: #4B5563;
            border: 1px solid #6B7280;
            color: #F9FAFB;
        }
        .stFileUploader:hover, .stTextInput:hover, .stNumberInput:hover {
            border-color: #3B82F6;
            background: #E5E7EB;
            transform: scale(1.02);
        }
        .usersetting-container.dark-mode .stFileUploader:hover,
        .usersetting-container.dark-mode .stTextInput:hover,
        .usersetting-container.dark-mode .stNumberInput:hover {
            background: #6B7280;
        }
        .stFileUploader label, .stTextInput label, .stNumberInput label {
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 0.5rem;
            text-align: center;
            display: block;
        }
        .usersetting-container.dark-mode .stFileUploader label,
        .usersetting-container.dark-mode .stTextInput label,
        .usersetting-container.dark-mode .stNumberInput label {
            color: #F9FAFB;
        }
        .stExpander {
            border: 1px solid #D1D5DB;
            border-radius: 12px;
            max-width: 510px;
            margin: 0.5rem auto;
        }
        .usersetting-container.dark-mode .stExpander {
            border: 1px solid #6B7280;
            background: #2D3748;
        }
        .stExpander summary {
            font-weight: 600;
            text-align: center;
        }
        .stRadio > label {
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        .usersetting-container.dark-mode .stRadio > label {
            color: #F9FAFB;
        }
        .stCaption {
            text-align: center;
            max-width: 510px;
            margin: 0 auto;
        }
        </style>
        <script>
        function applyUsersettingTheme() {
            const container = document.querySelector('.usersetting-container');
            if (container) {
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                container.classList.remove('light-mode', 'dark-mode');
                container.classList.add(prefersDark ? 'dark-mode' : 'light-mode');
            }
        }
        document.addEventListener('DOMContentLoaded', applyUsersettingTheme);
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyUsersettingTheme);
        </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="usersetting-container">', unsafe_allow_html=True)

    # Back to Dashboard button
    # if st.button("🔙 Back to Dashboard", key="back_dashboard"):
    #     st.session_state.current_app = None
    #     st.rerun()

    # ServerMapping section
    with st.expander("ServerMapping"):
        mapping_file = st.file_uploader("Upload ServerMapping (.xlsx or .csv)", type=["xlsx", "csv"])
        st.caption("Required columns: **Server, Operator, Algo** (case-insensitive).")
        st.download_button(
            "⬇️ Download Mapping Template (CSV)",
            data=pd.DataFrame({"Server": ["VS1","VS2"], "Operator": ["NAME","NAME"], "Algo": [8,1]}).to_csv(index=False).encode(),
            file_name="ServerMapping_template.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Google Auth section
    with st.expander("Google Auth"):
        st.caption("If running locally with files, this deletes local token.json. (Secrets-based tokens are managed in Streamlit Cloud.)")
        if st.button("🔁 Reset local token.json"):
            try:
                if os.path.exists(TOKEN_PATH):
                    os.remove(TOKEN_PATH)
                    st.success("Deleted token.json. You will be asked to sign in next time (local mode).")
                else:
                    st.info("No token.json found.")
            except Exception as e:
                st.error(f"Could not delete token: {e}")

    # Main interface
    st.title("User Setting Comparison")
    st.write("This tool manages user settings and configurations.")
    st.markdown(f"<div class='app-title'>🧭 {APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-subtle'>Compile operator/spec sheets from Google Drive and compare changes safely.</div>", unsafe_allow_html=True)

    mode = st.radio("Mode", ["Compile from Google Drive", "Compare Latest vs Last (Sheet1)"], index=0)

    if mode == "Compile from Google Drive":
        st.subheader("📦 Compile CSVs in a Drive folder into Compiled_User_Settings.xlsx")
        link = st.text_input("Paste Google Drive folder link (or folder ID)")
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            skiprows = st.number_input("CSV header lines to skip before real header", min_value=0, max_value=50, value=6, step=1)
        with c2:
            out_name = st.text_input("Output filename", value="Compiled_User_Settings.xlsx")
        with c3:
            st.markdown("<div class='block-gap'></div>", unsafe_allow_html=True)
            run_compile = st.button("🚀 Compile Now", type="primary", use_container_width=True)
        if run_compile:
            server_map = read_server_mapping(mapping_file)
            try:
                folder_id = extract_folder_id(link)
            except ValueError as e:
                st.error(str(e))
                st.stop()
            try:
                with st.status("Authenticating with Google…", expanded=False) as s:
                    service = authenticate_drive()
                    s.update(label="Listing files in folder…")
                    files = list_files_in_folder(service, folder_id)
                    csv_files = [f for f in files if str(f.get("name","")).lower().endswith(".csv")]
                    s.update(label=f"Found {len(csv_files)} CSV files. Processing…")
                    time.sleep(0.2)
                if not csv_files:
                    st.warning("No CSV files found in this folder.")
                    st.stop()
                with st.spinner("Downloading & processing…"):
                    compiled_df = process_csv_files(service, csv_files, server_map, skiprows=skiprows)
                if compiled_df.empty:
                    st.error("No valid data after processing.")
                    st.stop()
                operator_compiled = compiled_df.copy()
                specified = compiled_df.copy()
                specified = ensure_columns(specified, SPECIFIED_ORDER)
                specified = specified[SPECIFIED_ORDER]
                summary = generate_summary(compiled_df)
                xbytes = to_excel_bytes({
                    "Operator_Compiled": operator_compiled,
                    "Specified_Compiled": specified,
                    "Summary": summary
                })
                st.success(f"Built workbook from {len(csv_files)} CSV file(s).")
                m1, m2, m3 = st.columns(3)
                with m1: st.metric("Rows compiled", f"{len(compiled_df):,}")
                with m2: st.metric("Unique Users", compiled_df["User ID"].nunique())
                with m3: st.metric("Servers", compiled_df["Server"].nunique())
                st.download_button(
                    "⬇️ Download Compiled_User_Settings.xlsx",
                    data=xbytes,
                    file_name=out_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                tabs = st.tabs(["Specified_Compiled (preview)", "Summary", "Processed files"])
                with tabs[0]:
                    st.dataframe(specified.head(25), use_container_width=True)
                with tabs[1]:
                    st.dataframe(summary, use_container_width=True)
                with tabs[2]:
                    st.write("\n".join([f["name"] for f in csv_files]))
            except FileNotFoundError as e:
                st.error(str(e))
            except HttpError as e:
                st.error(f"Google API error: {e}")
            except Exception as e:
                st.exception(e)
    else:
        st.subheader("🔍 Compare LATEST compiled (Specified_Compiled) vs LAST workbook (Sheet1)")
        col1, col2 = st.columns(2)
        with col1:
            f_last = st.file_uploader("Upload **Last Workbook** (.xlsx) — must contain Sheet1", type=["xlsx"], key="last_file")
        with col2:
            f_latest = st.file_uploader("Upload **Latest Compiled** (.xlsx) — uses Specified_Compiled", type=["xlsx"], key="latest_file")
        if f_last and f_latest:
            last_bytes = f_last.read()
            latest_bytes = f_latest.read()
            try:
                last_df = read_sheet1_last(last_bytes)
                latest_df = clean_for_compare(read_specified_compiled(latest_bytes))
                st.success("Loaded: LAST from Sheet1, LATEST from Specified_Compiled.")
                added_df, removed_df, modified_df, all_diffs = compare_frames(last_df, latest_df)
                k1, k2, k3, k4 = st.columns(4)
                with k1: st.metric("Added", len(added_df))
                with k2: st.metric("Removed", len(removed_df))
                with k3: st.metric("Modified", len(modified_df))
                with k4: st.metric("Total Differences", len(all_diffs))
                st.markdown("---")
                tabs = st.tabs(["All Differences", "Added", "Removed", "Modified (Filterable)"])
                with tabs[0]:
                    st.dataframe(all_diffs, use_container_width=True, height=480)
                with tabs[1]:
                    st.dataframe(added_df, use_container_width=True, height=480)
                with tabs[2]:
                    st.dataframe(removed_df, use_container_width=True, height=480)
                with tabs[3]:
                    render_modified_with_filters(modified_df)
                xbytes = to_excel_bytes({
                    "All_Differences": all_diffs,
                    "Added": added_df,
                    "Removed": removed_df,
                    "Modified": modified_df
                })
                st.download_button(
                    "⬇️ Download Differences (Excel)",
                    data=xbytes,
                    file_name="user_settings_differences.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                with st.expander("Preview (first 10 rows)"):
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.write("**Latest (cleaned)**")
                        st.dataframe(latest_df.head(10), use_container_width=True)
                    with cc2:
                        st.write("**Last (cleaned)**")
                        st.dataframe(last_df.head(10), use_container_width=True)
            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.exception(e)
        else:
            st.info("Upload both Excel files to start.")
    st.markdown('</div>', unsafe_allow_html=True)
