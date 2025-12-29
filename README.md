# Forex Sentinel: Institutional-Grade Alert System

## 🚀 Overview
A cloud-native, Python-based algorithmic market scanner designed to identify **Delphic** and **Failure** structural setups on Forex pairs. 

Unlike standard linear scanners, this system utilizes **State Machine Logic** to track multi-stage setups (Setup -> Pullback -> Trigger) rather than simple instantaneous indicator checks.

## 🏗 Architecture
- **Core:** Flask (Server) + APScheduler (Precision Timing).
- **Data:** Yahoo Finance API (Pandas DataFrame manipulation).
- **Notification:** Telegram Bot API with HTML parsing.
- **Deployment:** Dockerized container on Cloud PaaS (Render).

## 🧠 Strategy Logic (State Machine)
The system does not simply trigger on Crossovers. It tracks state:
1.  **Macro Context:** Checks H4 SMA Trend + Statistical Conviction.
2.  **Micro State:** 
    -   `WAIT`: Monitoring for structural break.
    -   `GAPPING`: Price creates space from Mean Reversion.
    -   `IN_GAP`: Price pulls back into value zone.
    -   `TRIGGER`: Momentum confirmation (Signal).

## 🛡 Filters & Risk
- **Trap Depth:** Calculates the "depth" of a fakeout to invalidate weak signals.
- **Time Decay:** Invalidates setups that linger too long without triggering.
- **Trend Alignment:** Enforces multi-timeframe alignment (M15 signal + H4 Trend).

## 🔧 Tech Stack
- **Language:** Python 3.12
- **Libs:** Pandas, NumPy, YFinance, python-dotenv
- **Ops:** CI/CD via Git to Render Cloud