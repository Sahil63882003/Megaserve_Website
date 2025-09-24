import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
import warnings
from datetime import datetime, date
import openpyxl
import hashlib
import logging
import time

# Configure logging
logging.basicConfig(
    filename='jainam_data_processor_errors.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress SettingWithCopyWarning
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Valid credentials (for demo purposes; in production, use a secure database)
VALID_USERNAME = "Access_User"
VALID_PASSWORD_HASH = hash_password("Jainam@135")

def to_excel(df):
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Error in to_excel: {str(e)}")
        raise

def read_file(file, sheet=None):
    try:
        start_time = time.time()
        logger.info(f"Reading file {file.name} with size {file.size / 1024:.2f} KB")
        ext = os.path.splitext(file.name)[1].lower()
        if file.size > 10_000_000:  # 10 MB limit
            error_msg = f"File {file.name} is too large (>10MB). Please upload a smaller file."
            logger.error(error_msg)
            raise ValueError(error_msg)
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file, sheet_name=sheet if sheet else 0, engine='openpyxl')
        elif ext == '.csv':
            df = pd.read_csv(file)
        else:
            error_msg = f"Invalid file format for {file.name}. Please upload CSV or Excel files."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info(f"Successfully read {file.name} in {time.time() - start_time:.2f} seconds")
        return df
    except Exception as e:
        error_msg = f"Error reading file {file.name}: {str(e)}"
        logger.error(error_msg)
        raise

