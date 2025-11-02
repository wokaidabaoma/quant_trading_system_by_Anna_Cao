#!/bin/bash
# 快速查看最新信号

cd "$(dirname "$0")"
echo "🐔 华尔街母鸡 - 快速查看最新信号"
echo "================================"
python3 quick_log.py
echo ""
echo "按任意键退出..."
read -n 1