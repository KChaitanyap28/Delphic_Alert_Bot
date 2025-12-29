class DelphicParams:
    # Switches
    ENABLE_PIP_DIST_FILTER = True
    ENABLE_BAR_LIMIT_FILTER = True
    ENABLE_SMA_TREND_FILTER = True
    ENABLE_CONVICTION_FILTER = True
    
    # Constants
    CONVICTION_THRESHOLD = 0.25

    # --- OPTIMIZED DICTIONARIES (From your file) ---
    CROSS_DIST_THRESHOLDS = {
        'GBPUSDm': 16,
        'AUDUSDm': 12,
        'USDJPYm': 12,
        'EURJPYm': 13,
    }

    MAX_BARS_CROSS = {
        'GBPUSDm': 15,
        'AUDUSDm': 12,
        'USDJPYm': 19,
        'EURJPYm': 15,
    }
    
    DEFAULT_BAR_LIMIT = 12