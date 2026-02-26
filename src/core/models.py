import uuid
from enum import Enum
from typing import List, Optional

class NodeStatus(Enum):
    NORMAL = "normal"      # 초록색 (정상)
    WARNING = "warning"    # 노란색 (불안/응답지연 등)
    DEAD = "dead"          # 빨간색 (연결 실패)
    UNKNOWN = "unknown"    # 회색 (검사 전)

class NodeType(Enum):
    GROUP = "group"        # 하위 노드를 가지는 그룹 (폴더)
    DEVICE = "device"      # 실제 장비 (IP/Port 할당됨)

class NodeModel:
    def __init__(self, name: str, node_type: NodeType):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = node_type
        
        # Only used if type is DEVICE
        self.ip_address: str = ""
        self.port: Optional[int] = None
        self.check_interval_seconds: int = 60
        
        # 알림 설정
        self.enable_email_alert: bool = False
        self.alert_threshold_count: int = 3
        self.alert_emails: List[str] = []
        self.alert_interval_minutes: int = 30
        
        # 상태 정보
        self.status = NodeStatus.UNKNOWN
        self.last_check_time: str = ""
        self.last_response_time_ms: float = 0.0
        
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
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data: dict, parent_id: Optional[str] = None):
        node = cls(data["name"], NodeType(data.get("type", "device")))
        node.id = data.get("id", str(uuid.uuid4()))
        node.ip_address = data.get("ip_address", "")
        node.port = data.get("port")
        node.check_interval_seconds = data.get("check_interval_seconds", 60)
        node.enable_email_alert = data.get("enable_email_alert", False)
        node.alert_threshold_count = data.get("alert_threshold_count", 3)
        node.alert_emails = data.get("alert_emails", [])
        node.alert_interval_minutes = data.get("alert_interval_minutes", 30)
        node.parent_id = parent_id
        
        for child_data in data.get("children", []):
            child_node = cls.from_dict(child_data, parent_id=node.id)
            node.children.append(child_node)
            
        return node
