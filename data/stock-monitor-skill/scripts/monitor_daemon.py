#!/usr/bin/env python3
"""
Stock Monitor Daemon - 后台常驻进程
自动运行监控，智能控制频率，支持 graceful shutdown
"""

import sys
import time
import signal
import logging
from datetime import datetime
from pathlib import Path

# 设置日志
log_dir = Path.home() / ".stock_monitor"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 导入监控类
sys.path.insert(0, str(Path(__file__).parent))
from monitor import StockAlert, WATCHLIST

class MonitorDaemon:
    def __init__(self):
        self.monitor = StockAlert()
        self.running = True
        self.last_run_time = 0
        
        # 设置信号处理
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """优雅退出"""
        logger.info(f"收到信号 {signum}，正在关闭...")
        self.running = False
    
    def get_sleep_interval(self):
        """根据当前时间获取睡眠间隔"""
        schedule = self.monitor.should_run_now()
        if not schedule.get("run"):
            # 如果当前不需要运行，计算到下次运行的时间
            now = datetime.now()
            hour = now.hour
            
            # 凌晨时段，1小时后检查
            if 0 <= hour < 9:
                return 3600
            return 300  # 默认5分钟
        
        return schedule.get("interval", 300)
    
    def run(self):
        """主循环"""
        logger.info("=" * 60)
        logger.info("🚀 Stock Monitor Daemon 启动")
        logger.info(f"📋 监控标的: {len(WATCHLIST)} 只")
        logger.info("=" * 60)
        
        while self.running:
            try:
                # 检查是否应该执行
                schedule = self.monitor.should_run_now()
                
                if schedule.get("run"):
                    mode = schedule.get("mode", "normal")
                    stocks_count = len(schedule.get("stocks", []))
                    logger.info(f"[{mode}] 扫描 {stocks_count} 只标的...")
                    
                    # 执行监控
                    alerts = self.monitor.run_once(smart_mode=False)  # 已经判断过了
                    
                    if alerts:
                        logger.info(f"⚠️ 触发 {len(alerts)} 条预警")
                        # 这里会通过 message 工具发送通知
                    else:
                        logger.debug("✅ 无预警")
                    
                    self.last_run_time = time.time()
                
                # 计算睡眠间隔
                sleep_interval = self.get_sleep_interval()
                logger.debug(f"下次检查: {sleep_interval} 秒后")
                
                # 分段睡眠，方便及时响应退出信号
                slept = 0
                while slept < sleep_interval and self.running:
                    time.sleep(1)
                    slept += 1
                    
            except Exception as e:
                logger.error(f"运行出错: {e}", exc_info=True)
                time.sleep(60)  # 出错后等待1分钟重试
        
        logger.info("👋 Daemon 已停止")

if __name__ == '__main__':
    daemon = MonitorDaemon()
    daemon.run()
