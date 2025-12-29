import logging
from datetime import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from config.common import CommonConfig
from src.core.data import DataFetcher
from src.core.notifier import TelegramBot
from src.strategies.tools import Tools
from src.strategies.failure import FailureStrategy
from src.strategies.delphic import DelphicStrategy

app = Flask(__name__)
# Suppress Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global Cache
market_state_cache = {}

def is_trading_time():
    """Checks if current IST time is within user defined window."""
    now_ist = datetime.now(CommonConfig.TIMEZONE)
    
    # Create start and end time objects for today
    start_time = now_ist.replace(hour=CommonConfig.START_HOUR, minute=CommonConfig.START_MINUTE, second=0, microsecond=0)
    end_time = now_ist.replace(hour=CommonConfig.END_HOUR, minute=CommonConfig.END_MINUTE, second=0, microsecond=0)
    
    return start_time <= now_ist <= end_time

def scanner_job():
    # 1. TIME FILTER: Strict check
    if not is_trading_time():
        return # Do nothing if outside hours

    now_ist = datetime.now(CommonConfig.TIMEZONE)
    print(f"--- Scan: {now_ist.strftime('%H:%M:%S')} IST ---")
    
    # Special: Send "Session Started" message exactly at 06:30 scan
    # We check if we are within the first minute of the start time
    if now_ist.hour == CommonConfig.START_HOUR and now_ist.minute == CommonConfig.START_MINUTE:
        TelegramBot.send_raw("🌅 <b>Trading Session Started</b> (06:30 IST)\nBot is now scanning for M15 setups.")

    for symbol in CommonConfig.SYMBOLS:
        df = DataFetcher.get_data(symbol)
        
        if df is not None:
            # 1. Analyze Context
            current_context = Tools.analyze_market_context(df)
            
            # 2. State Change Alert
            previous_context = market_state_cache.get(symbol, "UNKNOWN")
            
            if current_context != previous_context:
                if current_context in ["BULLISH", "BEARISH"]:
                    TelegramBot.send_context_change(symbol, current_context)
                market_state_cache[symbol] = current_context
            
            # 3. Run Strategies
            FailureStrategy.run(df, symbol)
            DelphicStrategy.run(df, symbol)

def heartbeat_job():
    if not is_trading_time(): return # Silence outside hours

    print("--- Heartbeat ---")
    active_pairs = {k: v for k, v in market_state_cache.items() if v in ["BULLISH", "BEARISH"]}
    TelegramBot.send_heartbeat(active_pairs)

# --- SCHEDULER CONFIGURATION ---
scheduler = BackgroundScheduler(timezone=CommonConfig.TIMEZONE)

# 1. SCANNER: Exact Candle Close
# Runs at :00, :15, :30, :45 minutes.
# second='5' gives Yahoo 5 seconds to finalize the candle data.
scheduler.add_job(scanner_job, 'cron', minute='0,15,30,45', second='5')

# 2. HEARTBEAT: Every 2 Hours
# Runs at :05 minutes to avoid clashing with the scanner message
scheduler.add_job(heartbeat_job, 'cron', hour='*/2', minute='5')

scheduler.start()

@app.route('/')
def home():
    now_ist = datetime.now(CommonConfig.TIMEZONE)
    status = "OPEN" if is_trading_time() else "CLOSED"
    return f"Forex Sentinel Active. Market Status: {status} ({now_ist.strftime('%H:%M')} IST)", 200

if __name__ == "__main__":
    TelegramBot.send_raw(f"🚀 <b>System Updated</b>\nTimings adjusted: 06:30 - 20:30 IST.\nPrecision: M15 Close + 5s.")
    app.run(host='0.0.0.0', port=10000)