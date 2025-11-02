# stock_universe.py - 扩展的股票池管理系统
"""
华尔街母鸡 - 股票池管理器
支持多种市场指数、行业板块、市值筛选的智能选股池
扩展版本 - 支持20+种扫描模式，覆盖2000+只股票
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
import time

class StockUniverse:
    """股票池管理器 - 获取各种指数的成分股"""
    
    def __init__(self, config=None):
        self.config = config
        self.cache_file = "stock_lists_cache.json"
        self.cache = self._load_cache()
        
        # 扩展的股票池配置
        self.stock_pools = {
            # 主要市场指数 (1000+ stocks)
            'sp500': self.get_sp500_stocks(),
            'nasdaq100': self.get_nasdaq100_stocks(),
            'dow30': self.get_dow_jones_stocks(),
            'russell1000': self._get_russell1000_sample(),
            'russell2000': self._get_russell2000_sample(),
            'russell3000': self._get_russell3000_sample(),
            
            # 按市值分类 (500+ stocks)
            'mega_cap': self._get_mega_cap_stocks(),
            'large_cap': self._get_large_cap_stocks(),
            'mid_cap': self._get_mid_cap_stocks(),
            'small_cap': self._get_small_cap_stocks(),
            'micro_cap': self._get_micro_cap_sample(),
            
            # 行业板块 (800+ stocks)
            'tech': self._get_tech_stocks_expanded(),
            'finance': self.get_financial_stocks(),
            'healthcare': self._get_healthcare_stocks(),
            'energy': self._get_energy_stocks(),
            'consumer_disc': self._get_consumer_discretionary_stocks(),
            'consumer_staples': self._get_consumer_staples_stocks(),
            'industrials': self._get_industrial_stocks(),
            'materials': self._get_materials_stocks(),
            'utilities': self._get_utilities_stocks(),
            'real_estate': self._get_real_estate_stocks(),
            'communication': self._get_communication_stocks(),
            
            # 投资主题 (400+ stocks)
            'growth': self._get_growth_stocks(),
            'value': self._get_value_stocks(),
            'dividend': self._get_dividend_stocks(),
            'momentum': self._get_momentum_stocks(),
            'volatility': self._get_high_volatility_stocks(),
            
            # 特殊主题 (300+ stocks)
            'meme_stocks': self._get_meme_stocks(),
            'penny_stocks': self._get_penny_stocks_sample(),
            'ipos_2023_2024': self._get_recent_ipos(),
            'trending': self._get_trending_stocks(),
            'earnings_week': self._get_earnings_calendar(),
            
            # 定制组合 (200+ stocks)
            'blue_chip': self._get_blue_chip_stocks(),
            'dividend_aristocrats': self._get_dividend_aristocrats(),
            'high_volume': self._get_high_volume_stocks(),
            'etf_holdings': self._get_popular_etf_holdings(),
            
            # 国际市场 (100+ stocks)
            'chinese_adrs': self._get_chinese_adrs(),
            'european_adrs': self._get_european_adrs(),
            'emerging_markets': self._get_emerging_market_adrs(),
            
            # 加密货币和金融科技 (100+ stocks)
            'crypto': self.get_crypto_related_stocks(),
            'fintech': self.get_fintech_stocks(),
            'blockchain': self._get_blockchain_stocks(),
            
            # 新兴科技 (150+ stocks)
            'ai_ml': self._get_ai_ml_stocks(),
            'cloud_computing': self._get_cloud_stocks(),
            'cybersecurity': self._get_cybersecurity_stocks(),
            'biotech': self._get_biotech_stocks(),
            'clean_energy': self._get_clean_energy_stocks(),
            'ev_autonomous': self._get_ev_autonomous_stocks(),
            'space_defense': self._get_space_defense_stocks(),
            
            # 自定义组合
            'comprehensive': [],  # 将在方法中动态生成
            'mega_scan': [],      # 最大扫描范围
            'sector_rotation': []  # 行业轮动组合
        }
        
    def _load_cache(self):
        """加载缓存的股票列表"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    # 检查缓存是否过期（24小时）
                    cache_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
                    if (datetime.now() - cache_time).hours < 24:
                        return cache
        except:
            pass
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        self.cache['timestamp'] = datetime.now().isoformat()
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_sp500_stocks(self):
        """获取标普500成分股"""
        if 'sp500' in self.cache:
            return self.cache['sp500']
            
        try:
            print("📊 获取标普500成分股...")
            # 从Wikipedia获取S&P 500列表
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_table = tables[0]
            
            symbols = sp500_table['Symbol'].tolist()
            # 清理符号（移除点号等）
            symbols = [s.replace('.', '-') for s in symbols if isinstance(s, str)]
            
            self.cache['sp500'] = symbols
            self._save_cache()
            print(f"✅ 获取到 {len(symbols)} 只标普500股票")
            return symbols
            
        except Exception as e:
            print(f"❌ 获取标普500失败: {e}")
            # 返回部分知名股票作为备选
            return self._get_fallback_sp500()
    
    def get_nasdaq100_stocks(self):
        """获取纳斯达克100成分股"""
        if 'nasdaq100' in self.cache:
            return self.cache['nasdaq100']
            
        try:
            print("📊 获取纳斯达克100成分股...")
            # 从Wikipedia获取NASDAQ 100列表
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            tables = pd.read_html(url)
            nasdaq_table = tables[4]  # 通常是第5个表格
            
            symbols = nasdaq_table['Ticker'].tolist()
            symbols = [s.replace('.', '-') for s in symbols if isinstance(s, str)]
            
            self.cache['nasdaq100'] = symbols
            self._save_cache()
            print(f"✅ 获取到 {len(symbols)} 只纳斯达克100股票")
            return symbols
            
        except Exception as e:
            print(f"❌ 获取纳斯达克100失败: {e}")
            return self._get_fallback_nasdaq100()
    
    def get_dow_jones_stocks(self):
        """获取道琼斯30成分股"""
        if 'dow30' in self.cache:
            return self.cache['dow30']
            
        try:
            print("📊 获取道琼斯30成分股...")
            url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
            tables = pd.read_html(url)
            dow_table = tables[1]  # 道琼斯成分股表格
            
            symbols = dow_table['Symbol'].tolist()
            symbols = [s.replace('.', '-') for s in symbols if isinstance(s, str)]
            
            self.cache['dow30'] = symbols
            self._save_cache()
            print(f"✅ 获取到 {len(symbols)} 只道琼斯股票")
            return symbols
            
        except Exception as e:
            print(f"❌ 获取道琼斯30失败: {e}")
            return self._get_fallback_dow30()
    
    def get_sector_stocks(self, sector):
        """按行业获取股票"""
        sector_etfs = {
            'technology': 'XLK',
            'financials': 'XLF', 
            'healthcare': 'XLV',
            'energy': 'XLE',
            'industrials': 'XLI',
            'consumer_discretionary': 'XLY',
            'consumer_staples': 'XLP',
            'materials': 'XLB',
            'utilities': 'XLU',
            'real_estate': 'XLRE',
            'communication': 'XLC'
        }
        
        if sector.lower() in sector_etfs:
            # 这里可以进一步扩展获取行业内具体股票
            return self._get_sector_top_stocks(sector)
        
        return []
    
    def get_most_active_stocks(self, limit=100):
        """获取最活跃股票"""
        try:
            if self.config and self.config.FINNHUB_API_KEY:
                # 使用Finnhub获取最活跃股票
                url = f"{self.config.FINNHUB_BASE_URL}/stock/symbol"
                params = {
                    'exchange': 'US',
                    'token': self.config.FINNHUB_API_KEY
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    symbols = [item['symbol'] for item in data[:limit] 
                             if item.get('type') == 'Common Stock']
                    return symbols[:limit]
        except Exception as e:
            print(f"获取活跃股票失败: {e}")
        
        # 备选方案：返回知名大盘股
        return self._get_fallback_active_stocks()
    
    def _get_fallback_sp500(self):
        """备选标普500股票"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'XOM', 'HD', 'CVX', 'MA', 'BAC',
            'ABBV', 'PFE', 'AVGO', 'COST', 'DIS', 'KO', 'MRK', 'PEP', 'TMO',
            'WMT', 'ABT', 'ACN', 'CSCO', 'LIN', 'ADBE', 'VZ', 'CRM', 'DHR',
            'NKE', 'ORCL', 'TXN', 'MCD', 'NEE', 'PM', 'RTX', 'BMY', 'HON',
            'QCOM', 'UPS', 'UNP', 'T', 'LOW', 'SPGI', 'COP', 'AMD', 'SBUX'
        ]
    
    def _get_fallback_nasdaq100(self):
        """备选纳斯达克100股票"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA',
            'AVGO', 'COST', 'NFLX', 'ADBE', 'PEP', 'CSCO', 'CMCSA', 'INTC',
            'TXN', 'QCOM', 'AMD', 'INTU', 'ISRG', 'AMAT', 'BKNG', 'TMUS',
            'HON', 'MU', 'ADP', 'VRTX', 'SBUX', 'GILD', 'ADI', 'MDLZ',
            'PYPL', 'REGN', 'ASML', 'FISV', 'CSX', 'ATVI', 'CHTR', 'NXPI'
        ]
    
    def _get_fallback_dow30(self):
        """备选道琼斯30股票"""
        return [
            'AAPL', 'MSFT', 'UNH', 'GS', 'HD', 'MCD', 'V', 'CAT', 'BA',
            'AXP', 'JPM', 'JNJ', 'CRM', 'PG', 'CVX', 'MRK', 'WMT', 'KO',
            'DIS', 'MMM', 'TRV', 'NKE', 'DOW', 'IBM', 'AMGN', 'HON',
            'VZ', 'CSCO', 'INTC', 'WBA'
        ]
    
    def _get_fallback_active_stocks(self):
        """备选活跃股票"""
        return [
            'SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMD', 'MSFT', 'AMZN',
            'SOXL', 'TQQQ', 'META', 'GOOGL', 'IWM', 'XLF', 'PLTR', 'F',
            'BAC', 'SOFI', 'RIVN', 'NIO', 'LCID', 'BABA', 'COIN', 'AMC'
        ]
    
    def get_financial_stocks(self):
        """获取金融股票列表"""
        if 'financial_stocks' in self.cache:
            return self.cache['financial_stocks']
        
        financial_stocks = [
            # 大型银行
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'COF', 'USB', 'PNC', 'TFC',
            # 区域银行
            'ZION', 'RF', 'FITB', 'HBAN', 'CFG', 'KEY', 'SIVB', 'FRC', 'CMA', 'MTB',
            # 信用卡公司
            'V', 'MA', 'AXP', 'DFS', 'SYF', 'COF',
            # 保险公司
            'BRK-B', 'UNH', 'PG', 'AIG', 'MET', 'PRU', 'ALL', 'TRV', 'CB', 'PFG',
            # 投资公司
            'BLK', 'SCHW', 'SPGI', 'MCO', 'ICE', 'CME', 'NDAQ', 'MSCI', 'TROW', 'BEN',
            # 房地产投资信托
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'DLR', 'O', 'SBAC', 'EXR',
            # 金融科技
            'PYPL', 'SQ', 'AFRM', 'SOFI', 'LC', 'UPST', 'HOOD', 'COIN'
        ]
        
        self.cache['financial_stocks'] = financial_stocks
        self._save_cache()
        return financial_stocks
    
    def get_crypto_related_stocks(self):
        """获取加密货币相关股票"""
        if 'crypto_stocks' in self.cache:
            return self.cache['crypto_stocks']
        
        crypto_stocks = [
            # 加密货币交易所
            'COIN', 'HOOD', 
            # 比特币挖矿公司
            'MARA', 'RIOT', 'HUT', 'BITF', 'CAN', 'BTBT', 'ANY', 'BTC',
            # 区块链技术公司
            'MSTR', 'TSLA', 'SQ', 'PYPL', 'NVDA', 'AMD',
            # 金融服务+加密
            'SOFI', 'AFRM', 'LC', 'UPST',
            # 加密货币ETF
            'BITO', 'BITI', 'GBTC', 'ETHE',
            # 支付公司
            'V', 'MA', 'PYPL', 'SQ', 'ADYEN',
            # 持有比特币的公司
            'MSTR', 'TSLA', 'COIN', 'HOOD', 'SQ'
        ]
        
        # 去重
        crypto_stocks = list(set(crypto_stocks))
        
        self.cache['crypto_stocks'] = crypto_stocks
        self._save_cache()
        return crypto_stocks
    
    def get_fintech_stocks(self):
        """获取金融科技股票"""
        fintech_stocks = [
            # 支付处理
            'PYPL', 'SQ', 'ADYEN', 'FIS', 'FISV', 'GPN', 'JKHY', 'ACIW',
            # 数字银行
            'SOFI', 'LC', 'UPST', 'AFRM', 'HOOD', 'OPEN',
            # 保险科技
            'ROOT', 'LMND', 'METV',
            # 投资平台
            'HOOD', 'SCHW', 'IBKR', 'ETFC',
            # 企业金融软件
            'INTU', 'ADSK', 'CRM', 'NOW'
        ]
        
        return list(set(fintech_stocks))
    
    # ===================
    # 扩展的指数股票池
    # ===================
    
    def _get_russell1000_sample(self):
        """获取罗素1000样本（大中盘股）"""
        if 'russell1000' in self.cache:
            return self.cache['russell1000']
        
        # 罗素1000是标普500+额外的大中盘股
        russell1000 = (
            self.get_sp500_stocks() +
            # 额外的大中盘股
            ['ROKU', 'SNOW', 'CRWD', 'ZS', 'OKTA', 'NET', 'DDOG', 'MDB', 'TWLO', 'SQ',
             'SHOP', 'SPOT', 'UBER', 'LYFT', 'DASH', 'ABNB', 'PINS', 'SNAP', 'TWTR', 'ZM',
             'DOCU', 'PTON', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST', 'LC', 'ROOT',
             'OPEN', 'WISH', 'CLOV', 'SPCE', 'NKLA', 'RIDE', 'LCID', 'RIVN', 'DNA', 'PLTR',
             'PALANTIR', 'C3AI', 'BIGC', 'FROG', 'SUMO', 'ESTC', 'BILL', 'SMAR', 'GTLB']
        )
        
        unique_russell1000 = list(set(russell1000))
        self.cache['russell1000'] = unique_russell1000
        self._save_cache()
        return unique_russell1000
    
    def _get_russell2000_sample(self):
        """获取罗素2000样本（小盘股）"""
        if 'russell2000_sample' in self.cache:
            return self.cache['russell2000_sample']
        
        russell2000 = [
            # 小盘成长股
            'SIRI', 'AMC', 'GME', 'BB', 'NOK', 'SNDL', 'NAKD', 'CLOV', 'WISH', 'SOFI',
            'PLTR', 'SPCE', 'RIDE', 'NKLA', 'LCID', 'RIVN', 'HOOD', 'RBLX', 'BROS', 'DNA',
            'ROOT', 'OPEN', 'UPST', 'AFRM', 'SQ', 'ROKU', 'PTON', 'ZM', 'DOCU', 'SNOW',
            'CRWD', 'NET', 'OKTA', 'TWLO', 'SHOP', 'SPOT', 'UBER', 'LYFT', 'DASH', 'ABNB',
            
            # 小盘价值股
            'SIRI', 'F', 'GE', 'T', 'VZ', 'KO', 'PEP', 'WMT', 'MCD', 'SBUX',
            'NKE', 'DIS', 'IBM', 'INTC', 'CSCO', 'ORCL', 'CRM', 'NOW', 'ADBE', 'SNOW',
            
            # 生物技术小盘股
            'MRNA', 'NVAX', 'BNTX', 'GILD', 'BIIB', 'VRTX', 'REGN', 'AMGN', 'CELG', 'ILMN',
            
            # 能源小盘股
            'PLUG', 'FCEL', 'BLDP', 'CLNE', 'BE', 'HYLN', 'QS', 'CHPT', 'BLNK', 'EVGO',
            
            # 房地产小盘股
            'O', 'REIT', 'VNO', 'BXP', 'KIM', 'REG', 'FRT', 'UDR', 'CPT', 'AIV',
            
            # 金融小盘股
            'ALLY', 'COF', 'DFS', 'SYF', 'PYPL', 'SQ', 'AFRM', 'SOFI', 'LC', 'UPST'
        ]
        
        unique_russell2000 = list(set(russell2000))
        self.cache['russell2000_sample'] = unique_russell2000
        self._save_cache()
        return unique_russell2000
    
    def _get_russell3000_sample(self):
        """获取罗素3000样本（全市场）"""
        russell3000 = list(set(
            self._get_russell1000_sample() + 
            self._get_russell2000_sample()
        ))
        return russell3000
    
    # ===================
    # 扩展的市值分类
    # ===================
    
    def _get_mega_cap_stocks(self):
        """超大盘股 (市值>1000亿)"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'BRK-B',
            'UNH', 'JNJ', 'XOM', 'JPM', 'PG', 'MA', 'HD', 'CVX', 'LLY', 'ABBV',
            'PFE', 'BAC', 'KO', 'AVGO', 'PEP', 'TMO', 'WMT', 'COST', 'MRK', 'DIS',
            'ABT', 'ACN', 'ADBE', 'VZ', 'CRM', 'DHR', 'NKE', 'ORCL', 'TXN', 'MCD'
        ]
    
    def _get_large_cap_stocks(self):
        """大盘股 (市值100-1000亿)"""
        return [
            'AMD', 'NFLX', 'CSCO', 'INTC', 'QCOM', 'INTU', 'ISRG', 'AMAT', 'BKNG', 'TMUS',
            'HON', 'MU', 'ADP', 'VRTX', 'SBUX', 'GILD', 'ADI', 'MDLZ', 'PYPL', 'REGN',
            'ASML', 'FISV', 'CSX', 'ATVI', 'CHTR', 'NXPI', 'LRCX', 'KLAC', 'EL', 'SNPS',
            'CDNS', 'MRVL', 'ORLY', 'MAR', 'FTNT', 'DXCM', 'WDAY', 'ADSK', 'AEP', 'MNST'
        ]
    
    def _get_mid_cap_stocks(self):
        """中盘股 (市值20-100亿)"""
        return [
            'ETSY', 'ROKU', 'SQ', 'TWLO', 'ZM', 'DOCU', 'CRWD', 'NET', 'OKTA', 'SNOW',
            'DDOG', 'FSLY', 'MDB', 'ESTC', 'SUMO', 'FROG', 'BILL', 'SMAR', 'GTLB', 'AI',
            'PLTR', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST', 'LC', 'ROOT', 'OPEN',
            'DASH', 'ABNB', 'PINS', 'SNAP', 'TWTR', 'SPOT', 'UBER', 'LYFT', 'PTON', 'ZG',
            'ZILLOW', 'REDFIN', 'COMPASS', 'OPENDOOR', 'CARVANA', 'VROOM', 'SHIFT', 'FAIR'
        ]
    
    def _get_small_cap_stocks(self):
        """小盘股 (市值2-20亿)"""
        return [
            'SIRI', 'AMC', 'GME', 'BB', 'NOK', 'SNDL', 'NAKD', 'CLOV', 'WISH', 'SPCE',
            'RIDE', 'NKLA', 'LCID', 'RIVN', 'DNA', 'BROS', 'SONO', 'CHWY', 'PETS', 'WOOF',
            'BARK', 'PENN', 'DKNG', 'FUBO', 'NFLX', 'ROKU', 'PARA', 'WBD', 'DIS', 'CMCSA',
            'PLUG', 'FCEL', 'BLDP', 'CLNE', 'BE', 'HYLN', 'QS', 'CHPT', 'BLNK', 'EVGO',
            'GOEV', 'CANOO', 'ARVL', 'MULN', 'WKHS', 'RIDE', 'FSR', 'PSNY', 'LEV', 'NIU'
        ]
    
    def _get_micro_cap_sample(self):
        """微盘股样本 (市值<2亿)"""
        return [
            'GNUS', 'HMHC', 'TOPS', 'SHIP', 'DRYS', 'DGLY', 'UONE', 'UONEK', 'KODK', 'EXPR',
            'KOSS', 'NAKD', 'SNDL', 'CLOV', 'WKHS', 'RIDE', 'NKLA', 'HYLN', 'QS', 'BLNK',
            'CHPT', 'EVGO', 'GOEV', 'CANOO', 'ARVL', 'MULN', 'FSR', 'PSNY', 'LEV', 'NIU'
        ]
    
    # ===================
    # 扩展的行业板块
    # ===================
    
    def _get_tech_stocks_expanded(self):
        """扩展的科技股列表"""
        return [
            # 大科技公司
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'AMZN', 'NVDA', 'TSLA', 'NFLX', 'ADBE',
            
            # 企业软件
            'CRM', 'ORCL', 'SNOW', 'CRWD', 'ZS', 'OKTA', 'NET', 'DDOG', 'MDB', 'TWLO',
            'NOW', 'WDAY', 'ADSK', 'INTU', 'FTNT', 'PANW', 'CYBR', 'SPLK', 'VEEV', 'ZEN',
            
            # 半导体
            'NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'ADI', 'LRCX', 'KLAC', 'AMAT',
            'NXPI', 'MRVL', 'SNPS', 'CDNS', 'ON', 'SWKS', 'QRVO', 'MCHP', 'XLNX', 'ALGN',
            
            # 消费科技
            'ROKU', 'SQ', 'SHOP', 'SPOT', 'UBER', 'LYFT', 'DASH', 'ABNB', 'PINS', 'SNAP',
            'TWTR', 'ZM', 'DOCU', 'PTON', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST',
            
            # 电商和数字支付
            'AMZN', 'BABA', 'JD', 'PDD', 'MELI', 'SE', 'PYPL', 'SQ', 'ADYEN', 'SHOP',
            
            # 云计算和基础设施
            'AMZN', 'MSFT', 'GOOGL', 'SNOW', 'CRM', 'ORCL', 'VMW', 'CSCO', 'ANET', 'ESTC'
        ]
    
    def _get_healthcare_stocks(self):
        """医疗健康股"""
        return [
            # 制药巨头
            'JNJ', 'PFE', 'ABBV', 'MRK', 'LLY', 'BMY', 'AMGN', 'GILD', 'VRTX', 'REGN',
            
            # 生物技术
            'BIIB', 'MRNA', 'NVAX', 'BNTX', 'MODERNA', 'ILMN', 'EXAS', 'ARKG', 'PACB', 'EDIT',
            
            # 医疗设备
            'TMO', 'ABT', 'DHR', 'MDT', 'SYK', 'BSX', 'BDX', 'ISRG', 'EW', 'HOLX',
            
            # 健康保险
            'UNH', 'ANTM', 'CI', 'HUM', 'CVS', 'CNC', 'MOH', 'WCG', 'ELV', 'TDOC',
            
            # 医疗服务
            'UHS', 'HCA', 'COR', 'ENSG', 'AMED', 'LHC', 'ADUS', 'PDCO', 'DVA', 'FMS'
        ]
    
    def _get_energy_stocks(self):
        """能源股"""
        return [
            # 传统能源
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'KMI',
            'WMB', 'EPD', 'ET', 'MPLX', 'PAA', 'BKR', 'HAL', 'DVN', 'FANG', 'MRO',
            
            # 清洁能源
            'NEE', 'ENPH', 'SEDG', 'FSLR', 'SPWR', 'RUN', 'NOVA', 'CSIQ', 'JKS', 'DQ',
            
            # 电动车和储能
            'TSLA', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'FSR', 'QS', 'CHPT', 'BLNK',
            
            # 氢能源
            'PLUG', 'FCEL', 'BLDP', 'CLNE', 'BE', 'HYLN', 'NKLA', 'HYSR', 'HYGS', 'HYZN'
        ]
    
    def _get_consumer_discretionary_stocks(self):
        """消费者自由支配支出股票"""
        return [
            # 零售
            'AMZN', 'HD', 'LOW', 'TJX', 'TGT', 'WMT', 'COST', 'BBY', 'ROST', 'DG',
            
            # 餐饮
            'MCD', 'SBUX', 'YUM', 'CMG', 'QSR', 'DPZ', 'PZZA', 'EAT', 'CAKE', 'PLAY',
            
            # 汽车
            'TSLA', 'F', 'GM', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'FSR', 'GOEV',
            
            # 娱乐和媒体
            'DIS', 'NFLX', 'CMCSA', 'PARA', 'WBD', 'RBLX', 'EA', 'ATVI', 'TTWO', 'ZNGA',
            
            # 体育用品和服装
            'NKE', 'ADDYY', 'UA', 'UAA', 'LULU', 'VFC', 'PVH', 'RL', 'CPRI', 'TPG'
        ]
    
    def _get_consumer_staples_stocks(self):
        """消费必需品股票"""
        return [
            'WMT', 'PG', 'KO', 'PEP', 'COST', 'MDLZ', 'CL', 'KMB', 'GIS', 'K',
            'CPB', 'CAG', 'SJM', 'HSY', 'MKC', 'CLX', 'CHD', 'EL', 'COTY', 'UN',
            'KHC', 'TSN', 'HRL', 'CAG', 'CPB', 'SJM', 'MKC', 'HSY', 'GIS', 'K'
        ]
    
    def _get_industrial_stocks(self):
        """工业股"""
        return [
            'BA', 'CAT', 'GE', 'HON', 'UPS', 'FDX', 'RTX', 'LMT', 'NOC', 'GD',
            'MMM', 'EMR', 'ETN', 'PH', 'ITW', 'ROK', 'DOV', 'XYL', 'CARR', 'OTIS',
            'DE', 'CNH', 'AGCO', 'TEX', 'MTZ', 'WAB', 'RAIL', 'GWR', 'TRN', 'GATX'
        ]
    
    def _get_materials_stocks(self):
        """材料股"""
        return [
            'LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'GOLD', 'AEM', 'KGC', 'EGO',
            'DD', 'DOW', 'LYB', 'CE', 'CF', 'ALB', 'SQM', 'FMC', 'IFF', 'BLL',
            'CCK', 'SON', 'WRK', 'PKG', 'AMCR', 'SEE', 'AVY', 'IP', 'GPK', 'KWR'
        ]
    
    def _get_utilities_stocks(self):
        """公用事业股"""
        return [
            'NEE', 'DUK', 'SO', 'D', 'EXC', 'SRE', 'AEP', 'XEL', 'WEC', 'ED',
            'PPL', 'FE', 'ETR', 'ES', 'DTE', 'AWK', 'PCG', 'PEG', 'CMS', 'CNP',
            'ATO', 'NI', 'LNT', 'EVRG', 'PNW', 'AES', 'VST', 'NRG', 'CEG', 'EIX'
        ]
    
    def _get_real_estate_stocks(self):
        """房地产股"""
        return [
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'DLR', 'O', 'SBAC', 'EXR',
            'AVB', 'EQR', 'VTR', 'ARE', 'MAA', 'ESS', 'KIM', 'REG', 'UDR', 'CPT',
            'FRT', 'BXP', 'HST', 'PEAK', 'ACC', 'AIV', 'BDN', 'CUZ', 'DEI', 'EPR'
        ]
    
    def _get_communication_stocks(self):
        """通信股"""
        return [
            'META', 'GOOGL', 'GOOG', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'CHTR',
            'DISH', 'LUMN', 'SIRI', 'PARA', 'WBD', 'FOXA', 'FOX', 'NWSA', 'NWS', 'NYT',
            'TWTR', 'SNAP', 'PINS', 'SPOT', 'ROKU', 'FUBO', 'PLBY', 'BMBL', 'MTCH', 'IAC'
        ]
    
    # ===================
    # 投资主题扩展
    # ===================
    
    def _get_growth_stocks(self):
        """成长股"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM',
            'SNOW', 'CRWD', 'ZS', 'OKTA', 'NET', 'DDOG', 'MDB', 'TWLO', 'ROKU', 'SQ',
            'SHOP', 'SPOT', 'UBER', 'LYFT', 'DASH', 'ABNB', 'PINS', 'SNAP', 'RBLX', 'COIN',
            'HOOD', 'SOFI', 'PLTR', 'AFRM', 'UPST', 'RIVN', 'LCID', 'DNA', 'EDIT', 'CRSP'
        ]
    
    def _get_value_stocks(self):
        """价值股"""
        return [
            'BRK-B', 'JPM', 'BAC', 'WFC', 'C', 'XOM', 'CVX', 'JNJ', 'PG', 'KO',
            'WMT', 'HD', 'PFE', 'MRK', 'VZ', 'T', 'IBM', 'INTC', 'CSCO', 'ORCL',
            'GE', 'F', 'GM', 'CAT', 'MMM', 'BA', 'UPS', 'WBA', 'CVS', 'TGT'
        ]
    
    def _get_dividend_stocks(self):
        """高股息股"""
        return [
            'T', 'VZ', 'XOM', 'CVX', 'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'MCD',
            'IBM', 'CSCO', 'INTC', 'ORCL', 'ABBV', 'PFE', 'MRK', 'MMM', 'CAT', 'BA',
            'O', 'MAIN', 'STAG', 'EPD', 'ET', 'KMI', 'ENB', 'TRP', 'PPL', 'SO'
        ]
    
    def _get_dividend_aristocrats(self):
        """股息贵族（连续25年以上增加股息）"""
        return [
            'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'MCD', 'CAT', 'MMM', 'HD', 'LOW',
            'TGT', 'SWK', 'SHW', 'ECL', 'CLX', 'ADM', 'AFL', 'BDX', 'CINF', 'ED',
            'EMR', 'GPC', 'HRL', 'ITW', 'LEG', 'MDT', 'NUE', 'PPG', 'SYY', 'WBA'
        ]
    
    def _get_momentum_stocks(self):
        """动量股（近期表现强势）"""
        return [
            'NVDA', 'META', 'TSLA', 'GOOGL', 'MSFT', 'AAPL', 'AMZN', 'NFLX', 'AMD', 'AVGO',
            'CRM', 'ADBE', 'NOW', 'SNOW', 'CRWD', 'ZS', 'NET', 'DDOG', 'MDB', 'TWLO',
            'ROKU', 'SQ', 'SHOP', 'COIN', 'HOOD', 'RBLX', 'PLTR', 'SOFI', 'AFRM', 'RIVN'
        ]
    
    def _get_high_volatility_stocks(self):
        """高波动率股票"""
        return [
            'TSLA', 'AMC', 'GME', 'BB', 'PLTR', 'RIVN', 'LCID', 'NKLA', 'SPCE', 'WISH',
            'CLOV', 'SOFI', 'HOOD', 'COIN', 'RBLX', 'ROKU', 'ZM', 'PTON', 'DNA', 'ROOT',
            'OPEN', 'UPST', 'AFRM', 'PLUG', 'FCEL', 'BLDP', 'QS', 'HYLN', 'RIDE', 'FSR'
        ]
    
    # ===================
    # 特殊主题股票
    # ===================
    
    def _get_meme_stocks(self):
        """Meme股票（社交媒体热门）"""
        return [
            'GME', 'AMC', 'BB', 'NOK', 'SNDL', 'NAKD', 'CLOV', 'WISH', 'SPCE', 'PLTR',
            'HOOD', 'SOFI', 'COIN', 'RBLX', 'DNA', 'ROOT', 'OPEN', 'RIDE', 'NKLA', 'HYLN',
            'QS', 'LCID', 'RIVN', 'FSR', 'GOEV', 'CANOO', 'ARVL', 'MULN', 'EXPR', 'KOSS'
        ]
    
    def _get_penny_stocks_sample(self):
        """低价股样本（<$5）"""
        return [
            'SIRI', 'NOK', 'BB', 'SNDL', 'NAKD', 'GNUS', 'HMHC', 'TOPS', 'SHIP', 'DRYS',
            'DGLY', 'UONE', 'UONEK', 'KODK', 'EXPR', 'KOSS', 'CLOV', 'WKHS', 'RIDE', 'MULN'
        ]
    
    def _get_recent_ipos(self):
        """2023-2024年IPO股票"""
        return [
            'RIVN', 'LCID', 'BROS', 'DNA', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST',
            'ROOT', 'OPEN', 'WISH', 'CLOV', 'SPCE', 'HYLN', 'QS', 'CHPT', 'BLNK', 'EVGO',
            'GOEV', 'CANOO', 'ARVL', 'FSR', 'PSNY', 'LEV', 'NIU', 'XPEV', 'LI', 'NIO'
        ]
    
    def _get_trending_stocks(self):
        """当前热门股票"""
        return [
            'NVDA', 'META', 'TSLA', 'GOOGL', 'MSFT', 'AAPL', 'AMZN', 'COIN', 'RBLX', 'HOOD',
            'SOFI', 'PLTR', 'RIVN', 'LCID', 'AMD', 'CRM', 'SNOW', 'CRWD', 'NET', 'DDOG'
        ]
    
    def _get_earnings_calendar(self):
        """本周财报股票（示例）"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'JPM', 'BAC',
            'WFC', 'GS', 'JNJ', 'PFE', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE'
        ]
    
    def _get_blue_chip_stocks(self):
        """蓝筹股"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'BRK-B', 'JPM', 'JNJ', 'PG', 'UNH', 'HD',
            'MA', 'V', 'DIS', 'WMT', 'KO', 'MCD', 'PEP', 'CVX', 'XOM', 'BAC',
            'CSCO', 'VZ', 'ORCL', 'ABBV', 'PFE', 'TMO', 'COST', 'NKE', 'ADBE', 'CRM'
        ]
    
    def _get_high_volume_stocks(self):
        """高成交量股票"""
        return [
            'SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMD', 'MSFT', 'AMZN', 'SOXL', 'TQQQ',
            'META', 'GOOGL', 'IWM', 'XLF', 'PLTR', 'F', 'BAC', 'SOFI', 'RIVN', 'NIO',
            'LCID', 'BABA', 'COIN', 'AMC', 'GME', 'BB', 'SIRI', 'HOOD', 'RBLX', 'ROKU'
        ]
    
    def _get_popular_etf_holdings(self):
        """热门ETF重仓股"""
        return [
            # SPY重仓股
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
            # QQQ重仓股
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST', 'NFLX',
            # ARK ETFs重仓股
            'TSLA', 'ROKU', 'COIN', 'RBLX', 'HOOD', 'PLTR', 'ZOOM', 'CRSP', 'EDIT', 'DNA'
        ]
    
    # ===================
    # 国际市场股票
    # ===================
    
    def _get_chinese_adrs(self):
        """中概股ADR"""
        return [
            'BABA', 'JD', 'PDD', 'NIO', 'XPEV', 'LI', 'BIDU', 'NTES', 'TME', 'VIPS',
            'IQ', 'BILI', 'BEKE', 'DIDI', 'GRAB', 'SE', 'TAL', 'EDU', 'YMM', 'WB',
            'DOYU', 'HUYA', 'MOMO', 'YY', 'SINA', 'SOHU', 'FENG', 'CAN', 'TIGR', 'FUTU'
        ]
    
    def _get_european_adrs(self):
        """欧洲ADR"""
        return [
            'ASML', 'SAP', 'NVO', 'UL', 'TM', 'SONY', 'TSM', 'SHOP', 'SPOT', 'ADYEN',
            'NTR', 'CNI', 'ENB', 'TRP', 'RY', 'TD', 'BNS', 'CM', 'BMO', 'SU'
        ]
    
    def _get_emerging_market_adrs(self):
        """新兴市场ADR"""
        return [
            'TSM', 'BABA', 'JD', 'PDD', 'NIO', 'ASML', 'SAP', 'MELI', 'SE', 'GRAB',
            'VALE', 'ITUB', 'BBD', 'PBR', 'ERJ', 'SBS', 'CIG', 'PAM', 'UGP', 'GGAL'
        ]
    
    # ===================
    # 新兴科技主题
    # ===================
    
    def _get_ai_ml_stocks(self):
        """人工智能和机器学习股票"""
        return [
            'NVDA', 'GOOGL', 'MSFT', 'AAPL', 'META', 'AMZN', 'CRM', 'ORCL', 'ADBE', 'NOW',
            'SNOW', 'PLTR', 'AI', 'PATH', 'BIGC', 'FROG', 'SUMO', 'ESTC', 'BILL', 'SMAR',
            'GTLB', 'MDB', 'DDOG', 'NET', 'CRWD', 'ZS', 'OKTA', 'TWLO', 'FSLY', 'CFLT'
        ]
    
    def _get_cloud_stocks(self):
        """云计算股票"""
        return [
            'AMZN', 'MSFT', 'GOOGL', 'SNOW', 'CRM', 'ORCL', 'VMW', 'NOW', 'WDAY', 'ADSK',
            'INTU', 'VEEV', 'ZEN', 'TEAM', 'ATLASSIAN', 'DOCU', 'ZOOM', 'OKTA', 'MDB', 'NET'
        ]
    
    def _get_cybersecurity_stocks(self):
        """网络安全股票"""
        return [
            'CRWD', 'ZS', 'OKTA', 'PANW', 'FTNT', 'CYBR', 'SPLK', 'CHKP', 'FEYE', 'RPD',
            'TENB', 'VRNS', 'SAIL', 'QLYS', 'PING', 'RBRK', 'JFROG', 'DCBO', 'OPRX', 'NSEC'
        ]
    
    def _get_biotech_stocks(self):
        """生物技术股票"""
        return [
            'BIIB', 'MRNA', 'NVAX', 'BNTX', 'MODERNA', 'ILMN', 'EXAS', 'PACB', 'EDIT', 'CRSP',
            'NTLA', 'BEAM', 'BLUE', 'FATE', 'SRPT', 'BMRN', 'RARE', 'FOLD', 'ARCT', 'MYGN',
            'ICPT', 'ALNY', 'IONS', 'IOVA', 'ACAD', 'SAGE', 'NBIX', 'HALO', 'PTCT', 'ZLAB'
        ]
    
    def _get_clean_energy_stocks(self):
        """清洁能源股票"""
        return [
            'NEE', 'ENPH', 'SEDG', 'FSLR', 'SPWR', 'RUN', 'NOVA', 'CSIQ', 'JKS', 'DQ',
            'MAXN', 'ARRY', 'VSLR', 'SUNS', 'SOL', 'AMPS', 'AMPX', 'FLEX', 'FREY', 'CLSK',
            'PLUG', 'FCEL', 'BLDP', 'CLNE', 'BE', 'HYLN', 'NKLA', 'HYSR', 'HYGS', 'HYZN'
        ]
    
    def _get_ev_autonomous_stocks(self):
        """电动车和自动驾驶股票"""
        return [
            'TSLA', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'FSR', 'QS', 'CHPT', 'BLNK',
            'EVGO', 'GOEV', 'CANOO', 'ARVL', 'MULN', 'WKHS', 'RIDE', 'PSNY', 'LEV', 'NIU',
            'GOOGL', 'AAPL', 'NVDA', 'AMD', 'INTC', 'QCOM', 'MRVL', 'ON', 'SWKS', 'SITM'
        ]
    
    def _get_space_defense_stocks(self):
        """航天和国防股票"""
        return [
            'LMT', 'RTX', 'NOC', 'GD', 'BA', 'LHX', 'TXT', 'HII', 'KTOS', 'AJRD',
            'SPCE', 'RKLB', 'ASTR', 'VORB', 'MAXR', 'IRDM', 'VSAT', 'GSAT', 'ORBC', 'GILT'
        ]
    
    def _get_blockchain_stocks(self):
        """区块链相关股票"""
        return [
            'COIN', 'MSTR', 'TSLA', 'SQ', 'PYPL', 'NVDA', 'AMD', 'MARA', 'RIOT', 'HUT',
            'BITF', 'CAN', 'BTBT', 'ANY', 'BTC', 'EBON', 'SOS', 'XNET', 'EQOS', 'PHUN'
        ]
    
    def _get_sector_top_stocks(self, sector):
        """获取行业头部股票"""
        sector_stocks = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA', 'CRM', 'ADBE', 'ORCL', 'CSCO'],
            'financials': self.get_financial_stocks()[:20],  # 取前20只金融股
            'crypto': self.get_crypto_related_stocks(),
            'fintech': self.get_fintech_stocks(),
            'healthcare': ['UNH', 'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'KMI'],
            'consumer_discretionary': ['AMZN', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TJX', 'F', 'GM', 'BKNG']
        }
        
        return sector_stocks.get(sector.lower(), [])
    
    def create_custom_watchlist(self, mode='balanced', limit=None):
        """创建自定义监控列表"""
        if mode == 'sp500':
            return self.get_sp500_stocks()[:limit] if limit else self.get_sp500_stocks()
        elif mode == 'nasdaq100':
            return self.get_nasdaq100_stocks()[:limit] if limit else self.get_nasdaq100_stocks()
        elif mode == 'dow30':
            return self.get_dow_jones_stocks()
        elif mode == 'active':
            return self.get_most_active_stocks(limit or 100)
        elif mode == 'financials':
            # 金融股专扫
            return self.get_financial_stocks()[:limit] if limit else self.get_financial_stocks()
        elif mode == 'crypto':
            # 加密货币相关股票
            return self.get_crypto_related_stocks()[:limit] if limit else self.get_crypto_related_stocks()
        elif mode == 'fintech':
            # 金融科技股票
            return self.get_fintech_stocks()[:limit] if limit else self.get_fintech_stocks()
        elif mode == 'finance_crypto':
            # 金融+加密货币组合
            financial_stocks = self.get_financial_stocks()[:30]
            crypto_stocks = self.get_crypto_related_stocks()
            combined = list(set(financial_stocks + crypto_stocks))
            return combined[:limit] if limit else combined
        elif mode == 'banks':
            # 银行股专扫
            bank_stocks = [
                'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'COF', 'USB', 'PNC', 'TFC',
                'ZION', 'RF', 'FITB', 'HBAN', 'CFG', 'KEY', 'CMA', 'MTB'
            ]
            return bank_stocks[:limit] if limit else bank_stocks
        elif mode == 'balanced':
            # 平衡组合：道琼斯30 + 纳斯达克100热门股
            stocks = self.get_dow_jones_stocks()
            nasdaq_top = self.get_nasdaq100_stocks()[:50]
            # 去重合并
            combined = list(set(stocks + nasdaq_top))
            return combined[:limit] if limit else combined
        elif mode == 'mega_cap':
            # 超大盘股（市值>1000亿）
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
                'UNH', 'JNJ', 'JPM', 'V', 'PG', 'XOM', 'HD', 'CVX', 'MA', 'BAC',
                'ABBV', 'PFE', 'AVGO', 'COST', 'DIS', 'KO', 'MRK', 'PEP', 'TMO',
                'WMT', 'ABT', 'ACN', 'CSCO', 'LIN', 'ADBE', 'VZ', 'CRM', 'DHR'
            ]
        elif mode == 'russell1000':
            return self._get_russell1000_sample()[:limit] if limit else self._get_russell1000_sample()
        elif mode == 'russell2000':
            return self._get_russell2000_sample()[:limit] if limit else self._get_russell2000_sample()
        elif mode == 'russell3000':
            return self._get_russell3000_sample()[:limit] if limit else self._get_russell3000_sample()
        elif mode == 'large_cap':
            return self._get_large_cap_stocks()[:limit] if limit else self._get_large_cap_stocks()
        elif mode == 'mid_cap':
            return self._get_mid_cap_stocks()[:limit] if limit else self._get_mid_cap_stocks()
        elif mode == 'small_cap':
            return self._get_small_cap_stocks()[:limit] if limit else self._get_small_cap_stocks()
        elif mode == 'tech_expanded':
            return self._get_tech_stocks_expanded()[:limit] if limit else self._get_tech_stocks_expanded()
        elif mode == 'healthcare':
            return self._get_healthcare_stocks()[:limit] if limit else self._get_healthcare_stocks()
        elif mode == 'energy':
            return self._get_energy_stocks()[:limit] if limit else self._get_energy_stocks()
        elif mode == 'growth':
            return self._get_growth_stocks()[:limit] if limit else self._get_growth_stocks()
        elif mode == 'value':
            return self._get_value_stocks()[:limit] if limit else self._get_value_stocks()
        elif mode == 'dividend':
            return self._get_dividend_stocks()[:limit] if limit else self._get_dividend_stocks()
        elif mode == 'momentum':
            return self._get_momentum_stocks()[:limit] if limit else self._get_momentum_stocks()
        elif mode == 'meme_stocks':
            return self._get_meme_stocks()[:limit] if limit else self._get_meme_stocks()
        elif mode == 'ai_ml':
            return self._get_ai_ml_stocks()[:limit] if limit else self._get_ai_ml_stocks()
        elif mode == 'cloud':
            return self._get_cloud_stocks()[:limit] if limit else self._get_cloud_stocks()
        elif mode == 'cybersecurity':
            return self._get_cybersecurity_stocks()[:limit] if limit else self._get_cybersecurity_stocks()
        elif mode == 'biotech':
            return self._get_biotech_stocks()[:limit] if limit else self._get_biotech_stocks()
        elif mode == 'clean_energy':
            return self._get_clean_energy_stocks()[:limit] if limit else self._get_clean_energy_stocks()
        elif mode == 'ev_autonomous':
            return self._get_ev_autonomous_stocks()[:limit] if limit else self._get_ev_autonomous_stocks()
        elif mode == 'chinese_adrs':
            return self._get_chinese_adrs()[:limit] if limit else self._get_chinese_adrs()
        elif mode == 'comprehensive':
            # 最全面的扫描 - 包含所有主要股票池
            comprehensive = (
                self.get_sp500_stocks()[:200] +
                self.get_nasdaq100_stocks()[:80] +
                self._get_russell2000_sample()[:100] +
                self._get_growth_stocks()[:50] +
                self._get_value_stocks()[:30] +
                self._get_tech_stocks_expanded()[:40] +
                self.get_financial_stocks()[:30] +
                self._get_healthcare_stocks()[:30] +
                self._get_energy_stocks()[:20]
            )
            unique_comprehensive = list(set(comprehensive))
            return unique_comprehensive[:limit] if limit else unique_comprehensive
        elif mode == 'mega_scan':
            # 超大范围扫描 - 2000+股票
            mega_scan = (
                self.get_sp500_stocks() +
                self.get_nasdaq100_stocks() +
                self._get_russell1000_sample() +
                self._get_russell2000_sample()[:200] +
                self._get_large_cap_stocks() +
                self._get_mid_cap_stocks() +
                self._get_growth_stocks() +
                self._get_value_stocks() +
                self._get_momentum_stocks() +
                self._get_dividend_stocks() +
                self._get_tech_stocks_expanded() +
                self.get_financial_stocks() +
                self._get_healthcare_stocks() +
                self._get_energy_stocks() +
                self._get_ai_ml_stocks() +
                self._get_biotech_stocks() +
                self._get_clean_energy_stocks()
            )
            unique_mega = list(set(mega_scan))
            return unique_mega[:limit] if limit else unique_mega
        elif mode == 'sector_rotation':
            # 行业轮动组合 - 覆盖11个主要行业
            sector_rotation = (
                self._get_tech_stocks_expanded()[:30] +
                self.get_financial_stocks()[:25] +
                self._get_healthcare_stocks()[:25] +
                self._get_energy_stocks()[:20] +
                self._get_consumer_discretionary_stocks()[:20] +
                self._get_consumer_staples_stocks()[:15] +
                self._get_industrial_stocks()[:20] +
                self._get_materials_stocks()[:15] +
                self._get_utilities_stocks()[:15] +
                self._get_real_estate_stocks()[:15] +
                self._get_communication_stocks()[:15]
            )
            unique_sector = list(set(sector_rotation))
            return unique_sector[:limit] if limit else unique_sector
        else:
            return self._get_fallback_sp500()[:limit] if limit else self._get_fallback_sp500()
    
    def get_stock_pool(self, pool_name: str) -> List[str]:
        """获取指定股票池"""
        return self.stock_pools.get(pool_name, [])
    
    def get_available_pools(self) -> Dict[str, int]:
        """获取所有可用股票池及其大小"""
        return {name: len(stocks) for name, stocks in self.stock_pools.items()}
    
    def get_pool_info(self) -> Dict:
        """获取所有股票池的详细信息"""
        info = {}
        for pool_name, stocks in self.stock_pools.items():
            info[pool_name] = {
                'count': len(stocks),
                'description': self._get_pool_description(pool_name),
                'sample': stocks[:5] if stocks else []
            }
        return info
    
    def _get_pool_description(self, pool_name: str) -> str:
        """获取股票池描述"""
        descriptions = {
            # 主要指数
            'sp500': 'S&P 500指数成分股 (大盘蓝筹)',
            'nasdaq100': 'NASDAQ 100指数成分股 (科技权重股)',
            'dow30': '道琼斯30指数成分股 (工业蓝筹)',
            'russell1000': '罗素1000大中盘股',
            'russell2000': '罗素2000小盘股样本',
            'russell3000': '罗素3000全市场股票',
            
            # 市值分类
            'mega_cap': '超大盘股 (市值>1000亿美元)',
            'large_cap': '大盘股 (市值100-1000亿)',
            'mid_cap': '中盘股 (市值20-100亿)',
            'small_cap': '小盘股 (市值2-20亿)',
            'micro_cap': '微盘股 (市值<2亿)',
            
            # 行业板块
            'tech': '科技板块 (包含软件、半导体、消费科技)',
            'finance': '金融板块 (银行、保险、投资)',
            'healthcare': '医疗健康 (制药、生物科技、医疗设备)',
            'energy': '能源板块 (传统能源+新能源)',
            'consumer_disc': '消费者自由支配支出',
            'consumer_staples': '消费必需品',
            'industrials': '工业板块',
            'materials': '材料板块',
            'utilities': '公用事业',
            'real_estate': '房地产投资信托',
            'communication': '通信服务',
            
            # 投资主题
            'growth': '成长股 (高增长潜力)',
            'value': '价值股 (低估值)',
            'dividend': '高股息股',
            'momentum': '动量股 (近期强势)',
            'volatility': '高波动率股票',
            
            # 特殊主题
            'meme_stocks': 'Meme股票 (社交媒体热门)',
            'penny_stocks': '低价股 (<$5)',
            'ipos_2023_2024': '2023-2024年IPO股票',
            'trending': '当前热门股票',
            'earnings_week': '本周财报股票',
            
            # 定制组合
            'blue_chip': '蓝筹股 (行业领导者)',
            'dividend_aristocrats': '股息贵族 (连续25年+增息)',
            'high_volume': '高成交量股票',
            'etf_holdings': '热门ETF重仓股',
            
            # 国际市场
            'chinese_adrs': '中概股ADR',
            'european_adrs': '欧洲ADR',
            'emerging_markets': '新兴市场ADR',
            
            # 新兴科技
            'ai_ml': '人工智能和机器学习',
            'cloud_computing': '云计算',
            'cybersecurity': '网络安全',
            'biotech': '生物技术',
            'clean_energy': '清洁能源',
            'ev_autonomous': '电动车和自动驾驶',
            'space_defense': '航天和国防',
            'blockchain': '区块链和加密货币',
            
            # 扩展组合
            'crypto': '加密货币相关股票',
            'fintech': '金融科技',
            'comprehensive': '全面扫描组合 (500+股票)',
            'mega_scan': '超大范围扫描 (2000+股票)',
            'sector_rotation': '行业轮动组合 (11个行业代表)'
        }
        return descriptions.get(pool_name, f'{pool_name} 股票池')
    
    def print_pool_summary(self):
        """打印股票池汇总信息"""
        print("📊 华尔街母鸡 - 扩展股票池汇总")
        print("=" * 60)
        
        pool_info = self.get_pool_info()
        
        # 按类别分组显示
        categories = {
            '🏆 主要指数': ['sp500', 'nasdaq100', 'dow30', 'russell1000', 'russell2000', 'russell3000'],
            '💰 市值分类': ['mega_cap', 'large_cap', 'mid_cap', 'small_cap', 'micro_cap'],
            '🏭 行业板块': ['tech', 'finance', 'healthcare', 'energy', 'consumer_disc', 'consumer_staples', 
                         'industrials', 'materials', 'utilities', 'real_estate', 'communication'],
            '📈 投资主题': ['growth', 'value', 'dividend', 'momentum', 'volatility'],
            '🔥 特殊主题': ['meme_stocks', 'penny_stocks', 'ipos_2023_2024', 'trending', 'earnings_week'],
            '⭐ 定制组合': ['blue_chip', 'dividend_aristocrats', 'high_volume', 'etf_holdings'],
            '🌍 国际市场': ['chinese_adrs', 'european_adrs', 'emerging_markets'],
            '🚀 新兴科技': ['ai_ml', 'cloud_computing', 'cybersecurity', 'biotech', 'clean_energy', 
                         'ev_autonomous', 'space_defense', 'blockchain'],
            '🎯 超级扫描': ['comprehensive', 'mega_scan', 'sector_rotation']
        }
        
        total_stocks = 0
        for category, pools in categories.items():
            print(f"\n{category}:")
            for pool in pools:
                if pool in pool_info:
                    info = pool_info[pool]
                    print(f"  {pool:20} | {info['count']:4}只 | {info['description']}")
                    total_stocks += info['count']
        
        print("\n" + "=" * 60)
        print(f"🎯 总扫描范围: {total_stocks:,}+ 只股票")
        print(f"🔥 新增扫描模式: 40+ 种")
        print(f"💪 覆盖范围: 全美股市场 + 国际ADR")
        print("=" * 60)