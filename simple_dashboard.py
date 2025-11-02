# simple_dashboard.py - 简化版看板
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("📈 华尔街母鸡 - 简化版看板")

# 股票输入
symbol = st.sidebar.text_input("股票代码", "AAPL")

if symbol:
    try:
        # 获取数据
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d", interval="15m")
        
        if not df.empty:
            current_price = df['Close'].iloc[-1]
            price_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
            
            # 显示基本信息
            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"{symbol} 价格", f"${current_price:.2f}", f"{price_change:.2f}%")
            with col2:
                st.metric("成交量", f"{df['Volume'].iloc[-1]:,.0f}")
            
            # 绘制图表
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="K线"
            ))
            
            fig.update_layout(title=f"{symbol} 5日走势", height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # 数据表格
            st.subheader("最新数据")
            st.dataframe(df.tail(10))
            
        else:
            st.error("无法获取数据")
            
    except Exception as e:
        st.error(f"错误: {e}")

st.info("🚀 如果看到这个页面，说明Streamlit工作正常！")