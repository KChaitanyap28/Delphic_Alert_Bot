import requests
from config.common import CommonConfig

class TelegramBot:
    @staticmethod
    def send_raw(message):
        if not CommonConfig.TG_TOKEN: return
        url = f"https://api.telegram.org/bot{CommonConfig.TG_TOKEN}/sendMessage"
        payload = {"chat_id": CommonConfig.TG_CHAT_ID, "text": message, "parse_mode": "HTML"}
        try: requests.post(url, json=payload, timeout=5)
        except Exception as e: print(f"TG Error: {e}")

    @staticmethod
    def send_signal(symbol, strategy, direction, price, details=""):
        emoji = "🟢" if direction == "LONG" else "🔴"
        msg = (
            f"🚨 <b>TRADE SIGNAL</b> 🚨\n\n"
            f"<b>Pair:</b> {symbol}\n"
            f"<b>Strat:</b> {strategy} {direction} {emoji}\n"
            f"<b>Price:</b> {price}\n"
            f"<b>Time:</b> M15 Close\n"
            f"-------------------\n"
            f"<i>{details}</i>"
        )
        TelegramBot.send_raw(msg)

    @staticmethod
    def send_context_change(symbol, new_state):
        emoji = "📈" if new_state == "BULLISH" else ("📉" if new_state == "BEARISH" else "⚪")
        msg = (
            f"👀 <b>WATCHLIST UPDATE</b>\n\n"
            f"<b>{symbol}</b> is now <b>{new_state}</b> {emoji}\n"
            f"<i>Conditions (SMA H4 + Conviction) are aligned. Waiting for setups.</i>"
        )
        TelegramBot.send_raw(msg)

    @staticmethod
    def send_heartbeat(active_pairs):
        msg = "💓 <b>MARKET PULSE (2H Check)</b>\n\n"
        if not active_pairs:
            msg += "<i>No pairs are currently trending aligned.</i>"
        else:
            msg += "<b>Currently Tradable Context:</b>\n"
            for pair, direction in active_pairs.items():
                icon = "🟢" if direction == "BULLISH" else "🔴"
                msg += f"{icon} {pair} ({direction})\n"
        
        msg += "\n<i>Check your charts for developing structures.</i>"
        TelegramBot.send_raw(msg)