import os
import pytz

class CommonConfig:
    TG_TOKEN = os.environ.get("TG_TOKEN")
    TG_CHAT_ID = os.environ.get("TG_CHAT")

    # Yahoo Finance Symbols
    SYMBOLS = ["GBPUSD=X", "AUDUSD=X", "JPY=X", "EURJPY=X"]
    
    TIMEFRAME = "15m"
    SMA_H4_LONG = 640
    SMA_H4_SHORT = 288
    
    SYMBOL_MAP = {
        "GBPUSD=X": "GBPUSDm",
        "AUDUSD=X": "AUDUSDm",
        "JPY=X": "USDJPYm",
        "EURJPY=X": "EURJPYm"
    }

    PIP_SIZES = { 
        "GBPUSDm": 0.0001, 
        "AUDUSDm": 0.0001, 
        "USDJPYm": 0.01, 
        "EURJPYm": 0.01 
    }

    TIMEZONE = pytz.timezone("Asia/Kolkata")
    START_HOUR = 6
    START_MINUTE = 30
    END_HOUR = 20
    END_MINUTE = 30