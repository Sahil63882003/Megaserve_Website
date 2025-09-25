import streamlit as st
import pandas as pd

def run():
    # Custom CSS for attractive and user-friendly dashboard
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --accent1: #6D28D9;
            --dash-purple: #6D28D9;
            --dash-pink: #DB2777;
            --admin-accent: linear-gradient(135deg, #6D28D9 0%, #DB2777 100%);
            --font-family: 'Inter', sans-serif;
            --border-radius: 12px;
            --transition: 0.3s ease;
            --shadow-light: 0 8px 20px rgba(0,0,0,0.1);
            --shadow-dark: 0 12px 30px rgba(0,0,0,0.15);
            --success-bg: #D1FAE5;
            --success-border: #10B981;
        }
        
        .main {
            padding: 2vw;
            width: 100%;
            max-width: 100vw;
            margin: 0 auto;
            box-sizing: border-box;
            overflow-x: hidden;
            background: #F9FAFB;
        }
        
        h1 {
            font-family: var(--font-family);
            font-weight: 800;
            text-align: center;
            font-size: clamp(2rem, 6vw, 2.8rem);
            margin: 1.5rem 0;
            background: var(--admin-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stFileUploader > div > div > div {
            border-radius: var(--border-radius);
            border: 2px dashed #ccc;
            padding: 1.5rem;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
            background: #FFFFFF;
            transition: all var(--transition);
        }
        
        .stFileUploader > div > div > div:hover {
            border-color: var(--dash-purple);
            background: #F8F9FA;
        }
        
        .stButton > button {
            background-image: var(--admin-accent);
            border: none;
            border-radius: var(--border-radius);
            color: white;
            padding: 1rem 2rem;
            font-weight: 600;
            font-family: var(--font-family);
            font-size: clamp(1rem, 3vw, 1.2rem);
            transition: all var(--transition);
            width: 100%;
            box-sizing: border-box;
            margin: 1.5rem 0;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(109,40,217,0.3);
        }
        
        .stInfo {
            background-color: #dbeafe;
            border-left: 5px solid var(--accent1);
            padding: 1rem;
            border-radius: var(--border-radius);
            margin-bottom: 1.5rem;
            font-size: clamp(0.9rem, 2.5vw, 1.1rem);
            font-family: var(--font-family);
        }
        
        .dashboard-card {
            background: #FFFFFF;
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-light);
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all var(--transition);
        }
        
        .dashboard-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-dark);
        }
        
        .dashboard-card .user-info {
            font-family: var(--font-family);
            font-size: clamp(1rem, 3vw, 1.2rem);
            font-weight: 600;
        }
        
        .dashboard-card .action-buy {
            background: var(--success-bg);
            color: var(--success-border);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
        }
        
        .dashboard-card .action-sell {
            background: #FEE2E2;
            color: #EF4444;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
        }
        
        .dashboard-card .lots {
            font-family: var(--font-family);
            font-size: clamp(1rem, 3vw, 1.2rem);
            font-weight: 600;
            color: var(--dash-purple);
        }
        
        /* Responsive adjustments */
        @media (max-width: 1024px) {
            .main {
                padding: 1.5vw;
            }
            h1 {
                font-size: clamp(1.8rem, 5vw, 2.5rem);
            }
            .dashboard-card {
                padding: 1.2rem;
            }
        }
        
        @media (max-width: 600px) {
            .main {
                padding: 1rem;
            }
            h1 {
                font-size: clamp(1.6rem, 4vw, 2rem);
            }
            .dashboard-card {
                flex-direction: column;
                gap: 0.5rem;
                padding: 1rem;
            }
            .dashboard-card .user-info, .dashboard-card .lots {
                font-size: clamp(0.9rem, 2.5vw, 1.1rem);
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .main {
                background: #1F2937;
                color: #F3F4F6;
            }
            .stFileUploader > div > div > div {
                background: rgba(255,255,255,0.1);
                border: 2px dashed rgba(255,255,255,0.2);
            }
            .stFileUploader > div > div > div:hover {
                border-color: var(--dash-pink);
            }
            .stInfo {
                background: rgba(255,255,255,0.1);
                border-left-color: var(--accent1);
            }
            .dashboard-card {
                background: rgba(255,255,255,0.05);
                box-shadow: var(--shadow-dark);
            }
            .dashboard-card .user-info, .dashboard-card .lots {
                color: #F3F4F6;
            }
        }
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """, unsafe_allow_html=True)

    # Main content
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown("""
        <h1>
            🛡️ Hedge Manager Dashboard
        </h1>
    """, unsafe_allow_html=True)
    # st.info("👇 Upload a POS CSV file to view hedge actions. Ensure columns: UserID, Symbol, Product, Buy Qty, Sell Qty.")

    # File upload
    uploaded_file = st.file_uploader(
        "Drop your POS CSV file here or click to browse",
        type=["csv"],
        key="pos_file",
        label_visibility="collapsed"
    )

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
                    return 1

            df['LotSize'] = df['Symbol'].apply(get_lot_size)

            # Group and aggregate
            summary = (
                df.groupby(['UserID', 'OptionType'], as_index=False)
                  .agg({'Buy Qty': 'sum', 'Sell Qty': 'sum', 'LotSize': 'max'})
            )

            # Calculate difference and lots
            summary['difference'] = summary['Buy Qty'] - summary['Sell Qty']
            summary['lots'] = summary['difference'] / summary['LotSize']

            # Filter to only show rows with difference != 0
            summary = summary[summary['difference'] != 0]

            # Determine action to hedge (opposite of current position)
            summary['ActionToHedge'] = summary['difference'].apply(
                lambda x: 'Sell' if x > 0 else 'Buy'
            )
            summary['LotsToHedge'] = abs(summary['lots']).round(2)

            # Select relevant columns
            summary = summary[['UserID', 'OptionType', 'ActionToHedge', 'LotsToHedge']]

            # Display dashboard
            st.markdown("### 📊 Hedge Actions Required")
            if not summary.empty:
                for _, row in summary.iterrows():
                    action_class = 'action-buy' if row['ActionToHedge'] == 'Buy' else 'action-sell'
                    st.markdown(f"""
                        <div class="dashboard-card">
                            <span class="user-info">{row['UserID']} ({row['OptionType']})</span>
                            <span class="{action_class}">{row['ActionToHedge']}</span>
                            <span class="lots">{row['LotsToHedge']} Lots</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Download button
                csv = summary.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Hedge Actions as CSV",
                    data=csv,
                    file_name="hedge_actions.csv",
                    mime="text/csv",
                    key="download_summary"
                )
            else:
                st.info("No hedge actions required. All positions are balanced.")

    else:
        st.info("👆 Upload a POS CSV file to view hedge actions.")

    # Footer
    st.markdown("""
        ---
        <div style='text-align: center; color: #888; font-size: clamp(0.9rem, 2.5vw, 1rem);'>
            Powered by Streamlit | Designed for 2025 UX Excellence | Developed by Saksham
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
