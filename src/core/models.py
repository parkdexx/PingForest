import uuid
from enum import Enum
from typing import List, Optional

class NodeStatus(Enum):
    NORMAL = "normal"      # 초록색 (정상)
    WARNING = "warning"    # 노란색 (불안/응답지연 등)
    DEAD = "dead"          # 빨간색 (연결 실패)
    UNKNOWN = "unknown"    # 회색 (검사 전)

class NodeType(Enum):
    DEVICE = "device"

class NodeModel:
    def __init__(self, name: str, node_type: NodeType = NodeType.DEVICE):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = node_type
        
        # IP/Port 정보 (비워두면 폴더처럼 동작)
        self.ip_address: str = ""
        self.port: Optional[int] = None
        self.check_interval_seconds: int = 60
        
        # 알림 설정
        self.enable_email_alert: bool = False
        self.alert_threshold_count: int = 3
        self.alert_emails: List[str] = []
        self.alert_interval_minutes: int = 30
        
        # 상태 정보
        self.ping_status = NodeStatus.UNKNOWN
        self.port_status = NodeStatus.UNKNOWN
        self.last_check_time: str = ""
        self.ping_response_time_ms: float = 0.0
        self.port_response_time_ms: float = 0.0
        
        # 대시보드 설정
        self.send_to_dashboard: bool = True
        self.dashboard_color: str = "#ffffff"
        self.dashboard_icon: str = "fa5s.desktop"
        
        # 런타임 로그 (휘발성)
        self.logs: List[str] = []
        
        # 트리 구조
        self.parent_id: Optional[str] = None
        self.children: List['NodeModel'] = []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "ip_address": self.ip_address,
            "port": self.port,
            "check_interval_seconds": self.check_interval_seconds,
            "enable_email_alert": self.enable_email_alert,
            "alert_threshold_count": self.alert_threshold_count,
            "alert_emails": self.alert_emails,
            "alert_interval_minutes": self.alert_interval_minutes,
            "send_to_dashboard": self.send_to_dashboard,
            "dashboard_color": self.dashboard_color,
            "dashboard_icon": self.dashboard_icon,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data: dict, parent_id: Optional[str] = None):
        # 마이그레이션: 기존 group 타입도 device로 강제 변환
        node = cls(data["name"], NodeType.DEVICE)
        node.id = data.get("id", str(uuid.uuid4()))
        node.ip_address = data.get("ip_address", "")
        node.port = data.get("port")
        node.check_interval_seconds = data.get("check_interval_seconds", 60)
        node.enable_email_alert = data.get("enable_email_alert", False)
        node.alert_threshold_count = data.get("alert_threshold_count", 3)
        node.alert_emails = data.get("alert_emails", [])
        node.alert_interval_minutes = data.get("alert_interval_minutes", 30)
        node.send_to_dashboard = data.get("send_to_dashboard", True)
        node.dashboard_color = data.get("dashboard_color", "#ffffff")
        node.dashboard_icon = data.get("dashboard_icon", "fa5s.desktop")
        node.parent_id = parent_id
        
        for child_data in data.get("children", []):
            child_node = cls.from_dict(child_data, parent_id=node.id)
            node.children.append(child_node)
            
        return node