def process_files(file1, file2, file3, sheet_name, date_input):
    try:
        start_time = time.time()
        logger.info("Starting file processing")

        # Read files
        progress_bar = st.progress(0)
        with st.spinner("Reading files..."):
            logger.info("Progress: 10% - Reading files")
            progress_bar.progress(10)
            df1 = read_file(file1)
            df2 = read_file(file2, sheet='Record')
            df3 = read_file(file3, sheet=sheet_name)

        # Validate DataFrames
        for df, name in [(df1, 'file1'), (df2, 'file2'), (df3, 'file3')]:
            if not isinstance(df, pd.DataFrame):
                error_msg = f"Error: {name} did not load as a DataFrame. Got type {type(df)}."
                logger.error(error_msg)
                raise ValueError(error_msg)
            if df.empty:
                error_msg = f"File {name} is empty."
                logger.error(error_msg)
                raise ValueError(error_msg)

        logger.info("Progress: 20% - Files validated")
        progress_bar.progress(20)

        # Process df3 sections
        with st.spinner("Processing file3 sections..."):
            try:
                logger.info("Extracting sections from file3")
                mtm_row_index = df3[df3["Unnamed: 0"] == "MTM"].index[0]
                capital_deployed_row_index = df3[df3["Unnamed: 0"] == "Capital Deployed"].index[0]
                max_loss_row_index = df3[df3["Unnamed: 0"] == "Max SL"].index[0]
                AVG_row_index = df3[df3["Unnamed: 0"] == "AVG %"].index[0]
            except IndexError as e:
                error_msg = f"Required sections (MTM, Capital Deployed, Max SL, AVG %) not found in file3. Details: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except KeyError as e:
                error_msg = f"'Unnamed: 0' column not found in file3. {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        logger.info("Progress: 30% - Sections extracted")
        progress_bar.progress(30)

        # Split df3 into sections
        mtm_df = df3.iloc[mtm_row_index:capital_deployed_row_index + 1]
        capital_deployed_df = df3.iloc[capital_deployed_row_index:max_loss_row_index + 1]
        max_loss_df = df3.iloc[max_loss_row_index:AVG_row_index + 1]

        # Process mtm_df
        with st.spinner("Processing MTM section..."):
            try:
                logger.info("Processing MTM section")
                mtm_df = mtm_df.drop(index=mtm_df.index[0]).reset_index(drop=True)
                mtm_df.columns = mtm_df.iloc[0]
                mtm_df = mtm_df.drop(index=0).reset_index(drop=True)
                mtm_df = mtm_df[:-1]
                if 'IDs' not in mtm_df.columns:
                    error_msg = "Error: 'IDs' column not found in MTM section of file3."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                non_null_ids = mtm_df['IDs'].dropna().tolist()
                if not non_null_ids:
                    error_msg = "Error: No valid IDs found in MTM section."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"Error processing MTM section: {str(e)}"
                logger.error(error_msg)
                raise

        logger.info("Progress: 40% - MTM processed")
        progress_bar.progress(40)

        # Process capital_deployed_df
        with st.spinner("Processing Capital Deployed section..."):
            try:
                logger.info("Processing Capital Deployed section")
                capital_deployed_df = capital_deployed_df.drop(index=capital_deployed_df.index[0]).reset_index(drop=True)
                capital_deployed_df.columns = capital_deployed_df.iloc[0]
                capital_deployed_df = capital_deployed_df.drop(index=0).reset_index(drop=True)
                capital_deployed_df = capital_deployed_df[:-1]
                if 'IDs' not in capital_deployed_df.columns:
                    error_msg = "Error: 'IDs' column not found in Capital Deployed section."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"Error processing Capital Deployed section: {str(e)}"
                logger.error(error_msg)
                raise

        logger.info("Progress: 50% - Capital Deployed processed")
        progress_bar.progress(50)

        # Process max_loss_df
        with st.spinner("Processing Max SL section..."):
            try:
                logger.info("Processing Max SL section")
                max_loss_df = max_loss_df.drop(index=max_loss_df.index[0]).reset_index(drop=True)
                max_loss_df.columns = max_loss_df.iloc[0]
                max_loss_df = max_loss_df.drop(index=0).reset_index(drop=True)
                max_loss_df = max_loss_df[:-1]
                if 'IDs' not in max_loss_df.columns:
                    error_msg = "Error: 'IDs' column not found in Max SL section."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"Error processing Max SL section: {str(e)}"
                logger.error(error_msg)
                raise

        logger.info("Progress: 60% - Max SL processed")
        progress_bar.progress(60)

        # Filter df1 by IDs
        with st.spinner("Filtering file1 by IDs..."):
            try:
                logger.info("Filtering df1 by IDs")
                if 'UserID' not in df1.columns:
                    error_msg = "Error: 'UserID' column not found in file1."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                df_new = df1[df1["UserID"].isin(non_null_ids)]
                if df_new.empty:
                    error_msg = "No matching UserIDs found in file1."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                df_new['Date'] = pd.to_datetime(df_new['Date'])
            except Exception as e:
                error_msg = f"Error filtering or converting Date in file1: {str(e)}"
                logger.error(error_msg)
                raise

        # Filter by date
        try:
            logger.info("Filtering df1 by date")
            match_date = pd.to_datetime(date_input)
            matched_rows = df_new[df_new['Date'].dt.date == match_date.date()]
            if matched_rows.empty:
                error_msg = f"No data found for date {date_input} in file1."
                logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error filtering by date: {str(e)}"
            logger.error(error_msg)
            raise

        logger.info("Progress: 70% - Date filtered")
        progress_bar.progress(70)

        # Drop unnecessary columns
        try:
            logger.info("Dropping unnecessary columns")
            cols_to_drop = ['Date', 'SNO', 'Enabled', 'LoggedIn', 'SqOff Done',
                            'Broker', 'Qty Multiplier', 'Available Margin', 'Total Orders',
                            'Total Lots', 'SERVER', 'Unnamed: 16', 'Unnamed: 17',
                            'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20']
            matched_rows = matched_rows.drop(columns=[col for col in cols_to_drop if col in matched_rows.columns])
        except Exception as e:
            error_msg = f"Error dropping columns: {str(e)}"
            logger.error(error_msg)
            raise

        # Map values and ensure numeric conversion
        try:
            logger.info("Mapping values to dataframes")
            if 'MTM (All)' not in matched_rows.columns:
                error_msg = "Error: 'MTM (All)' column not found in file1."
                logger.error(error_msg)
                raise ValueError(error_msg)
            # Convert 'MTM (All)' to numeric, handling errors
            matched_rows['MTM (All)'] = pd.to_numeric(matched_rows['MTM (All)'], errors='coerce')
            if matched_rows['MTM (All)'].isna().any():
                error_msg = "Error: Non-numeric values found in 'MTM (All)' column of file1."
                logger.error(error_msg)
                raise ValueError(error_msg)
            # Validate IDs mapping for MTM
            unmatched_ids_mtm = set(mtm_df['IDs'].dropna()) - set(matched_rows['UserID'])
            if unmatched_ids_mtm:
                logger.warning(f"IDs in file3 (MTM section) not found in file1: {unmatched_ids_mtm}")
            mtm_df['mtm'] = mtm_df['IDs'].map(matched_rows.set_index('UserID')['MTM (All)'])

            if 'ALLOCATION' not in matched_rows.columns:
                error_msg = "Error: 'ALLOCATION' column not found in file1."
                logger.error(error_msg)
                raise ValueError(error_msg)
            # Convert 'ALLOCATION' to numeric
            matched_rows['ALLOCATION'] = pd.to_numeric(matched_rows['ALLOCATION'], errors='coerce')
            if matched_rows['ALLOCATION'].isna().any():
                error_msg = "Error: Non-numeric values found in 'ALLOCATION' column of file1."
                logger.error(error_msg)
                raise ValueError(error_msg)
            capital_deployed_df['Allocation'] = (capital_deployed_df['IDs'].map(matched_rows.set_index('UserID')['ALLOCATION']) * 100)

            if 'MAX LOSS' not in matched_rows.columns:
                error_msg = "Error: 'MAX LOSS' column not found in file1."
                logger.error(error_msg)
                raise ValueError(error_msg)
            # Convert 'MAX LOSS' to numeric
            matched_rows['MAX LOSS'] = pd.to_numeric(matched_rows['MAX LOSS'], errors='coerce')
            if matched_rows['MAX LOSS'].isna().any():
                error_msg = "Error: Non-numeric values found in 'MAX LOSS' column of file1."
                logger.error(error_msg)
                raise ValueError(error_msg)
            # Validate IDs mapping for max_loss
            unmatched_ids_max_loss = set(max_loss_df['IDs'].dropna()) - set(matched_rows['UserID'])
            if unmatched_ids_max_loss:
                logger.warning(f"IDs in file3 (Max SL section) not found in file1: {unmatched_ids_max_loss}")
            max_loss_df['max_loss'] = max_loss_df['IDs'].map(matched_rows.set_index('UserID')['MAX LOSS'])
        except Exception as e:
            error_msg = f"Error mapping values: {str(e)}"
            logger.error(error_msg)
            raise

        logger.info("Progress: 80% - Values mapped")
        progress_bar.progress(80)

        # Filter invalid rows
        try:
            logger.info("Filtering invalid rows")
            mtm_df = mtm_df[mtm_df['IDs'].notna() & (mtm_df['IDs'] != '')]
            capital_deployed_df = capital_deployed_df[capital_deployed_df['IDs'].notna() & (capital_deployed_df['IDs'] != '')]
            max_loss_df = max_loss_df[max_loss_df['IDs'].notna() & (max_loss_df['IDs'] != '')]
            if mtm_df.empty or capital_deployed_df.empty or max_loss_df.empty:
                error_msg = "No valid rows after filtering."
                logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error filtering invalid rows: {str(e)}"
            logger.error(error_msg)
            raise

        # Expand mtm_df with alias rows
        try:
            logger.info("Expanding mtm_df with alias rows")
            alias_values = ['PS', 'VT', 'GB', 'RD', 'RM']
            new_rows = []
            for _, row in mtm_df.iterrows():
                new_rows.append(row.to_dict())
                for alias in alias_values:
                    empty_row = {col: np.nan for col in mtm_df.columns}
                    empty_row['Alias'] = alias
                    new_rows.append(empty_row)
            mtm_df = pd.DataFrame(new_rows).reset_index(drop=True)
        except Exception as e:
            error_msg = f"Error expanding mtm_df: {str(e)}"
            logger.error(error_msg)
            raise

        # Expand capital_deployed_df
        try:
            logger.info("Expanding capital_deployed_df")
            new_rows = []
            for _, row in capital_deployed_df.iterrows():
                new_rows.append(row.to_dict())
                for alias in alias_values:
                    empty_row = {col: np.nan for col in capital_deployed_df.columns}
                    empty_row['Alias'] = alias
                    new_rows.append(empty_row)
            capital_deployed_df = pd.DataFrame(new_rows).reset_index(drop=True)
        except Exception as e:
            error_msg = f"Error expanding capital_deployed_df: {str(e)}"
            logger.error(error_msg)
            raise

        # Expand max_loss_df
        try:
            logger.info("Expanding max_loss_df")
            new_rows = []
            for _, row in max_loss_df.iterrows():
                new_rows.append(row.to_dict())
                for alias in alias_values:
                    empty_row = {col: np.nan for col in max_loss_df.columns}
                    empty_row['Alias'] = alias
                    new_rows.append(empty_row)
            max_loss_df = pd.DataFrame(new_rows).reset_index(drop=True)
        except Exception as e:
            error_msg = f"Error expanding max_loss_df: {str(e)}"
            logger.error(error_msg)
            raise

        logger.info("Progress: 90% - DataFrames expanded")
        progress_bar.progress(90)

        # Process df2
        with st.spinner("Processing file2..."):
            try:
                logger.info("Processing df2")
                custom_header = ['UserID', 'User Alias', 'Algo', 'VT', 'GB', 'PS', 'RD', 'RM', 'ALLOCATION', 'MAX LOSS']
                all_data = []
                i = 0
                user_id_found = False
                while i < len(df2):
                    row = df2.iloc[i]
                    try:
                        if row.astype(str).str.contains("UserID", case=False, na=False).any():
                            user_id_found = True
                            header_row_idx = i
                            data_start_idx = i + 1
                            date_val = None
                            if header_row_idx > 0:
                                date_row = df2.iloc[header_row_idx - 1]
                                for val in date_row:
                                    try:
                                        dt = pd.to_datetime(val, dayfirst=True, errors='raise')
                                        if dt.year >= 2020:
                                            date_val = dt
                                            break
                                    except:
                                        continue
                            if date_val is None:
                                date_val = pd.NaT
                            data_rows = []
                            j = data_start_idx
                            while j < len(df2):
                                row_j = df2.iloc[j]
                                if row_j.isnull().all() or row_j.astype(str).str.contains("UserID", case=False, na=False).any():
                                    break
                                data_rows.append(row_j.tolist())
                                j += 1
                            if data_rows:
                                block_df = pd.DataFrame(data_rows, columns=custom_header)
                                block_df["Date"] = date_val
                                all_data.append(block_df)
                            i = j
                        else:
                            i += 1
                    except Exception as inner_e:
                        error_msg = f"Error processing df2 at row {i}: {str(inner_e)}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                if not user_id_found:
                    error_msg = "Error: 'UserID' column not found in file2 (Record sheet)."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                if not all_data:
                    error_msg = "Error: No valid data blocks found in file2."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                df2 = pd.concat(all_data, ignore_index=True)
                df2 = df2.drop(columns=['Algo', 'MAX LOSS'])
                # Convert component columns to numeric, log non-numeric values
                component_cols = ['VT', 'GB', 'PS', 'RD', 'RM']
                for col in component_cols:
                    original_values = df2[col].copy()
                    df2[col] = pd.to_numeric(df2[col], errors='coerce')
                    if df2[col].isna().any():
                        # Log non-numeric values with row indices
                        non_numeric_rows = df2[original_values.notna() & df2[col].isna()]
                        non_numeric_values = non_numeric_rows[['UserID', col]].to_dict('records')
                        logger.warning(f"Non-numeric values in '{col}' column of file2: {non_numeric_values}")
                        # Replace NaN with 0 to continue processing
                        df2[col] = df2[col].fillna(0)
                target_date = pd.to_datetime(date_input).normalize()
                df2 = df2[df2['Date'] == target_date]
                if df2.empty:
                    error_msg = f"No data found for {target_date.date()} in file2."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                df2 = df2.iloc[:-1].reset_index(drop=True)
            except Exception as e:
                error_msg = f"Error processing df2: {str(e)}"
                logger.error(error_msg)
                raise

        # Fill component allocations
        try:
            logger.info("Filling component allocations")
            component_cols = ['PS', 'VT', 'GB', 'RD', 'RM']
            current_userid = None
            for i, row in capital_deployed_df.iterrows():
                if pd.notna(row['IDs']):
                    current_userid = row['IDs']
                elif current_userid and row['Alias'] in component_cols:
                    alias = row['Alias']
                    matching_row = df2[df2['UserID'] == current_userid]
                    if not matching_row.empty:
                        value = matching_row.iloc[0][alias]
                        capital_deployed_df.at[i, 'Allocation'] = float(value) * 10_000_000
        except Exception as e:
            error_msg = f"Error filling component allocations: {str(e)}"
            logger.error(error_msg)
            raise

        # Handle unnamed column
        try:
            logger.info("Handling unnamed column")
            nan_column_name = capital_deployed_df.columns[capital_deployed_df.columns.isna()]
            if not nan_column_name.empty:
                nan_column_name = nan_column_name[0]
                # Log non-numeric values in Allocation and unnamed column
                original_allocation = capital_deployed_df['Allocation'].copy()
                original_unnamed = capital_deployed_df[nan_column_name].copy()
                capital_deployed_df['Allocation'] = pd.to_numeric(capital_deployed_df['Allocation'], errors='coerce')
                if capital_deployed_df['Allocation'].isna().any():
                    non_numeric_allocation = capital_deployed_df[original_allocation.notna() & capital_deployed_df['Allocation'].isna()]
                    logger.warning(f"Non-numeric values in 'Allocation' column: {non_numeric_allocation[['IDs', 'Allocation']].to_dict('records')}")
                # Convert unnamed column to numeric
                capital_deployed_df[nan_column_name] = pd.to_numeric(capital_deployed_df[nan_column_name], errors='coerce')
                if capital_deployed_df[nan_column_name].isna().any():
                    non_numeric_unnamed = capital_deployed_df[original_unnamed.notna() & capital_deployed_df[nan_column_name].isna()]
                    logger.warning(f"Non-numeric values in unnamed column '{nan_column_name}': {non_numeric_unnamed[['IDs', nan_column_name]].to_dict('records')}")
                # Fill NaN in Allocation with unnamed column values
                capital_deployed_df['Allocation'] = capital_deployed_df['Allocation'].fillna(capital_deployed_df[nan_column_name])
                # Replace remaining NaN in Allocation with 0
                capital_deployed_df['Allocation'] = capital_deployed_df['Allocation'].fillna(0)
                capital_deployed_df = capital_deployed_df.drop(columns=[nan_column_name])
            else:
                # If no unnamed column, ensure Allocation is numeric
                original_allocation = capital_deployed_df['Allocation'].copy()
                capital_deployed_df['Allocation'] = pd.to_numeric(capital_deployed_df['Allocation'], errors='coerce')
                if capital_deployed_df['Allocation'].isna().any():
                    non_numeric_allocation = capital_deployed_df[original_allocation.notna() & capital_deployed_df['Allocation'].isna()]
                    logger.warning(f"Non-numeric values in 'Allocation' column: {non_numeric_allocation[['IDs', 'Allocation']].to_dict('records')}")
                    capital_deployed_df['Allocation'] = capital_deployed_df['Allocation'].fillna(0)
        except Exception as e:
            error_msg = f"Error handling unnamed column: {str(e)}"
            logger.error(error_msg)
            raise

        # Finalize mtm_df
        try:
            logger.info("Finalizing mtm_df")
            mtm_df = mtm_df[["IDs", "Alias", "mtm"]]
            original_mtm = mtm_df['mtm'].copy()
            mtm_df['mtm'] = pd.to_numeric(mtm_df['mtm'], errors='coerce')
            if mtm_df['mtm'].isna().any():
                # Log rows with NaN in mtm
                nan_mtm_rows = mtm_df[original_mtm.notna() & mtm_df['mtm'].isna()]
                logger.warning(f"Non-numeric or missing values in 'mtm' column: {nan_mtm_rows[['IDs', 'Alias', 'mtm']].to_dict('records')}")
                # Replace NaN with 0 to continue processing
                mtm_df['mtm'] = mtm_df['mtm'].fillna(0)
        except Exception as e:
            error_msg = f"Error finalizing mtm_df: {str(e)}"
            logger.error(error_msg)
            raise

        # Map MTM
        try:
            logger.info("Mapping MTM")
            unique_mtm_df = mtm_df.drop_duplicates(subset='IDs', keep='first')
            capital_deployed_df['MTM'] = capital_deployed_df['IDs'].map(unique_mtm_df.set_index('IDs')['mtm'])
            capital_deployed_df['MTM'] = pd.to_numeric(capital_deployed_df['MTM'], errors='coerce')
            if capital_deployed_df['MTM'].isna().any():
                error_msg = "Error: Non-numeric values found in 'MTM' column after mapping."
                logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error mapping MTM: {str(e)}"
            logger.error(error_msg)
            raise

        # Proportional MTM allocation
        try:
            logger.info("Applying proportional MTM allocation")
            df = capital_deployed_df.copy()
            df['Allocation'] = pd.to_numeric(df['Allocation'], errors='coerce')
            df['MTM'] = pd.to_numeric(df['MTM'], errors='coerce')
            if df['Allocation'].isna().any() or df['MTM'].isna().any():
                error_msg = "Error: Non-numeric values found in 'Allocation' or 'MTM' columns."
                logger.error(error_msg)
                raise ValueError(error_msg)
            i = 0
            while i < len(df):
                if pd.notna(df.at[i, 'IDs']):
                    main_mtm = float(df.at[i, 'MTM'])
                    component_indices = []
                    j = i + 1
                    while j < len(df) and pd.isna(df.at[j, 'IDs']):
                        if not pd.isna(df.at[j, 'Allocation']):
                            component_indices.append(j)
                        j += 1
                    total_allocation = float(df.loc[component_indices, 'Allocation'].sum())
                    if total_allocation > 0 and pd.notna(main_mtm):
                        for idx in component_indices:
                            allocation = float(df.at[idx, 'Allocation'])
                            proportion = allocation / total_allocation
                            df.at[idx, 'MTM'] = round(main_mtm * proportion, 2)
                    i = j
                else:
                    i += 1
            capital_deployed_df = df
        except Exception as e:
            error_msg = f"Error applying proportional MTM allocation: {str(e)}"
            logger.error(error_msg)
            raise

        # Combine with max_loss_df
        try:
            logger.info("Combining with max_loss_df")
            original_max_loss = max_loss_df['max_loss'].copy()
            max_loss_df['max_loss'] = pd.to_numeric(max_loss_df['max_loss'], errors='coerce')
            if max_loss_df['max_loss'].isna().any():
                # Log rows with NaN in max_loss
                nan_max_loss_rows = max_loss_df[original_max_loss.notna() & max_loss_df['max_loss'].isna()]
                logger.warning(f"Non-numeric or missing values in 'max_loss' column: {nan_max_loss_rows[['IDs', 'Alias', 'max_loss']].to_dict('records')}")
                # Replace NaN with 0 to continue processing
                max_loss_df['max_loss'] = max_loss_df['max_loss'].fillna(0)
            capital_deployed_df["  "] = "|"
            capital_deployed_df["IDs(1)"] = max_loss_df["IDs"]
            capital_deployed_df["Alias(1)"] = max_loss_df["Alias"]
            capital_deployed_df["max_loss"] = max_loss_df["max_loss"]
        except Exception as e:
            error_msg = f"Error combining with max_loss_df: {str(e)}"
            logger.error(error_msg)
            raise

        # Rename columns
        try:
            logger.info("Renaming columns")
            capital_deployed_df = capital_deployed_df.rename(columns={
                'IDs': 'User ID',
                'Alias': 'Component',
                'Allocation': 'Capital Deployed',
                'MTM': 'MTM',
                '  ': '|',
                'IDs(1)': 'User ID (SL)',
                'Alias(1)': 'Component (SL)',
                'max_loss': 'Max Loss'
            })
        except Exception as e:
            error_msg = f"Error renaming columns: {str(e)}"
            logger.error(error_msg)
            raise

        # Select only the required columns to avoid extra columns with NaN
        try:
            logger.info("Selecting required columns")
            required_columns = ['User ID', 'Component', 'Capital Deployed', 'MTM', '|', 'User ID (SL)', 'Component (SL)', 'Max Loss']
            capital_deployed_df = capital_deployed_df[required_columns]
        except Exception as e:
            error_msg = f"Error selecting required columns: {str(e)}"
            logger.error(error_msg)
            raise

        # Clean NaN values for JSON compatibility
        try:
            logger.info("Cleaning NaN values in capital_deployed_df for JSON compatibility")
            # Log rows with NaN values
            nan_rows = capital_deployed_df[capital_deployed_df.isna().any(axis=1)]
            if not nan_rows.empty:
                logger.warning(f"Rows with NaN values in capital_deployed_df: {nan_rows.to_dict('records')}")
            # Define column types
            string_columns = ['User ID', 'Component', 'User ID (SL)', 'Component (SL)', '|']
            numeric_columns = ['Capital Deployed', 'MTM', 'Max Loss']
            # Replace NaN in string columns with empty string
            for col in string_columns:
                if col in capital_deployed_df.columns:
                    capital_deployed_df[col] = capital_deployed_df[col].fillna('')
            # Replace NaN in numeric columns with 0 (already handled, but ensure consistency)
            for col in numeric_columns:
                if col in capital_deployed_df.columns:
                    capital_deployed_df[col] = pd.to_numeric(capital_deployed_df[col], errors='coerce').fillna(0)
        except Exception as e:
            error_msg = f"Error cleaning NaN values in capital_deployed_df: {str(e)}"
            logger.error(error_msg)
            raise

        logger.info(f"Processing completed in {time.time() - start_time:.2f} seconds")
        progress_bar.progress(100)
        return capital_deployed_df
    except Exception as e:
        error_msg = f"Unexpected error in process_files: {str(e)}"
        logger.error(error_msg)
        raise
    finally:
        progress_bar.empty()

