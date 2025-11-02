#!/bin/bash
# 华尔街母鸡 - 技术指标分析看板启动器

cd "$(dirname "$0")"

echo "🚀 华尔街母鸡 - 技术指标分析系统"
echo "=================================="
echo ""
echo "选择要启动的功能:"
echo ""
echo "1) 📈 日内交易看板 (实时K线+成交量分析)"
echo "2) 📊 原版Dashboard (PostgreSQL)"
echo "3) 🔧 安装依赖包"
echo "4) 📚 查看技术指标使用指南"
echo "5) ⚙️  运行技术指标测试"
echo "6) 🚪 退出"
echo ""

read -p "请选择 (1-6): " choice

case $choice in
    1)
        echo "🚀 启动日内交易看板..."
        python3 launch_intraday.py
        ;;
    2)
        echo "📊 启动原版Dashboard..."
        streamlit run dashboard.py --server.port 8501
        ;;
    3)
        echo "🔧 安装依赖包..."
        pip3 install -r requirements.txt
        echo "✅ 依赖安装完成"
        ;;
    4)
        echo "📚 打开技术指标使用指南..."
        if command -v open &> /dev/null; then
            open "技术指标使用指南.md"
        else
            cat "技术指标使用指南.md"
        fi
        ;;
    5)
        echo "⚙️ 运行技术指标测试..."
        python3 -c "
from data_manager import DataManager
from config import Config
import pandas as pd

# 测试技术指标
config = Config()
dm = DataManager(config)

print('🔍 测试获取AAPL数据...')
df = dm.get_stock_data('AAPL', '1mo')

if df is not None:
    print('✅ 数据获取成功!')
    print(f'📊 数据量: {len(df)} 条')
    print(f'📈 最新价格: \${df[\"Close\"].iloc[-1]:.2f}')
    print(f'📈 RSI: {df[\"RSI\"].iloc[-1]:.1f}')
    print(f'📈 成交量比率: {df[\"volume_ratio\"].iloc[-1]:.1f}x')
    print(f'📈 动量评分: {df[\"momentum_score\"].iloc[-1]:.0f}')
    print(f'📈 信号强度: {df[\"signal_strength\"].iloc[-1]}')
else:
    print('❌ 数据获取失败')
"
        ;;
    6)
        echo "👋 再见!"
        exit 0
        ;;
    *)
        echo "❌ 无效选择，请重新运行"
        ;;
esac

echo ""
echo "按任意键继续..."
read -n 1