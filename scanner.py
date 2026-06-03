import os
import numpy as np
import pandas as pd
from datetime import datetime

CORR_THRESHOLD_HIGH = 0.82
CORR_THRESHOLD_LOW = 0.30
CHOP_THRESHOLD = 0.75

def generate_html_dashboard(r_ce, r_pe, h_max, l_min, signal, details):
    """Generates a modern, responsive HTML file using Tailwind CSS."""
    
    # Define dynamic theme colors based on signal status
    if "BEARISH" in signal:
        bg_color, text_color, badge_style = "bg-red-50", "text-red-700", "bg-red-500 text-white"
    elif "BULLISH" in signal:
        bg_color, text_color, badge_style = "bg-green-50", "text-green-700", "bg-green-500 text-white"
    elif "CHOP" in signal:
        bg_color, text_color, badge_style = "bg-yellow-50", "text-yellow-700", "bg-yellow-500 text-white"
    else:
        bg_color, text_color, badge_style = "bg-gray-50", "text-gray-700", "bg-gray-400 text-white"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty Shape Mimicry Workstation</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen flex flex-col justify-between">

    <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="h-3 w-3 bg-indigo-500 rounded-full animate-pulse"></div>
                <h1 class="text-xl font-bold tracking-tight">SHAPE MIMICRY ENGINE</h1>
            </div>
            <div class="text-sm text-slate-400 font-mono">
                Last Scanned: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-12 w-full flex-grow flex flex-col justify-center">
        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 sm:p-8 backdrop-blur-sm shadow-xl space-y-8">
            
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-6 border-b border-slate-700">
                <div>
                    <p class="text-xs font-semibold tracking-wider text-slate-400 uppercase">Current Scanner Signal</p>
                    <h2 class="text-2xl font-black mt-1 tracking-tight">{signal.replace('_', ' ')}</h2>
                </div>
                <span class="px-4 py-1.5 rounded-full text-xs font-bold tracking-wide uppercase {badge_style}">
                    {signal.split('_')[0]}
                </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <span class="text-xs font-medium text-slate-400 tracking-wider uppercase">Call Correlation (r_CE)</span>
                    <span class="text-4xl font-mono font-bold mt-2 text-indigo-400">{r_ce:.2f}</span>
                    <p class="text-xs text-slate-500 mt-2">Targeting institutional ceiling metrics</p>
                </div>
                <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <span class="text-xs font-medium text-slate-400 tracking-wider uppercase">Put Correlation (r_PE)</span>
                    <span class="text-4xl font-mono font-bold mt-2 text-sky-400">{r_pe:.2f}</span>
                    <p class="text-xs text-slate-500 mt-2">Targeting institutional floor matrices</p>
                </div>
            </div>

            <div class="{bg_color} border border-current/10 rounded-xl p-5 {text_color}">
                <h3 class="text-sm font-bold tracking-wider uppercase opacity-80 mb-3">Execution Parameters</h3>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-sm">
                    <div><span class="block text-xs font-sans uppercase opacity-60">Entry Zone</span> <strong class="text-lg font-bold">{details.get('entry', 'N/A')}</strong></div>
                    <div><span class="block text-xs font-sans uppercase opacity-60">Stop Loss</span> <strong class="text-lg font-bold">{details.get('sl', 'N/A')}</strong></div>
                    <div><span class="block text-xs font-sans uppercase opacity-60">Target Floor</span> <strong class="text-lg font-bold">{details.get('target', 'N/A')}</strong></div>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 pt-4 text-xs font-mono text-slate-400">
                <div>Morning Initial High: <span class="text-slate-200 font-bold">{h_max}</span></div>
                <div class="text-right">Morning Initial Low: <span class="text-slate-200 font-bold">{l_min}</span></div>
            </div>
        </div>
    </main>

    <footer class="border-t border-slate-800 py-6 bg-slate-950/40 text-center text-xs text-slate-500 font-mono">
        Algos sync dynamically directly via private GitHub workflows.
    </footer>

</body>
</html>"""
    
    with open("index.html", "w") as f:
        f.write(html_content)
    print("Dashboard static layout generated output as index.html successfully.")

def run_shape_mimicry_analysis(nifty_df, ce_df, pe_df):
    df = pd.merge(nifty_df, ce_df, on='timestamp', suffixes=('_nifty', '_ce'))
    df = pd.merge(df, pe_df, on='timestamp')
    df.rename(columns={'oi': 'oi_pe'}, inplace=True)
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    morning_df = df[(df['timestamp'].dt.time >= pd.to_datetime('09:30:00').time()) & 
                    (df['timestamp'].dt.time <= pd.to_datetime('11:00:00').time())].copy()
    
    h_max = round(morning_df['close'].max(), 2)
    l_min = round(morning_df['close'].min(), 2)
    
    r_ce = morning_df['close'].corr(morning_df['oi_ce'])
    r_pe = morning_df['close'].corr(morning_df['oi_pe'])
    r_ce = 0.0 if np.isnan(r_ce) else r_ce
    r_pe = 0.0 if np.isnan(r_pe) else r_pe

    signal = "NO_TRADE_CONDITIONS_MET"
    details = {"entry": "N/A", "sl": "N/A", "target": "N/A"}

    if r_ce >= CORR_THRESHOLD_HIGH and r_pe <= CORR_THRESHOLD_LOW:
        signal = "BEARISH_REVERSAL_LOCKED"
        details = {"entry": f"{h_max - 20} - {h_max}", "sl": str(h_max + 10), "target": str(l_min)}
    elif r_pe >= CORR_THRESHOLD_HIGH and r_ce <= CORR_THRESHOLD_LOW:
        signal = "BULLISH_REVERSAL_LOCKED"
        details = {"entry": f"{l_min} - {l_min + 20}", "sl": str(l_min - 10), "target": str(h_max)}
    elif r_ce >= CHOP_THRESHOLD and r_pe >= CHOP_THRESHOLD:
        signal = "SKIP_DAY_INSTITUTIONAL_CHOP"

    generate_html_dashboard(r_ce, r_pe, h_max, l_min, signal, details)

if __name__ == "__main__":
    # Standard dummy matrix population for compilation testing
    times = pd.date_range("2026-06-04 09:30:00", "2026-06-04 11:00:00", freq="5min")
    mock_nifty = pd.DataFrame({'timestamp': times, 'close': np.sin(np.linspace(0, 3, len(times))) * 50 + 24000})
    mock_ce = pd.DataFrame({'timestamp': times, 'oi': np.sin(np.linspace(0, 3, len(times))) * 100000 + 1500000})
    mock_pe = pd.DataFrame({'timestamp': times, 'oi': np.linspace(1000000, 1050000, len(times))})
    
    run_shape_mimicry_analysis(mock_nifty, mock_ce, mock_pe)
