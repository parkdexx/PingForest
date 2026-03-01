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
        
        self.current_log_date = None
        self._check_rollover()

    def _check_rollover(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != getattr(self, "current_log_date", None):
            self.current_log_date = current_date
            
            for h in list(self.logger.handlers):
                if isinstance(h, logging.FileHandler):
                    self.logger.removeHandler(h)
                    
            log_file = os.path.join(self.log_dir, f"{current_date}.txt")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            has_console = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in self.logger.handlers)
            if not has_console:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

    def log_info(self, message: str):
        self._check_rollover()
        self.logger.info(message)

    def log_error(self, message: str):
        self._check_rollover()
        self.logger.error(message)
        
    def log_connection_status(self, node_name: str, details: str):
        self._check_rollover()
        self.logger.info(f"Connection Status | {node_name} | {details}")

# Singleton-like instance for quick use
global_logger = AppLogger()
