# dashboard.py
import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.graph_objects as go

st.set_page_config(page_title="NIFTY Options – Signals & PnL", layout="wide")

DATA = Path("data")
CANDLES = DATA / "nifty_spot_3min.csv"
POSITIONS = DATA / "positions.csv"
BACKTEST = DATA / "backtest_equity.csv"

st.title("NIFTY Options — Live Signals, Risk & PnL")

# --- Candles & indicators
st.subheader("NIFTY 3-min — Price / RSI / MACD")
if CANDLES.exists():
    dc = pd.read_csv(CANDLES, parse_dates=["timestamp"]).sort_values("timestamp")
    # Price
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=dc["timestamp"], open=dc["open"], high=dc["high"],
        low=dc["low"], close=dc["close"], name="NIFTY"
    ))
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(2)
    with cols[0]:
        st.caption("RSI (14)")
        if "RSI" in dc.columns:
            rsi = go.Figure()
            rsi.add_trace(go.Scatter(x=dc["timestamp"], y=dc["RSI"], name="RSI"))
            rsi.add_hline(y=70); rsi.add_hline(y=30)
            st.plotly_chart(rsi, use_container_width=True)
        else:
            st.info("RSI not found yet.")
    with cols[1]:
        st.caption("MACD")
        if "MACD" in dc.columns and "Signal" in dc.columns:
            m = go.Figure()
            m.add_trace(go.Scatter(x=dc["timestamp"], y=dc["MACD"], name="MACD"))
            m.add_trace(go.Scatter(x=dc["timestamp"], y=dc["Signal"], name="Signal"))
            st.plotly_chart(m, use_container_width=True)
        else:
            st.info("MACD/Signal not found yet.")
else:
    st.warning("No candle file yet. Run bot.py to generate data.")

# --- Open positions
st.subheader("Open Positions")
if POSITIONS.exists():
    dp = pd.read_csv(POSITIONS, parse_dates=["entry_time","exit_time"], keep_default_na=False)
    open_pos = dp[dp["status"]=="OPEN"]
    if not open_pos.empty:
        st.dataframe(open_pos, use_container_width=True, height=230)
    else:
        st.success("No open positions.")
else:
    st.info("positions.csv not present yet.")

# --- Closed trades & PnL
st.subheader("Closed Trades & PnL")
if POSITIONS.exists():
    dp = pd.read_csv(POSITIONS, parse_dates=["entry_time","exit_time"], keep_default_na=False)
    closed = dp[dp["status"]=="CLOSED"].copy().sort_values("exit_time")
    if not closed.empty:
        closed["pnl_cum"] = closed["pnl"].cumsum()
        st.dataframe(closed.tail(200), use_container_width=True, height=260)
        pnl = go.Figure()
        pnl.add_trace(go.Scatter(x=closed["exit_time"], y=closed["pnl_cum"], name="Cum PnL"))
        st.plotly_chart(pnl, use_container_width=True)
    else:
        st.info("No closed trades yet.")
else:
    st.info("positions.csv not present yet.")

# --- Backtest equity curve
st.subheader("Backtest Equity Curve")
if BACKTEST.exists():
    be = pd.read_csv(BACKTEST, parse_dates=["timestamp"])
    if not be.empty:
        eq = go.Figure()
        eq.add_trace(go.Scatter(x=be["timestamp"], y=be["equity"], name="Equity"))
        st.plotly_chart(eq, use_container_width=True)
    else:
        st.info("Backtest equity is empty yet.")
else:
    st.info("backtest_equity.csv not present yet.")