# signal_generator.py - 信号生成器
from datetime import datetime

class SignalGenerator:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.signals = []
        
    def scan_for_signals(self, symbol):
        """扫描单个股票的交易信号"""
        signals = []
        
        # 获取数据
        df = self.data_manager.get_stock_data(symbol)
        if df is None or len(df) < 50:
            return signals
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 1. 金叉信号
        if (df['EMA50'].iloc[-3] < df['EMA200'].iloc[-3] and
            df['EMA50'].iloc[-2] < df['EMA200'].iloc[-2] and
            df['EMA50'].iloc[-1] > df['EMA200'].iloc[-1]):
            signals.append({
                'type': 'BUY',
                'reason': '金叉形成',
                'strength': 'STRONG'
            })
        
        # 2. RSI超卖反弹
        if latest['RSI'] < 30 and latest['RSI'] > prev['RSI']:
            signals.append({
                'type': 'BUY',
                'reason': 'RSI超卖反弹',
                'strength': 'MEDIUM'
            })
        
        # 3. 布林带突破
        if (latest['close'] > latest['BB_upper'] and 
            latest['volume_ratio'] > 2):
            signals.append({
                'type': 'BUY',
                'reason': '布林带突破+放量',
                'strength': 'STRONG'
            })
        
        # 4. MACD金叉
        if (prev['MACD'] < prev['MACD_signal'] and
            latest['MACD'] > latest['MACD_signal']):
            signals.append({
                'type': 'BUY',
                'reason': 'MACD金叉',
                'strength': 'MEDIUM'
            })
        
        # 5. 做空信号 - RSI超买
        if latest['RSI'] > 70 and latest['RSI'] < prev['RSI']:
            signals.append({
                'type': 'SHORT',
                'reason': 'RSI超买回落',
                'strength': 'MEDIUM'
            })
        
        # 6. 死叉信号
        if (df['EMA50'].iloc[-3] > df['EMA200'].iloc[-3] and
            df['EMA50'].iloc[-2] > df['EMA200'].iloc[-2] and
            df['EMA50'].iloc[-1] < df['EMA200'].iloc[-1]):
            signals.append({
                'type': 'SHORT',
                'reason': '死叉形成',
                'strength': 'STRONG'
            })
        
        # 整合信号
        if signals:
            # 获取内幕交易
            insider_trades = self.data_manager.get_insider_trading(symbol)
            
            return {
                'symbol': symbol,
                'price': latest['close'],
                'volume_ratio': latest['volume_ratio'],
                'RSI': latest['RSI'],
                'ATR': latest['ATR'],
                'signals': signals,
                'insider_trades': insider_trades,
                'timestamp': datetime.now()
            }
        
        return None
    
    def calculate_position_size(self, signal, account_size, risk_percent=0.02):
        """计算仓位大小和止损"""
        price = signal['price']
        atr = signal['ATR']
        
        # 风险金额
        risk_amount = account_size * risk_percent
        
        # 止损距离（2倍ATR）
        stop_distance = atr * 2
        
        # 计算股数
        shares = int(risk_amount / stop_distance)
        
        # 如果是做空信号，建议反向ETF
        if any(s['type'] == 'SHORT' for s in signal['signals']):
            inverse_etf = self._suggest_inverse_etf(signal['symbol'])
            return {
                'action': 'SHORT',
                'shares': shares,
                'stop_loss': price + stop_distance,  # 做空止损在上方
                'take_profit': price - (stop_distance * 2),  # 2:1风险回报
                'inverse_etf': inverse_etf,
                'position_value': shares * price
            }
        else:
            return {
                'action': 'BUY',
                'shares': shares,
                'stop_loss': price - stop_distance,
                'take_profit': price + (stop_distance * 2),
                'position_value': shares * price
            }
    
    def _suggest_inverse_etf(self, symbol):
        """建议对应的反向ETF"""
        sector_etfs = {
            'AAPL': 'PSQ',  # 科技股 -> 纳斯达克反向
            'MSFT': 'PSQ',
            'GOOGL': 'PSQ',
            'JPM': 'SKF',   # 金融股反向
            'XOM': 'ERY',   # 能源股反向
        }
        
        # 默认建议
        if symbol in sector_etfs:
            return sector_etfs[symbol]
        else:
            return 'SH'  # 标普500反向