from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeView, QPushButton, QHeaderView, QFrame, QFormLayout, QLineEdit, QSpinBox, QListWidget, QComboBox, QMenu, QMessageBox, QSplitter, QFileDialog
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QColor, QBrush, QAction
from PySide6.QtCore import Qt, QModelIndex, Signal, Slot, QTimer, QSettings

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
        
        self.settings = QSettings("PingForestApp", "PingForest")
        
        self.init_ui()
        self.populate_tree()
        self.monitor_engine.log_updated.connect(self.on_log_updated)
        
        # 주기적으로 트리뷰 리프레시를 위해 Qt 타이머 사용 (간단한 구현)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.populate_tree)
        self.refresh_timer.start(1000)

    def on_log_updated(self, msg: str):
        self.log_list.insertItem(0, msg)
        # Limit to 100 entries to prevent memory leak
        if self.log_list.count() > 100:
            self.log_list.takeItem(100)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 1. 좌측: 트리 뷰
        
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.clicked.connect(self.on_tree_clicked)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_tree_context_menu)
        
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(["노드명", "IP상태", "Port상태"])
        self.tree_view.setModel(self.tree_model)
        
        # 헤더 텍스트 중앙 정렬
        self.tree_view.header().setDefaultAlignment(Qt.AlignCenter)
        
        # 사용자가 너비 조절 가능하게 변경 (Interactive)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.Interactive)
        
        # 기본 너비 세팅
        self.tree_view.header().resizeSection(0, 180)
        self.tree_view.header().resizeSection(1, 80)
        self.tree_view.header().resizeSection(2, 80)
        
        # 하단 조작 버튼
        btn_layout = QHBoxLayout()
        import_btn = QPushButton("트리 가져오기 (Import)")
        export_btn = QPushButton("트리 내보내기 (Export)")
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(export_btn)
        
        import_btn.clicked.connect(self.on_import_tree)
        export_btn.clicked.connect(self.on_export_tree)
        
        # 대시보드 버튼 (옵션)
        dashboard_btn = QPushButton("대시보드 보기")
        dashboard_btn.setProperty("class", "secondary")
        dashboard_btn.clicked.connect(self.on_show_dashboard)
        btn_layout.addWidget(dashboard_btn)
        
        left_layout.addWidget(self.tree_view)
        left_layout.addLayout(btn_layout)
        
        self.main_splitter.addWidget(left_widget)
        
        # 2. 우측: 컨텐츠 영역 (상단 상세 패널, 하단 로그 패널)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
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
        self.input_ip = QLineEdit()
        self.input_port = QSpinBox()
        self.input_port.setRange(0, 65535)
        self.input_interval = QSpinBox()
        self.input_interval.setRange(1, 3600)
        self.input_interval.setSuffix(" 초")
        
        self.status_layout = QVBoxLayout()
        
        self.ping_status_layout = QHBoxLayout()
        self.ping_status_ind = StatusIndicator(16)
        self.ping_status_text = QLabel("Ping: 알 수 없음")
        self.ping_status_layout.addWidget(self.ping_status_ind)
        self.ping_status_layout.addWidget(self.ping_status_text)
        self.ping_status_layout.addStretch()
        
        self.port_status_layout = QHBoxLayout()
        self.port_status_ind = StatusIndicator(16)
        self.port_status_text = QLabel("Port: 알 수 없음")
        self.port_status_layout.addWidget(self.port_status_ind)
        self.port_status_layout.addWidget(self.port_status_text)
        self.port_status_layout.addStretch()
        
        self.status_layout.addLayout(self.ping_status_layout)
        self.status_layout.addLayout(self.port_status_layout)
        
        form_layout.addRow("이름:", self.input_name)
        form_layout.addRow("IP/Host:", self.input_ip)
        form_layout.addRow("Port (옵션):", self.input_port)
        form_layout.addRow("체크 주기:", self.input_interval)
        form_layout.addRow("현재 상태:", self.status_layout)
        
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
        
        self.main_splitter.addWidget(right_widget)
        
        # Splitter 초기 비율 설정 (트리뷰: 350px, 우측 패널 나머지)
        self.main_splitter.setSizes([350, 850])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        
        self._current_selected_node_id = None
        
        # Load Settings (Window Geometry & Splitter State)
        self._load_settings()

    def _load_settings(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        splitter_state = self.settings.value("main_splitter")
        if splitter_state:
            self.main_splitter.restoreState(splitter_state)
            
        tree_header_state = self.settings.value("tree_header")
        if tree_header_state:
            self.tree_view.header().restoreState(tree_header_state)

    def closeEvent(self, event):
        # Save Settings
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("main_splitter", self.main_splitter.saveState())
        self.settings.setValue("tree_header", self.tree_view.header().saveState())
        super().closeEvent(event)

    def populate_tree(self):
        # Save exact selection context before clearing
        selected_indexes = self.tree_view.selectedIndexes()
        
        self.tree_model.invisibleRootItem().removeRows(0, self.tree_model.rowCount())
        for node in self.node_manager.root_nodes:
            self._add_node_to_tree(node, self.tree_model.invisibleRootItem())
            
        self.tree_view.expandAll()
        
        # Restore Tree Selection 
        if self._current_selected_node_id:
            self._restore_selection()
            
    def _restore_selection(self):
        match_list = self.tree_model.match(
            self.tree_model.index(0, 0),
            Qt.UserRole,
            self._current_selected_node_id,
            1,
            Qt.MatchExactly | Qt.MatchRecursive
        )
        if match_list:
            self.tree_view.setCurrentIndex(match_list[0])

    def _add_node_to_tree(self, node: NodeModel, parent_item: QStandardItem):
        # Name Item
        name_item = QStandardItem(node.name)
        name_item.setData(node.id, Qt.UserRole)
        
        # Status Items 
        ping_status_text = "N/A"
        port_status_text = "N/A"
        overall_ping_status = NodeStatus.UNKNOWN
        overall_port_status = NodeStatus.UNKNOWN
        
        emoji_map = {
            NodeStatus.NORMAL: "🟢",
            NodeStatus.WARNING: "🟡",
            NodeStatus.DEAD: "🔴",
            NodeStatus.UNKNOWN: "⚪"
        }
        
        if node.type == NodeType.DEVICE:
            ping_emoji = emoji_map.get(node.ping_status, "⚪")
            port_emoji = emoji_map.get(node.port_status, "⚪") if node.port and node.port > 0 else "➖"
            
            # IP가 없으면 단순 폴더 역할이므로 상태 표시 X
            if not node.ip_address:
                ping_emoji = "📁"
                port_emoji = "📁"
            
            overall_ping_status = node.ping_status
            overall_port_status = node.port_status
            
            ping_status_text = ping_emoji
            port_status_text = port_emoji
                
        ping_item = QStandardItem(ping_status_text)
        ping_item.setTextAlignment(Qt.AlignCenter)
        
        port_item = QStandardItem(port_status_text)
        port_item.setTextAlignment(Qt.AlignCenter)
        
        color_map = {
            NodeStatus.NORMAL: QColor("#00c73c"),
            NodeStatus.WARNING: QColor("#f4ab2e"),
            NodeStatus.DEAD: QColor("#f04452"),
            NodeStatus.UNKNOWN: QColor("#b0b8c1")
        }
        
        if node.type == NodeType.DEVICE:
            ping_item.setForeground(QBrush(color_map.get(overall_ping_status, QColor("#b0b8c1"))))
            if node.port and node.port > 0:
                port_item.setForeground(QBrush(color_map.get(overall_port_status, QColor("#b0b8c1"))))
            else:
                port_item.setForeground(QBrush(QColor("#b0b8c1")))
            
        parent_item.appendRow([name_item, ping_item, port_item])
        
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
        self.input_ip.setText(node.ip_address)
        self.input_port.setValue(node.port if node.port else 0)
        self.input_interval.setValue(node.check_interval_seconds)
        
        # 상태 텍스트 
        if not node.ip_address:
            self.ping_status_text.setText("폴더(검사 안함)")
            self.port_status_text.setText("")
            self.ping_status_ind.set_status(NodeStatus.UNKNOWN)
            self.port_status_ind.set_status(NodeStatus.UNKNOWN)
        else:
            self.ping_status_ind.set_status(node.ping_status)
            if node.ping_status == NodeStatus.NORMAL:
                self.ping_status_text.setText(f"Ping: 정상 ({node.ping_response_time_ms:.1f}ms)")
            elif node.ping_status == NodeStatus.WARNING:
                self.ping_status_text.setText(f"Ping: 지연 ({node.ping_response_time_ms:.1f}ms)")
            elif node.ping_status == NodeStatus.DEAD:
                self.ping_status_text.setText(f"Ping: 연결 실패")
            else:
                self.ping_status_text.setText("Ping: 검사 대기중")
                
            if node.port and node.port > 0:
                self.port_status_ind.set_status(node.port_status)
                if node.port_status == NodeStatus.NORMAL:
                    self.port_status_text.setText(f"Port: 정상 ({node.port_response_time_ms:.1f}ms)")
                elif node.port_status == NodeStatus.WARNING:
                    self.port_status_text.setText(f"Port: 지연 ({node.port_response_time_ms:.1f}ms)")
                elif node.port_status == NodeStatus.DEAD:
                    self.port_status_text.setText(f"Port: 연결 실패")
                else:
                    self.port_status_text.setText("Port: 대기중")
            else:
                self.port_status_ind.set_status(NodeStatus.UNKNOWN)
                self.port_status_text.setText("Port: 미사용")
        
        # 로그 패널 갱신 시뮬레이션 (임시)
        self.log_list.clear()
        self.log_list.addItem(f"[{node.last_check_time}] {node.name} 모니터링 상세 정보 갱신.")

    def on_save_clicked(self):
        if not self._current_selected_node_id: return
        node = self.node_manager.get_node(self._current_selected_node_id)
        if not node: return
        
        node.name = self.input_name.text()
        node.ip_address = self.input_ip.text()
        node.port = self.input_port.value() if self.input_port.value() > 0 else None
        node.check_interval_seconds = self.input_interval.value()
        
        self.monitor_engine.update_node_worker(node)
            
        self.node_manager.save_data()
        self.populate_tree()
        self.log_list.insertItem(0, "설정이 저장되었습니다.")

    def on_add_device(self, force_parent_id=None):
        parent_id = force_parent_id if force_parent_id is not None else self._current_selected_node_id
        if parent_id == "": # 최상위 추가 강제
            parent_id = None
        
        parent = self.node_manager.get_node(parent_id) if parent_id else None
        
        new_node = NodeModel("새 장치", NodeType.DEVICE)
            
        self.node_manager.add_node(new_node, parent_id)
        self.monitor_engine.update_node_worker(new_node)
        self.populate_tree()

    def on_import_tree(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "트리 가져오기", "", "JSON 파일 (*.json);;모든 파일 (*)")
        if file_path:
            # 먼저 모니터링 엔진 정지
            self.monitor_engine.stop_monitoring()
            
            success = self.node_manager.import_data(file_path)
            if success:
                self._current_selected_node_id = None
                self.populate_tree()
                # 새 트리에 맞게 모니터링 재개
                self.monitor_engine.start_monitoring()
                self.log_list.insertItem(0, f"'{file_path}'에서 트리를 성공적으로 가져왔습니다.")
            else:
                QMessageBox.warning(self, "가져오기 실패", "트리 데이터를 가져오는 데 실패했습니다.")
                self.monitor_engine.start_monitoring() # 실패해도 다시 재개
                
    def on_export_tree(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "트리 내보내기", "pingforest_export.json", "JSON 파일 (*.json);;모든 파일 (*)")
        if file_path:
            success = self.node_manager.export_data(file_path)
            if success:
                self.log_list.insertItem(0, f"'{file_path}'로 트리를 내보냈습니다.")
                QMessageBox.information(self, "내보내기 완료", "트리 데이터를 성공적으로 내보냈습니다.")
            else:
                QMessageBox.warning(self, "내보내기 실패", "트리 데이터를 내보내는 데 실패했습니다.")

    def on_show_dashboard(self):
        from src.ui.dashboard_window import DashboardWindow
        if not hasattr(self, 'dashboard_window') or not self.dashboard_window.isVisible():
            self.dashboard_window = DashboardWindow(self.node_manager)
            self.dashboard_window.show()

    def on_tree_context_menu(self, position):
        index = self.tree_view.indexAt(position)
        menu = QMenu()
        
        if not index.isValid():
            # 빈 공간 우클릭 시
            add_root_action = QAction("최상위 노드 추가", self)
            add_root_action.triggered.connect(lambda: self.on_add_device(force_parent_id="")) 
            # force_parent_id="" (빈 문자열)을 넘겨서 최상위 노드로 추가되게 함 (None을 넘기면 현재 선택된 노드의 자식으로 들어갈 수 있으므로)
            menu.addAction(add_root_action)
            menu.exec(self.tree_view.viewport().mapToGlobal(position))
            return
            
        item = self.tree_model.itemFromIndex(index)
        if not item: return
        node_id = item.data(Qt.UserRole)
        # 만약 상태 열(1열)을 클릭한 경우 Name 열(0열)의 데이터를 가져와야 함
        if not node_id:
            sibling = index.siblingAtColumn(0)
            item = self.tree_model.itemFromIndex(sibling)
            node_id = item.data(Qt.UserRole) if item else None
            
        if not node_id: return
        
        node = self.node_manager.get_node(node_id)
        if not node: return
        
        add_child_action = QAction(f"'{node.name}'의 하위 노드 추가", self)
        add_child_action.triggered.connect(lambda: self.on_add_device(force_parent_id=node.id))
        menu.addAction(add_child_action)
        
        menu.addSeparator()
        
        delete_action = QAction(f"'{node.name}' 삭제", self)
        delete_action.triggered.connect(lambda: self._delete_node_with_confirm(node))
        menu.addAction(delete_action)
        
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
        
    def _delete_node_with_confirm(self, node: NodeModel):
        msg = f"'{node.name}' 노드를 삭제하시겠습니까?"
        if node.children:
            msg += "\n\n⚠️ 주의: 하위에 포함된 모든 자식 노드들도 함께 삭제됩니다!"
            
        reply = QMessageBox.question(self, '노드 삭제 확인', msg,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.node_manager.remove_node(node.id)
            if self._current_selected_node_id == node.id:
                self._current_selected_node_id = None
            self.populate_tree()
