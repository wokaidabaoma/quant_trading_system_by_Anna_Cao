# notification.py - Mac多渠道通知系统
import subprocess
import os
from datetime import datetime
import json

class MacNotification:
    def __init__(self):
        self.log_file = "logs/trading_signals.log"
        # 创建日志目录
        os.makedirs("logs", exist_ok=True)
        
    def send_signal(self, signal, position):
        """发送多渠道通知"""
        # 1. Mac系统通知
        self.send_mac_notification(signal, position)
        
        # 2. 控制台彩色输出
        self.print_colored_signal(signal, position)
        
        # 3. 保存到日志文件
        self.save_to_log(signal, position)
        
        # 4. 如果是强信号，播放声音
        if any(s['strength'] == 'STRONG' for s in signal['signals']):
            self.play_sound()
    
    def send_mac_notification(self, signal, position):
        """Mac桌面通知"""
        action = "🟢 买入" if position['action'] == 'BUY' else "🔴 卖出"
        title = f"🐔 {signal['symbol']} {action}信号"
        subtitle = f"价格: ${signal['price']:.2f}"
        message = f"RSI:{signal['RSI']:.1f} | 止损:${position['stop_loss']:.2f} | 止盈:${position['take_profit']:.2f}"
        
        script = f'''
        display notification "{message}" with title "{title}" subtitle "{subtitle}"
        '''
        
        try:
            subprocess.run(["osascript", "-e", script], check=True)
        except:
            pass  # 忽略通知错误
    
    def play_sound(self):
        """播放系统声音"""
        try:
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
        except:
            pass
    
    def print_colored_signal(self, signal, position):
        """彩色控制台输出"""
        # ANSI颜色代码
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        
        color = GREEN if position['action'] == 'BUY' else RED
        
        print(f"""
{YELLOW}{'='*60}{RESET}
{BOLD}{color}🐔 交易信号 - {signal['symbol']}{RESET}
{YELLOW}{'='*60}{RESET}

{BLUE}📊 技术指标:{RESET}
  • 价格: ${signal['price']:.2f}
  • RSI: {signal['RSI']:.1f}
  • 成交量比: {signal['volume_ratio']:.1f}x
  • ATR: {signal['ATR']:.2f}

{BLUE}📈 信号类型:{RESET}""")
        
        for s in signal['signals']:
            emoji = "🟢" if s['type'] == 'BUY' else "🔴"
            strength_color = RED if s['strength'] == 'STRONG' else YELLOW
            print(f"  {emoji} {s['reason']} {strength_color}[{s['strength']}]{RESET}")
        
        print(f"""
{BLUE}💼 仓位建议:{RESET}
  • {color}操作: {position['action']}{RESET}
  • 股数: {position['shares']}
  • 止损: ${position['stop_loss']:.2f} (-{((signal['price']-position['stop_loss'])/signal['price']*100):.1f}%)
  • 止盈: ${position['take_profit']:.2f} (+{((position['take_profit']-signal['price'])/signal['price']*100):.1f}%)
  • 仓位价值: ${position['position_value']:.2f}
""")
        
        if position.get('inverse_etf'):
            print(f"  • 建议反向ETF: {position['inverse_etf']}")
        
        if signal.get('insider_trades'):
            print(f"\n{BLUE}💰 内幕交易:{RESET}")
            for trade in signal['insider_trades'][:3]:
                print(f"  • {trade['name']}: ${trade['value']:,.0f}")
        
        print(f"{YELLOW}{'='*60}{RESET}\n")
    
    def save_to_log(self, signal, position):
        """保存到日志文件（JSON格式）"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': signal['symbol'],
            'price': signal['price'],
            'RSI': signal['RSI'],
            'volume_ratio': signal['volume_ratio'],
            'signals': signal['signals'],
            'position': {
                'action': position['action'],
                'shares': position['shares'],
                'stop_loss': position['stop_loss'],
                'take_profit': position['take_profit'],
                'position_value': position['position_value']
            }
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def send_daily_summary(self, summary):
        """发送每日总结"""
        # ANSI颜色代码
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        
        print(f"""
{BOLD}{BLUE}📅 每日市场总结{RESET}
{YELLOW}{'='*60}{RESET}

🌡️ 市场情绪:
  • VIX: {summary['sentiment']['VIX']['value']:.2f} - {summary['sentiment']['VIX']['signal']}
  • 市场广度: {summary['sentiment'].get('breadth', {}).get('value', 'N/A')}%

📊 今日统计:
  • 扫描股票数: {len(summary.get('scanned_symbols', []))}
  • 信号数量: {summary['signal_count']}
  • 强势股票: {', '.join(summary['strong_stocks'][:5]) if summary['strong_stocks'] else '无'}
  • 弱势股票: {', '.join(summary['weak_stocks'][:5]) if summary['weak_stocks'] else '无'}

{YELLOW}{'='*60}{RESET}
""")
        
        # Mac通知
        script = f'''
        display notification "信号数: {summary['signal_count']} | VIX: {summary['sentiment']['VIX']['value']:.2f}" with title "🐔 每日总结" sound name "Glass"
        '''
        subprocess.run(["osascript", "-e", script])

# 添加兼容性
NotificationSystem = MacNotification  # 兼容旧代码