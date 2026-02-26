import subprocess
import platform
import re
from typing import Tuple

class PingService:
    @staticmethod
    def check_ping(ip_address: str, timeout_ms: int = 1000) -> Tuple[bool, float]:
        """
        Pings an IP address and returns (success: bool, response_time_ms: float)
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
        
        # Windows timeout is in milliseconds, Linux/Mac is in seconds
        timeout_val = str(timeout_ms) if platform.system().lower() == 'windows' else str(max(1, timeout_ms // 1000))
        
        command = ['ping', param, '1', timeout_param, timeout_val, ip_address]
        
        try:
            # shell=True is generally discouraged, but sometimes needed on Windows for ping to hide console
            startupinfo = None
            if platform.system().lower() == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo
            )
            
            if process.returncode == 0:
                # 파싱 로직 (Windows 기준 '시간=XXms' 또는 'time=XXms')
                match = re.search(r'(시간|time)[=<](\d+)ms', process.stdout, re.IGNORECASE)
                time_ms = float(match.group(2)) if match else 1.0 # 응답시간이 <1ms 인 경우 대비
                return True, time_ms
            else:
                return False, 0.0
                
        except Exception as e:
            print(f"Ping failed for {ip_address}: {e}")
            return False, 0.0
