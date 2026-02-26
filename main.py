import sys
import os

# src 모듈 경로가 인식되도록 sys.path 에 최상위 디렉토리 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.core.node_manager import NodeManager
from src.core.monitor_engine import MonitorEngine

def main():
    app = QApplication(sys.argv)
    
    node_manager = NodeManager()
    
    # 더미 데이터 (임시)
    if not node_manager.root_nodes:
        from src.core.models import NodeModel, NodeType
        g1 = NodeModel("Database Servers", NodeType.GROUP)
        d1 = NodeModel("DB-01 (로컬)", NodeType.DEVICE)
        d1.ip_address = "127.0.0.1"
        d1.check_interval_seconds = 2
        d2 = NodeModel("DB-02 (가짜IP)", NodeType.DEVICE)
        d2.ip_address = "192.168.99.99"
        d2.check_interval_seconds = 2
        node_manager.add_node(g1)
        node_manager.add_node(d1, g1.id)
        node_manager.add_node(d2, g1.id)
        
    monitor_engine = MonitorEngine(node_manager)
    monitor_engine.start_monitoring()
    
    window = MainWindow(node_manager, monitor_engine)
    window.show()
    
    ret = app.exec()
    monitor_engine.stop_monitoring()
    sys.exit(ret)

if __name__ == "__main__":
    main()
