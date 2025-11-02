# launch_intraday.py - 启动日内交易看板
import subprocess
import sys
import os

def launch_dashboard():
    """启动Streamlit日内交易看板"""
    print("🚀 启动华尔街母鸡日内交易看板...")
    print("📊 功能特色:")
    print("   - 实时K线图和技术指标")
    print("   - 成交量异动监控")
    print("   - VWAP偏离分析") 
    print("   - RSI超买超卖提醒")
    print("   - 日内交易策略建议")
    print("   - 自动刷新监控")
    print()
    
    try:
        # 检查是否安装了streamlit
        subprocess.run([sys.executable, "-c", "import streamlit"], check=True, capture_output=True)
        
        # 启动streamlit应用
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "intraday_dashboard.py",
            "--server.port", "8502",
            "--server.headless", "true",
            "--server.fileWatcherType", "none"
        ]
        
        print("🌐 启动地址: http://localhost:8502")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except subprocess.CalledProcessError:
        print("❌ 未安装streamlit，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "plotly"])
        print("✅ 安装完成，重新启动...")
        launch_dashboard()
    
    except KeyboardInterrupt:
        print("\n👋 华尔街母鸡日内看板已停止")
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    launch_dashboard()