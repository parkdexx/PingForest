from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QScrollArea, QFrame
from PySide6.QtCore import Qt, QTimer
from src.core.node_manager import NodeManager
from src.core.models import NodeStatus, NodeType
from src.ui.styles import TOSS_STYLE_QSS
from src.ui.components.status_indicator import StatusIndicator

class DashboardCard(QFrame):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setObjectName("DashboardCard")
        self.setStyleSheet("""
            #DashboardCard {
                background-color: white;
                border: 1px solid #e5e8eb;
                border-radius: 16px;
                padding: 20px;
            }
            #DashboardCard:hover {
                border: 1px solid #3182f6;
                background-color: #f9fafb;
            }
            .CardTitle {
                font-size: 16px;
                font-weight: bold;
                color: #191f28;
            }
            .CardSub {
                font-size: 13px;
                color: #8b95a1;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # 상단 (이름 및 상태 등)
        top_layout = QHBoxLayout()
        self.title_label = QLabel(node.name)
        self.title_label.setProperty("class", "CardTitle")
        self.status_ind = StatusIndicator(20)
        
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.status_ind)
        
        layout.addLayout(top_layout)
        
        # 하단 (IP, 상태 텍스트)
        self.ip_label = QLabel(node.ip_address if node.ip_address else "N/A")
        self.ip_label.setProperty("class", "CardSub")
        
        self.status_detail = QLabel("대기중")
        self.status_detail.setProperty("class", "CardSub")
        
        layout.addStretch()
        layout.addWidget(self.ip_label)
        layout.addWidget(self.status_detail)
        
        self.update_ui()
        
    def update_ui(self):
        self.title_label.setText(self.node.name)
        self.ip_label.setText(self.node.ip_address if self.node.ip_address else "N/A")
        self.status_ind.set_status(self.node.status)
        
        if self.node.status == NodeStatus.NORMAL:
            self.status_detail.setText(f"정상 ({self.node.last_response_time_ms:.1f}ms)")
            self.status_detail.setStyleSheet("color: #00c73c; font-weight: bold;")
        elif self.node.status == NodeStatus.WARNING:
            self.status_detail.setText(f"지연 ({self.node.last_response_time_ms:.1f}ms)")
            self.status_detail.setStyleSheet("color: #f4ab2e; font-weight: bold;")
        elif self.node.status == NodeStatus.DEAD:
            self.status_detail.setText("연결 실패")
            self.status_detail.setStyleSheet("color: #f04452; font-weight: bold;")
        else:
            self.status_detail.setText("대기중")
            self.status_detail.setStyleSheet("color: #8b95a1;")

class DashboardWindow(QWidget):
    def __init__(self, node_manager: NodeManager):
        super().__init__()
        self.node_manager = node_manager
        self.setWindowTitle("PingForest - Dashboard")
        self.resize(1000, 700)
        self.setStyleSheet(TOSS_STYLE_QSS)
        
        self.cards = []
        
        self.init_ui()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_cards)
        self.refresh_timer.start(1500)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("모니터링 대시보드")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #191f28;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        fullscreen_btn = QPushButton("전체화면 전환")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        header_layout.addWidget(fullscreen_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll Area for Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(20)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        self.populate_grid()
        
    def populate_grid(self):
        # Clear existing
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        self.cards.clear()
            
        devices = self.node_manager.get_all_devices()
        
        # 3 columns layout
        cols = 3
        for idx, device in enumerate(devices):
            row = idx // cols
            col = idx % cols
            card = DashboardCard(device)
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)

    def refresh_cards(self):
        # In a real scenario, we might just update the existing cards instead of repopulating.
        # But for simplicity, if length changes, repopulate. Otherwise, update.
        devices = self.node_manager.get_all_devices()
        if len(devices) != len(self.cards):
            self.populate_grid()
        else:
            for card in self.cards:
                card.update_ui()
                
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
