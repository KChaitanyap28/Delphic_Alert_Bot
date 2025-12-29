from config.common import CommonConfig
from config.delphic_params import DelphicParams as DP
from src.strategies.tools import Tools
from src.core.notifier import TelegramBot

# State Constants
WAIT = "WAIT"
GAPPING = "GAPPING"
IN_GAP = "IN_GAP"
AWAITING_TRIGGER = "AWAITING_TRIGGER"

# Global State Dictionary (Persistent Memory)
delphic_memory = {} 
# Structure: { "GBPUSDm": { "LONG": {"state": "WAIT", ...}, "SHORT": {...} } }

class DelphicStrategy:
    @staticmethod
    def _init_memory(symbol):
        if symbol not in delphic_memory:
            delphic_memory[symbol] = {
                "LONG": {"state": WAIT, "entry_bar": None, "bars_in_gap": 0},
                "SHORT": {"state": WAIT, "entry_bar": None, "bars_in_gap": 0}
            }

    @staticmethod
    def run(df, symbol):
        sym_key = CommonConfig.SYMBOL_MAP.get(symbol, symbol)
        pip_size = CommonConfig.PIP_SIZES.get(sym_key, 0.0001)
        
        DelphicStrategy._init_memory(symbol)
        mem = delphic_memory[symbol]
        
        # We need the last 2 candles to detect transitions
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # --- LONG LOGIC ---
        long_state = mem["LONG"]
        
        # 1. Transition: WAIT -> GAPPING (Trend starts UP)
        if long_state['state'] == WAIT:
            if prev['MA18'] <= prev['MA40'] and curr['MA18'] > curr['MA40']:
                long_state['state'] = GAPPING

        # 2. Transition: GAPPING -> IN_GAP (Price pulls back into zone)
        elif long_state['state'] == GAPPING:
            if curr['low'] < curr['MA18'] and curr['high'] > curr['MA40']:
                long_state['state'] = IN_GAP
                long_state['bars_in_gap'] = 0
            elif curr['MA18'] <= curr['MA40']: # Trend Failed
                long_state['state'] = WAIT

        # 3. Transition: IN_GAP -> SIGNAL (The Trigger)
        elif long_state['state'] == IN_GAP:
            long_state['bars_in_gap'] += 1
            
            # Exit conditions
            if curr['MA18'] <= curr['MA40'] or long_state['bars_in_gap'] > 12:
                long_state['state'] = WAIT
            else:
                # Check Filters BEFORE Signal to save processing
                valid = True
                
                # Filter: Pip Dist
                if DP.ENABLE_PIP_DIST_FILTER:
                     if ((curr['close'] - curr['MA40'])/pip_size) > DP.CROSS_DIST_THRESHOLDS.get(sym_key, 100): valid = False

                # Trigger Logic: Green Candle, Close > Open, Close > MA18
                if valid and curr['close'] > curr['open'] and curr['close'] > curr['MA18']:
                     TelegramBot.send_signal(symbol, "DELPHIC", "LONG", f"{curr['close']:.5f}", "Touch/Drift Complete")
                     long_state['state'] = WAIT # Reset after signal

        # --- SHORT LOGIC ---
        short_state = mem["SHORT"]
        
        if short_state['state'] == WAIT:
            if prev['MA18'] >= prev['MA40'] and curr['MA18'] < curr['MA40']:
                short_state['state'] = GAPPING

        elif short_state['state'] == GAPPING:
            if curr['high'] > curr['MA18'] and curr['low'] < curr['MA40']:
                short_state['state'] = IN_GAP
                short_state['bars_in_gap'] = 0
            elif curr['MA18'] >= curr['MA40']:
                short_state['state'] = WAIT

        elif short_state['state'] == IN_GAP:
            short_state['bars_in_gap'] += 1
            
            if curr['MA18'] >= curr['MA40'] or short_state['bars_in_gap'] > 12:
                short_state['state'] = WAIT
            else:
                valid = True
                if DP.ENABLE_PIP_DIST_FILTER:
                     if ((curr['MA40'] - curr['close'])/pip_size) > DP.CROSS_DIST_THRESHOLDS.get(sym_key, 100): valid = False
                
                # Trigger Logic: Red Candle, Close < Open, Close < MA18
                if valid and curr['close'] < curr['open'] and curr['close'] < curr['MA18']:
                     TelegramBot.send_signal(symbol, "DELPHIC", "SHORT", f"{curr['close']:.5f}", "Touch/Drift Complete")
                     short_state['state'] = WAIT