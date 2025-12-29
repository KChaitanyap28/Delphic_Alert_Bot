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
    start_time = now_ist.replace(hour=CommonConfig.START_HOUR, minute=CommonConfig.START_MINUTE, second=0, microsecond=0)
    end_time = now_ist.replace(hour=CommonConfig.END_HOUR, minute=CommonConfig.END_MINUTE, second=0, microsecond=0)
    return start_time <= now_ist <= end_time

def scanner_job():
    if not is_trading_time():
        return 

    now_ist = datetime.now(CommonConfig.TIMEZONE)
    print(f"--- Scan: {now_ist.strftime('%H:%M:%S')} IST ---")
    
    if now_ist.hour == CommonConfig.START_HOUR and now_ist.minute == CommonConfig.START_MINUTE:
        TelegramBot.send_raw("🌅 <b>Trading Session Started</b> (06:30 IST)\nBot is now scanning for M15 setups.")

    for symbol in CommonConfig.SYMBOLS:
        df = DataFetcher.get_data(symbol)
        
        if df is not None:
            current_context = Tools.analyze_market_context(df)
            previous_context = market_state_cache.get(symbol, "UNKNOWN")
            
            if current_context != previous_context:
                if current_context in ["BULLISH", "BEARISH"]:
                    TelegramBot.send_context_change(symbol, current_context)
                market_state_cache[symbol] = current_context
            
            FailureStrategy.run(df, symbol)
            DelphicStrategy.run(df, symbol)

def heartbeat_job():
    if not is_trading_time(): return
    active_pairs = {k: v for k, v in market_state_cache.items() if v in ["BULLISH", "BEARISH"]}
    TelegramBot.send_heartbeat(active_pairs)

# --- SCHEDULER ---
scheduler = BackgroundScheduler(timezone=CommonConfig.TIMEZONE)
scheduler.add_job(scanner_job, 'cron', minute='0,15,30,45', second='5')
scheduler.add_job(heartbeat_job, 'cron', hour='*/2', minute='5')
scheduler.start()

try:
    now = datetime.now(CommonConfig.TIMEZONE).strftime('%H:%M IST')
    TelegramBot.send_raw(f"🚀 <b>Cloud Deploy Successful</b>\nTime: {now}\nStatus: {'TRADING ACTIVE' if is_trading_time() else 'SLEEPING (Outside Hours)'}")
except:
    pass

@app.route('/')
def home():
    now_ist = datetime.now(CommonConfig.TIMEZONE)
    status = "OPEN" if is_trading_time() else "CLOSED"
    return f"Forex Sentinel Active. Market Status: {status} ({now_ist.strftime('%H:%M')} IST)", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)