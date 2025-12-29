class FailureParams:
    # Switches
    ENABLE_TRAP_DEPTH_FILTER = True
    ENABLE_TIME_LIMIT_FILTER = True
    ENABLE_SMA_TREND_FILTER = True
    ENABLE_CONVICTION_FILTER = True
    
    # Constants
    CONVICTION_THRESHOLD = 0.25
    PIP_BUFFER = 0.0005

    # --- OPTIMIZED DICTIONARIES (From your file) ---
    TRAP_DEPTH_PIPS = {
        'GBPUSDm': 18,
        'AUDUSDm': 10,
        'USDJPYm': 10,
        'EURJPYm': 12,
    }

    MAX_BARS_SINCE_CROSS = {
        'GBPUSDm': 12,
        'AUDUSDm': 12,
        'USDJPYm': 29,
        'EURJPYm': 27,
    }
    
    DEFAULT_BAR_LIMIT = 12