# dashboard.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Trading Dashboard", layout="wide")

# 数据库连接
engine = create_engine('postgresql://localhost/trading')

# 标题
st.title("📈 中短线交易监控面板")

# 侧边栏
with st.sidebar:
    st.header("控制面板")
    refresh_rate = st.selectbox("刷新频率", [30, 60, 300], index=1)
    
# 主要指标
col1, col2, col3, col4 = st.columns(4)

# 获取最新数据
latest_signals = pd.read_sql(
    "SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10",
    engine
)

positions = pd.read_sql(
    "SELECT * FROM positions WHERE status='OPEN'",
    engine
)

with col1:
    st.metric("今日信号", len(latest_signals))
    
with col2:
    st.metric("开仓数量", len(positions))
    
with col3:
    # 计算总盈亏
    total_pnl = positions['profit_loss'].sum() if not positions.empty else 0
    st.metric("总盈亏", f"${total_pnl:,.2f}")
    
with col4:
    # VIX
    vix_query = "SELECT vix FROM market_sentiment ORDER BY timestamp DESC LIMIT 1"
    vix_value = pd.read_sql(vix_query, engine)
    if not vix_value.empty:
        st.metric("VIX", f"{vix_value.iloc[0]['vix']:.2f}")

# 信号表格
st.header("最新交易信号")
st.dataframe(latest_signals)

# 持仓表格
st.header("当前持仓")
st.dataframe(positions)

# 自动刷新
st.button("刷新数据")