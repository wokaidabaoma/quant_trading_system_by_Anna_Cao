# enable_premium_apis.py - 启用付费API功能
"""
切换到付费API数据源，获得更高质量的实时数据
"""

import streamlit as st
from data_manager import DataManager
from config import Config
import pandas as pd

def create_premium_dashboard():
    """使用付费API的高级看板"""
    st.title("📈 华尔街母鸡 - 高级版看板 (付费API)")
    
    config = Config()
    data_manager = DataManager(config)
    
    # 检查API配置
    col1, col2, col3 = st.columns(3)
    
    with col1:
        finnhub_status = "✅ 已配置" if config.FINNHUB_API_KEY else "❌ 未配置"
        st.metric("Finnhub API", finnhub_status)
    
    with col2:
        polygon_status = "✅ 已配置" if config.POLYGON_API_KEY else "❌ 未配置"
        st.metric("Polygon API", polygon_status)
    
    with col3:
        av_status = "✅ 已配置" if config.ALPHA_VANTAGE_API_KEY else "❌ 未配置"
        st.metric("Alpha Vantage", av_status)
    
    st.markdown("---")
    
    # 股票选择
    symbol = st.sidebar.text_input("股票代码", "AAPL")
    
    if symbol and config.FINNHUB_API_KEY:
        # 实时价格 (Finnhub)
        st.subheader("🔥 实时数据 (Finnhub API)")
        real_time = data_manager.get_real_time_price(symbol)
        
        if real_time:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("实时价格", f"${real_time['price']:.2f}")
            with col2:
                st.metric("涨跌", f"${real_time['change']:.2f}", f"{real_time['change_percent']:.2f}%")
            with col3:
                st.metric("日高", f"${real_time['high']:.2f}")
            with col4:
                st.metric("日低", f"${real_time['low']:.2f}")
        
        # 内幕交易 (Finnhub)
        st.subheader("🕵️ 内幕交易动态")
        insider_trades = data_manager.get_insider_trading(symbol)
        
        if insider_trades:
            insider_df = pd.DataFrame(insider_trades)
            st.dataframe(insider_df)
        else:
            st.info("暂无内幕交易数据")
        
        # 公司新闻 (Finnhub)
        st.subheader("📰 公司新闻")
        news = data_manager.get_company_news(symbol, days=7)
        
        if news:
            for article in news[:3]:  # 显示最新3条
                with st.expander(f"📖 {article.get('headline', '无标题')}"):
                    st.write(article.get('summary', '无摘要'))
                    st.markdown(f"[阅读全文]({article.get('url', '#')})")
        else:
            st.info("暂无新闻数据")
        
        # 分析师建议 (Finnhub)
        st.subheader("🎯 分析师建议")
        recommendations = data_manager.get_analyst_recommendations(symbol)
        
        if recommendations:
            rec_data = {
                '强烈买入': recommendations.get('strongBuy', 0),
                '买入': recommendations.get('buy', 0), 
                '持有': recommendations.get('hold', 0),
                '卖出': recommendations.get('sell', 0),
                '强烈卖出': recommendations.get('strongSell', 0)
            }
            
            st.bar_chart(rec_data)
        else:
            st.info("暂无分析师建议")
    
    elif not config.FINNHUB_API_KEY:
        st.error("请在.env文件中配置FINNHUB_API_KEY")
    
    # API使用优势说明
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🌟 付费API优势")
    st.sidebar.markdown("""
    **Finnhub API:**
    - ✅ 真正实时数据
    - ✅ 内幕交易监控
    - ✅ 新闻事件分析
    - ✅ 分析师评级
    
    **vs Yahoo Finance:**
    - ⚠️ 延迟15-20分钟
    - ❌ 无内幕交易数据
    - ❌ 无分析师数据
    - ❌ 无新闻整合
    """)

if __name__ == "__main__":
    create_premium_dashboard()