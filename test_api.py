#!/usr/bin/env python3
# 测试API连接

from dotenv import load_dotenv
load_dotenv()

from config import Config
from data_manager import DataManager

def test_apis():
    print("🔄 测试API连接...")
    
    config = Config()
    dm = DataManager(config)
    
    # 测试实时价格
    print("\n📊 测试Finnhub实时价格...")
    price_data = dm.get_real_time_price('AAPL')
    if price_data and price_data.get('price'):
        print(f"✅ AAPL实时价格: ${price_data['price']:.2f}")
        print(f"   涨跌: {price_data.get('change', 0):.2f} ({price_data.get('change_percent', 0):.2f}%)")
    else:
        print("❌ 实时价格获取失败")
    
    # 测试内幕交易
    print("\n💰 测试内幕交易数据...")
    insider_data = dm.get_insider_trading('AAPL')
    print(f"✅ 获取到 {len(insider_data)} 条内幕交易记录")
    
    if insider_data:
        for trade in insider_data[:2]:
            print(f"   • {trade.get('name', 'N/A')}: {trade.get('action', 'N/A')} ${trade.get('value', 0):,.0f}")
    
    # 测试分析师建议
    print("\n📈 测试分析师建议...")
    recommendations = dm.get_analyst_recommendations('AAPL')
    if recommendations:
        print(f"✅ 分析师建议: 强买{recommendations.get('strongBuy', 0)} 买入{recommendations.get('buy', 0)} 持有{recommendations.get('hold', 0)}")
    else:
        print("❌ 分析师建议获取失败")
    
    # 测试新闻
    print("\n📰 测试公司新闻...")
    news = dm.get_company_news('AAPL', days=3)
    print(f"✅ 获取到 {len(news)} 条新闻")
    
    if news:
        for article in news[:2]:
            print(f"   • {article.get('headline', 'N/A')[:50]}...")
    
    print("\n🎉 API测试完成!")

if __name__ == "__main__":
    test_apis()