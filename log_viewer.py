#!/usr/bin/env python3
# log_viewer.py - 华尔街母鸡日志查看器

import json
import os
from datetime import datetime
import pandas as pd
from collections import defaultdict
import sys

class LogViewer:
    """交易信号日志查看器"""
    
    def __init__(self, log_file="logs/trading_signals.log"):
        self.log_file = log_file
        self.signals = []
        self.load_logs()
    
    def load_logs(self):
        """加载所有日志记录"""
        if not os.path.exists(self.log_file):
            print(f"❌ 日志文件不存在: {self.log_file}")
            return
        
        self.signals = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            signal = json.loads(line.strip())
                            signal['datetime'] = datetime.fromisoformat(signal['timestamp'])
                            self.signals.append(signal)
                        except json.JSONDecodeError:
                            continue
            
            print(f"✅ 已加载 {len(self.signals)} 条交易信号记录")
        except Exception as e:
            print(f"❌ 加载日志失败: {e}")
    
    def show_latest(self, count=10):
        """显示最新的N条记录"""
        print(f"\n📊 最新 {count} 条交易信号")
        print("=" * 80)
        
        latest_signals = sorted(self.signals, key=lambda x: x['datetime'], reverse=True)[:count]
        
        for i, signal in enumerate(latest_signals, 1):
            self._print_signal_summary(signal, i)
    
    def show_today(self):
        """显示今日所有信号"""
        today = datetime.now().date()
        today_signals = [s for s in self.signals if s['datetime'].date() == today]
        
        print(f"\n📅 今日交易信号 ({today})")
        print("=" * 80)
        
        if not today_signals:
            print("⚪ 今日暂无交易信号")
            return
        
        # 按时间排序
        today_signals.sort(key=lambda x: x['datetime'])
        
        for i, signal in enumerate(today_signals, 1):
            self._print_signal_summary(signal, i)
        
        # 今日统计
        self._print_daily_stats(today_signals, today)
    
    def show_by_symbol(self, symbol):
        """显示特定股票的所有信号"""
        symbol = symbol.upper()
        symbol_signals = [s for s in self.signals if s['symbol'] == symbol]
        
        print(f"\n🎯 {symbol} 历史交易信号")
        print("=" * 80)
        
        if not symbol_signals:
            print(f"⚪ 未找到 {symbol} 的交易信号")
            return
        
        # 按时间排序
        symbol_signals.sort(key=lambda x: x['datetime'], reverse=True)
        
        for i, signal in enumerate(symbol_signals, 1):
            self._print_signal_detail(signal, i)
    
    def show_statistics(self, days=7):
        """显示统计信息"""
        print(f"\n📈 近{days}天交易统计")
        print("=" * 80)
        
        # 时间过滤
        cutoff_date = datetime.now().date()
        if days > 0:
            from datetime import timedelta
            cutoff_date = datetime.now().date() - timedelta(days=days)
        
        recent_signals = [s for s in self.signals if s['datetime'].date() >= cutoff_date]
        
        if not recent_signals:
            print("⚪ 指定时间范围内无交易信号")
            return
        
        # 基础统计
        total_signals = len(recent_signals)
        buy_signals = len([s for s in recent_signals if s['position']['action'] == 'BUY'])
        short_signals = len([s for s in recent_signals if s['position']['action'] == 'SHORT'])
        
        print(f"📊 信号总数: {total_signals}")
        print(f"🟢 买入信号: {buy_signals} ({buy_signals/total_signals*100:.1f}%)")
        print(f"🔴 做空信号: {short_signals} ({short_signals/total_signals*100:.1f}%)")
        
        # 按股票统计
        symbol_stats = defaultdict(list)
        for signal in recent_signals:
            symbol_stats[signal['symbol']].append(signal)
        
        print(f"\n🎯 活跃股票 TOP10:")
        sorted_symbols = sorted(symbol_stats.items(), key=lambda x: len(x[1]), reverse=True)
        for i, (symbol, signals) in enumerate(sorted_symbols[:10], 1):
            buy_count = len([s for s in signals if s['position']['action'] == 'BUY'])
            short_count = len([s for s in signals if s['position']['action'] == 'SHORT'])
            print(f"  {i:2d}. {symbol:<6} - {len(signals):2d}次 (🟢{buy_count} 🔴{short_count})")
        
        # 按日期统计
        date_stats = defaultdict(list)
        for signal in recent_signals:
            date_stats[signal['datetime'].date()].append(signal)
        
        print(f"\n📅 每日信号分布:")
        sorted_dates = sorted(date_stats.items(), reverse=True)
        for date, signals in sorted_dates:
            buy_count = len([s for s in signals if s['position']['action'] == 'BUY'])
            short_count = len([s for s in signals if s['position']['action'] == 'SHORT'])
            print(f"  {date} - {len(signals):2d}次 (🟢{buy_count} 🔴{short_count})")
        
        # 信号类型统计
        signal_types = defaultdict(int)
        for signal in recent_signals:
            for sig in signal['signals']:
                signal_types[sig['reason']] += 1
        
        print(f"\n🔍 信号类型分布:")
        for signal_type, count in sorted(signal_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {signal_type:<15} - {count:2d}次")
    
    def show_performance(self):
        """显示信号表现分析（模拟）"""
        print(f"\n💰 信号表现分析（基于2:1盈亏比模拟）")
        print("=" * 80)
        
        if not self.signals:
            print("⚪ 无数据可分析")
            return
        
        total_trades = len(self.signals)
        win_rate = 0.6  # 假设60%胜率
        wins = int(total_trades * win_rate)
        losses = total_trades - wins
        
        # 模拟盈亏
        win_amount = wins * 2  # 每次盈利2单位
        loss_amount = losses * 1  # 每次亏损1单位
        net_profit = win_amount - loss_amount
        
        print(f"📊 模拟交易结果:")
        print(f"  总交易次数: {total_trades}")
        print(f"  盈利次数: {wins} ({win_rate*100:.1f}%)")
        print(f"  亏损次数: {losses} ({(1-win_rate)*100:.1f}%)")
        print(f"  净盈亏比: {net_profit/total_trades:.2f}:1")
        
        if net_profit > 0:
            print(f"  🎉 总体盈利: +{net_profit} 单位")
        else:
            print(f"  📉 总体亏损: {net_profit} 单位")
    
    def export_to_csv(self, filename=None):
        """导出为CSV文件"""
        if not filename:
            filename = f"trading_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.signals:
            print("⚪ 无数据可导出")
            return
        
        # 准备数据
        data = []
        for signal in self.signals:
            for sig in signal['signals']:
                data.append({
                    'timestamp': signal['timestamp'],
                    'symbol': signal['symbol'],
                    'price': signal['price'],
                    'RSI': signal['RSI'],
                    'volume_ratio': signal['volume_ratio'],
                    'signal_type': sig['type'],
                    'signal_reason': sig['reason'],
                    'signal_strength': sig['strength'],
                    'action': signal['position']['action'],
                    'shares': signal['position']['shares'],
                    'stop_loss': signal['position']['stop_loss'],
                    'take_profit': signal['position']['take_profit'],
                    'position_value': signal['position']['position_value']
                })
        
        # 创建DataFrame并导出
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ 已导出到: {filename}")
    
    def _print_signal_summary(self, signal, index):
        """打印信号摘要"""
        dt = signal['datetime'].strftime('%m-%d %H:%M')
        action = signal['position']['action']
        action_emoji = "🟢" if action == "BUY" else "🔴"
        
        reasons = [s['reason'] for s in signal['signals']]
        reason_text = ', '.join(reasons[:2])  # 只显示前2个原因
        
        print(f"{index:2d}. {action_emoji} {signal['symbol']:<6} ${signal['price']:>7.2f} "
              f"RSI:{signal['RSI']:5.1f} | {reason_text} | {dt}")
    
    def _print_signal_detail(self, signal, index):
        """打印信号详情"""
        dt = signal['datetime'].strftime('%Y-%m-%d %H:%M:%S')
        action = signal['position']['action']
        action_emoji = "🟢" if action == "BUY" else "🔴"
        
        print(f"\n{index}. {action_emoji} {signal['symbol']} - {dt}")
        print(f"   💰 价格: ${signal['price']:.2f}")
        print(f"   📊 RSI: {signal['RSI']:.1f} | 成交量比: {signal['volume_ratio']:.1f}x")
        print(f"   🎯 操作: {action} {signal['position']['shares']}股")
        print(f"   🛡️ 止损: ${signal['position']['stop_loss']:.2f}")
        print(f"   🎯 止盈: ${signal['position']['take_profit']:.2f}")
        
        for sig in signal['signals']:
            strength_emoji = "🔥" if sig['strength'] == 'STRONG' else "📈"
            print(f"   {strength_emoji} {sig['reason']} [{sig['strength']}]")
    
    def _print_daily_stats(self, signals, date):
        """打印每日统计"""
        buy_signals = [s for s in signals if s['position']['action'] == 'BUY']
        short_signals = [s for s in signals if s['position']['action'] == 'SHORT']
        
        print(f"\n📊 {date} 统计:")
        print(f"   总信号: {len(signals)} | 买入: {len(buy_signals)} | 做空: {len(short_signals)}")
        
        if buy_signals:
            buy_symbols = [s['symbol'] for s in buy_signals]
            print(f"   🟢 买入: {', '.join(buy_symbols)}")
        
        if short_signals:
            short_symbols = [s['symbol'] for s in short_signals]
            print(f"   🔴 做空: {', '.join(short_symbols)}")

def main():
    """主函数"""
    viewer = LogViewer()
    
    if len(sys.argv) < 2:
        print("🐔 华尔街母鸡日志查看器")
        print("=" * 40)
        print("用法:")
        print("  python3 log_viewer.py latest [数量]     - 查看最新N条记录")
        print("  python3 log_viewer.py today            - 查看今日信号")
        print("  python3 log_viewer.py stats [天数]      - 查看统计信息")
        print("  python3 log_viewer.py symbol AAPL      - 查看特定股票")
        print("  python3 log_viewer.py performance      - 查看表现分析")
        print("  python3 log_viewer.py export          - 导出CSV文件")
        print("\n示例:")
        print("  python3 log_viewer.py today")
        print("  python3 log_viewer.py latest 20")
        print("  python3 log_viewer.py stats 30")
        print("  python3 log_viewer.py symbol MARA")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'latest':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        viewer.show_latest(count)
    
    elif command == 'today':
        viewer.show_today()
    
    elif command == 'stats':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        viewer.show_statistics(days)
    
    elif command == 'symbol':
        if len(sys.argv) < 3:
            print("❌ 请指定股票代码，例如: python3 log_viewer.py symbol AAPL")
            return
        symbol = sys.argv[2]
        viewer.show_by_symbol(symbol)
    
    elif command == 'performance':
        viewer.show_performance()
    
    elif command == 'export':
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        viewer.export_to_csv(filename)
    
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()