# indicators_config.py - 技术指标配置文件
"""
华尔街母鸡 - 全套技术指标参数配置
包含79.4%胜率的RSI、最优MACD参数等经过验证的指标设置
"""

class TechnicalIndicators:
    """技术指标参数配置类"""
    
    # === 基础移动平均线系统 ===
    EMA_FAST = 12       # 短期EMA
    EMA_SLOW = 26       # 长期EMA  
    EMA_MEDIUM = 50     # 中期EMA
    EMA_LONG = 200      # 长期EMA
    
    # === RSI - 相对强弱指标 (79.4%胜率) ===
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30   # 超卖线
    RSI_OVERBOUGHT = 70 # 超买线
    
    # === MACD - 双参数系统 ===
    # 标准参数
    MACD_FAST = 12
    MACD_SLOW = 26  
    MACD_SIGNAL = 9
    
    # Linda Raschke参数 (更灵敏，EMA回报率1.60)
    MACD_RASCHKE_FAST = 3
    MACD_RASCHKE_SLOW = 10
    MACD_RASCHKE_SIGNAL = 16
    
    # === 布林带 - 77.8%成功率 ===
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2   # 标准差倍数
    
    # === ATR - 平均真实波幅 ===
    ATR_PERIOD = 14
    ATR_STOP_MULTIPLIER = 2.0   # 止损倍数
    ATR_BREAKOUT_MULTIPLIER = 1.0  # 突破确认倍数
    
    # === 成交量指标 ===
    VOLUME_MA_PERIOD = 20
    VOLUME_RATIO_ALERT = 2.0    # 放量警报阈值
    VOLUME_RATIO_LOW = 0.5      # 缩量阈值
    
    # === ADX - 趋势强度 ===
    ADX_PERIOD = 14
    ADX_TREND_THRESHOLD = 25    # 趋势明显阈值
    ADX_SIDEWAYS_THRESHOLD = 20 # 震荡市阈值
    
    # === 随机指标 (Stochastic) ===
    STOCH_K_PERIOD = 14
    STOCH_K_SMOOTH = 3
    STOCH_D_SMOOTH = 3
    STOCH_OVERSOLD = 20
    STOCH_OVERBOUGHT = 80
    
    # === 威廉指标 (Williams %R) ===
    WILLR_PERIOD = 14
    WILLR_OVERSOLD = -80
    WILLR_OVERBOUGHT = -20
    
    # === MFI - 资金流量指标 ===
    MFI_PERIOD = 14
    MFI_OVERSOLD = 20
    MFI_OVERBOUGHT = 80
    
    # === 肯特纳通道 ===
    KC_PERIOD = 20
    KC_MULTIPLIER = 2
    
    # === 唐奇安通道 (海龟交易法则) ===
    DC_PERIOD = 20
    
    # === Parabolic SAR ===
    SAR_ACCELERATION = 0.02
    SAR_MAXIMUM = 0.2
    
    # === SuperTrend ===
    ST_PERIOD = 10
    ST_MULTIPLIER = 3
    
    # === 一目均衡表 (Ichimoku) ===
    ICHIMOKU_TENKAN = 9     # 转换线
    ICHIMOKU_KIJUN = 26     # 基准线
    ICHIMOKU_SENKOU = 52    # 先行带B
    ICHIMOKU_DISPLACEMENT = 26  # 位移
    
    # === CMF - Chaikin资金流 ===
    CMF_PERIOD = 20
    
    # === VWMA - 成交量加权移动平均 ===
    VWMA_PERIOD = 20
    
    # === 斐波那契回撤 ===
    FIBONACCI_PERIOD = 50
    FIBONACCI_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 1.0]
    
    # === 图表形态检测 ===
    PATTERN_WINDOW = 20
    PATTERN_MIN_BARS = 5

class MarketSentiment:
    """市场情绪指标配置"""
    
    # === VIX - 波动率指数 ===
    VIX_EXTREME_FEAR = 50      # 极度恐慌
    VIX_FEAR = 25              # 恐慌
    VIX_NORMAL_HIGH = 20       # 正常偏高
    VIX_NORMAL_LOW = 15        # 正常偏低
    VIX_EXTREME_GREED = 10     # 极度贪婪
    
    # === Put/Call比率 ===
    PUT_CALL_EXTREME_FEAR = 1.5     # 恐慌底部
    PUT_CALL_FEAR = 1.1             # 过度悲观
    PUT_CALL_GREED = 0.6            # 过度乐观
    
    # === 恐惧贪婪指数 ===
    FEAR_GREED_EXTREME_FEAR = 25
    FEAR_GREED_FEAR = 45
    FEAR_GREED_NEUTRAL = 55
    FEAR_GREED_GREED = 75
    FEAR_GREED_EXTREME_GREED = 90

