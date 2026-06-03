import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURATION THRESHOLDS ---
CORR_THRESHOLD_HIGH = 0.82
CORR_THRESHOLD_LOW = 0.30
CHOP_THRESHOLD = 0.75

def send_telegram_alert(message):
    """Sends a live trade alert directly to your phone."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Telegram credentials missing. Skipping alert.")
        print(message)
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_index() == 200:
            print("Alert sent successfully via Telegram!")
        else:
            print(f"Telegram API Error: {response.text}")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def run_shape_mimicry_analysis(nifty_df, ce_df, pe_df):
    """
    Executes the Pearson correlation math across morning curves.
    Expected columns: 'timestamp', 'close' for Nifty; 'timestamp', 'oi' for options.
    """
    # 1. Merge the datasets on exact 5-minute intervals
    df = pd.merge(nifty_df, ce_df, on='timestamp', suffixes=('_nifty', '_ce'))
    df = pd.merge(df, pe_df, on='timestamp')
    df.rename(columns={'oi': 'oi_pe'}, inplace=True)
    
    # 2. Filter strictly for the pristine morning window (9:30 AM to 11:00 AM)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    morning_df = df[(df['timestamp'].dt.time >= pd.to_datetime('09:30:00').time()) & 
                    (df['timestamp'].dt.time <= pd.to_datetime('11:00:00').time())].copy()
    
    if len(morning_df) < 15:
        return "⚠️ Data Error: Insufficient 5-minute bars to calculate reliable correlation."

    # 3. Establish structural boundary levels
    h_max = round(morning_df['close'].max(), 2)
    l_min = round(morning_df['close'].min(), 2)
    
    # 4. Compute Pearson Correlation Coefficients (r)
    r_ce = morning_df['close'].corr(morning_df['oi_ce'])
    r_pe = morning_df['close'].corr(morning_df['oi_pe'])
    
    # Handle NaN values mathematically
    r_ce = 0.0 if np.isnan(r_ce) else r_ce
    r_pe = 0.0 if np.isnan(r_pe) else r_pe

    # 5. Execute Purely Mechanical Signaling Logic
    alert_msg = f"📊 *NIFTY SHAPE MIMICRY REPORT*\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    alert_msg += f"• Call Correlation ($r_{{CE}}$): `{r_ce:.2f}`\n"
    alert_msg += f"• Put Correlation ($r_{{PE}}$): `{r_pe:.2f}`\n"
    alert_msg += f"• Morning High: `{h_max}` | Low: `{l_min}`\n\n"

    if r_ce >= CORR_THRESHOLD_HIGH and r_pe <= CORR_THRESHOLD_LOW:
        alert_msg += "🚨 *SIGNAL LOCKED: BEARISH REVERSAL (CE MIRROR)*\n"
        alert_msg += f"• *Action:* Sell Call / Buy Put\n"
        alert_msg += f"• *Entry Zone:* {h_max - 20} to {h_max}\n"
        alert_msg += f"• *Stop Loss (SL):* {h_max + 10}\n"
        alert_msg += f"• *Target (Tgt):* {l_min}"
        
    elif r_pe >= CORR_THRESHOLD_HIGH and r_ce <= CORR_THRESHOLD_LOW:
        alert_msg += "🚀 *SIGNAL LOCKED: BULLISH REVERSAL (PE MIRROR)*\n"
        alert_msg += f"• *Action:* Buy Call / Sell Put\n"
        alert_msg += f"• *Entry Zone:* {l_min} to {l_min + 20}\n"
        alert_msg += f"• *Stop Loss (SL):* {l_min - 10}\n"
        alert_msg += f"• *Target (Tgt):* {h_max}"
        
    elif r_ce >= CHOP_THRESHOLD and r_pe >= CHOP_THRESHOLD:
        alert_msg += "❌ *STATUS: NO TRADE (CHOP TRAP)*\nBoth sides are mirroring Nifty. Institutions are stacking straddles. Stay out."
    else:
        alert_msg += "⏳ *STATUS: NO TRADE CONDITIONS MET*\nLines show weak correlation or random noise."

    return alert_msg

if __name__ == "__main__":
    # NOTE: Plug in your live broker fetch code here to populate these DataFrames.
    # For baseline runner testing, we feed it dummy placeholders:
    times = pd.date_range("2026-06-04 09:30:00", "2026-06-04 11:00:00", freq="5min")
    mock_nifty = pd.DataFrame({'timestamp': times, 'close': np.sin(np.linspace(0, 3, len(times))) * 50 + 24000})
    mock_ce = pd.DataFrame({'timestamp': times, 'oi': np.sin(np.linspace(0, 3, len(times))) * 100000 + 1500000})
    mock_pe = pd.DataFrame({'timestamp': times, 'oi': np.linspace(1000000, 1050000, len(times))})
    
    final_report = run_shape_mimicry_analysis(mock_nifty, mock_ce, mock_pe)
    send_telegram_alert(final_report)
