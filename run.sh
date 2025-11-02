#!/bin/bash

# 简化版启动脚本
echo "🐔 华尔街母鸡交易系统"
echo "======================"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 启动PostgreSQL和Redis
brew services start postgresql 2>/dev/null
brew services start redis 2>/dev/null

# 创建日志目录
mkdir -p logs

echo ""
echo "选择运行模式："
echo "1) 完整运行（定时扫描）"
echo "2) 单次扫描"
echo "3) 监控模式"
read -p "请选择 [1-3]: " choice

case $choice in
    1)
        echo "启动定时扫描..."
        python main.py
        ;;
    2)
        echo "运行单次扫描..."
        python main.py once
        ;;
    3)
        echo "启动监控器..."
        python monitor.py
        ;;
    *)
        echo "无效选择"
        ;;
esac