class TradingSignals:
    """交易信号配置"""
    
    # === 多指标共振买入信号 (75%+胜率) ===
    CONFLUENCE_SIGNAL_CONDITIONS = {
        'rsi_oversold': True,       # RSI < 30
        'macd_bullish': True,       # MACD金叉
        'bb_support': True,         # 价格触及BB下轨
        'volume_surge': True,       # 成交量 > 2倍均量
        'vix_fear': True           # VIX > 25
    }
    
    # === 自定义评分系统权重 ===
    MOMENTUM_SCORE_WEIGHTS = {
        'rsi_oversold': 2,          # RSI超卖 +2分
        'rsi_overbought': -2,       # RSI超买 -2分
        'macd_bullish': 1,          # MACD金叉 +1分
        'ema_golden_cross': 3,      # EMA金叉 +3分
        'volume_surge': 2,          # 放量 +2分
        'trend_strength': 1,        # 强趋势 +1分
        'stoch_oversold': 1,        # 随机指标超卖 +1分
        'insider_buying': 1,        # 内幕买入 +1分
        'fcf_yield': 1             # 自由现金流收益率 +1分
    }
    
    # === 信号强度阈值 ===
    STRONG_BUY_THRESHOLD = 6
    BUY_THRESHOLD = 3
    NEUTRAL_THRESHOLD = 0
    SELL_THRESHOLD = -3
    STRONG_SELL_THRESHOLD = -6

class RiskManagement:
    """风险管理配置"""
    
    # === 基于ATR的止损止盈 ===
    STOP_LOSS_ATR_MULTIPLIER = 2.0      # 止损: 2倍ATR
    TAKE_PROFIT_ATR_MULTIPLIER = 3.0     # 止盈: 3倍ATR
    
    # === 仓位管理 ===
    MAX_POSITION_SIZE = 0.05            # 单一持仓最大5%
    MAX_SECTOR_EXPOSURE = 0.20          # 单一行业最大20%
    MAX_DAILY_RISK = 0.02               # 单日最大风险2%
    
    # === 波动率调整 ===
    HIGH_VOL_THRESHOLD = 30             # 高波动率阈值(VIX)
    LOW_VOL_THRESHOLD = 15              # 低波动率阈值
    
    HIGH_VOL_POSITION_REDUCTION = 0.5   # 高波动期仓位减半
    LOW_VOL_POSITION_INCREASE = 1.5     # 低波动期仓位增加

class IntradaySettings:
    """日内交易配置"""
    
    # === 时间框架 ===
    TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h']
    DEFAULT_TIMEFRAME = '15m'
    
    # === VWAP配置 ===
    VWAP_DEVIATION_ALERT = 2.0          # VWAP偏离警报(%)
    
    # === 成交量异动 ===
    INTRADAY_VOLUME_ALERT = 3.0         # 日内成交量异动阈值
    PRICE_MOVEMENT_ALERT = 3.0          # 价格异动阈值(%)
    
    # === 实时监控 ===
    REFRESH_INTERVALS = [10, 30, 60, 300]  # 刷新间隔(秒)
    DEFAULT_REFRESH = 30
    
    # === 交易时段 ===
    PREMARKET_START = "04:00"           # 盘前开始
    MARKET_OPEN = "09:30"               # 开盘
    MARKET_CLOSE = "16:00"              # 收盘
    AFTERHOURS_END = "20:00"            # 盘后结束

class AlertThresholds:
    """警报阈值配置"""
    
    # === 技术指标警报 ===
    RSI_EXTREME_OVERSOLD = 20           # RSI极度超卖
    RSI_EXTREME_OVERBOUGHT = 80         # RSI极度超买
    
    # === 成交量警报 ===
    VOLUME_SPIKE_THRESHOLD = 5.0        # 成交量暴增
    VOLUME_DRY_UP_THRESHOLD = 0.3       # 成交量枯竭
    
    # === 价格警报 ===
    PRICE_GAP_THRESHOLD = 5.0           # 价格跳空(%)
    INTRADAY_RANGE_THRESHOLD = 10.0     # 日内波幅(%)
    
    # === 市场警报 ===
    VIX_SPIKE_THRESHOLD = 40            # VIX暴增
    MARKET_BREADTH_THRESHOLD = 0.3      # 市场广度

class BacktestSettings:
    """回测配置"""
    
    # === 回测参数 ===
    INITIAL_CAPITAL = 100000            # 初始资金
    COMMISSION_RATE = 0.001             # 手续费率
    SLIPPAGE_RATE = 0.0005             # 滑点率
    
    # === 基准指标 ===
    BENCHMARK_SYMBOL = "SPY"            # 基准指数
    
    # === 评估指标 ===
    MIN_WIN_RATE = 0.6                 # 最低胜率要求
    MIN_PROFIT_FACTOR = 1.5            # 最低盈利因子
    MAX_DRAWDOWN = 0.15                # 最大回撤限制

# 导出主要配置类
__all__ = [
    'TechnicalIndicators',
    'MarketSentiment', 
    'TradingSignals',
    'RiskManagement',
    'IntradaySettings',
    'AlertThresholds',
    'BacktestSettings'
]