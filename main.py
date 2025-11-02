# main.py - 主程序
import os
import sys
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv
import asyncio

# 加载环境变量
load_dotenv()

# 导入模块
from config import Config
from data_manager import DataManager
from signal_generator import SignalGenerator
from notification import MacNotification

class TradingSystem:
    def __init__(self):
        print("🐔 初始化华尔街母鸡交易系统...")
        self.config = Config()
        self.data_manager = DataManager(self.config)
        self.signal_generator = SignalGenerator(self.data_manager)
        self.notification = MacNotification()
        
    def scan_stocks(self):
        """扫描股票 - 支持批处理和大规模扫描"""
        start_time = datetime.now()
        print(f"\n⏰ 开始扫描 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 扫描模式: {self.config.SCAN_MODE}")
        print(f"🎯 股票数量: {len(self.config.WATCHLIST)}")
        print(f"📦 批处理大小: {self.config.BATCH_SIZE}")
        print("-" * 80)
        
        # 获取市场情绪
        sentiment = self.data_manager.get_market_sentiment()
        
        # 统计数据
        all_signals = []
        strong_stocks = []
        weak_stocks = []
        scanned_symbols = []
        error_symbols = []
        
        # 分批处理股票
        total_stocks = len(self.config.WATCHLIST)
        for i in range(0, total_stocks, self.config.BATCH_SIZE):
            batch = self.config.WATCHLIST[i:i + self.config.BATCH_SIZE]
            batch_num = i // self.config.BATCH_SIZE + 1
            total_batches = (total_stocks + self.config.BATCH_SIZE - 1) // self.config.BATCH_SIZE
            
            print(f"\n📦 批次 {batch_num}/{total_batches} ({len(batch)} 只股票)")
            print("=" * 60)
            
            # 扫描当前批次
            batch_signals = self._scan_batch(batch, scanned_symbols, strong_stocks, weak_stocks, error_symbols)
            all_signals.extend(batch_signals)
            
            # 批次间休息
            if i + self.config.BATCH_SIZE < total_stocks:
                print(f"⏳ 批次间休息 {self.config.API_DELAY * 10:.1f} 秒...")
                time.sleep(self.config.API_DELAY * 10)
        
        # 计算扫描时间
        end_time = datetime.now()
        scan_duration = (end_time - start_time).total_seconds()
        
        # 发送总结
        self._send_scan_summary(sentiment, all_signals, strong_stocks, weak_stocks, 
                               scanned_symbols, error_symbols, scan_duration)
        
        return all_signals
    
    def _scan_batch(self, batch, scanned_symbols, strong_stocks, weak_stocks, error_symbols):
        """扫描一个批次的股票"""
        batch_signals = []
        
        for symbol in batch:
            try:
                print(f"📊 {symbol:<6}", end='', flush=True)
                scanned_symbols.append(symbol)
                
                # 获取信号
                signal = self.signal_generator.scan_for_signals(symbol)
                
                if signal:
                    # 计算仓位
                    position = self.signal_generator.calculate_position_size(
                        signal,
                        self.config.ACCOUNT_SIZE,
                        self.config.MAX_RISK_PER_TRADE
                    )
                    
                    # 发送通知
                    self.notification.send_signal(signal, position)
                    batch_signals.append(signal)
                    
                    # 分类
                    if position['action'] == 'BUY':
                        strong_stocks.append(symbol)
                        print(" 🟢", end='')
                    else:
                        weak_stocks.append(symbol)
                        print(" 🔴", end='')
                else:
                    print(" ⚪", end='')
                
                # API限流
                time.sleep(self.config.API_DELAY)
                
            except Exception as e:
                error_symbols.append(symbol)
                print(f" ❌", end='')
                # 记录错误但继续扫描
                pass
            
            # 每10个股票换行
            if (scanned_symbols.index(symbol) + 1) % 10 == 0:
                print()
        
        print()  # 批次结束换行
        return batch_signals
    
    def _send_scan_summary(self, sentiment, all_signals, strong_stocks, weak_stocks, 
                          scanned_symbols, error_symbols, scan_duration):
        """发送扫描总结"""
        print("\n" + "=" * 80)
        print("📊 扫描总结")
        print("=" * 80)
        
        print(f"⏱️  扫描时间: {scan_duration:.1f} 秒")
        print(f"📈 总扫描数: {len(scanned_symbols)} 只")
        print(f"🎯 发现信号: {len(all_signals)} 个")
        print(f"🟢 买入信号: {len(strong_stocks)} 只")
        print(f"🔴 卖出信号: {len(weak_stocks)} 只")
        print(f"❌ 扫描失败: {len(error_symbols)} 只")
        
        if strong_stocks:
            print(f"\n🟢 强势股票 ({len(strong_stocks)}):")
            for i, stock in enumerate(strong_stocks):
                print(f"   {stock}", end='')
                if (i + 1) % 8 == 0:
                    print()
            print()
        
        if weak_stocks:
            print(f"\n🔴 弱势股票 ({len(weak_stocks)}):")
            for i, stock in enumerate(weak_stocks):
                print(f"   {stock}", end='')
                if (i + 1) % 8 == 0:
                    print()
            print()
        
        if error_symbols:
            print(f"\n❌ 失败股票: {', '.join(error_symbols[:10])}")
            if len(error_symbols) > 10:
                print(f"   ...还有 {len(error_symbols) - 10} 只")
        
        # 发送每日总结
        if datetime.now().hour in [9, 15]:
            summary = {
                'sentiment': sentiment,
                'signal_count': len(all_signals),
                'strong_stocks': strong_stocks,
                'weak_stocks': weak_stocks,
                'scanned_symbols': scanned_symbols
            }
            self.notification.send_daily_summary(summary)
        
        print("=" * 80)
    
    def run_once(self):
        """运行一次扫描"""
        try:
            self.scan_stocks()
        except Exception as e:
            print(f"❌ 扫描错误: {e}")
    
    def run_schedule(self):
        """按计划运行"""
        print("🐔 华尔街母鸡系统启动成功!")
        print("📅 扫描时间: 9:00, 10:30, 14:00, 15:30")
        print("-" * 60)
        
        # 设置定时任务
        schedule.every().day.at("09:00").do(self.run_once)
        schedule.every().day.at("10:30").do(self.run_once)
        schedule.every().day.at("14:00").do(self.run_once)
        schedule.every().day.at("15:30").do(self.run_once)
        
        # 立即运行一次
        self.run_once()
        
        # 持续运行
        print("\n💤 等待下次扫描... (按Ctrl+C退出)")
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        # 只运行一次
        system = TradingSystem()
        system.run_once()
    else:
        # 持续运行
        system = TradingSystem()
        system.run_schedule()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 华尔街母鸡系统已停止")
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")