def run():
    try:
        if 'error_logs' not in st.session_state:
            st.session_state['error_logs'] = []
        if st.session_state['error_logs']:
            st.markdown('<div class="error-container fade-in">', unsafe_allow_html=True)
            st.markdown('<h3 class="text-lg font-semibold mb-4">Error Log</h3>', unsafe_allow_html=True)
            for error in st.session_state['error_logs']:
                st.markdown(f'<pre>{error}</pre>', unsafe_allow_html=True)
            if st.button("Clear Error Logs", help="Clear the displayed error logs."):
                st.session_state['error_logs'] = []
                st.success("Error logs cleared.")
            st.markdown('</div>', unsafe_allow_html=True)

        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        if 'form_inputs' not in st.session_state:
            st.session_state.form_inputs = {'file1': None, 'file2': None, 'file3': None, 'sheet_name': '', 'date': None}
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'output' not in st.session_state:
            st.session_state.output = None

        def get_css(theme):
            if theme == 'dark':
                background = "linear-gradient(135deg, #1F2937 0%, #374151 100%)"
                container_bg = "#2D3748"
                text_color = "#FFFFFF"
                input_bg = "#4B5563"
                input_border = "#6B7280"
                button_bg = "linear-gradient(90deg, #06B6D4, #3B82F6)"
                button_hover = "linear-gradient(90deg, #0E7490, #1E40AF)"
                header_gradient = "linear-gradient(to right, #34D399, #60A5FA)"
                error_bg = "#4B5563"
                error_border = "#EF4444"
                error_text = "#FECACA"
                success_bg = "#4B5563"
                success_border = "#10B981"
                success_text = "#D1FAE5"
                tooltip_bg = "#1E40AF"
                tooltip_text = "#FFFFFF"
                progress_bg = "#3B82F6"
                toggle_bg = "#4B5563"
                toggle_border = "#6B7280"
                login_bg = "linear-gradient(145deg, #374151, #1F2937)"
                login_border = "#4B5563"
                card_shadow = "0 12px 24px rgba(0, 0, 0, 0.3)"
            else:
                background = "linear-gradient(135deg, #E5E7EB 0%, #A5B4FC 100%)"
                container_bg = "#FFFFFF"
                text_color = "#1F2937"
                input_bg = "#F9FAFB"
                input_border = "#D1D5DB"
                button_bg = "linear-gradient(90deg, #10B981, #3B82F6)"
                button_hover = "linear-gradient(90deg, #047857, #1E40AF)"
                header_gradient = "linear-gradient(to right, #10B981, #3B82F6)"
                error_bg = "#FEE2E2"
                error_border = "#EF4444"
                error_text = "#B91C1C"
                success_bg = "#D1FAE5"
                success_border = "#10B981"
                success_text = "#065F46"
                tooltip_bg = "#1E40AF"
                tooltip_text = "#FFFFFF"
                progress_bg = "#10B981"
                toggle_bg = "#E5E7EB"
                toggle_border = "#D1D5DB"
                login_bg = "linear-gradient(145deg, #FFFFFF, #F3F4F6)"
                login_border = "#D1D5DB"
                card_shadow = "0 8px 16px rgba(0, 0, 0, 0.1)"

            return f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            .error-container {{
                border: 2px solid #C53030;
                border-radius: 0.5rem;
                background: {error_bg};
                padding: 1.5rem;
                margin: 2rem auto;
                max-width: 900px;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
                color: {error_text};
            }}
            .stApp {{
                background: {background};
                min-height: 100vh;
                padding: 2rem;
                font-family: 'Inter', sans-serif;
                transition: all 0.3s ease;
            }}
            .container {{
                background: {container_bg};
                border-radius: 0.75rem;
                box-shadow: {card_shadow};
                padding: 2rem;
                max-width: 550px;
                margin: auto;
                transition: transform 0.3s ease;
            }}
            .container:hover {{
                transform: translateY(-3px);
            }}
            .header h1 {{
                font-size: 2.5rem;
                font-weight: 700;
                text-align: center;
                background: {header_gradient};
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
            }}
            .header p {{
                text-align: center;
                color: {text_color};
                font-size: 1rem;
                opacity: 0.8;
                margin-bottom: 1.5rem;
            }}
            .stFileUploader, .stTextInput, .stDateInput {{
                background: {input_bg};
                border-radius: 0.5rem;
                padding: 0.75rem;
                margin-bottom: 1rem;
                border: 1px solid {input_border};
                transition: all 0.3s ease;
                border-radius: 12px;
            }}
            .stFileUploader:hover, .stTextInput:hover, .stDateInput:hover {{
                border-color: #3B82F6;
                background: #E5E7EB;
                transform: scale(1.02);
            }}
            .stFileUploader label, .stTextInput label, .stDateInput label {{
                font-weight: 600;
                color: {text_color};
                margin-bottom: 0.5rem;
            }}
            .stButton>button {{
                background: {button_bg};
                border: none;
                border-radius: 0.5rem;
                padding: 0.75rem;
                font-size: 1rem;
                font-weight: 600;
                color: {text_color};
                width: 100%;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                border-radius: 12px;
            }}
            .stButton>button:hover {{
                background: {button_hover};
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            .stButton>button:disabled {{
                background: #9CA3AF;
                cursor: not-allowed;
                transform: none;
            }}
            .reset-button {{
                background: linear-gradient(90deg, #F87171, #EF4444);
                border: none;
                border-radius: 0.5rem;
                padding: 0.75rem;
                font-size: 1rem;
                font-weight: 600;
                color: {text_color};
                width: 100%;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                border-radius: 12px;
            }}
            .reset-button:hover {{
                background: linear-gradient(90deg, #B91C1C, #991B1B);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            .error-message {{
                background: {error_bg};
                border: 1px solid {error_border};
                border-radius: 0.5rem;
                padding: 0.75rem;
                color: {error_text};
                font-weight: 500;
                margin-top: 1rem;
                animation: slideIn 0.5s ease-out;
                border-radius: 12px;
            }}
            .success-message {{
                background: {success_bg};
                border: 1px solid {success_border};
                border-radius: 0.5rem;
                padding: 0.75rem;
                color: {success_text};
                font-weight: 500;
                margin-top: 1rem;
                animation: slideIn 0.5s ease-out;
                border-radius: 12px;
            }}
            .file-preview, .validation-message {{
                color: {text_color};
                font-size: 0.85rem;
                margin-top: 0.25rem;
                font-style: italic;
            }}
            .file-size-gauge {{
                width: 100%;
                height: 10px;
                background: #E5E7EB;
                border-radius: 5px;
                overflow: hidden;
                margin-top: 0.25rem;
            }}
            .file-size-gauge-bar {{
                height: 100%;
                background: {progress_bg};
                transition: width 0.3s ease;
            }}
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .loading-spinner {{
                border: 4px solid {text_color};
                border-top: 4px solid {progress_bg};
                border-radius: 50%;
                width: 24px;
                height: 24px;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 0.5rem;
            }}
            .tooltip {{
                position: relative;
                display: inline-block;
                color: {text_color};
            }}
            .tooltip .tooltiptext {{
                visibility: hidden;
                width: 180px;
                background-color: {tooltip_bg};
                color: {tooltip_text};
                text-align: center;
                border-radius: 6px;
                padding: 6px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -90px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 0.85rem;
            }}
            .tooltip:hover .tooltiptext {{
                visibility: visible;
                opacity: 1;
            }}
            .stExpander {{
                background: {input_bg};
                border: 1px solid {input_border};
                border-radius: 0.5rem;
            }}
            .stExpander summary {{
                color: {text_color};
                font-weight: 600;
            }}
            .footer {{
                text-align: center;
                color: {text_color};
                opacity: 0.6;
                font-size: 0.8rem;
                margin-top: 2rem;
                animation: fadeIn 1s ease-in;
            }}
            .theme-toggle {{
                background: {toggle_bg};
                border: 1px solid {toggle_border};
                border-radius: 0.5rem;
                padding: 0.5rem;
                font-size: 1rem;
                font-weight: 600;
                color: {text_color};
                width: 100%;
                max-width: 150px;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
            .theme-toggle:hover {{
                background: {button_hover};
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            .theme-toggle span {{
                font-size: 1.2rem;
            }}
            .login-container {{
                background: {login_bg};
                border-radius: 1rem;
                box-shadow: {card_shadow};
                padding: 2rem;
                max-width: 400px;
                margin: 5rem auto;
                border: 1px solid {login_border};
                animation: fadeIn 0.5s ease-in;
            }}
            .login-header {{
                font-size: 1.75rem;
                font-weight: 600;
                text-align: center;
                margin-bottom: 1.5rem;
                color: {text_color};
            }}
            .login-input {{
                background: {input_bg};
                border: 1px solid {input_border};
                border-radius: 12px;
                padding: 0.75rem;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            }}
            .login-input:hover {{
                border-color: #3B82F6;
                background: #E5E7EB;
                transform: scale(1.02);
            }}
            .login-button {{
                background: {button_bg};
                border: none;
                border-radius: 12px;
                padding: 0.75rem;
                font-size: 1rem;
                font-weight: 600;
                color: {text_color};
                width: 100%;
                transition: all 0.3s ease;
            }}
            .login-button:hover {{
                background: {button_hover};
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            .input-icon {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background: {input_bg};
                border: 1px solid {input_border};
                border-radius: 12px;
                padding: 0.5rem;
                margin-bottom: 1rem;
            }}
            .input-icon svg {{
                margin-left: 0.5rem;
                color: {text_color};
                opacity: 0.6;
            }}
            .input-icon input {{
                border: none;
                background: transparent;
                width: 100%;
                outline: none;
                color: {text_color};
                font-family: 'Inter', sans-serif;
            }}
            .input-icon input::placeholder {{
                color: {text_color};
                opacity: 0.6;
            }}
            .row-widget-stMarkdown {{
                margin-bottom: -15px;
            }}
            .button-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 1rem;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            </style>
            """

        st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'

        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"

        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown("""
                <h1 style='margin-bottom: 0;'>Jainam Data Processor</h1>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(f"{theme_icon} Toggle Theme", key="theme_toggle", help="Toggle between light and dark theme"):
                st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
                st.rerun()

        with st.container():
            st.markdown('<div class="tooltip">📁 Compiled MTM Sheet<span class="tooltiptext">Excel/CSV with MTM data.</span></div>', unsafe_allow_html=True)
            file1 = st.file_uploader("Upload Compiled MTM Sheet", type=["xlsx", "csv"], key="file1", label_visibility="collapsed")
            if file1:
                st.session_state.form_inputs['file1'] = file1
                st.markdown(f'<div class="file-preview">Uploaded: {file1.name} ({file1.size / 1024:.2f} KB)</div>', unsafe_allow_html=True)

            st.markdown('<div class="tooltip">📁 Jainam Daily Allocation<span class="tooltiptext">Excel/CSV with allocation data.</span></div>', unsafe_allow_html=True)
            file2 = st.file_uploader("Upload Jainam Daily Allocation", type=["xlsx", "csv"], key="file2", label_visibility="collapsed")
            if file2:
                st.session_state.form_inputs['file2'] = file2
                st.markdown(f'<div class="file-preview">Uploaded: {file2.name} ({file2.size / 1024:.2f} KB)</div>', unsafe_allow_html=True)

            st.markdown('<div class="tooltip">📁 Updated JAINAM DAILY<span class="tooltiptext">Excel/CSV with updated daily data.</span></div>', unsafe_allow_html=True)
            file3 = st.file_uploader("Upload Updated JAINAM DAILY", type=["xlsx", "csv"], key="file3", label_visibility="collapsed")
            if file3:
                st.session_state.form_inputs['file3'] = file3
                st.markdown(f'<div class="file-preview">Uploaded: {file3.name} ({file3.size / 1024:.2f} KB)</div>', unsafe_allow_html=True)

            st.markdown('<div class="tooltip">📝 Sheet Name<span class="tooltiptext">Enter the exact sheet name (e.g., JULY 2025).</span></div>', unsafe_allow_html=True)
            sheet_name = st.text_input("Enter Sheet Name", value=st.session_state.form_inputs['sheet_name'], placeholder="Enter sheet name (e.g., JULY 2025)", label_visibility="collapsed")
            if sheet_name:
                st.session_state.form_inputs['sheet_name'] = sheet_name

            st.markdown(
                f'<div class="tooltip">📅 Date<span class="tooltiptext">Select a date up to today ({date.today().strftime("%B %d, %Y")}).</span></div>',
                unsafe_allow_html=True
            )
            
            date_input = st.date_input(
                "Select Date",
                max_value=date.today(),
                value=st.session_state.form_inputs['date'],
                label_visibility="collapsed"
            )
            
            if date_input:
                st.session_state.form_inputs['date'] = date_input

        col1, spacer, col2 = st.columns([1, 3, 1])
        with col1:
            process_clicked = st.button("⚙️ Process Files", key="process_btn")
        with col2:
            reset_clicked = st.button("🔄 Reset Form", key="reset_btn", help="Clear all inputs")

        if reset_clicked:
            try:
                logger.info("Reset button clicked, clearing form inputs")
                st.session_state.form_inputs = {'file1': None, 'file2': None, 'file3': None, 'sheet_name': '', 'date': None}
                st.session_state.output = None
                st.success("Form reset successfully.")
                st.rerun()
            except Exception as e:
                error_msg = f"Error during reset: {str(e)}"
                logger.error(error_msg)
                st.session_state['error_logs'].append(f"{datetime.now()}: {error_msg}")
                st.error(error_msg)

        if process_clicked:
            try:
                logger.info("Process button clicked")
                if not all([file1, file2, file3, sheet_name, date_input]):
                    error_msg = "All fields are required."
                    logger.error(error_msg)
                    st.session_state['error_logs'].append(f"{datetime.now()}: {error_msg}")
                    st.markdown(f'<div class="error-message">{error_msg}</div>', unsafe_allow_html=True)
                    return

                # Run processing in the main thread
                with st.spinner("Processing files, please wait..."):
                    st.session_state.output = process_files(file1, file2, file3, sheet_name, date_input)
                st.markdown('<div class="success-message">✅ Files processed successfully! View the data below.</div>', unsafe_allow_html=True)

            except Exception as e:
                error_msg = f"Unexpected error during file processing: {str(e)}"
                logger.error(error_msg)
                st.session_state['error_logs'].append(f"{datetime.now()}: {error_msg}")
                st.markdown(f'<div class="error-message">{error_msg}</div>', unsafe_allow_html=True)
                if "Non-numeric values" in str(e) or "missing values" in str(e):
                    st.markdown('<div class="error-message">⚠️ Non-numeric or missing values found in input files. Check the log file for details and clean the data.</div>', unsafe_allow_html=True)

        if st.session_state.output is not None:
            try:
                logger.info("Displaying processed data")
                st.subheader("Processed Data")
                # Ensure DataFrame is clean for display
                display_df = st.session_state.output.copy()
                # Log any remaining NaN values
                nan_rows = display_df[display_df.isna().any(axis=1)]
                if not nan_rows.empty:
                    logger.warning(f"Rows with NaN values before display: {nan_rows.to_dict('records')}")
                # Replace NaN in all columns for display
                string_columns = ['User ID', 'Component', 'User ID (SL)', 'Component (SL)', '|']
                numeric_columns = ['Capital Deployed', 'MTM', 'Max Loss']
                for col in string_columns:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].fillna('')
                for col in numeric_columns:
                    if col in display_df.columns:
                        display_df[col] = pd.to_numeric(display_df[col], errors='coerce').fillna(0)
                st.dataframe(
                    display_df.style.format({
                        'Capital Deployed': '{:,.2f}',
                        'MTM': '{:,.2f}',
                        'Max Loss': '{:,.2f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )

                output_excel = to_excel(st.session_state.output)
                filename = f"jainam_{st.session_state.form_inputs['date'].strftime('%Y-%m-%d')}.xlsx"
                st.download_button(
                    "📥 Download Processed Data",
                    data=output_excel,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                error_msg = f"Error displaying processed data: {str(e)}"
                logger.error(error_msg)
                st.session_state['error_logs'].append(f"{datetime.now()}: {error_msg}")
                st.error(error_msg)

        st.markdown('<div class="footer">Jainam Data Processor v1.0 | Developed By Sahil</div>', unsafe_allow_html=True)

    except Exception as e:
        error_msg = f"Unexpected error in main: {str(e)}"
        logger.error(error_msg)
        st.session_state['error_logs'].append(f"{datetime.now()}: {error_msg}")
        st.error(error_msg)

if __name__ == '__main__':
    run()
