from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QScrollArea, QFrame
from PySide6.QtCore import Qt, QTimer
from datetime import datetime
from src.core.node_manager import NodeManager
from src.core.models import NodeStatus, NodeType
from src.ui.styles import TOSS_STYLE_QSS
import qtawesome as qta

class DashboardCard(QFrame):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setObjectName("DashboardCard")
        # Removing WA_TranslucentBackground as it can conflict with QSS border updates on Windows
        self._last_dashboard_color = getattr(self.node, 'dashboard_color', '#ffffff')
        self._current_dashboard_icon = getattr(self.node, 'dashboard_icon', 'fa5s.desktop')
        self.setStyleSheet(f"""
            #DashboardCard {{
                background-color: white;
                border: 1px solid #e5e8eb;
                border-top: 4px solid {node.dashboard_color};
                border-radius: 16px;
                padding: 20px;
            }}
            #DashboardCard:hover {{
                border: 1px solid #3182f6;
                border-top: 4px solid #3182f6;
                background-color: #f9fafb;
            }}
            .CardTitle {{
                font-size: 16px;
                font-weight: bold;
                color: #191f28;
            }}
            .CardSub {{
                font-size: 13px;
                color: #8b95a1;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # 상단 (이름 및 상태 등)
        top_layout = QHBoxLayout()
        self.icon_label = QLabel()
        try:
            ic_name = getattr(self.node, 'dashboard_icon', 'fa5s.desktop')
            ic_color = getattr(self.node, 'dashboard_color', '#333d4b')
            if ic_color == '#ffffff': ic_color = '#333d4b' # 흰색 배경에 흰색 아이콘 방지
            self.icon_label.setPixmap(qta.icon(ic_name, color=ic_color).pixmap(24, 24))
        except Exception:
            self.icon_label.setPixmap(qta.icon("fa5s.desktop", color="#333d4b").pixmap(24, 24))
            
        self.title_label = QLabel(node.name)
        self.title_label.setProperty("class", "CardTitle")
        
        top_layout.addWidget(self.icon_label)
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # 하단 (IP, 상태 텍스트)
        self.ip_label = QLabel(node.ip_address if node.ip_address else "N/A")
        self.ip_label.setProperty("class", "CardSub")
        
        self.status_detail = QLabel("Ping: 대기중")
        self.status_detail.setProperty("class", "CardSub")
        
        self.port_status_detail = QLabel("Port: 미사용")
        self.port_status_detail.setProperty("class", "CardSub")
        
        layout.addStretch()
        layout.addWidget(self.ip_label)
        layout.addWidget(self.status_detail)
        layout.addWidget(self.port_status_detail)
        
        self.update_ui()
        
    def update_ui(self):
        new_color = getattr(self.node, 'dashboard_color', '#ffffff')
        new_icon = getattr(self.node, 'dashboard_icon', 'fa5s.desktop')
        
        # Only update the stylesheet if the color has changed to prevent UI glitches and save CPU
        if self._last_dashboard_color != new_color:
            self._last_dashboard_color = new_color
            self.setStyleSheet(f"""
                #DashboardCard {{
                    background-color: white;
                    border: 1px solid #e5e8eb;
                    border-top: 4px solid {new_color};
                    border-radius: 16px;
                    padding: 20px;
                }}
                #DashboardCard:hover {{
                    border: 1px solid #3182f6;
                    border-top: 4px solid #3182f6;
                    background-color: #f9fafb;
                }}
                .CardTitle {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #191f28;
                }}
                .CardSub {{
                    font-size: 13px;
                    color: #8b95a1;
                }}
            """)
            self.style().unpolish(self)
            self.style().polish(self)
        
        # Update icon if changed
        try:
            ic_color = new_color
            if ic_color == '#ffffff': ic_color = '#333d4b' # 흰색 배경 방지
            self.icon_label.setPixmap(qta.icon(new_icon, color=ic_color).pixmap(24, 24))
        except Exception:
            self.icon_label.setPixmap(qta.icon("fa5s.desktop", color="#333d4b").pixmap(24, 24))
            
        self.title_label.setText(self.node.name)
        self.ip_label.setText(self.node.ip_address if self.node.ip_address else "N/A")
        
        if self.node.ping_status == NodeStatus.NORMAL:
            self.status_detail.setText(f"Ping: 정상 ({self.node.ping_response_time_ms:.1f}ms)")
            self.status_detail.setStyleSheet("color: #00c73c; font-weight: bold;")
        elif self.node.ping_status == NodeStatus.WARNING:
            self.status_detail.setText(f"Ping: 지연 ({self.node.ping_response_time_ms:.1f}ms)")
            self.status_detail.setStyleSheet("color: #f4ab2e; font-weight: bold;")
        elif self.node.ping_status == NodeStatus.DEAD:
            self.status_detail.setText("Ping: 연결 실패")
            self.status_detail.setStyleSheet("color: #f04452; font-weight: bold;")
        else:
            self.status_detail.setText("Ping: 대기중")
            self.status_detail.setStyleSheet("color: #8b95a1;")

        if hasattr(self.node, 'port') and self.node.port and self.node.port > 0:
            if self.node.port_status == NodeStatus.NORMAL:
                self.port_status_detail.setText(f"Port: 정상 ({self.node.port_response_time_ms:.1f}ms)")
                self.port_status_detail.setStyleSheet("color: #00c73c; font-weight: bold;")
            elif self.node.port_status == NodeStatus.WARNING:
                self.port_status_detail.setText(f"Port: 지연 ({self.node.port_response_time_ms:.1f}ms)")
                self.port_status_detail.setStyleSheet("color: #f4ab2e; font-weight: bold;")
            elif self.node.port_status == NodeStatus.DEAD:
                self.port_status_detail.setText("Port: 연결 실패")
                self.port_status_detail.setStyleSheet("color: #f04452; font-weight: bold;")
            else:
                self.port_status_detail.setText("Port: 대기중")
                self.port_status_detail.setStyleSheet("color: #8b95a1;")
        else:
            self.port_status_detail.setText("Port: 미사용")
            self.port_status_detail.setStyleSheet("color: #8b95a1;")

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
        self.header_title = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.header_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #191f28;")
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        
        self.fullscreen_btn = QPushButton("전체화면 전환")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        header_layout.addWidget(self.fullscreen_btn)
        
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
            
        devices = [d for d in self.node_manager.get_all_devices() if getattr(d, 'send_to_dashboard', True)]
        
        # 3 columns layout
        cols = 3
        for idx, device in enumerate(devices):
            row = idx // cols
            col = idx % cols
            card = DashboardCard(device)
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)

    def refresh_cards(self):
        self.header_title.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        devices = [d for d in self.node_manager.get_all_devices() if getattr(d, 'send_to_dashboard', True)]
        # 카드의 개수나 노드 순서가 바뀌었으면 다시 렌더링
        if len(devices) != len(self.cards):
            self.populate_grid()
        else:
            for i, card in enumerate(self.cards):
                if card.node.id != devices[i].id:
                    self.populate_grid()
                    return
                card.update_ui()
                
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("전체화면 전환")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("창모드 전환")
