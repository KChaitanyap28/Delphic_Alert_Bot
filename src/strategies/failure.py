from config.common import CommonConfig
from config.failure_params import FailureParams as FP
from src.strategies.tools import Tools
from src.core.notifier import TelegramBot

# State Constants
WAIT = "WAIT"
SETUP = "SETUP" # MA Cross occurred
READY = "READY" # Price crossed MA18, waiting for MA40 cross

failure_memory = {}

class FailureStrategy:
    @staticmethod
    def _init_memory(symbol):
        if symbol not in failure_memory:
            failure_memory[symbol] = {
                "LONG": {"state": WAIT, "min_below": 1e9},
                "SHORT": {"state": WAIT, "max_above": 0.0}
            }

    @staticmethod
    def run(df, symbol):
        sym_key = CommonConfig.SYMBOL_MAP.get(symbol, symbol)
        pip_size = CommonConfig.PIP_SIZES.get(sym_key, 0.0001)
        FailureStrategy._init_memory(symbol)
        mem = failure_memory[symbol]
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # --- LONG LOGIC ---
        long_state = mem["LONG"]
        
        # 1. Setup: MA18 Crosses DOWN MA40
        if long_state['state'] == WAIT:
            if prev['MA18'] >= prev['MA40'] and curr['MA18'] < curr['MA40']:
                long_state['state'] = SETUP
                long_state['min_below'] = curr['low']
        
        # 2. Setup Phase: Track lowest low
        elif long_state['state'] == SETUP:
            long_state['min_below'] = min(long_state['min_below'], curr['low'])
            
            # Cancel if MA18 crosses back UP
            if curr['MA18'] >= curr['MA40']: 
                long_state['state'] = WAIT
            # Ready if Price goes ABOVE MA18 (Potential Failure building)
            elif curr['close'] > curr['MA18']:
                long_state['state'] = READY

        # 3. Ready Phase: Waiting for MA40 Break
        elif long_state['state'] == READY:
            long_state['min_below'] = min(long_state['min_below'], curr['low'])
            
            if curr['MA18'] >= curr['MA40']:
                long_state['state'] = WAIT
            
            # TRIGGER: Close > MA40
            elif curr['close'] > curr['MA40']:
                # Run Filters
                valid = True
                cross_idx = Tools.find_cross_index(df, direction='down', lookback=60)
                
                # Use cached min_below for Trap Depth
                if FP.ENABLE_TRAP_DEPTH_FILTER:
                    if ((curr['MA40'] - long_state['min_below'])/pip_size) > FP.TRAP_DEPTH_PIPS.get(sym_key, 30): valid = False
                
                if valid and FP.ENABLE_SMA_TREND_FILTER:
                    if Tools.analyze_market_context(df) != "BULLISH": valid = False
                
                if valid:
                    TelegramBot.send_signal(symbol, "FAILURE", "LONG", f"{curr['close']:.5f}", "Sweep/Fakeout")
                
                long_state['state'] = WAIT # Reset

        # --- SHORT LOGIC ---
        short_state = mem["SHORT"]
        
        if short_state['state'] == WAIT:
            if prev['MA18'] <= prev['MA40'] and curr['MA18'] > curr['MA40']:
                short_state['state'] = SETUP
                short_state['max_above'] = curr['high']
        
        elif short_state['state'] == SETUP:
            short_state['max_above'] = max(short_state['max_above'], curr['high'])
            
            if curr['MA18'] <= curr['MA40']: short_state['state'] = WAIT
            elif curr['close'] < curr['MA18']: short_state['state'] = READY

        elif short_state['state'] == READY:
            short_state['max_above'] = max(short_state['max_above'], curr['high'])
            
            if curr['MA18'] <= curr['MA40']: short_state['state'] = WAIT
            elif curr['close'] < curr['MA40']:
                # Run Filters
                valid = True
                
                if FP.ENABLE_TRAP_DEPTH_FILTER:
                    if ((short_state['max_above'] - curr['MA40'])/pip_size) > FP.TRAP_DEPTH_PIPS.get(sym_key, 30): valid = False
                
                if valid and FP.ENABLE_SMA_TREND_FILTER:
                    if Tools.analyze_market_context(df) != "BEARISH": valid = False
                
                if valid:
                    TelegramBot.send_signal(symbol, "FAILURE", "SHORT", f"{curr['close']:.5f}", "Sweep/Fakeout")
                
                short_state['state'] = WAIT