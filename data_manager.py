# data_manager.py - 数据管理器
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 尝试导入talib，如果失败则使用替代方案
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("⚠️ TA-Lib未安装，使用内置指标计算")

class DataManager:
    def __init__(self, config):
        self.config = config
        self.cache = {}
        
    def get_stock_data(self, symbol, period='3mo'):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty or len(df) < 50:
                return None
            
            df = self._calculate_indicators(df)
            return df
            
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
            return None
    
    def _calculate_indicators(self, df):
        """计算全套技术指标"""
        # 基础移动平均线系统
        df['EMA12'] = df['Close'].ewm(span=12).mean()
        df['EMA26'] = df['Close'].ewm(span=26).mean()
        df['EMA50'] = df['Close'].ewm(span=self.config.EMA_SHORT).mean()
        df['EMA200'] = df['Close'].ewm(span=self.config.EMA_LONG).mean()
        
        # RSI指标 (14周期)
        if TALIB_AVAILABLE:
            df['RSI'] = talib.RSI(df['Close'].values, timeperiod=14)
        else:
            df['RSI'] = self._calculate_rsi(df['Close'])
        
        # 布林带 (20, 2)
        df = self._calculate_bollinger_bands(df)
        
        # MACD - 两套参数
        df = self._calculate_macd_standard(df)  # 标准参数
        df = self._calculate_macd_raschke(df)   # Linda Raschke参数
        
        # ATR - 平均真实波幅
        if TALIB_AVAILABLE:
            df['ATR'] = talib.ATR(df['High'].values, df['Low'].values, df['Close'].values, timeperiod=14)
        else:
            df['ATR'] = self._calculate_atr(df)
        
        # 成交量指标
        df = self._calculate_volume_indicators(df)
        
        # VWAP - 成交量加权平均价
        df['VWAP'] = self._calculate_vwap(df)
        
        # 支撑阻力位
        df = self._calculate_support_resistance(df)
        
        # ADX - 趋势强度指标
        if TALIB_AVAILABLE:
            df['ADX'] = talib.ADX(df['High'].values, df['Low'].values, df['Close'].values, timeperiod=14)
            df['+DI'] = talib.PLUS_DI(df['High'].values, df['Low'].values, df['Close'].values, timeperiod=14)
            df['-DI'] = talib.MINUS_DI(df['High'].values, df['Low'].values, df['Close'].values, timeperiod=14)
        else:
            df['ADX'] = 25  # 默认中性值
            df['+DI'] = 25  # 简化处理
            df['-DI'] = 25
        
        # 随机指标 (Stochastic)
        if TALIB_AVAILABLE:
            df['%K'], df['%D'] = talib.STOCH(df['High'].values, df['Low'].values, df['Close'].values, 
                                            fastk_period=14, slowk_period=3, slowd_period=3)
            # 威廉指标 (Williams %R)
            df['Williams_%R'] = talib.WILLR(df['High'].values, df['Low'].values, df['Close'].values, timeperiod=14)
            # MFI - 资金流量指标
            df['MFI'] = talib.MFI(df['High'].values, df['Low'].values, df['Close'].values, df['Volume'].values, timeperiod=14)
        else:
            # 简化的随机指标计算
            df['%K'] = self._calculate_stochastic_k(df)
            df['%D'] = df['%K'].rolling(3).mean()
            df['Williams_%R'] = self._calculate_williams_r(df)
            df['MFI'] = self._calculate_mfi_simple(df)
        
        # 肯特纳通道 (Keltner Channel)
        df = self._calculate_keltner_channel(df)
        
        # 唐奇安通道 (Donchian Channel)
        df = self._calculate_donchian_channel(df)
        
        # Parabolic SAR
        if TALIB_AVAILABLE:
            df['SAR'] = talib.SAR(df['High'].values, df['Low'].values, acceleration=0.02, maximum=0.2)
        else:
            df['SAR'] = df['Close'] * 0.98  # 简化处理
        
        # SuperTrend指标
        df = self._calculate_supertrend(df)
        
        # 一目均衡表 (Ichimoku)
        df = self._calculate_ichimoku(df)
        
        # CMF - Chaikin资金流
        df = self._calculate_cmf(df)
        
        # 成交量加权移动平均 (VWMA)
        df['VWMA'] = self._calculate_vwma(df)
        
        # 自定义评分系统
        df = self._calculate_momentum_score(df)
        
        df['close'] = df['Close']
        return df
    
    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_bollinger_bands(self, df):
        sma = df['Close'].rolling(window=self.config.BOLLINGER_PERIOD).mean()
        std = df['Close'].rolling(window=self.config.BOLLINGER_PERIOD).std()
        
        df['BB_upper'] = sma + (std * self.config.BOLLINGER_STD)
        df['BB_middle'] = sma
        df['BB_lower'] = sma - (std * self.config.BOLLINGER_STD)
        return df
    
    def _calculate_macd_standard(self, df):
        """标准MACD参数 (12, 26, 9)"""
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        
        df['MACD'] = ema12 - ema26
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        return df
    
    def _calculate_macd_raschke(self, df):
        """Linda Raschke MACD参数 (3, 10, 16) - 更灵敏"""
        ema3 = df['Close'].ewm(span=3).mean()
        ema10 = df['Close'].ewm(span=10).mean()
        
        df['MACD_fast'] = ema3 - ema10
        df['MACD_fast_signal'] = df['MACD_fast'].ewm(span=16).mean()
        df['MACD_fast_histogram'] = df['MACD_fast'] - df['MACD_fast_signal']
        return df
    
    def _calculate_atr(self, df):
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean()
        return atr
    
    def get_market_sentiment(self):
        try:
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="5d")
            
            if not vix_data.empty:
                current_vix = vix_data['Close'].iloc[-1]
                vix_signal = self._interpret_vix(current_vix)
            else:
                current_vix = 20.0
                vix_signal = "中性"
            
            return {
                'VIX': {
                    'value': current_vix,
                    'signal': vix_signal
                }
            }
            
        except Exception as e:
            return {
                'VIX': {'value': 20.0, 'signal': '中性'}
            }
    
    def _interpret_vix(self, vix_value):
        if vix_value < 15:
            return "极度乐观"
        elif vix_value < 20:
            return "乐观"
        elif vix_value < 25:
            return "中性"
        elif vix_value < 30:
            return "担忧"
        else:
            return "恐慌"
    
    def get_real_time_price(self, symbol):
        """使用Finnhub获取实时价格"""
        try:
            url = f"{self.config.FINNHUB_BASE_URL}/quote"
            params = {
                'symbol': symbol,
                'token': self.config.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': data.get('c', 0),  # current price
                    'change': data.get('d', 0),  # change
                    'change_percent': data.get('dp', 0),  # change percent
                    'high': data.get('h', 0),  # high
                    'low': data.get('l', 0),  # low
                    'open': data.get('o', 0),  # open
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"Finnhub API错误: {e}")
        
        # 备用yfinance
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2d", interval="1h")
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                previous_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
                change = current_price - previous_price
                change_percent = (change / previous_price * 100) if previous_price != 0 else 0
                
                return {
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'high': data['High'].iloc[-1],
                    'low': data['Low'].iloc[-1],
                    'open': data['Open'].iloc[-1],
                    'timestamp': datetime.now()
                }
        except:
            pass
        
        return None
    
    def get_insider_trading(self, symbol):
        """使用Finnhub获取内幕交易数据"""
        try:
            # 获取过去30天的内幕交易
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.config.FINNHUB_BASE_URL}/stock/insider-transactions"
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': self.config.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                trades = []
                
                for trade in data.get('data', [])[:5]:  # 最近5笔交易
                    trades.append({
                        'name': trade.get('name', 'Unknown'),
                        'action': 'BUY' if trade.get('transactionCode') in ['P', 'A'] else 'SELL',
                        'value': trade.get('transactionValue', 0),
                        'shares': trade.get('share', 0),
                        'date': trade.get('transactionDate', '')
                    })
                
                return trades
                
        except Exception as e:
            print(f"获取内幕交易失败: {e}")
        
        # 返回空列表而不是模拟数据
        return []
    
    def _calculate_volume_indicators(self, df):
        """成交量相关指标"""
        # 基础成交量指标
        df['volume_avg'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_avg']
        
        # OBV - 能量潮
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        return df
    
    def _calculate_vwap(self, df):
        """VWAP - 成交量加权平均价"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        return vwap
    
    def _calculate_support_resistance(self, df):
        """支撑阻力位计算"""
        # 枢轴点 (Pivot Points)
        df['pivot_point'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['resistance_1'] = 2 * df['pivot_point'] - df['Low']
        df['support_1'] = 2 * df['pivot_point'] - df['High']
        df['resistance_2'] = df['pivot_point'] + (df['High'] - df['Low'])
        df['support_2'] = df['pivot_point'] - (df['High'] - df['Low'])
        
        # 前期高低点
        df['resistance_20d'] = df['High'].rolling(20).max()
        df['support_20d'] = df['Low'].rolling(20).min()
        df['resistance_52w'] = df['High'].rolling(252).max()
        df['support_52w'] = df['Low'].rolling(252).min()
        
        return df
    
    def _calculate_keltner_channel(self, df):
        """肯特纳通道"""
        middle = df['Close'].ewm(span=20).mean()
        atr = df['ATR']
        
        df['KC_upper'] = middle + (2 * atr)
        df['KC_middle'] = middle
        df['KC_lower'] = middle - (2 * atr)
        
        return df
    
    def _calculate_donchian_channel(self, df):
        """唐奇安通道"""
        df['DC_upper'] = df['High'].rolling(20).max()
        df['DC_lower'] = df['Low'].rolling(20).min()
        df['DC_middle'] = (df['DC_upper'] + df['DC_lower']) / 2
        
        return df
    
    def _calculate_supertrend(self, df, period=10, multiplier=3):
        """SuperTrend指标"""
        hl2 = (df['High'] + df['Low']) / 2
        atr = df['ATR']
        
        # 计算基础上下轨
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        # 初始化
        df['ST_upper'] = upper_band
        df['ST_lower'] = lower_band
        df['SuperTrend'] = 0.0
        df['ST_direction'] = 1
        
        for i in range(1, len(df)):
            # 调整上下轨
            if upper_band.iloc[i] < df['ST_upper'].iloc[i-1] or df['Close'].iloc[i-1] > df['ST_upper'].iloc[i-1]:
                df.loc[df.index[i], 'ST_upper'] = upper_band.iloc[i]
            else:
                df.loc[df.index[i], 'ST_upper'] = df['ST_upper'].iloc[i-1]
                
            if lower_band.iloc[i] > df['ST_lower'].iloc[i-1] or df['Close'].iloc[i-1] < df['ST_lower'].iloc[i-1]:
                df.loc[df.index[i], 'ST_lower'] = lower_band.iloc[i]
            else:
                df.loc[df.index[i], 'ST_lower'] = df['ST_lower'].iloc[i-1]
            
            # 计算SuperTrend
            if df['Close'].iloc[i] <= df['ST_lower'].iloc[i]:
                df.loc[df.index[i], 'ST_direction'] = -1
            elif df['Close'].iloc[i] >= df['ST_upper'].iloc[i]:
                df.loc[df.index[i], 'ST_direction'] = 1
            else:
                df.loc[df.index[i], 'ST_direction'] = df['ST_direction'].iloc[i-1]
            
            if df['ST_direction'].iloc[i] == 1:
                df.loc[df.index[i], 'SuperTrend'] = df['ST_lower'].iloc[i]
            else:
                df.loc[df.index[i], 'SuperTrend'] = df['ST_upper'].iloc[i]
        
        return df
    
    def _calculate_ichimoku(self, df):
        """一目均衡表"""
        # 转换线 (Tenkan-sen): 9期高低点平均
        high_9 = df['High'].rolling(9).max()
        low_9 = df['Low'].rolling(9).min()
        df['tenkan_sen'] = (high_9 + low_9) / 2
        
        # 基准线 (Kijun-sen): 26期高低点平均
        high_26 = df['High'].rolling(26).max()
        low_26 = df['Low'].rolling(26).min()
        df['kijun_sen'] = (high_26 + low_26) / 2
        
        # 先行带A (Senkou Span A): (转换线 + 基准线) / 2，向前移26期
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        
        # 先行带B (Senkou Span B): 52期高低点平均，向前移26期
        high_52 = df['High'].rolling(52).max()
        low_52 = df['Low'].rolling(52).min()
        df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)
        
        # 滞后线 (Chikou Span): 收盘价向后移26期
        df['chikou_span'] = df['Close'].shift(-26)
        
        return df
    
    def _calculate_cmf(self, df, period=20):
        """Chaikin资金流"""
        money_flow_multiplier = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        money_flow_volume = money_flow_multiplier * df['Volume']
        
        cmf = money_flow_volume.rolling(period).sum() / df['Volume'].rolling(period).sum()
        df['CMF'] = cmf.fillna(0)
        
        return df
    
    def _calculate_vwma(self, df, period=20):
        """成交量加权移动平均"""
        vwma = (df['Close'] * df['Volume']).rolling(period).sum() / df['Volume'].rolling(period).sum()
        return vwma
    
    def _calculate_momentum_score(self, df):
        """自定义动量评分系统"""
        score = 0
        
        # 技术面评分 (最高6分)
        conditions = [
            df['RSI'] < 30,  # RSI超卖 +2分
            df['RSI'] > 70,  # RSI超买 -2分
            df['MACD'] > df['MACD_signal'],  # MACD金叉 +1分
            df['EMA12'] > df['EMA26'],  # 短期EMA金叉 +1分
            df['Close'] > df['EMA50'],  # 价格在EMA50之上 +1分
            df['Close'] > df['EMA200'],  # 价格在EMA200之上 +1分
        ]
        
        weights = [2, -2, 1, 1, 1, 1]
        
        for condition, weight in zip(conditions, weights):
            score += condition.astype(int) * weight
        
        # 成交量评分 (最高2分)
        score += (df['volume_ratio'] > 2).astype(int) * 2  # 放量 +2分
        score += (df['volume_ratio'] < 0.5).astype(int) * (-1)  # 缩量 -1分
        
        # 趋势强度评分 (最高2分)
        score += (df['ADX'] > 25).astype(int) * 1  # 强趋势 +1分
        score += (df['+DI'] > df['-DI']).astype(int) * 1  # 上升趋势 +1分
        
        # 超买超卖评分
        score += (df['%K'] < 20).astype(int) * 1  # 随机指标超卖 +1分
        score += (df['%K'] > 80).astype(int) * (-1)  # 随机指标超买 -1分
        
        df['momentum_score'] = score
        
        # 综合信号强度
        df['signal_strength'] = np.where(df['momentum_score'] >= 6, 'STRONG_BUY',
                                np.where(df['momentum_score'] >= 3, 'BUY',
                                np.where(df['momentum_score'] <= -6, 'STRONG_SELL',
                                np.where(df['momentum_score'] <= -3, 'SELL', 'NEUTRAL'))))
        
        return df
    
    def get_company_news(self, symbol, days=7):
        """获取公司新闻"""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.config.FINNHUB_BASE_URL}/company-news"
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': self.config.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data[:5]  # 返回最新5条新闻
                
        except Exception as e:
            print(f"获取新闻失败: {e}")
        
        return []
    
    def get_analyst_recommendations(self, symbol):
        """获取分析师建议"""
        try:
            url = f"{self.config.FINNHUB_BASE_URL}/stock/recommendation"
            params = {
                'symbol': symbol,
                'token': self.config.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    latest = data[0]
                    return {
                        'buy': latest.get('buy', 0),
                        'hold': latest.get('hold', 0),
                        'sell': latest.get('sell', 0),
                        'strongBuy': latest.get('strongBuy', 0),
                        'strongSell': latest.get('strongSell', 0),
                        'period': latest.get('period', '')
                    }
                    
        except Exception as e:
            print(f"获取分析师建议失败: {e}")
        
        return None
    
    def _calculate_stochastic_k(self, df, period=14):
        """简化的随机指标%K计算"""
        low_min = df['Low'].rolling(period).min()
        high_max = df['High'].rolling(period).max()
        k_percent = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        return k_percent.fillna(50)
    
    def _calculate_williams_r(self, df, period=14):
        """简化的威廉指标计算"""
        high_max = df['High'].rolling(period).max()
        low_min = df['Low'].rolling(period).min()
        wr = -100 * ((high_max - df['Close']) / (high_max - low_min))
        return wr.fillna(-50)
    
    def _calculate_mfi_simple(self, df, period=14):
        """简化的资金流量指标计算"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(period).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(period).sum()
        
        mfi = 100 - (100 / (1 + positive_flow / negative_flow))
        return mfi.fillna(50)
    
    def get_vix_sentiment(self):
        """获取VIX恐慌贪婪指数"""
        try:
            import yfinance as yf
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="5d")
            
            if not vix_data.empty:
                current_vix = vix_data['Close'].iloc[-1]
                
                # VIX情绪判断
                if current_vix < 15:
                    sentiment = "极度贪婪"
                    signal = "SELL"
                elif current_vix < 20:
                    sentiment = "贪婪"
                    signal = "CAUTION"
                elif current_vix < 25:
                    sentiment = "中性"
                    signal = "NEUTRAL"
                elif current_vix < 30:
                    sentiment = "恐惧"
                    signal = "BUY"
                else:
                    sentiment = "极度恐惧"
                    signal = "STRONG_BUY"
                
                return {
                    'value': current_vix,
                    'sentiment': sentiment,
                    'signal': signal
                }
        except Exception as e:
            print(f"获取VIX数据失败: {e}")
        
        return {'value': 20.0, 'sentiment': '中性', 'signal': 'NEUTRAL'}