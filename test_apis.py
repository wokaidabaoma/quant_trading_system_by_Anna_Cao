# test_apis.py - 测试付费API连接
"""
测试脚本：验证所有付费API是否正常工作
"""

from config import Config
from data_manager import DataManager

def test_apis():
    """测试所有API连接"""
    print("🔍 开始测试付费API连接...")
    print("=" * 50)
    
    # 初始化配置和数据管理器
    config = Config()
    dm = DataManager(config)
    
    # 检查API密钥配置
    print("📋 API配置检查:")
    print(f"Finnhub API: {'✅ 已配置' if config.FINNHUB_API_KEY else '❌ 未配置'}")
    print(f"  密钥: {config.FINNHUB_API_KEY[:10]}..." if config.FINNHUB_API_KEY else "")
    
    print(f"Polygon API: {'✅ 已配置' if config.POLYGON_API_KEY else '❌ 未配置'}")  
    print(f"  密钥: {config.POLYGON_API_KEY[:10]}..." if config.POLYGON_API_KEY else "")
    
    print(f"Alpha Vantage: {'✅ 已配置' if config.ALPHA_VANTAGE_API_KEY else '❌ 未配置'}")
    print(f"  密钥: {config.ALPHA_VANTAGE_API_KEY[:10]}..." if config.ALPHA_VANTAGE_API_KEY else "")
    
    print("\n" + "=" * 50)
    
    # 测试符号
    test_symbol = "AAPL"
    print(f"🧪 测试股票: {test_symbol}")
    print("=" * 50)
    
    # 1. 测试实时价格 (Finnhub)
    print("\n1️⃣ 测试Finnhub实时价格API...")
    try:
        real_time_data = dm.get_real_time_price(test_symbol)
        if real_time_data:
            print("✅ Finnhub API连接成功!")
            print(f"  实时价格: ${real_time_data.get('price', 'N/A'):.2f}")
            print(f"  涨跌幅: {real_time_data.get('change_percent', 'N/A'):.2f}%")
            print(f"  日高: ${real_time_data.get('high', 'N/A'):.2f}")
            print(f"  日低: ${real_time_data.get('low', 'N/A'):.2f}")
        else:
            print("❌ Finnhub API连接失败")
    except Exception as e:
        print(f"❌ Finnhub API错误: {e}")
    
    # 2. 测试内幕交易 (Finnhub)
    print("\n2️⃣ 测试Finnhub内幕交易API...")
    try:
        insider_data = dm.get_insider_trading(test_symbol)
        if insider_data:
            print(f"✅ 获取到 {len(insider_data)} 条内幕交易记录")
            if insider_data:
                latest = insider_data[0]
                print(f"  最新交易: {latest.get('name', 'N/A')} - {latest.get('action', 'N/A')}")
        else:
            print("⚠️ 无内幕交易数据 (可能正常)")
    except Exception as e:
        print(f"❌ 内幕交易API错误: {e}")
    
    # 3. 测试公司新闻 (Finnhub)
    print("\n3️⃣ 测试Finnhub新闻API...")
    try:
        news_data = dm.get_company_news(test_symbol, days=7)
        if news_data:
            print(f"✅ 获取到 {len(news_data)} 条新闻")
            if news_data:
                latest_news = news_data[0]
                headline = latest_news.get('headline', 'N/A')
                print(f"  最新新闻: {headline[:50]}...")
        else:
            print("⚠️ 无新闻数据")
    except Exception as e:
        print(f"❌ 新闻API错误: {e}")
    
    # 4. 测试分析师评级 (Finnhub)
    print("\n4️⃣ 测试Finnhub分析师评级API...")
    try:
        analyst_data = dm.get_analyst_recommendations(test_symbol)
        if analyst_data:
            print("✅ 获取到分析师评级数据")
            total = sum([
                analyst_data.get('strongBuy', 0),
                analyst_data.get('buy', 0),
                analyst_data.get('hold', 0),
                analyst_data.get('sell', 0),
                analyst_data.get('strongSell', 0)
            ])
            print(f"  分析师总数: {total}")
            print(f"  强烈买入: {analyst_data.get('strongBuy', 0)}")
            print(f"  买入: {analyst_data.get('buy', 0)}")
            print(f"  持有: {analyst_data.get('hold', 0)}")
        else:
            print("⚠️ 无分析师评级数据")
    except Exception as e:
        print(f"❌ 分析师API错误: {e}")
    
    # 5. 测试VIX情绪
    print("\n5️⃣ 测试VIX情绪指标...")
    try:
        vix_data = dm.get_vix_sentiment()
        if vix_data:
            print("✅ VIX数据获取成功")
            print(f"  VIX值: {vix_data.get('value', 'N/A'):.2f}")
            print(f"  市场情绪: {vix_data.get('sentiment', 'N/A')}")
            print(f"  交易信号: {vix_data.get('signal', 'N/A')}")
        else:
            print("❌ VIX数据获取失败")
    except Exception as e:
        print(f"❌ VIX API错误: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API测试完成!")
    print("如果看到✅标记，说明对应API工作正常")
    print("如果看到❌标记，请检查API密钥或网络连接")
    print("⚠️ 某些API可能因为市场时间或数据可用性显示无数据，这是正常的")

if __name__ == "__main__":
    test_apis()