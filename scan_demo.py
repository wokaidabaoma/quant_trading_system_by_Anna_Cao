#!/usr/bin/env python3
# 扫描模式演示脚本

from dotenv import load_dotenv
load_dotenv()

from stock_universe import StockUniverse
from config import Config
import sys

def show_scan_modes():
    """展示所有可用的扫描模式"""
    print("🐔 华尔街母鸡 - 扫描模式选择")
    print("=" * 50)
    
    config = Config()
    universe = StockUniverse(config)
    
    modes = {
        'sp500': '标普500指数 (大盘股)',
        'nasdaq100': '纳斯达克100 (科技股)',
        'dow30': '道琼斯30 (蓝筹股)',
        'mega_cap': '超大盘股 (市值>1000亿)',
        'balanced': '平衡组合 (推荐)',
        'active': '最活跃股票',
        'financials': '金融股专扫 🏦',
        'crypto': '加密货币相关 ₿',
        'fintech': '金融科技 💳',
        'finance_crypto': '金融+加密组合 🏦₿',
        'banks': '银行股专扫 🏛️'
    }
    
    print("📊 可用扫描模式:")
    for mode, desc in modes.items():
        print(f"  {mode:<12} - {desc}")
    
    print("\n" + "=" * 50)
    
    # 让用户选择模式
    choice = input("请选择扫描模式 (默认: balanced): ").strip() or 'balanced'
    
    if choice not in modes:
        print(f"❌ 无效模式: {choice}")
        return
    
    # 获取股票列表
    print(f"\n📊 获取 {modes[choice]} 股票列表...")
    stocks = universe.create_custom_watchlist(mode=choice, limit=50)
    
    if stocks:
        print(f"✅ 获取到 {len(stocks)} 只股票:")
        for i, stock in enumerate(stocks):
            print(f"{stock:<6}", end='')
            if (i + 1) % 10 == 0:
                print()
        print("\n")
        
        # 询问是否开始扫描
        start_scan = input("是否开始扫描这些股票? (y/N): ").strip().lower()
        
        if start_scan == 'y':
            # 设置环境变量并启动扫描
            import os
            os.environ['SCAN_MODE'] = choice
            os.environ['MAX_STOCKS_PER_SCAN'] = str(len(stocks))
            
            print(f"\n🚀 启动 {modes[choice]} 扫描...")
            print("=" * 50)
            
            # 导入并运行主系统
            from main import TradingSystem
            system = TradingSystem()
            system.run_once()
    else:
        print("❌ 获取股票列表失败")

def quick_test():
    """快速测试小批量扫描"""
    print("🧪 快速测试模式")
    print("=" * 30)
    
    import os
    os.environ['SCAN_MODE'] = 'dow30'
    os.environ['MAX_STOCKS_PER_SCAN'] = '10'
    os.environ['BATCH_SIZE'] = '5'
    
    from main import TradingSystem
    system = TradingSystem()
    system.run_once()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        quick_test()
    else:
        show_scan_modes()