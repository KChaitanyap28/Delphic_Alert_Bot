# 📈 Forex Sentinel: Institutional-Grade Market Scanner

![Status](https://img.shields.io/badge/Status-Live-success)
![Platform](https://img.shields.io/badge/Cloud-Render-blueviolet)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Forex Sentinel** is a cloud-native, autonomous algorithmic trading alert system designed to monitor Forex markets 24/5. Unlike standard retail indicators that trigger on simple price crossovers, this system utilizes **State Machine Logic** to track complex, multi-stage structural setups (Delphic & Failure) in real-time.

It separates **Macro Context** (Trend/Conviction) from **Micro Triggers** (Entry Signals), ensuring alerts are only generated during high-probability market conditions.

---

## 🚀 Key Features

*   **🧠 State Machine Architecture:** Tracks the "Lifecycle" of a trade (Wait → Setup → Pullback → Trigger) rather than checking instantaneous conditions.
*   **☁️ Cloud Native & Autonomous:** Deployed on Render PaaS with UptimeRobot keep-alive, ensuring 99.9% uptime with zero local hardware dependency.
*   **⏱️ Precision Timing:** Synced to IST Trading Hours (06:30 - 20:30) with specific cron logic to scan exactly 5 seconds after M15 candle closures.
*   **🛡️ Institutional Filtering:**
    *   **Context Filter:** Validates M15 signals against H4 SMA Trends and Statistical Conviction.
    *   **Trap Depth:** Invalidates setups that push too deep against the trend (Fakeout vs. Reversal detection).
    *   **Time Decay:** Expires setups that fail to trigger within a specific window.
*   **📡 Smart Notifications:**
    *   **Signal Alerts:** Instant Telegram notifications for trade entries.
    *   **Watchlist Updates:** Alerts when a pair enters a "Tradable" state (Bullish/Bearish).
    *   **Heartbeats:** Periodic system health checks every 2 hours.

---

## 🏗️ System Architecture

The project follows a modular, Separation-of-Concerns (SoC) architecture, making it scalable and maintainable.

```text
ForexSentinel/
├── config/                 # Configuration & Optimized Parameters
│   ├── common.py           # Global settings (Timezone, API Keys, Pairs)
│   ├── delphic_params.py   # Strategy-specific thresholds
│   └── failure_params.py   # Strategy-specific thresholds
├── src/
│   ├── core/               # Infrastructure Layer
│   │   ├── data.py         # Yahoo Finance Data Ingestion & Cleaning
│   │   └── notifier.py     # Telegram API Integration
│   ├── strategies/         # Logic Layer
│   │   ├── tools.py        # Shared Math (Cross detection, Conviction)
│   │   ├── delphic.py      # Delphic Strategy Engine (State Machine)
│   │   └── failure.py      # Failure Strategy Engine
├── app.py                  # Main Orchestrator (Flask + APScheduler)
└── requirements.txt        # Dependencies
```

---

## 🧠 Strategy Logic

The bot operates two distinct strategy engines simultaneously:

### 1. The Delphic Strategy
Based on Moving Average mean reversion principles.
*   **Logic:** Identifies a strong trend break (Gap), waits for a pullback into the value zone (In Gap), and triggers on momentum resumption.
*   **Filters:** Pip Distance from Mean, Time Limit, H4 Trend Alignment.

### 2. The Failure Strategy
Based on Trap Trading principles.
*   **Logic:** Identifies when price traps traders on the wrong side of the MA18/MA40 band and sharply reverses.
*   **Filters:** Trap Depth (Max Pips against trend), Time Limit, Statistical Conviction.

---

## 🛠️ Technology Stack

*   **Core:** Python 3.11
*   **Data Ingestion:** `yfinance` (Yahoo Finance API)
*   **Scheduling:** `APScheduler` (BackgroundCronJob)
*   **Server:** `Flask` + `Gunicorn`
*   **Notification:** Telegram Bot API
*   **Environment:** `python-dotenv` for local security, Environment Variables for Cloud.

---

## ⚙️ Installation & Local Development

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YourUsername/Forex-Sentinel.git
    cd Forex-Sentinel
    ```

2.  **Install Dependencies**
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -r requirements.txt
    ```

3.  **Configure Secrets**
    Create a `.env` file in the root directory:
    ```ini
    TG_TOKEN=your_telegram_bot_token
    TG_CHAT=your_telegram_chat_id
    ```

4.  **Run Diagnostics**
    Verify logic and connectivity without waiting for the scheduler:
    ```bash
    python debug_run.py
    ```

---

## ☁️ Deployment (Render)

This project is optimized for deployment on **Render.com** (Free Tier).

1.  Push code to a private GitHub repository.
2.  Create a new **Web Service** on Render connected to the repo.
3.  **Build Command:** `pip install -r requirements.txt`
4.  **Start Command:** `gunicorn app:app`
5.  **Environment Variables:** Add `TG_TOKEN` and `TG_CHAT`.
6.  **Keep-Alive:** Configure UptimeRobot to ping the Render URL every 5 minutes to prevent sleep mode.

---

## ⚠️ Disclaimer

*This software is for educational and research purposes only. It does not constitute financial advice. Algorithmic trading involves significant risk. The developers are not responsible for financial losses incurred through the use of this software.*