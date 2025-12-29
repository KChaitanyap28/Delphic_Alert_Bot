import os
import pytz

class CommonConfig:
    TG_TOKEN = os.environ.get("7637881639:AAH3BpXgQHdd0Du6nCT-fg3oE7SYbuPaLVA")
    TG_CHAT_ID = os.environ.get("5440231825")

    # Yahoo Finance Symbols
    SYMBOLS = ["GBPUSD=X", "AUDUSD=X", "JPY=X", "EURJPY=X"]
    
    # Timeframe
    TIMEFRAME = "15m"
    
    # Indicators
    SMA_H4_LONG = 640
    SMA_H4_SHORT = 288
    
    # Symbol Mapping
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

    # --- S-TIER TIME SETTINGS ---
    TIMEZONE = pytz.timezone("Asia/Kolkata")
    START_HOUR = 6
    START_MINUTE = 30
    END_HOUR = 20
    END_MINUTE = 30