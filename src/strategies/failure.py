from config.common import CommonConfig
from config.failure_params import FailureParams as FP
from src.strategies.tools import Tools
from src.core.notifier import TelegramBot

# State Constants (Mapped to Numba: 0=WAIT, 1=SETUP, 2=EXECUTION)
WAIT = "WAIT"
SETUP = "SETUP"
EXECUTION = "EXECUTION"

failure_memory = {}

class FailureStrategy:
    @staticmethod
    def _init_memory(symbol):
        if symbol not in failure_memory:
            failure_memory[symbol] = {
                "LONG": {"state": WAIT, "min_below": 1e9, "cross_idx": None, "lowest_since_cross": 1e9},
                "SHORT": {"state": WAIT, "max_above": 0.0, "cross_idx": None, "highest_since_cross": 0.0}
            }

    @staticmethod
    def run(df, symbol):
        sym_key = CommonConfig.SYMBOL_MAP.get(symbol, symbol)
        pip_size = CommonConfig.PIP_SIZES.get(sym_key, 0.0001)
        FailureStrategy._init_memory(symbol)
        mem = failure_memory[symbol]
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        current_idx = df.index[-1] # Use numeric index if possible, but DataFrame index works
        
        # =======================
        # === FAILURE LONG ===
        # =======================
        ls = mem["LONG"]
        
        # Update extreme low since cross (Global Tracker for Trap Filter)
        if ls['state'] != WAIT:
            if curr['low'] < ls['lowest_since_cross']: ls['lowest_since_cross'] = curr['low']

        # 1. WAIT -> SETUP (Cross DOWN)
        if ls['state'] == WAIT:
            if prev['MA18'] >= prev['MA40'] and curr['MA18'] < curr['MA40']:
                ls['state'] = SETUP
                ls['min_below'] = 1e9
                ls['cross_idx'] = curr.name # Timestamp or Index
                ls['lowest_since_cross'] = curr['low']

        # 2. SETUP -> EXECUTION (Waiting for setup condition)
        elif ls['state'] == SETUP:
            if curr['high'] > curr['MA18'] and curr['low'] < curr['MA40']:
                ls['state'] = EXECUTION
            elif curr['MA18'] >= curr['MA40']: ls['state'] = WAIT

        # 3. EXECUTION Phase
        elif ls['state'] == EXECUTION:
            # Track lowest Close while below MA18
            if curr['low'] < curr['MA18']:
                ls['min_below'] = min(ls['min_below'], curr['close'])
            
            if curr['MA18'] >= curr['MA40']:
                ls['state'] = WAIT
            # TRIGGER: Close Cross UP MA40
            elif curr['close'] > curr['MA40']:
                valid = True
                
                # Filter: Time Limit (Approximate by candles count if possible, or skip if complex)
                # Note: We rely on the Bot running continuously, so 'cross_idx' is valid
                # For simplicity in Live Bot, we skip complex time-math here or assume < 30 bars
                
                # Filter: Trap Depth (Uses the tracked lowest_since_cross)
                if FP.ENABLE_TRAP_DEPTH_FILTER:
                    dist = (curr['MA40'] - ls['lowest_since_cross']) / pip_size
                    if dist > FP.TRAP_DEPTH_PIPS.get(sym_key, 30): valid = False
                
                # Filter: SMA Trend
                if valid and FP.ENABLE_SMA_TREND_FILTER:
                    if not (curr['close'] > curr['SMA_H4_Long'] and curr['close'] > curr['SMA_H4_Short']): valid = False
                
                # Filter: Conviction
                if valid and FP.ENABLE_CONVICTION_FILTER:
                    if Tools.get_conviction(df, direction='long') < FP.CONVICTION_THRESHOLD: valid = False

                if valid:
                    TelegramBot.send_signal(symbol, "FAILURE", "LONG", f"{curr['close']:.5f}", "Trap Recovery")
                
                ls['state'] = WAIT

        # =======================
        # === FAILURE SHORT ===
        # =======================
        ss = mem["SHORT"]
        
        if ss['state'] != WAIT:
            if curr['high'] > ss['highest_since_cross']: ss['highest_since_cross'] = curr['high']

        if ss['state'] == WAIT:
            if prev['MA18'] <= prev['MA40'] and curr['MA18'] > curr['MA40']:
                ss['state'] = SETUP
                ss['max_above'] = 0.0
                ss['cross_idx'] = curr.name
                ss['highest_since_cross'] = curr['high']

        elif ss['state'] == SETUP:
            if curr['low'] < curr['MA18'] and curr['high'] > curr['MA40']:
                ss['state'] = EXECUTION
            elif curr['MA18'] <= curr['MA40']: ss['state'] = WAIT

        elif ss['state'] == EXECUTION:
            if curr['high'] > curr['MA18']:
                ss['max_above'] = max(ss['max_above'], curr['close'])
            
            if curr['MA18'] <= curr['MA40']:
                ss['state'] = WAIT
            elif curr['close'] < curr['MA40']:
                valid = True
                
                if FP.ENABLE_TRAP_DEPTH_FILTER:
                    dist = (ss['highest_since_cross'] - curr['MA40']) / pip_size
                    if dist > FP.TRAP_DEPTH_PIPS.get(sym_key, 30): valid = False
                
                if valid and FP.ENABLE_SMA_TREND_FILTER:
                    if not (curr['close'] < curr['SMA_H4_Long'] and curr['close'] < curr['SMA_H4_Short']): valid = False
                
                if valid and FP.ENABLE_CONVICTION_FILTER:
                    if Tools.get_conviction(df, direction='short') < FP.CONVICTION_THRESHOLD: valid = False

                if valid:
                    TelegramBot.send_signal(symbol, "FAILURE", "SHORT", f"{curr['close']:.5f}", "Trap Recovery")
                
                ss['state'] = WAIT