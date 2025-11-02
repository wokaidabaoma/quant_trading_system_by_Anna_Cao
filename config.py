# config.py - 系统配置
import os
from datetime import datetime

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env文件已加载")
except ImportError:
    print("⚠️ python-dotenv未安装，使用系统环境变量")

class Config:
    def __init__(self):
        # 账户设置
        self.ACCOUNT_SIZE = float(os.getenv('ACCOUNT_SIZE', 100000))
        self.MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', 0.02))
        
        # API配置
        self.FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
        self.POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
        self.ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
        
        # 检查API密钥
        if not self.FINNHUB_API_KEY:
            print("⚠️  警告: 未找到FINNHUB_API_KEY，某些功能可能受限")
        if not self.POLYGON_API_KEY:
            print("⚠️  警告: 未找到POLYGON_API_KEY，某些功能可能受限")
        if not self.ALPHA_VANTAGE_API_KEY:
            print("⚠️  警告: 未找到ALPHA_VANTAGE_API_KEY，某些功能可能受限")
        
        # API端点
        self.FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'
        self.POLYGON_BASE_URL = 'https://api.polygon.io/v2'
        self.ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
        
        # 股票扫描模式配置
        self.SCAN_MODE = os.getenv('SCAN_MODE', 'balanced')  # 可选: sp500, nasdaq100, dow30, active, balanced, mega_cap, custom
        self.MAX_STOCKS_PER_SCAN = int(os.getenv('MAX_STOCKS_PER_SCAN', 100))  # 每次扫描最大股票数
        self.BATCH_SIZE = int(os.getenv('BATCH_SIZE', 20))  # 批处理大小
        self.API_DELAY = float(os.getenv('API_DELAY', 0.1))  # API调用间隔(秒)
        
        # 默认监控股票列表（如果动态获取失败使用）
        self.DEFAULT_WATCHLIST = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
            'JPM', 'BAC', 'WFC', 'C', 'GS',
            'WMT', 'HD', 'MCD', 'NKE', 'SBUX'
        ]
        
        # 动态生成监控列表
        self.WATCHLIST = self._get_dynamic_watchlist()
        
        # 技术指标参数
        self.EMA_SHORT = 50
        self.EMA_LONG = 200
        self.RSI_PERIOD = 14
        self.RSI_OVERSOLD = 30
        self.RSI_OVERBOUGHT = 70
        self.BOLLINGER_PERIOD = 20
        self.BOLLINGER_STD = 2
        
    def _get_dynamic_watchlist(self):
        """动态生成监控股票列表"""
        try:
            from stock_universe import StockUniverse
            universe = StockUniverse(self)
            
            print(f"📊 使用扫描模式: {self.SCAN_MODE}")
            watchlist = universe.create_custom_watchlist(
                mode=self.SCAN_MODE, 
                limit=self.MAX_STOCKS_PER_SCAN
            )
            
            if watchlist:
                print(f"✅ 获取到 {len(watchlist)} 只股票进行监控")
                return watchlist
            else:
                print("⚠️  动态获取失败，使用默认列表")
                return self.DEFAULT_WATCHLIST
                
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return self.DEFAULT_WATCHLIST
    
    def refresh_watchlist(self):
        """刷新监控列表"""
        self.WATCHLIST = self._get_dynamic_watchlist()
        return self.WATCHLIST
    
    def is_market_hours(self):
        now = datetime.now()
        return 9 <= now.hour <= 16 and now.weekday() < 5