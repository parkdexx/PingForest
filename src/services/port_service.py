import socket
from typing import Tuple
import time

class PortService:
    @staticmethod
    def check_port(ip_address: str, port: int, timeout_sec: float = 2.0) -> Tuple[bool, float]:
        """
        Checks if a TCP port is open and returns (success: bool, response_time_ms: float)
        """
        start_time = time.time()
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout_sec)
                result = s.connect_ex((ip_address, port))
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000.0
                
                if result == 0:
                    return True, response_time_ms
                else:
                    return False, 0.0
        except Exception as e:
            print(f"Port check failed for {ip_address}:{port} - {e}")
            return False, 0.0
