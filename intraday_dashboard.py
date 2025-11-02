# intraday_dashboard.py - 日内交易成交量分析看板
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from data_manager import DataManager
from config import Config
from stock_scanner import StockScanner
import time

st.set_page_config(
    page_title="日内交易看板", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化配置和数据管理器
config = Config()
data_manager = DataManager(config)
stock_scanner = StockScanner(data_manager, config)

# 自定义CSS样式
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .signal-strong-buy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .signal-buy {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .signal-sell {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
    }
    .signal-neutral {
        background: linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%);
    }
    .volume-alert {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 10px;
        color: #262730;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 标题和副标题
st.title("📈 日内交易成交量分析看板")
st.markdown("---")

# 侧边栏控制
with st.sidebar:
    st.header("🎛️ 控制面板")
    
    # 股票选择
    symbol = st.text_input("股票代码", value="AAPL", help="输入美股代码，如AAPL, TSLA, NVDA")
    
    # 刷新间隔
    refresh_interval = st.selectbox(
        "刷新间隔", 
        options=[10, 30, 60, 300], 
        index=1,
        format_func=lambda x: f"{x}秒"
    )
    
    # 时间周期选择
    timeframe = st.selectbox(
        "时间周期",
        options=["1m", "5m", "15m", "30m", "1h"],
        index=2
    )
    
    # 数据周期
    period = st.selectbox(
        "数据周期",
        options=["1d", "5d", "1mo", "3mo"],
        index=1
    )
    
    # 成交量分析参数
    st.subheader("📊 成交量分析")
    volume_threshold = st.slider("成交量异动阈值", 1.5, 5.0, 2.0, 0.1)
    price_change_threshold = st.slider("价格变动阈值(%)", 1.0, 10.0, 3.0, 0.5)
    
    # 技术指标显示选择
    st.subheader("📈 技术指标")
    show_vwap = st.checkbox("显示VWAP", True)
    show_bollinger = st.checkbox("显示布林带", True)
    show_support_resistance = st.checkbox("显示支撑阻力", True)
    show_volume_profile = st.checkbox("显示成交量分布", False)
    
    # 自动刷新
    auto_refresh = st.checkbox("自动刷新", False)
    if auto_refresh:
        st.info(f"每{refresh_interval}秒自动刷新")

# 获取数据 - 升级为混合数据源
@st.cache_data(ttl=15)  # 缩短缓存到15秒获得更实时的数据
def get_intraday_data(symbol, period, interval):
    try:
        # 优先使用yfinance获取历史数据（稳定性好）
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return None
            
        # 计算基础指标
        df = calculate_intraday_indicators(df)
        return df
    except Exception as e:
        st.error(f"获取{symbol}数据失败: {e}")
        return None

@st.cache_data(ttl=5)  # 实时价格缓存5秒
def get_real_time_quote(symbol):
    """获取实时报价 - 使用Finnhub API"""
    return data_manager.get_real_time_price(symbol)

def calculate_intraday_indicators(df):
    """计算日内交易指标"""
    # VWAP
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    # 布林带 (20期)
    df['BB_middle'] = df['Close'].rolling(20).mean()
    df['BB_std'] = df['Close'].rolling(20).std()
    df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
    
    # 成交量指标
    df['volume_ma'] = df['Volume'].rolling(20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_ma']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 价格变化
    df['price_change'] = df['Close'].pct_change() * 100
    
    # 支撑阻力位（基于当日高低点）
    df['daily_high'] = df['High'].expanding().max()
    df['daily_low'] = df['Low'].expanding().min()
    
    # VWAP偏离度
    df['vwap_deviation'] = ((df['Close'] - df['VWAP']) / df['VWAP']) * 100
    
    return df

# 主要数据获取
df = get_intraday_data(symbol, period, timeframe)

if df is not None and not df.empty:
    # 获取实时报价（Finnhub API）
    real_time_quote = get_real_time_quote(symbol)
    
    if real_time_quote:
        # 使用实时价格
        current_price = real_time_quote.get('price', df['Close'].iloc[-1])
        price_change = real_time_quote.get('change_percent', 0)
        daily_high = real_time_quote.get('high', df['High'].iloc[-1])
        daily_low = real_time_quote.get('low', df['Low'].iloc[-1])
        
        if 'timestamp' in real_time_quote:
            last_updated = real_time_quote['timestamp'].strftime("%H:%M:%S")
            st.sidebar.success(f"🔥 实时数据 (更新于 {last_updated})")
        else:
            st.sidebar.success("🔥 实时数据已获取")
    else:
        # 备用历史价格
        current_price = df['Close'].iloc[-1]
        price_change = df['price_change'].iloc[-1] if 'price_change' in df.columns else 0
        daily_high = df['High'].iloc[-1]
        daily_low = df['Low'].iloc[-1]
        
        st.sidebar.warning("⚠️ 使用延迟数据")
    
    # 确保价格数据不为None
    current_price = current_price if current_price is not None else df['Close'].iloc[-1]
    price_change = price_change if price_change is not None else 0
    daily_high = daily_high if daily_high is not None else df['High'].iloc[-1]
    daily_low = daily_low if daily_low is not None else df['Low'].iloc[-1]
    
    # 其他指标数据
    current_volume = df['Volume'].iloc[-1]
    current_volume_ratio = df['volume_ratio'].iloc[-1] if 'volume_ratio' in df.columns else 1.0
    vwap_current = df['VWAP'].iloc[-1] if 'VWAP' in df.columns else current_price
    rsi_current = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
    
    # 主要指标卡片
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{symbol}</h3>
            <h2>${current_price:.2f}</h2>
            <p>价格变动: {price_change:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # 确保成交量数据不为None
        safe_volume_ratio = current_volume_ratio if current_volume_ratio is not None else 1.0
        safe_current_volume = current_volume if current_volume is not None else 0
        
        volume_color = "signal-strong-buy" if safe_volume_ratio > volume_threshold else "signal-neutral"
        st.markdown(f"""
        <div class="metric-card {volume_color}">
            <h3>成交量比率</h3>
            <h2>{safe_volume_ratio:.1f}x</h2>
            <p>当前量: {safe_current_volume:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # 确保VWAP数据不为None
        safe_vwap = vwap_current if vwap_current is not None else current_price
        safe_price = current_price if current_price is not None else 0
        
        vwap_signal = "above" if safe_price > safe_vwap else "below"
        vwap_color = "signal-buy" if vwap_signal == "above" else "signal-sell"
        st.markdown(f"""
        <div class="metric-card {vwap_color}">
            <h3>VWAP</h3>
            <h2>${safe_vwap:.2f}</h2>
            <p>位置: {vwap_signal.upper()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # 确保RSI数据不为None
        safe_rsi = rsi_current if rsi_current is not None else 50
        
        if safe_rsi > 70:
            rsi_color = "signal-sell"
            rsi_signal = "超买"
        elif safe_rsi < 30:
            rsi_color = "signal-strong-buy"
            rsi_signal = "超卖"
        else:
            rsi_color = "signal-neutral"
            rsi_signal = "中性"
            
        st.markdown(f"""
        <div class="metric-card {rsi_color}">
            <h3>RSI</h3>
            <h2>{safe_rsi:.1f}</h2>
            <p>{rsi_signal}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        # VIX情绪指标
        vix_data = data_manager.get_vix_sentiment()
        safe_vix_value = vix_data.get('value', 20.0) if vix_data else 20.0
        safe_vix_sentiment = vix_data.get('sentiment', '中性') if vix_data else '中性'
        
        st.markdown(f"""
        <div class="metric-card signal-neutral">
            <h3>VIX情绪</h3>
            <h2>{safe_vix_value:.1f}</h2>
            <p>{safe_vix_sentiment}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 成交量异动警报
    if safe_volume_ratio > volume_threshold and abs(price_change) > price_change_threshold:
        st.markdown(f"""
        <div class="volume-alert">
            <h3>🚨 成交量异动警报!</h3>
            <p>成交量比率 {safe_volume_ratio:.1f}x | 价格变动 {price_change:.2f}% | 建议关注！</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 选项卡布局
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 主图表", "📊 成交量分析", "🎯 日内策略", "📋 实时监控", "🚀 高级分析", "🎯 选股信号"])
    
    with tab1:
        st.subheader(f"{symbol} 日内走势图")
        
        # 创建K线图
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('价格走势', '成交量', 'RSI'),
            row_heights=[0.6, 0.25, 0.15]
        )
        
        # K线图
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="K线"
            ),
            row=1, col=1
        )
        
        # VWAP
        if show_vwap and 'VWAP' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['VWAP'],
                    mode='lines',
                    name='VWAP',
                    line=dict(color='orange', width=2)
                ),
                row=1, col=1
            )
        
        # 布林带
        if show_bollinger and 'BB_upper' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_upper'],
                    mode='lines',
                    name='BB上轨',
                    line=dict(color='red', width=1, dash='dash'),
                    showlegend=False
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_lower'],
                    mode='lines',
                    name='BB下轨',
                    line=dict(color='green', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)'
                ),
                row=1, col=1
            )
        
        # 支撑阻力位
        if show_support_resistance:
            fig.add_hline(
                y=df['daily_high'].iloc[-1],
                line_dash="dot",
                line_color="red",
                annotation_text="日内高点",
                row=1, col=1
            )
            fig.add_hline(
                y=df['daily_low'].iloc[-1],
                line_dash="dot",
                line_color="green",
                annotation_text="日内低点",
                row=1, col=1
            )
        
        # 成交量
        colors = ['red' if row['Close'] < row['Open'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='成交量',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        # 成交量均线
        if 'volume_ma' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['volume_ma'],
                    mode='lines',
                    name='量均线',
                    line=dict(color='blue', width=1)
                ),
                row=2, col=1
            )
        
        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=2)
                ),
                row=3, col=1
            )
            
            # RSI 超买超卖线
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        fig.update_layout(
            height=800,
            title=f"{symbol} 日内交易分析图表",
            xaxis_rangeslider_visible=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("📊 成交量深度分析")
        
        # 成交量统计
        col1, col2 = st.columns(2)
        
        with col1:
            # 成交量比率分布
            fig_vol_ratio = px.histogram(
                df.dropna(subset=['volume_ratio']),
                x='volume_ratio',
                nbins=30,
                title="成交量比率分布",
                labels={'volume_ratio': '成交量比率', 'count': '频次'}
            )
            fig_vol_ratio.add_vline(
                x=volume_threshold,
                line_dash="dash",
                line_color="red",
                annotation_text=f"阈值 {volume_threshold}"
            )
            st.plotly_chart(fig_vol_ratio, use_container_width=True)
        
        with col2:
            # 价格与成交量关系
            fig_price_vol = px.scatter(
                df.dropna(),
                x='volume_ratio',
                y='price_change',
                color='RSI',
                title="价格变动 vs 成交量比率",
                labels={
                    'volume_ratio': '成交量比率',
                    'price_change': '价格变动(%)',
                    'RSI': 'RSI'
                },
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_price_vol, use_container_width=True)
        
        # 成交量异动时点
        anomaly_df = df[
            (df['volume_ratio'] > volume_threshold) & 
            (abs(df['price_change']) > price_change_threshold)
        ].copy()
        
        if not anomaly_df.empty:
            st.subheader("🚨 成交量异动时点")
            anomaly_df['时间'] = anomaly_df.index
            anomaly_df['价格'] = anomaly_df['Close']
            anomaly_df['成交量比率'] = anomaly_df['volume_ratio'].round(2)
            anomaly_df['价格变动%'] = anomaly_df['price_change'].round(2)
            
            display_cols = ['时间', '价格', '成交量比率', '价格变动%', 'RSI']
            st.dataframe(
                anomaly_df[display_cols].tail(10),
                use_container_width=True
            )
        else:
            st.info("当前时段无成交量异动")
    
    with tab3:
        st.subheader("🎯 日内交易策略建议")
        
        # 策略信号计算
        latest_data = df.iloc[-1]
        
        signals = []
        
        # VWAP策略
        if latest_data['Close'] > latest_data['VWAP']:
            if latest_data['volume_ratio'] > 1.5:
                signals.append({
                    "策略": "VWAP突破",
                    "信号": "买入",
                    "强度": "强",
                    "描述": f"价格在VWAP({latest_data['VWAP']:.2f})之上，且放量"
                })
        else:
            if latest_data['volume_ratio'] > 1.5:
                signals.append({
                    "策略": "VWAP支撑",
                    "信号": "卖出",
                    "强度": "中",
                    "描述": f"价格跌破VWAP({latest_data['VWAP']:.2f})"
                })
        
        # RSI策略
        if latest_data['RSI'] < 30:
            signals.append({
                "策略": "RSI超卖",
                "信号": "买入",
                "强度": "强",
                "描述": f"RSI({latest_data['RSI']:.1f})进入超卖区域"
            })
        elif latest_data['RSI'] > 70:
            signals.append({
                "策略": "RSI超买",
                "信号": "卖出",
                "强度": "强",
                "描述": f"RSI({latest_data['RSI']:.1f})进入超买区域"
            })
        
        # 布林带策略
        if 'BB_upper' in df.columns:
            if latest_data['Close'] > latest_data['BB_upper']:
                signals.append({
                    "策略": "布林带突破",
                    "信号": "观察",
                    "强度": "中",
                    "描述": "价格突破布林带上轨，注意回调"
                })
            elif latest_data['Close'] < latest_data['BB_lower']:
                signals.append({
                    "策略": "布林带支撑",
                    "信号": "买入",
                    "强度": "中",
                    "描述": "价格触及布林带下轨，可能反弹"
                })
        
        # 成交量策略
        if latest_data['volume_ratio'] > 3:
            signals.append({
                "策略": "异常放量",
                "信号": "关注",
                "强度": "高",
                "描述": f"成交量达到均量{latest_data['volume_ratio']:.1f}倍，重大事件"
            })
        
        # 显示策略信号
        if signals:
            signals_df = pd.DataFrame(signals)
            st.dataframe(signals_df, use_container_width=True)
        else:
            st.info("当前无明显交易信号")
        
        # 日内操作建议
        st.subheader("💡 操作建议")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**做多条件:**")
            st.markdown(f"""
            - 价格 > VWAP ({latest_data['VWAP']:.2f})
            - RSI < 30 或 30-50区间
            - 成交量比率 > 1.5
            - 价格接近布林带下轨
            """)
            
        with col2:
            st.markdown("**做空条件:**")
            st.markdown(f"""
            - 价格 < VWAP ({latest_data['VWAP']:.2f})
            - RSI > 70 或 50-70区间
            - 成交量比率 > 2.0
            - 价格接近布林带上轨
            """)
        
        # 止损止盈建议
        atr_value = abs(latest_data['High'] - latest_data['Low'])  # 简化ATR
        st.subheader("🛡️ 风险管理")
        st.markdown(f"""
        **基于ATR的止损止盈:**
        - 止损距离: ±{atr_value:.2f} (1倍ATR)
        - 止盈距离: ±{atr_value*2:.2f} (2倍ATR)
        - 当前ATR: {atr_value:.2f}
        """)
    
    with tab4:
        st.subheader("📋 实时监控面板")
        
        # 实时数据表格
        latest_5 = df.tail(5).copy()
        latest_5.index = latest_5.index.strftime('%H:%M:%S')
        
        display_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'volume_ratio', 'RSI', 'VWAP']
        available_columns = [col for col in display_columns if col in latest_5.columns]
        
        st.dataframe(
            latest_5[available_columns].round(2),
            use_container_width=True
        )
        
        # 实时警报
        st.subheader("🔔 实时警报")
        
        alerts = []
        
        if current_volume_ratio > volume_threshold:
            alerts.append(f"⚠️ 成交量异动: {current_volume_ratio:.1f}x")
        
        if abs(price_change) > price_change_threshold:
            alerts.append(f"📈 价格剧烈波动: {price_change:.2f}%")
        
        if rsi_current > 70:
            alerts.append(f"🔴 RSI超买: {rsi_current:.1f}")
        elif rsi_current < 30:
            alerts.append(f"🟢 RSI超卖: {rsi_current:.1f}")
        
        if 'vwap_deviation' in df.columns:
            vwap_dev = df['vwap_deviation'].iloc[-1]
            if abs(vwap_dev) > 2:
                alerts.append(f"📊 VWAP偏离: {vwap_dev:.1f}%")
        
        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("✅ 当前无警报")
        
        # 自动刷新计时器
        if auto_refresh:
            placeholder = st.empty()
            for seconds in range(refresh_interval, 0, -1):
                placeholder.text(f"下次刷新: {seconds}秒")
                time.sleep(1)
            placeholder.empty()
            st.experimental_rerun()
    
    with tab5:
        st.subheader("🚀 高级分析 - 付费API功能")
        
        # API状态检查
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
        
        # 实时数据面板
        if real_time_quote:
            st.subheader("🔥 实时数据面板")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # 安全获取实时数据，确保不为None
            safe_price = real_time_quote.get('price') or 0
            safe_change_percent = real_time_quote.get('change_percent') or 0
            safe_change = real_time_quote.get('change') or 0
            safe_high = real_time_quote.get('high') or 0
            safe_low = real_time_quote.get('low') or 0
            
            with col1:
                st.metric(
                    "实时价格", 
                    f"${safe_price:.2f}",
                    f"{safe_change_percent:.2f}%"
                )
            
            with col2:
                st.metric("涨跌额", f"${safe_change:.2f}")
            
            with col3:
                st.metric("今日高点", f"${safe_high:.2f}")
            
            with col4:
                st.metric("今日低点", f"${safe_low:.2f}")
            
            # 实时价格趋势
            price_trend = "📈 上涨" if safe_change > 0 else "📉 下跌" if safe_change < 0 else "➡️ 平盘"
            
            if 'timestamp' in real_time_quote and real_time_quote['timestamp']:
                timestamp_str = real_time_quote['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                st.info(f"**趋势**: {price_trend} | **更新时间**: {timestamp_str}")
            else:
                st.info(f"**趋势**: {price_trend}")
        
        # 内幕交易分析
        st.subheader("🕵️ 内幕交易分析")
        
        @st.cache_data(ttl=300)  # 5分钟缓存
        def get_insider_data(symbol):
            return data_manager.get_insider_trading(symbol)
        
        insider_trades = get_insider_data(symbol)
        
        if insider_trades:
            insider_df = pd.DataFrame(insider_trades)
            
            # 内幕交易统计
            buy_trades = [t for t in insider_trades if t['action'] == 'BUY']
            sell_trades = [t for t in insider_trades if t['action'] == 'SELL']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                # 安全计算买入金额，处理None值
                buy_value = sum(t.get('value', 0) or 0 for t in buy_trades)
                st.metric("内幕买入", len(buy_trades), f"${buy_value:,.0f}")
            with col2:
                # 安全计算卖出金额，处理None值  
                sell_value = sum(t.get('value', 0) or 0 for t in sell_trades)
                st.metric("内幕卖出", len(sell_trades), f"${sell_value:,.0f}")
            with col3:
                net_sentiment = len(buy_trades) - len(sell_trades)
                sentiment_text = "看涨" if net_sentiment > 0 else "看跌" if net_sentiment < 0 else "中性"
                st.metric("内幕情绪", sentiment_text, net_sentiment)
            
            # 详细交易表格
            st.dataframe(insider_df, use_container_width=True)
            
            # 内幕交易警报
            if len(buy_trades) >= 2:
                st.success("🚨 内幕人士密集买入，可能有利好消息！")
            elif len(sell_trades) >= 2:
                st.warning("⚠️ 内幕人士密集卖出，需要谨慎！")
                
        else:
            st.info("📊 近30天无内幕交易数据")
        
        # 公司新闻分析
        st.subheader("📰 新闻情绪分析")
        
        @st.cache_data(ttl=600)  # 10分钟缓存
        def get_news_data(symbol):
            return data_manager.get_company_news(symbol, days=3)
        
        news_data = get_news_data(symbol)
        
        if news_data:
            st.info(f"📈 获取到 {len(news_data)} 条最新新闻")
            
            for i, article in enumerate(news_data[:5]):  # 显示最新5条
                with st.expander(f"📖 {article.get('headline', '无标题')[:60]}..."):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(article.get('summary', '无摘要')[:200] + "...")
                        
                        # 简单情绪分析
                        headline = article.get('headline', '').lower()
                        if any(word in headline for word in ['beat', 'exceed', 'strong', 'growth', 'profit']):
                            st.success("😊 正面情绪")
                        elif any(word in headline for word in ['miss', 'decline', 'loss', 'weak', 'concern']):
                            st.error("😟 负面情绪")
                        else:
                            st.info("😐 中性情绪")
                    
                    with col2:
                        if article.get('url'):
                            st.markdown(f"[阅读全文]({article.get('url')})")
                        
                        # 新闻时间
                        if 'datetime' in article:
                            news_time = pd.to_datetime(article['datetime'], unit='s')
                            st.caption(f"⏰ {news_time.strftime('%m-%d %H:%M')}")
        else:
            st.info("📰 暂无最新新闻")
        
        # 分析师评级
        st.subheader("🎯 分析师评级")
        
        @st.cache_data(ttl=3600)  # 1小时缓存
        def get_analyst_data(symbol):
            return data_manager.get_analyst_recommendations(symbol)
        
        analyst_data = get_analyst_data(symbol)
        
        if analyst_data:
            # 评级分布
            ratings = {
                '强烈买入': analyst_data.get('strongBuy', 0),
                '买入': analyst_data.get('buy', 0),
                '持有': analyst_data.get('hold', 0),
                '卖出': analyst_data.get('sell', 0),
                '强烈卖出': analyst_data.get('strongSell', 0)
            }
            
            # 计算综合评分
            total_analysts = sum(ratings.values())
            if total_analysts > 0:
                weighted_score = (
                    ratings['强烈买入'] * 5 + 
                    ratings['买入'] * 4 + 
                    ratings['持有'] * 3 + 
                    ratings['卖出'] * 2 + 
                    ratings['强烈卖出'] * 1
                ) / total_analysts
                
                if weighted_score >= 4.5:
                    consensus = "强烈买入 🚀"
                    color = "green"
                elif weighted_score >= 3.5:
                    consensus = "买入 📈"
                    color = "blue"
                elif weighted_score >= 2.5:
                    consensus = "持有 ➡️"
                    color = "orange"
                else:
                    consensus = "卖出 📉"
                    color = "red"
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("分析师共识", consensus)
                    st.metric("总评级数", f"{total_analysts} 位分析师")
                    st.metric("综合评分", f"{weighted_score:.1f}/5.0")
                
                with col2:
                    # 评级分布图
                    fig_ratings = px.bar(
                        x=list(ratings.keys()),
                        y=list(ratings.values()),
                        title="分析师评级分布",
                        color=list(ratings.values()),
                        color_continuous_scale='RdYlGn'
                    )
                    fig_ratings.update_layout(height=300)
                    st.plotly_chart(fig_ratings, use_container_width=True)
        else:
            st.info("🎯 暂无分析师评级数据")
        
        # API使用统计
        st.markdown("---")
        st.subheader("📊 API使用状态")
        
        api_info = {
            "数据源": ["Finnhub (实时)", "Yahoo Finance (历史)", "内置计算 (技术指标)"],
            "更新频率": ["5秒", "15秒", "实时计算"],
            "数据类型": ["实时报价、新闻、内幕交易", "K线数据、成交量", "RSI、MACD、布林带等"]
        }
        
        api_df = pd.DataFrame(api_info)
        st.dataframe(api_df, use_container_width=True)
        
        # 数据质量对比
        st.info("""
        🌟 **付费API vs 免费数据对比**:
        - **实时性**: Finnhub API 实时 vs Yahoo Finance 15-20分钟延迟
        - **数据丰富度**: 包含内幕交易、新闻、分析师评级 vs 仅基础价格数据
        - **准确性**: 交易所直连数据 vs 第三方聚合数据
        - **更新频率**: 秒级更新 vs 分钟级更新
        """)
    
    with tab6:
        st.subheader("🎯 智能选股与交易信号")
        
        # 选股控制面板
        col1, col2, col3 = st.columns(3)
        
        with col1:
            scan_type = st.selectbox(
                "选股策略",
                options=["all", "strong_buy", "buy", "oversold", "breakout"],
                index=0,
                format_func=lambda x: {
                    "all": "全市场扫描",
                    "strong_buy": "强烈买入信号", 
                    "buy": "买入信号",
                    "oversold": "超卖反弹",
                    "breakout": "放量突破"
                }.get(x, x)
            )
        
        with col2:
            scan_universe = st.selectbox(
                "扫描范围",
                options=[
                    "watchlist", "sp500", "nasdaq100", "dow30", "russell2000", 
                    "comprehensive", "mega_scan", "sector_rotation",
                    "mega_cap", "large_cap", "mid_cap", "small_cap",
                    "tech_expanded", "finance", "healthcare", "energy",
                    "growth", "value", "dividend", "momentum",
                    "ai_ml", "cloud", "cybersecurity", "biotech", "clean_energy",
                    "meme_stocks", "chinese_adrs", "trending"
                ],
                format_func=lambda x: {
                    "watchlist": "📋 观察列表 (20只)",
                    "sp500": "🏆 标普500指数 (500只)",
                    "nasdaq100": "🚀 纳斯达克100 (100只)",
                    "dow30": "🏭 道琼斯30 (30只)",
                    "russell2000": "📈 罗素2000小盘股 (200只)",
                    "comprehensive": "🎯 全面扫描 (500+只)",
                    "mega_scan": "🔥 超大范围扫描 (2000+只)",
                    "sector_rotation": "🔄 行业轮动 (11个行业)",
                    "mega_cap": "💰 超大盘股 (>1000亿市值)",
                    "large_cap": "🏢 大盘股 (100-1000亿)",
                    "mid_cap": "🏬 中盘股 (20-100亿)",
                    "small_cap": "🏪 小盘股 (2-20亿)",
                    "tech_expanded": "💻 科技板块扩展 (100+只)",
                    "finance": "🏦 金融板块 (80+只)",
                    "healthcare": "🏥 医疗健康 (60+只)",
                    "energy": "⚡ 能源板块 (50+只)",
                    "growth": "📈 成长股 (40只)",
                    "value": "💎 价值股 (30只)",
                    "dividend": "💵 高股息股 (30只)",
                    "momentum": "🚀 动量股 (30只)",
                    "ai_ml": "🤖 AI人工智能 (30只)",
                    "cloud": "☁️ 云计算 (20只)",
                    "cybersecurity": "🔒 网络安全 (20只)",
                    "biotech": "🧬 生物技术 (30只)",
                    "clean_energy": "🌱 清洁能源 (30只)",
                    "meme_stocks": "🔥 Meme热门股 (30只)",
                    "chinese_adrs": "🇨🇳 中概股ADR (30只)",
                    "trending": "📊 当前热门 (20只)"
                }.get(x, x)
            )
        
        with col3:
            if st.button("🔍 开始扫描", type="primary"):
                st.session_state.start_scan = True
        
        # 显示扫描结果
        if hasattr(st.session_state, 'start_scan') and st.session_state.start_scan:
            # 显示扫描范围信息
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            with st.spinner(f"🔍 正在扫描 {scan_universe} 股票池..."):
                
                # 获取扫描股票列表
                from stock_universe import StockUniverse
                stock_universe = StockUniverse(config)
                
                if scan_universe == "watchlist":
                    scan_symbols = config.WATCHLIST[:20]  # 限制20只避免超时
                else:
                    # 使用扩展的股票池
                    scan_symbols = stock_universe.create_custom_watchlist(
                        mode=scan_universe, 
                        limit=200 if scan_universe in ["mega_scan", "comprehensive"] else 100
                    )
                    
                    # 如果返回空列表，使用备选方案
                    if not scan_symbols:
                        scan_symbols = config.WATCHLIST[:20]
                
                # 显示扫描信息
                progress_text.text(f"📊 扫描范围: {len(scan_symbols)} 只股票")
                progress_bar.progress(0.3)
                
                # 执行扫描
                scan_results = stock_scanner.scan_universe(scan_symbols, scan_type)
                
                progress_bar.progress(1.0)
                progress_text.text(f"✅ 扫描完成: {len(scan_symbols)} 只股票")
                
                st.session_state.scan_results = scan_results
                st.session_state.start_scan = False
        
        # 显示扫描结果
        if hasattr(st.session_state, 'scan_results') and not st.session_state.scan_results.empty:
            results_df = st.session_state.scan_results
            
            st.success(f"✅ 发现 {len(results_df)} 只符合条件的股票")
            
            # 概览统计
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                strong_buy_count = len(results_df[results_df['signal_strength'] == 'STRONG_BUY'])
                st.metric("强烈买入", strong_buy_count)
            
            with col2:
                buy_count = len(results_df[results_df['signal_strength'] == 'BUY'])
                st.metric("买入", buy_count)
            
            with col3:
                oversold_count = len(results_df[results_df['RSI'] < 30])
                st.metric("超卖机会", oversold_count)
            
            with col4:
                breakout_count = len(results_df[results_df['volume_ratio'] > 2.0])
                st.metric("放量突破", breakout_count)
            
            # 详细结果表格
            st.subheader("📊 详细选股结果")
            
            # 格式化显示数据
            display_df = results_df.copy()
            display_df['当前价格'] = display_df['current_price'].apply(lambda x: f"${x:.2f}")
            display_df['信号强度'] = display_df['signal_strength']
            display_df['综合评分'] = display_df['total_score']
            display_df['RSI'] = display_df['RSI'].apply(lambda x: f"{x:.1f}")
            display_df['成交量比'] = display_df['volume_ratio'].apply(lambda x: f"{x:.1f}x")
            display_df['日涨跌%'] = display_df['price_change_1d'].apply(lambda x: f"{x:.2f}%")
            display_df['入场点'] = display_df['entry_point'].apply(lambda x: f"${x:.2f}")
            display_df['止损点'] = display_df['stop_loss'].apply(lambda x: f"${x:.2f}")
            display_df['止盈1'] = display_df['take_profit_1'].apply(lambda x: f"${x:.2f}")
            display_df['风险回报比'] = display_df['risk_reward_ratio'].apply(lambda x: f"1:{x:.1f}")
            
            # 选择要显示的列
            display_columns = [
                'symbol', '当前价格', '信号强度', '综合评分', 'RSI', 
                '成交量比', '日涨跌%', '入场点', '止损点', '止盈1', '风险回报比'
            ]
            
            st.dataframe(
                display_df[display_columns],
                use_container_width=True,
                height=400
            )
            
            # 选择股票查看详细信号
            if len(results_df) > 0:
                st.subheader("🎯 详细交易信号")
                
                selected_symbol = st.selectbox(
                    "选择股票查看详细信号",
                    options=results_df['symbol'].tolist(),
                    key="detail_symbol"
                )
                
                if selected_symbol:
                    selected_stock = results_df[results_df['symbol'] == selected_symbol].iloc[0]
                    
                    # 显示详细交易建议
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📈 买入信号分析")
                        
                        # 信号强度颜色
                        signal_color = {
                            'STRONG_BUY': '🟢',
                            'BUY': '🔵', 
                            'WEAK_BUY': '🟡',
                            'NEUTRAL': '⚪',
                            'WEAK_SELL': '🟠',
                            'SELL': '🔴',
                            'STRONG_SELL': '⚫'
                        }.get(selected_stock['signal_strength'], '⚪')
                        
                        st.markdown(f"""
                        **交易建议**: {signal_color} {selected_stock['signal_strength']}
                        
                        **技术指标分析**:
                        - RSI: {selected_stock['RSI']:.1f} ({('超卖' if selected_stock['RSI'] < 30 else '超买' if selected_stock['RSI'] > 70 else '正常')})
                        - MACD信号: {selected_stock['MACD_signal']}
                        - 成交量比率: {selected_stock['volume_ratio']:.1f}x
                        - VWAP位置: {selected_stock['vwap_position']}
                        
                        **基本面信号**:
                        - 内幕交易: {selected_stock['insider_signal']}
                        - 新闻情绪: {selected_stock['news_sentiment']}
                        - 分析师评级: {selected_stock['analyst_rating']}
                        """)
                    
                    with col2:
                        st.markdown("### 💰 交易执行计划")
                        
                        st.markdown(f"""
                        **入场策略**:
                        - 入场价位: ${selected_stock['entry_point']:.2f}
                        - 建议仓位: 2-5% (根据风险承受能力调整)
                        
                        **风险管理**:
                        - 止损价位: ${selected_stock['stop_loss']:.2f}
                        - 止盈目标1: ${selected_stock['take_profit_1']:.2f} 
                        - 止盈目标2: ${selected_stock['take_profit_2']:.2f}
                        - 风险回报比: 1:{selected_stock['risk_reward_ratio']:.1f}
                        
                        **操作建议**:
                        """)
                        
                        # 具体操作建议
                        if selected_stock['signal_strength'] in ['STRONG_BUY', 'BUY']:
                            st.success("""
                            ✅ **建议操作**: 可考虑买入
                            - 分批建仓，不要一次性全仓
                            - 严格执行止损计划
                            - 达到止盈1后可减仓一半
                            """)
                        elif selected_stock['signal_strength'] in ['STRONG_SELL', 'SELL']:
                            st.error("""
                            ❌ **建议操作**: 避免买入/考虑卖出
                            - 如已持有可考虑减仓
                            - 等待更好的入场时机
                            """)
                        else:
                            st.info("""
                            ⚪ **建议操作**: 观望
                            - 信号不够明确，建议观望
                            - 等待更强的技术信号
                            """)
                        
                        # 风险提醒
                        st.warning("""
                        ⚠️ **风险提醒**:
                        - 本分析仅供参考，不构成投资建议
                        - 请结合自身风险承受能力做出决策
                        - 务必设置止损，控制风险
                        """)
        
        # 如果没有扫描结果，显示示例
        elif not hasattr(st.session_state, 'scan_results'):
            st.info("👆 点击「开始扫描」按钮来发现交易机会")
            
            # 显示功能介绍
            st.markdown("""
            ### 🎯 智能选股功能特色 (扩展版)
            
            **多指标共振策略** (历史胜率79.4%):
            - ✅ RSI超卖反弹信号
            - ✅ MACD金叉确认
            - ✅ 布林带支撑位买入
            - ✅ 放量突破验证
            - ✅ EMA趋势确认
            
            **🚀 扩展扫描范围** (新增):
            - 📈 **2000+只股票池**: 覆盖全美股市场
            - 🏆 **多指数支持**: S&P500、纳斯达克100、罗素2000
            - 🏭 **11个行业板块**: 科技、金融、医疗、能源等
            - 💰 **市值分层扫描**: 超大盘、大盘、中盘、小盘
            - 🤖 **新兴科技主题**: AI、云计算、生物技术、清洁能源
            - 🔥 **热门主题**: Meme股、中概股、IPO股票
            - 🎯 **智能组合**: 全面扫描、超大范围、行业轮动
            
            **基本面加分项**:
            - 🕵️ 内幕交易监控
            - 📰 新闻情绪分析
            - 🎯 分析师评级
            - 📊 机构资金流向
            
            **风险管理系统**:
            - 🛡️ ATR动态止损
            - 📈 多目标止盈
            - ⚖️ 风险回报比计算
            - 📊 仓位管理建议
            
            **选股策略说明**:
            - **全市场扫描**: 综合评分排序
            - **强烈买入**: 8分以上高分股票
            - **买入信号**: 5-8分优质机会
            - **超卖反弹**: RSI<30的反弹机会
            - **放量突破**: 成交量>2倍的突破股
            """)

else:
    st.error(f"无法获取 {symbol} 的数据，请检查股票代码是否正确")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🚀 华尔街母鸡 - 专业级量化交易系统</p>
    <p>📊 数据来源: Finnhub API (实时) + Yahoo Finance (历史) + 内置技术指标</p>
    <p>🔥 核心功能: 实时报价 | 内幕交易 | 新闻情绪 | 分析师评级 | 智能选股 | 交易信号</p>
    <p>🎯 选股策略: 79.4%胜率RSI + 多指标共振 + ATR风险管理</p>
    <p>⚠️ 投资有风险，入市需谨慎。本系统仅供参考，不构成投资建议。</p>
</div>
""", unsafe_allow_html=True)