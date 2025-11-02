#!/usr/bin/env python3
# quick_log.py - 快速日志查看器

import json
import os
from datetime import datetime

def quick_view():
    """快速查看最新日志"""
    log_file = "logs/trading_signals.log"
    
    if not os.path.exists(log_file):
        print("❌ 日志文件不存在")
        return
    
    print("🐔 华尔街母鸡 - 最新交易信号")
    print("="*50)
    
    signals = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        signal = json.loads(line.strip())
                        signals.append(signal)
                    except:
                        continue
    except Exception as e:
        print(f"❌ 读取日志失败: {e}")
        return
    
    if not signals:
        print("⚪ 暂无交易信号")
        return
    
    # 显示最新5条
    recent_signals = signals[-5:]
    
    for i, signal in enumerate(recent_signals, 1):
        dt = datetime.fromisoformat(signal['timestamp'])
        action = signal['position']['action']
        action_emoji = "🟢" if action == "BUY" else "🔴"
        
        reasons = [s['reason'] for s in signal['signals']]
        reason_text = reasons[0] if reasons else '未知'
        
        print(f"{i}. {action_emoji} {signal['symbol']:<6} ${signal['price']:>7.2f} "
              f"RSI:{signal['RSI']:5.1f} | {reason_text}")
        print(f"   📅 {dt.strftime('%m-%d %H:%M')} | "
              f"仓位: {signal['position']['shares']}股 "
              f"(${signal['position']['position_value']:,.0f})")
    
    print(f"\n📊 总记录数: {len(signals)}")
    
    # 今日统计
    today = datetime.now().date()
    today_signals = []
    for signal in signals:
        signal_date = datetime.fromisoformat(signal['timestamp']).date()
        if signal_date == today:
            today_signals.append(signal)
    
    if today_signals:
        buy_count = len([s for s in today_signals if s['position']['action'] == 'BUY'])
        short_count = len([s for s in today_signals if s['position']['action'] == 'SHORT'])
        print(f"📅 今日: {len(today_signals)}个信号 (🟢{buy_count} 🔴{short_count})")
    else:
        print("📅 今日暂无信号")

if __name__ == "__main__":
    quick_view()