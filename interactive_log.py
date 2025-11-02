#!/usr/bin/env python3
# interactive_log.py - 交互式日志浏览器

import json
import os
from datetime import datetime, timedelta
from log_viewer import LogViewer

class InteractiveLogBrowser:
    """交互式日志浏览器"""
    
    def __init__(self):
        self.viewer = LogViewer()
        self.running = True
    
    def run(self):
        """运行交互式界面"""
        self.show_welcome()
        
        while self.running:
            try:
                self.show_menu()
                choice = input("\n请选择操作 (1-9): ").strip()
                self.handle_choice(choice)
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                input("按回车键继续...")
    
    def show_welcome(self):
        """显示欢迎界面"""
        print("\n" + "="*60)
        print("🐔 华尔街母鸡 - 交互式日志浏览器")
        print("="*60)
        print(f"📁 日志文件: {self.viewer.log_file}")
        print(f"📊 已加载记录: {len(self.viewer.signals)} 条")
        if self.viewer.signals:
            latest = max(self.viewer.signals, key=lambda x: x['datetime'])
            print(f"🕐 最新记录: {latest['datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "-"*50)
        print("📋 功能菜单:")
        print("  1. 查看今日信号")
        print("  2. 查看最新记录") 
        print("  3. 按股票查询")
        print("  4. 统计分析")
        print("  5. 表现分析")
        print("  6. 时间范围查询")
        print("  7. 导出数据")
        print("  8. 刷新日志")
        print("  9. 退出")
        print("-"*50)
    
    def handle_choice(self, choice):
        """处理用户选择"""
        if choice == '1':
            self.view_today()
        elif choice == '2':
            self.view_latest()
        elif choice == '3':
            self.view_by_symbol()
        elif choice == '4':
            self.view_statistics()
        elif choice == '5':
            self.view_performance()
        elif choice == '6':
            self.view_by_date_range()
        elif choice == '7':
            self.export_data()
        elif choice == '8':
            self.refresh_logs()
        elif choice == '9':
            self.running = False
        else:
            print("❌ 无效选择，请输入1-9")
            input("按回车键继续...")
    
    def view_today(self):
        """查看今日信号"""
        self.clear_screen()
        self.viewer.show_today()
        input("\n按回车键返回菜单...")
    
    def view_latest(self):
        """查看最新记录"""
        self.clear_screen()
        try:
            count = input("请输入要查看的记录数量 (默认10): ").strip()
            count = int(count) if count else 10
            self.viewer.show_latest(count)
        except ValueError:
            print("❌ 请输入有效数字")
        input("\n按回车键返回菜单...")
    
    def view_by_symbol(self):
        """按股票查询"""
        self.clear_screen()
        
        # 显示可用的股票
        symbols = set(s['symbol'] for s in self.viewer.signals)
        if symbols:
            print("📊 可用股票代码:")
            sorted_symbols = sorted(symbols)
            for i, symbol in enumerate(sorted_symbols):
                print(f"  {symbol}", end='  ')
                if (i + 1) % 8 == 0:  # 每8个换行
                    print()
            print("\n")
        
        symbol = input("请输入股票代码: ").strip().upper()
        if symbol:
            self.viewer.show_by_symbol(symbol)
        else:
            print("❌ 请输入有效的股票代码")
        input("\n按回车键返回菜单...")
    
    def view_statistics(self):
        """查看统计分析"""
        self.clear_screen()
        try:
            days = input("请输入统计天数 (默认7天): ").strip()
            days = int(days) if days else 7
            self.viewer.show_statistics(days)
        except ValueError:
            print("❌ 请输入有效数字")
        input("\n按回车键返回菜单...")
    
    def view_performance(self):
        """查看表现分析"""
        self.clear_screen()
        self.viewer.show_performance()
        input("\n按回车键返回菜单...")
    
    def view_by_date_range(self):
        """按时间范围查询"""
        self.clear_screen()
        try:
            print("📅 时间范围查询")
            print("格式: YYYY-MM-DD (例如: 2025-08-12)")
            
            start_date = input("开始日期 (留空表示7天前): ").strip()
            end_date = input("结束日期 (留空表示今天): ").strip()
            
            # 解析日期
            if not start_date:
                start_dt = datetime.now() - timedelta(days=7)
            else:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
            if not end_date:
                end_dt = datetime.now()
            else:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            
            # 过滤信号
            filtered_signals = [
                s for s in self.viewer.signals 
                if start_dt <= s['datetime'] <= end_dt
            ]
            
            print(f"\n📊 {start_dt.date()} 到 {end_dt.date()} 的交易信号")
            print("="*60)
            
            if not filtered_signals:
                print("⚪ 指定时间范围内无交易信号")
            else:
                # 按时间排序并显示
                filtered_signals.sort(key=lambda x: x['datetime'], reverse=True)
                for i, signal in enumerate(filtered_signals, 1):
                    self.viewer._print_signal_summary(signal, i)
                
                # 统计信息
                buy_count = len([s for s in filtered_signals if s['position']['action'] == 'BUY'])
                short_count = len([s for s in filtered_signals if s['position']['action'] == 'SHORT'])
                
                print(f"\n📈 期间统计:")
                print(f"   总信号: {len(filtered_signals)}")
                print(f"   买入信号: {buy_count}")
                print(f"   做空信号: {short_count}")
                
        except ValueError:
            print("❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
        except Exception as e:
            print(f"❌ 查询失败: {e}")
        
        input("\n按回车键返回菜单...")
    
    def export_data(self):
        """导出数据"""
        self.clear_screen()
        print("📤 数据导出")
        
        default_name = f"trading_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename = input(f"文件名 (默认: {default_name}): ").strip()
        
        if not filename:
            filename = default_name
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        try:
            self.viewer.export_to_csv(filename)
            print(f"✅ 文件已保存到当前目录: {filename}")
        except Exception as e:
            print(f"❌ 导出失败: {e}")
        
        input("\n按回车键返回菜单...")
    
    def refresh_logs(self):
        """刷新日志"""
        self.clear_screen()
        print("🔄 刷新日志数据...")
        
        old_count = len(self.viewer.signals)
        self.viewer.load_logs()
        new_count = len(self.viewer.signals)
        
        if new_count > old_count:
            print(f"✅ 发现 {new_count - old_count} 条新记录")
        else:
            print("✅ 日志已是最新")
        
        print(f"📊 当前总记录数: {new_count}")
        input("\n按回车键返回菜单...")
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')

def main():
    """主函数"""
    try:
        browser = InteractiveLogBrowser()
        browser.run()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")

if __name__ == "__main__":
    main()