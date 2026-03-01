import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal, QObject
from .models import NodeModel, NodeStatus, NodeType
from src.services.ping_service import PingService
from src.services.port_service import PortService

class MonitorWorker(QThread):
    # node_id, ping_status, ping_response_time, port_status, port_response_time, checked_at
    result_ready = Signal(str, object, float, object, float, str)
    
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
                    
                checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Check Ping
                ping_success, ping_time = PingService.check_ping(self.node.ip_address)
                ping_status = NodeStatus.NORMAL if ping_success else NodeStatus.DEAD
                
                # Check Port
                port_status = NodeStatus.UNKNOWN
                port_time = 0.0
                if self.node.port and self.node.port > 0:
                    port_success, port_time = PortService.check_port(self.node.ip_address, self.node.port)
                    port_status = NodeStatus.NORMAL if port_success else NodeStatus.DEAD
                
                # Signal the UI
                self.result_ready.emit(self.node.id, ping_status, ping_time, port_status, port_time, checked_at)
                
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

class MonitorEngine(QObject):
    log_updated = Signal(str)

    def __init__(self, node_manager):
        super().__init__()
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

    def _handle_result(self, node_id: str, ping_status: NodeStatus, ping_time: float, port_status: NodeStatus, port_time: float, checked_at: str):
        node = self.node_manager.get_node(node_id)
        if node:
            node.ping_status = ping_status
            node.port_status = port_status
            node.ping_response_time_ms = ping_time
            node.port_response_time_ms = port_time
            node.last_check_time = checked_at
            
            from src.core.logger import global_logger
            log_msg = f"Ping: {ping_status.name} ({ping_time:.1f}ms)"
            if node.port and node.port > 0:
                log_msg += f", Port({node.port}): {port_status.name} ({port_time:.1f}ms)"
            global_logger.log_connection_status(node.name, log_msg)
            
            # Emit to UI
            self.log_updated.emit(f"[{checked_at}] {node.name} | {log_msg}")

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
