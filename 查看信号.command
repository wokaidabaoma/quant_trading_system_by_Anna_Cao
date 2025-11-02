#!/bin/bash
# 华尔街母鸡信号查看器

cd "$(dirname "$0")"

echo "🐔 华尔街母鸡信号查看器"
echo "========================"
echo "1. 快速查看最新信号"
echo "2. 查看今日详情"
echo "3. 查看统计分析"
echo "4. 交互式浏览器"
echo "5. 扫描新信号"
echo "========================"

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo "🚀 快速查看最新信号..."
        python3 quick_log.py
        ;;
    2)
        echo "📊 查看今日详情..."
        python3 log_viewer.py today
        ;;
    3)
        echo "📈 查看统计分析..."
        python3 log_viewer.py stats
        ;;
    4)
        echo "🖥️ 启动交互式浏览器..."
        python3 interactive_log.py
        ;;
    5)
        echo "🔍 开始扫描..."
        python3 main.py once
        ;;
    *)
        echo "❌ 无效选择"
        ;;
esac

echo ""
echo "按任意键退出..."
read -n 1