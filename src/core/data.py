import yfinance as yf
import pandas as pd
from config.common import CommonConfig

class DataFetcher:
    @staticmethod
    def get_data(symbol):
        try:
            # Fetch 1 month of 15m data to ensure we have enough candles
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1mo", interval="15m")
            
            if df.empty:
                print(f"❌ No data found for {symbol}")
                return None
            
            # 1. Reset Index to make Date/Datetime a column
            df = df.reset_index()
            
            # 2. Standardize Column Names
            df.columns = [col.lower() for col in df.columns]
            
            # FIX: Yahoo returns 'datetime' for 15m data, but 'date' for daily.
            # We rename whichever exists to 'time' to be consistent.
            if 'datetime' in df.columns:
                df.rename(columns={'datetime': 'time'}, inplace=True)
            elif 'date' in df.columns:
                df.rename(columns={'date': 'time'}, inplace=True)
                
            # Remove Timezone info (Yahoo sends UTC offset, we want naive)
            if 'time' in df.columns:
                df['time'] = df['time'].dt.tz_localize(None)
            
            # Ensure we have enough data (Need ~700 for SMA 640)
            if len(df) < 700:
                print(f"⚠️ Not enough data for {symbol}: {len(df)} candles")
                return None

            # 3. Indicators Calculation
            df['MA18'] = df['close'].shift(1).rolling(18).mean()
            df['MA40'] = df['close'].shift(1).rolling(40).mean()
            
            # H4 SMA Logic
            df['SMA_H4_Long'] = df['close'].rolling(CommonConfig.SMA_H4_LONG).mean()
            df['SMA_H4_Short'] = df['close'].rolling(CommonConfig.SMA_H4_SHORT).mean()
            
            return df

        except Exception as e:
            print(f"❌ Yahoo Fetch Error {symbol}: {e}")
            return None