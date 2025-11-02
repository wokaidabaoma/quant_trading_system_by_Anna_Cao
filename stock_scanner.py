# stock_scanner.py - 选股和交易信号生成器
"""
华尔街母鸡 - 智能选股系统
基于79.4%胜率RSI + 多指标共振策略
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import concurrent.futures
import time

class StockScanner:
    def __init__(self, data_manager, config):
        self.data_manager = data_manager
        self.config = config
        
    def scan_universe(self, symbols: List[str], scan_type: str = "all") -> pd.DataFrame:
        """扫描股票池，生成选股结果"""
        print(f"🔍 开始扫描 {len(symbols)} 只股票...")
        
        results = []
        
        # 使用多线程加速扫描
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self._analyze_stock, symbol): symbol 
                for symbol in symbols
            }
            
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"❌ 分析 {symbol} 失败: {e}")
                
                # 添加小延迟避免API限制
                time.sleep(0.1)
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # 根据扫描类型过滤
        if scan_type == "strong_buy":
            df = df[df['signal_strength'] == 'STRONG_BUY']
        elif scan_type == "buy":
            df = df[df['signal_strength'].isin(['STRONG_BUY', 'BUY'])]
        elif scan_type == "oversold":
            df = df[df['RSI'] < 30]
        elif scan_type == "breakout":
            df = df[df['volume_ratio'] > 2.0]
        
        # 按综合评分排序
        df = df.sort_values('total_score', ascending=False)
        
        return df
    
    def _analyze_stock(self, symbol: str) -> Dict:
        """分析单只股票"""
        try:
            # 获取股票数据
            stock_data = self.data_manager.get_stock_data(symbol, period='3mo')
            if stock_data is None or len(stock_data) < 50:
                return None
            
            # 获取实时报价
            real_time_quote = self.data_manager.get_real_time_price(symbol)
            current_price = real_time_quote.get('price') if real_time_quote else stock_data['Close'].iloc[-1]
            
            # 计算交易信号
            signals = self._generate_trading_signals(stock_data)
            
            # 计算综合评分
            total_score = self._calculate_total_score(stock_data, signals)
            
            # 确定信号强度
            signal_strength = self._determine_signal_strength(total_score)
            
            # 计算入场出场点位
            entry_exit = self._calculate_entry_exit_points(stock_data, current_price)
            
            # 获取基本面数据
            fundamental_data = self._get_fundamental_signals(symbol)
            
            return {
                'symbol': symbol,
                'current_price': current_price or 0,
                'total_score': total_score,
                'signal_strength': signal_strength,
                'RSI': stock_data['RSI'].iloc[-1] if 'RSI' in stock_data.columns else 50,
                'MACD_signal': signals.get('macd_signal', 'NEUTRAL'),
                'volume_ratio': stock_data['volume_ratio'].iloc[-1] if 'volume_ratio' in stock_data.columns else 1.0,
                'price_change_1d': ((current_price or 0) / stock_data['Close'].iloc[-2] - 1) * 100 if len(stock_data) > 1 else 0,
                'entry_point': entry_exit['entry_point'],
                'stop_loss': entry_exit['stop_loss'],
                'take_profit_1': entry_exit['take_profit_1'],
                'take_profit_2': entry_exit['take_profit_2'],
                'risk_reward_ratio': entry_exit['risk_reward_ratio'],
                'insider_signal': fundamental_data.get('insider_signal', 'NEUTRAL'),
                'news_sentiment': fundamental_data.get('news_sentiment', 'NEUTRAL'),
                'analyst_rating': fundamental_data.get('analyst_rating', 'HOLD'),
                'vwap_position': 'ABOVE' if current_price > stock_data.get('VWAP', stock_data['Close']).iloc[-1] else 'BELOW',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ 分析 {symbol} 出错: {e}")
            return None
    
    def _generate_trading_signals(self, df: pd.DataFrame) -> Dict:
        """生成交易信号"""
        signals = {}
        
        latest = df.iloc[-1]
        
        # RSI信号 (79.4%胜率策略)
        if latest['RSI'] < 30:
            signals['rsi_signal'] = 'STRONG_BUY'
            signals['rsi_score'] = 3
        elif latest['RSI'] < 40:
            signals['rsi_signal'] = 'BUY'
            signals['rsi_score'] = 2
        elif latest['RSI'] > 70:
            signals['rsi_signal'] = 'STRONG_SELL'
            signals['rsi_score'] = -3
        elif latest['RSI'] > 60:
            signals['rsi_signal'] = 'SELL'
            signals['rsi_score'] = -2
        else:
            signals['rsi_signal'] = 'NEUTRAL'
            signals['rsi_score'] = 0
        
        # MACD信号
        if latest['MACD'] > latest['MACD_signal'] and latest['MACD_histogram'] > 0:
            signals['macd_signal'] = 'BUY'
            signals['macd_score'] = 2
        elif latest['MACD'] < latest['MACD_signal'] and latest['MACD_histogram'] < 0:
            signals['macd_signal'] = 'SELL'
            signals['macd_score'] = -2
        else:
            signals['macd_signal'] = 'NEUTRAL'
            signals['macd_score'] = 0
        
        # EMA趋势信号
        if latest['EMA12'] > latest['EMA26'] > latest['EMA50']:
            signals['trend_signal'] = 'STRONG_BUY'
            signals['trend_score'] = 3
        elif latest['EMA12'] > latest['EMA26']:
            signals['trend_signal'] = 'BUY'
            signals['trend_score'] = 1
        elif latest['EMA12'] < latest['EMA26'] < latest['EMA50']:
            signals['trend_signal'] = 'STRONG_SELL'
            signals['trend_score'] = -3
        else:
            signals['trend_signal'] = 'NEUTRAL'
            signals['trend_score'] = 0
        
        # 布林带信号
        if latest['Close'] < latest['BB_lower'] and latest['RSI'] < 35:
            signals['bb_signal'] = 'STRONG_BUY'
            signals['bb_score'] = 3
        elif latest['Close'] > latest['BB_upper'] and latest['RSI'] > 65:
            signals['bb_signal'] = 'STRONG_SELL'
            signals['bb_score'] = -3
        else:
            signals['bb_signal'] = 'NEUTRAL'
            signals['bb_score'] = 0
        
        # 成交量信号
        if latest['volume_ratio'] > 2.0:
            signals['volume_signal'] = 'BREAKOUT'
            signals['volume_score'] = 2
        elif latest['volume_ratio'] > 1.5:
            signals['volume_signal'] = 'ACTIVE'
            signals['volume_score'] = 1
        elif latest['volume_ratio'] < 0.5:
            signals['volume_signal'] = 'WEAK'
            signals['volume_score'] = -1
        else:
            signals['volume_signal'] = 'NORMAL'
            signals['volume_score'] = 0
        
        return signals
    
    def _calculate_total_score(self, df: pd.DataFrame, signals: Dict) -> float:
        """计算综合评分"""
        score = 0
        
        # 基础技术指标评分
        score += signals.get('rsi_score', 0)
        score += signals.get('macd_score', 0) 
        score += signals.get('trend_score', 0)
        score += signals.get('bb_score', 0)
        score += signals.get('volume_score', 0)
        
        # 额外加分项
        latest = df.iloc[-1]
        
        # 多指标共振加分
        if (signals.get('rsi_score', 0) > 0 and 
            signals.get('macd_score', 0) > 0 and 
            signals.get('trend_score', 0) > 0):
            score += 2  # 共振加分
        
        # ADX趋势强度加分
        if latest.get('ADX', 25) > 25:
            if signals.get('trend_score', 0) > 0:
                score += 1
            elif signals.get('trend_score', 0) < 0:
                score -= 1
        
        # 相对强度加分（价格相对EMA200的位置）
        if latest['Close'] > latest['EMA200']:
            score += 1
        elif latest['Close'] < latest['EMA200']:
            score -= 1
        
        return score
    
    def _determine_signal_strength(self, total_score: float) -> str:
        """确定信号强度"""
        if total_score >= 8:
            return 'STRONG_BUY'
        elif total_score >= 5:
            return 'BUY'
        elif total_score >= 2:
            return 'WEAK_BUY'
        elif total_score <= -8:
            return 'STRONG_SELL'
        elif total_score <= -5:
            return 'SELL'
        elif total_score <= -2:
            return 'WEAK_SELL'
        else:
            return 'NEUTRAL'
    
    def _calculate_entry_exit_points(self, df: pd.DataFrame, current_price: float) -> Dict:
        """计算入场出场点位"""
        latest = df.iloc[-1]
        atr = latest.get('ATR', abs(latest['High'] - latest['Low']))
        
        # 入场点位（当前价格）
        entry_point = current_price
        
        # 止损：2倍ATR
        stop_loss = entry_point - (2 * atr)
        
        # 止盈1：3倍ATR (风险回报比1:1.5)
        take_profit_1 = entry_point + (3 * atr)
        
        # 止盈2：5倍ATR (风险回报比1:2.5) 
        take_profit_2 = entry_point + (5 * atr)
        
        # 计算风险回报比
        risk = entry_point - stop_loss
        reward = take_profit_1 - entry_point
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            'entry_point': entry_point,
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'risk_reward_ratio': risk_reward_ratio,
            'atr_value': atr
        }
    
    def _get_fundamental_signals(self, symbol: str) -> Dict:
        """获取基本面信号"""
        signals = {}
        
        try:
            # 内幕交易信号
            insider_trades = self.data_manager.get_insider_trading(symbol)
            if insider_trades:
                buy_trades = [t for t in insider_trades if t.get('action') == 'BUY']
                sell_trades = [t for t in insider_trades if t.get('action') == 'SELL']
                
                if len(buy_trades) >= 2:
                    signals['insider_signal'] = 'BULLISH'
                elif len(sell_trades) >= 2:
                    signals['insider_signal'] = 'BEARISH'
                else:
                    signals['insider_signal'] = 'NEUTRAL'
            else:
                signals['insider_signal'] = 'NEUTRAL'
            
            # 新闻情绪
            news = self.data_manager.get_company_news(symbol, days=3)
            if news:
                positive_count = 0
                negative_count = 0
                
                for article in news[:3]:
                    headline = article.get('headline', '').lower()
                    if any(word in headline for word in ['beat', 'exceed', 'strong', 'growth', 'profit']):
                        positive_count += 1
                    elif any(word in headline for word in ['miss', 'decline', 'loss', 'weak', 'concern']):
                        negative_count += 1
                
                if positive_count > negative_count:
                    signals['news_sentiment'] = 'POSITIVE'
                elif negative_count > positive_count:
                    signals['news_sentiment'] = 'NEGATIVE'
                else:
                    signals['news_sentiment'] = 'NEUTRAL'
            else:
                signals['news_sentiment'] = 'NEUTRAL'
            
            # 分析师评级
            analyst_data = self.data_manager.get_analyst_recommendations(symbol)
            if analyst_data:
                total = sum([
                    analyst_data.get('strongBuy', 0),
                    analyst_data.get('buy', 0),
                    analyst_data.get('hold', 0),
                    analyst_data.get('sell', 0),
                    analyst_data.get('strongSell', 0)
                ])
                
                if total > 0:
                    weighted_score = (
                        analyst_data.get('strongBuy', 0) * 5 + 
                        analyst_data.get('buy', 0) * 4 + 
                        analyst_data.get('hold', 0) * 3 + 
                        analyst_data.get('sell', 0) * 2 + 
                        analyst_data.get('strongSell', 0) * 1
                    ) / total
                    
                    if weighted_score >= 4.5:
                        signals['analyst_rating'] = 'STRONG_BUY'
                    elif weighted_score >= 3.5:
                        signals['analyst_rating'] = 'BUY'
                    elif weighted_score <= 2.5:
                        signals['analyst_rating'] = 'SELL'
                    else:
                        signals['analyst_rating'] = 'HOLD'
                else:
                    signals['analyst_rating'] = 'HOLD'
            else:
                signals['analyst_rating'] = 'HOLD'
                
        except Exception as e:
            print(f"获取{symbol}基本面数据失败: {e}")
            signals = {
                'insider_signal': 'NEUTRAL',
                'news_sentiment': 'NEUTRAL', 
                'analyst_rating': 'HOLD'
            }
        
        return signals
    
    def generate_watchlist_signals(self, symbols: List[str]) -> pd.DataFrame:
        """为观察列表生成交易信号"""
        print("🎯 生成观察列表交易信号...")
        
        results = []
        for symbol in symbols[:10]:  # 限制前10只股票避免超时
            try:
                result = self._analyze_stock(symbol)
                if result and result['signal_strength'] in ['STRONG_BUY', 'BUY', 'STRONG_SELL', 'SELL']:
                    results.append(result)
                time.sleep(0.2)  # API限制
            except Exception as e:
                print(f"分析{symbol}失败: {e}")
                continue
        
        if results:
            df = pd.DataFrame(results)
            return df.sort_values('total_score', ascending=False)
        else:
            return pd.DataFrame()