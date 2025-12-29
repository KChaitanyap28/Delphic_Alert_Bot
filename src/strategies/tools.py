import pandas as pd
from config.common import CommonConfig
from config.failure_params import FailureParams
from config.delphic_params import DelphicParams

class Tools:
    @staticmethod
    def find_cross_index(df, ma_fast='MA18', ma_slow='MA40', lookback=60, direction='up'):
        """Finds the index where Fast MA crossed Slow MA."""
        current_idx = len(df) - 1
        start_search = max(0, current_idx - lookback)
        
        for i in range(current_idx, start_search, -1):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            
            if direction == 'up':
                if prev[ma_fast] <= prev[ma_slow] and curr[ma_fast] > curr[ma_slow]:
                    return i
            else:
                if prev[ma_fast] >= prev[ma_slow] and curr[ma_fast] < curr[ma_slow]:
                    return i
        return None

    @staticmethod
    def get_conviction(df, ma_col='MA40', direction='long', lookback=96):
        subset = df.iloc[-lookback:]
        if len(subset) == 0: return 0.0
        
        if direction == 'long':
            count = len(subset[subset['close'] > subset[ma_col]])
        else:
            count = len(subset[subset['close'] < subset[ma_col]])
            
        return count / len(subset)

    @staticmethod
    def analyze_market_context(df):
        """
        Determines if a pair is 'Tradable' based on H4 SMA and Conviction.
        Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        curr = df.iloc[-1]
        
        # 1. Check Bullish Context
        bullish_sma = curr['close'] > curr['SMA_H4_Long'] and curr['close'] > curr['SMA_H4_Short']
        bullish_conv = Tools.get_conviction(df, direction='long') >= 0.25 # Using your optimized threshold
        
        if bullish_sma and bullish_conv:
            return "BULLISH"
            
        # 2. Check Bearish Context
        bearish_sma = curr['close'] < curr['SMA_H4_Long'] and curr['close'] < curr['SMA_H4_Short']
        bearish_conv = Tools.get_conviction(df, direction='short') >= 0.25
        
        if bearish_sma and bearish_conv:
            return "BEARISH"
            
        return "NEUTRAL"