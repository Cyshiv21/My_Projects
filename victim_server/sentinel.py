import streamlit as st
import pandas as pd
import joblib
import time
import os

# --- CONFIGURATION ---
LOG_FILE = 'access_logs.csv'
MODEL_FILE = 'guard_dog_model.pkl'

st.set_page_config(page_title="AI Cyber Defense", layout="wide")
st.title("🛡️ AI Intelligent Brute Force Detection System")

# Load Model
if os.path.exists(MODEL_FILE):
    model = joblib.load(MODEL_FILE)
else:
    st.error("Model not found! Run train_model.py first.")
    st.stop()

# Layout
col1, col2 = st.columns(2)
placeholder = st.empty()
alert_box = st.empty()

def load_and_process_logs():
    """Reads the live log file and extracts AI features."""
    # FIX 1: If file doesn't exist, return empty DataFrames (not None)
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(), pd.DataFrame()

    try:
        # Read the CSV
        df = pd.read_csv(LOG_FILE)
        
        # FIX 2: Check if dataframe is empty immediately
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # FEATURE ENGINEERING
        cutoff_time = pd.Timestamp.now() - pd.Timedelta(seconds=60)
        recent_traffic = df[df['timestamp'] > cutoff_time]
        
        if recent_traffic.empty:
            return pd.DataFrame(), df  # Return full history, but empty recent stats

        # Group by IP
        ip_stats = recent_traffic.groupby('ip_address').agg(
            login_rate=('username', 'count'),
            failure_rate=('status', lambda x: (x == 'FAILED').sum())
        ).reset_index()

        return ip_stats, df
        
    except Exception as e:
        # FIX 3: In case of read error (file busy), return empty DataFrames
        return pd.DataFrame(), pd.DataFrame()

# --- LIVE MONITORING LOOP ---
st.write("🔴 System Status: MONITORING LIVE TRAFFIC...")

while True:
    # 1. Get Data
    ip_stats, raw_df = load_and_process_logs()
    
    with placeholder.container():
        # Display Stats
        col1.metric("Total Login Attempts (All Time)", len(raw_df) if not raw_df.empty else 0)
        
        if not ip_stats.empty:
            # 2. AI PREDICTION
            features = ip_stats[['login_rate', 'failure_rate']]
            predictions = model.predict(features)
            ip_stats['AI_Verdict'] = predictions # 0 = Safe, 1 = Attack
            
            # Show the table
            st.dataframe(ip_stats, use_container_width=True)

            # 3. DETECTION LOGIC
            attackers = ip_stats[ip_stats['AI_Verdict'] == 1]
            
            if not attackers.empty:
                attacker_ip = attackers.iloc[0]['ip_address']
                alert_box.error(f"🚨 ALERT: BRUTE FORCE DETECTED FROM IP: {attacker_ip}")
                
                # SIMULATE DEFENSE
                st.toast(f"🚫 Firewall Rule Added: BLOCK {attacker_ip}", icon="🛡️")
            else:
                alert_box.success("✅ System Secure. No threats detected.")
        else:
            alert_box.info("Waiting for traffic...")

    # Refresh every 1 second
    time.sleep(1)