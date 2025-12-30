from config.common import CommonConfig
from config.delphic_params import DelphicParams as DP
from src.core.notifier import TelegramBot

# State Constants
WAIT = "WAIT"
GAPPING = "GAPPING"         # State 1 in Numba
IN_GAP = "IN_GAP"           # State 2 in Numba
AWAITING_DIVE = "AWAITING_DIVE" # State 3 in Numba

delphic_memory = {} 

class DelphicStrategy:
    @staticmethod
    def _init_memory(symbol):
        if symbol not in delphic_memory:
            delphic_memory[symbol] = {
                "LONG": {"state": WAIT, "entry_bar": None, "bars_in_gap": 0, "bars_awaiting": 0},
                "SHORT": {"state": WAIT, "entry_bar": None, "bars_in_gap": 0, "bars_awaiting": 0}
            }

    @staticmethod
    def run(df, symbol):
        sym_key = CommonConfig.SYMBOL_MAP.get(symbol, symbol)
        pip_size = CommonConfig.PIP_SIZES.get(sym_key, 0.0001)
        
        DelphicStrategy._init_memory(symbol)
        mem = delphic_memory[symbol]
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # =======================
        # === DELPHIC LONG ===
        # =======================
        ls = mem["LONG"]
        
        # 1. WAIT -> GAPPING (Cross UP)
        if ls['state'] == WAIT:
            if prev['MA18'] <= prev['MA40'] and curr['MA18'] > curr['MA40']:
                ls['state'] = GAPPING
                
        # 2. GAPPING -> IN_GAP (Pullback)
        elif ls['state'] == GAPPING:
            if curr['low'] < curr['MA18'] and curr['high'] > curr['MA40']:
                ls['state'] = IN_GAP
                ls['entry_bar'] = curr.to_dict()
                ls['bars_in_gap'] = 0
            elif curr['MA18'] <= curr['MA40']: ls['state'] = WAIT

        # 3. IN_GAP Phase
        elif ls['state'] == IN_GAP:
            ls['bars_in_gap'] += 1
            if curr['MA18'] <= curr['MA40'] or ls['bars_in_gap'] > 12:
                ls['state'] = WAIT
            # Dive Logic: Price closed below MA40? Go to State 3
            elif ls['entry_bar']['close'] < ls['entry_bar']['MA40']:
                ls['state'] = AWAITING_DIVE
                ls['bars_awaiting'] = 0
            else:
                # Normal Trigger (Touch/Drift)
                valid = True
                if DP.ENABLE_PIP_DIST_FILTER:
                    if ((curr['close'] - curr['MA40'])/pip_size) > DP.CROSS_DIST_THRESHOLDS.get(sym_key, 100): valid = False
                
                if valid and curr['close'] > curr['open'] and curr['close'] > curr['MA18']:
                    TelegramBot.send_signal(symbol, "DELPHIC", "LONG", f"{curr['close']:.5f}", "Touch/Drift")
                    ls['state'] = WAIT

        # 4. AWAITING_DIVE (State 3)
        elif ls['state'] == AWAITING_DIVE:
            ls['bars_awaiting'] += 1
            if ls['bars_awaiting'] > 12 or curr['MA18'] <= curr['MA40']:
                ls['state'] = WAIT
            else:
                # Dive Trigger: Price reclaims MA18 and MA18 > MA40
                valid = True
                if DP.ENABLE_PIP_DIST_FILTER:
                    if ((curr['close'] - curr['MA40'])/pip_size) > DP.CROSS_DIST_THRESHOLDS.get(sym_key, 100): valid = False
                
                if valid and curr['close'] > curr['MA18'] and curr['MA18'] > curr['MA40']:
                    TelegramBot.send_signal(symbol, "DELPHIC", "LONG", f"{curr['close']:.5f}", "Dive Recovery")
                    ls['state'] = WAIT

        # =======================
        # === DELPHIC SHORT ===
        # =======================
        ss = mem["SHORT"]
        
        if ss['state'] == WAIT:
            if prev['MA18'] >= prev['MA40'] and curr['MA18'] < curr['MA40']:
                ss['state'] = GAPPING

        elif ss['state'] == GAPPING:
            if curr['high'] > curr['MA18'] and curr['low'] < curr['MA40']:
                ss['state'] = IN_GAP
                ss['entry_bar'] = curr.to_dict()
                ss['bars_in_gap'] = 0
            elif curr['MA18'] >= curr['MA40']: ss['state'] = WAIT

        elif ss['state'] == IN_GAP:
            ss['bars_in_gap'] += 1
            if curr['MA18'] >= curr['MA40'] or ss['bars_in_gap'] > 12:
                ss['state'] = WAIT
            elif ss['entry_bar']['close'] > ss['entry_bar']['MA40']:
                ss['state'] = AWAITING_DIVE
                ss['bars_awaiting'] = 0
            else:
                valid = True
                if DP.ENABLE_PIP_DIST_FILTER:
                    if ((curr['MA40'] - curr['close'])/pip_size) > DP.CROSS_DIST_THRESHOLDS.get(sym_key, 100): valid = False
                
                if valid and curr['close'] < curr['open'] and curr['close'] < curr['MA18']:
                    TelegramBot.send_signal(symbol, "DELPHIC", "SHORT", f"{curr['close']:.5f}", "Touch/Drift")
                    ss['state'] = WAIT

        elif ss['state'] == AWAITING_DIVE:
            ss['bars_awaiting'] += 1
            if ss['bars_awaiting'] > 12 or curr['MA18'] >= curr['MA40']:
                ss['state'] = WAIT
            else:
                valid = True
                if DP.ENABLE_PIP_DIST_FILTER:
                    if ((curr['MA40'] - curr['close'])/pip_size) > DP.CROSS_DIST_THRESHOLDS.get(sym_key, 100): valid = False
                
                if valid and curr['close'] < curr['MA18'] and curr['MA18'] < curr['MA40']:
                    TelegramBot.send_signal(symbol, "DELPHIC", "SHORT", f"{curr['close']:.5f}", "Dive Recovery")
                    ss['state'] = WAIT