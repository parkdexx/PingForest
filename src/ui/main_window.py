from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeView, QPushButton, QHeaderView, QFrame, QFormLayout, QLineEdit, QSpinBox, QListWidget, QComboBox
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QColor, QBrush
from PySide6.QtCore import Qt, QModelIndex, Signal, Slot, QTimer

from src.core.node_manager import NodeManager
from src.core.monitor_engine import MonitorEngine
from src.core.models import NodeModel, NodeType, NodeStatus
from src.ui.styles import TOSS_STYLE_QSS
from src.ui.components.status_indicator import StatusIndicator

class MainWindow(QMainWindow):
    def __init__(self, node_manager: NodeManager, monitor_engine: MonitorEngine):
        super().__init__()
        self.node_manager = node_manager
        self.monitor_engine = monitor_engine
        
        self.setWindowTitle("PingForest 🌲")
        self.resize(1200, 800)
        self.setStyleSheet(TOSS_STYLE_QSS)
        
        self.init_ui()
        self.populate_tree()
        
        # 주기적으로 트리뷰 리프레시를 위해 Qt 타이머 사용 (간단한 구현)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.populate_tree)
        self.refresh_timer.start(1000)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 1. 좌측: 트리 뷰
        left_layout = QVBoxLayout()
        self.tree_view = QTreeView()
        self.tree_view.setFixedWidth(350)
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.clicked.connect(self.on_tree_clicked)
        
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(["자산명", "상태"])
        self.tree_view.setModel(self.tree_model)
        
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tree_view.header().resizeSection(1, 100)
        
        # 하단 조작 버튼
        btn_layout = QHBoxLayout()
        add_group_btn = QPushButton("그룹 추가")
        add_device_btn = QPushButton("장치 추가")
        btn_layout.addWidget(add_group_btn)
        btn_layout.addWidget(add_device_btn)
        
        add_group_btn.clicked.connect(self.on_add_group)
        add_device_btn.clicked.connect(self.on_add_device)
        
        # 대시보드 버튼 (옵션)
        dashboard_btn = QPushButton("대시보드 보기")
        dashboard_btn.setProperty("class", "secondary")
        dashboard_btn.clicked.connect(self.on_show_dashboard)
        btn_layout.addWidget(dashboard_btn)
        
        left_layout.addWidget(self.tree_view)
        left_layout.addLayout(btn_layout)
        
        main_layout.addLayout(left_layout)
        
        # 2. 우측: 컨텐츠 영역 (상단 상세 패널, 하단 로그 패널)
        right_layout = QVBoxLayout()
        
        # 상단 (상세 정보 폼)
        self.detail_panel = QFrame()
        self.detail_panel.setObjectName("detailPanel")
        detail_layout = QVBoxLayout(self.detail_panel)
        self.detail_title = QLabel("노드 상세 설정")
        self.detail_title.setProperty("class", "PanelTitle")
        detail_layout.addWidget(self.detail_title)
        
        # 폼 레이아웃 (선택된 노드의 정보 표시 및 수정)
        form_layout = QFormLayout()
        self.input_name = QLineEdit()
        self.input_type = QComboBox()
        self.input_type.addItems(["그룹 (Group)", "장치 (Device)"])
        self.input_type.setEnabled(False) # 타입 변경은 구현 복잡도로 인해 막아둠
        self.input_ip = QLineEdit()
        self.input_port = QSpinBox()
        self.input_port.setRange(0, 65535)
        self.input_interval = QSpinBox()
        self.input_interval.setRange(1, 3600)
        self.input_interval.setSuffix(" 초")
        
        self.status_ind_label = QHBoxLayout()
        self.status_ind = StatusIndicator(16)
        self.status_text = QLabel("알 수 없음")
        self.status_ind_label.addWidget(self.status_ind)
        self.status_ind_label.addWidget(self.status_text)
        self.status_ind_label.addStretch()
        
        form_layout.addRow("이름:", self.input_name)
        form_layout.addRow("유형:", self.input_type)
        form_layout.addRow("IP/Host:", self.input_ip)
        form_layout.addRow("Port (옵션):", self.input_port)
        form_layout.addRow("체크 주기:", self.input_interval)
        form_layout.addRow("현재 상태:", self.status_ind_label)
        
        self.save_btn = QPushButton("저장")
        self.save_btn.clicked.connect(self.on_save_clicked)
        self.save_btn.setFixedWidth(100)
        
        detail_layout.addLayout(form_layout)
        detail_layout.addWidget(self.save_btn, alignment=Qt.AlignRight)
        detail_layout.addStretch()
        
        right_layout.addWidget(self.detail_panel, stretch=2)
        
        # 하단 (로그 뷰어)
        self.log_panel = QFrame()
        self.log_panel.setObjectName("logPanel")
        log_layout = QVBoxLayout(self.log_panel)
        self.log_title = QLabel("네트워크 연결 로그")
        self.log_title.setProperty("class", "PanelTitle")
        
        self.log_list = QListWidget()
        log_layout.addWidget(self.log_title)
        log_layout.addWidget(self.log_list, stretch=1)
        
        right_layout.addWidget(self.log_panel, stretch=1)
        
        main_layout.addLayout(right_layout)
        
        self._current_selected_node_id = None

    def populate_tree(self):
        self.tree_model.invisibleRootItem().removeRows(0, self.tree_model.rowCount())
        for node in self.node_manager.root_nodes:
            self._add_node_to_tree(node, self.tree_model.invisibleRootItem())
            
        self.tree_view.expandAll()

    def _add_node_to_tree(self, node: NodeModel, parent_item: QStandardItem):
        # Name Item
        name_item = QStandardItem(node.name)
        name_item.setData(node.id, Qt.UserRole)
        
        # Status Item 
        status_text = "N/A"
        if node.type == NodeType.DEVICE:
            if node.status == NodeStatus.NORMAL:
                status_text = f"{node.last_response_time_ms:.1f}ms"
            elif node.status == NodeStatus.WARNING:
                status_text = "지연"
            elif node.status == NodeStatus.DEAD:
                status_text = "연결 실패"
            elif node.status == NodeStatus.UNKNOWN:
                status_text = "대기중"
                
        status_item = QStandardItem(status_text)
        status_item.setTextAlignment(Qt.AlignCenter)
        
        color_map = {
            NodeStatus.NORMAL: QColor("#00c73c"),
            NodeStatus.WARNING: QColor("#f4ab2e"),
            NodeStatus.DEAD: QColor("#f04452"),
            NodeStatus.UNKNOWN: QColor("#b0b8c1")
        }
        
        if node.type == NodeType.DEVICE:
            status_item.setForeground(QBrush(color_map.get(node.status, QColor("#b0b8c1"))))
            
        parent_item.appendRow([name_item, status_item])
        
        for child in node.children:
            self._add_node_to_tree(child, name_item)

    def on_tree_clicked(self, index: QModelIndex):
        item = self.tree_model.itemFromIndex(index)
        if not item: return
        node_id = item.data(Qt.UserRole)
        # 만약 상태 열(1열)을 클릭한 경우 Name 열(0열)의 데이터를 가져와야 함
        if not node_id:
            sibling = index.siblingAtColumn(0)
            item = self.tree_model.itemFromIndex(sibling)
            node_id = item.data(Qt.UserRole) if item else None
            
        if node_id:
            self._current_selected_node_id = node_id
            self._load_node_details(node_id)

    def _load_node_details(self, node_id: str):
        node = self.node_manager.get_node(node_id)
        if not node: return
        
        self.input_name.setText(node.name)
        self.input_type.setCurrentIndex(0 if node.type == NodeType.GROUP else 1)
        self.input_ip.setText(node.ip_address)
        self.input_port.setValue(node.port if node.port else 0)
        self.input_interval.setValue(node.check_interval_seconds)
        self.status_ind.set_status(node.status)
        
        # 상태 텍스트 
        if node.type == NodeType.GROUP:
            self.status_text.setText("그룹입니다.")
            self.input_ip.setEnabled(False)
            self.input_port.setEnabled(False)
            self.input_interval.setEnabled(False)
        else:
            self.input_ip.setEnabled(True)
            self.input_port.setEnabled(True)
            self.input_interval.setEnabled(True)
            if node.status == NodeStatus.NORMAL:
                self.status_text.setText(f"정상 ({node.last_response_time_ms:.1f}ms) - Last Check: {node.last_check_time}")
            elif node.status == NodeStatus.WARNING:
                self.status_text.setText(f"지연 ({node.last_response_time_ms:.1f}ms) - Last Check: {node.last_check_time}")
            elif node.status == NodeStatus.DEAD:
                self.status_text.setText(f"연결 실패 - Last Check: {node.last_check_time}")
            else:
                self.status_text.setText("검사 대기중")
        
        # 로그 패널 갱신 시뮬레이션 (임시)
        self.log_list.clear()
        self.log_list.addItem(f"[{node.last_check_time}] {node.name} 모니터링 중... (상태: {node.status.name})")

    def on_save_clicked(self):
        if not self._current_selected_node_id: return
        node = self.node_manager.get_node(self._current_selected_node_id)
        if not node: return
        
        node.name = self.input_name.text()
        node.ip_address = self.input_ip.text()
        node.port = self.input_port.value() if self.input_port.value() > 0 else None
        node.check_interval_seconds = self.input_interval.value()
        
        # 그룹이면 상태 변경 무의미
        if node.type == NodeType.DEVICE:
            self.monitor_engine.update_node_worker(node)
            
        self.node_manager.save_data()
        self.populate_tree()
        self.log_list.insertItem(0, "설정이 저장되었습니다.")

    def on_add_group(self):
        parent_id = self._current_selected_node_id
        parent = self.node_manager.get_node(parent_id) if parent_id else None
        
        new_node = NodeModel("새 그룹", NodeType.GROUP)
        # 만약 선택된 노드가 디바이스면 추가 불가하거나, 디바이스의 부모를 선택
        if parent and parent.type == NodeType.DEVICE:
            parent_id = parent.parent_id
            
        self.node_manager.add_node(new_node, parent_id)
        self.populate_tree()
        
    def on_add_device(self):
        parent_id = self._current_selected_node_id
        parent = self.node_manager.get_node(parent_id) if parent_id else None
        
        new_node = NodeModel("새 장치", NodeType.DEVICE)
        if parent and parent.type == NodeType.DEVICE:
            parent_id = parent.parent_id
            
        self.node_manager.add_node(new_node, parent_id)
        self.monitor_engine.update_node_worker(new_node)
        self.populate_tree()

    def on_show_dashboard(self):
        from src.ui.dashboard_window import DashboardWindow
        if not hasattr(self, 'dashboard_window') or not self.dashboard_window.isVisible():
            self.dashboard_window = DashboardWindow(self.node_manager)
            self.dashboard_window.show()
