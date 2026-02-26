import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from .models import NodeModel, NodeStatus, NodeType
from src.services.ping_service import PingService
from src.services.port_service import PortService

class MonitorWorker(QThread):
    # node_id, status, response_time, checked_at
    result_ready = Signal(str, object, float, str)
    
    def __init__(self, node: NodeModel):
        super().__init__()
        self.node = node
        self.is_running = True
        
    def run(self):
        while self.is_running:
            try:
                if self.node.type != NodeType.DEVICE or not self.node.ip_address:
                    time.sleep(1)
                    continue
                    
                success, response_time = False, 0.0
                checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Check based on port definition
                if self.node.port and self.node.port > 0:
                    success, response_time = PortService.check_port(self.node.ip_address, self.node.port)
                else:
                    success, response_time = PingService.check_ping(self.node.ip_address)
                
                status = NodeStatus.NORMAL if success else NodeStatus.DEAD
                
                # Signal the UI
                self.result_ready.emit(self.node.id, status, response_time, checked_at)
                
            except Exception as e:
                print(f"Error checking node {self.node.name}: {e}")
                
            # Sleep until next check
            # For simplicity, sleep in chunks to allow thread to be stopped gracefully
            sleep_time = self.node.check_interval_seconds
            for _ in range(int(sleep_time)):
                if not self.is_running:
                    break
                time.sleep(1)

    def stop(self):
        self.is_running = False

class MonitorEngine:
    def __init__(self, node_manager):
        self.node_manager = node_manager
        self.workers = {}  # node_id -> MonitorWorker

    def start_monitoring(self):
        devices = self.node_manager.get_all_devices()
        for device in devices:
            self._start_worker(device)

    def _start_worker(self, node: NodeModel):
        if node.id in self.workers:
            self.workers[node.id].stop()
            self.workers[node.id].wait()
            
        worker = MonitorWorker(node)
        worker.result_ready.connect(self._handle_result)
        self.workers[node.id] = worker
        worker.start()

    def _handle_result(self, node_id: str, status: NodeStatus, response_time: float, checked_at: str):
        node = self.node_manager.get_node(node_id)
        if node:
            node.status = status
            node.last_response_time_ms = response_time
            node.last_check_time = checked_at
            
            # TODO: Here we would trigger UI updates and check for Email Alerts / Logging

    def stop_monitoring(self):
        for worker in self.workers.values():
            worker.stop()
        for worker in self.workers.values():
            worker.wait()
        self.workers.clear()

    def update_node_worker(self, node: NodeModel):
        """Called when a node's configuration changes"""
        # Restart the worker to pick up new intervals, IPs, ports, etc.
        self._start_worker(node)
