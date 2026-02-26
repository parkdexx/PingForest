import logging
import os
from datetime import datetime

class AppLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.logger = logging.getLogger("PingForest")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers if instantiated multiple times
        if not self.logger.handlers:
            # 일자별 파일 로그
            # Note: Requirements requested yyyy-MM-dd.txt format
            current_date = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"{current_date}.txt")
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 콘솔 로그
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            
            # 포맷
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str):
        self.logger.error(message)
        
    def log_connection_status(self, node_name: str, status: str, response_time: float):
        self.logger.info(f"Connection Status | {node_name} | {status} | {response_time}ms")

# Singleton-like instance for quick use
global_logger = AppLogger()
