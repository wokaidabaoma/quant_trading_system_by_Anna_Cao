# monitor.py - 实时日志监控
import json
import time
import os
from datetime import datetime

def monitor_signals():
    """监控交易信号"""
    log_file = "logs/trading_signals.log"
    
    # 颜色代码
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    print(f"{YELLOW}🐔 华尔街母鸡 - 信号监控器{RESET}")
    print("=" * 60)
    print(f"监控文件: {log_file}")
    print(f"按Ctrl+C退出\n")
    
    # 读取现有日志
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        print(f"📊 历史信号: {len(lines)} 条\n")
        
        # 显示最后5条
        print("最近信号:")
        print("-" * 60)
        for line in lines[-5:]:
            try:
                signal = json.loads(line)
                symbol = signal['symbol']
                action = signal['position']['action']
                price = signal['price']
                time_str = signal['timestamp']
                
                color = GREEN if action == 'BUY' else RED
                print(f"{color}{symbol}: {action} @ ${price:.2f}{RESET} - {time_str}")
            except:
                pass
    
    print("\n" + "=" * 60)
    print("⏳ 等待新信号...\n")
    
    # 实时监控
    last_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
    
    while True:
        try:
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                
                if current_size > last_size:
                    with open(log_file, 'r') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                    
                    for line in new_lines:
                        try:
                            signal = json.loads(line)
                            symbol = signal['symbol']
                            action = signal['position']['action']
                            price = signal['price']
                            
                            color = GREEN if action == 'BUY' else RED
                            print(f"{BLUE}[新信号]{RESET} {color}{symbol}: {action} @ ${price:.2f}{RESET}")
                            
                            # Mac通知
                            os.system(f"""osascript -e 'display notification "{symbol} {action} @ ${price:.2f}" with title "🐔 新信号" sound name "Glass"'""")
                            
                        except:
                            pass
                    
                    last_size = current_size
            
            time.sleep(2)  # 每2秒检查一次
            
        except KeyboardInterrupt:
            print("\n监控器已停止")
            break

if __name__ == "__main__":
    monitor_signals()