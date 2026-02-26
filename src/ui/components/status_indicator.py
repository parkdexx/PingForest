from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from src.core.models import NodeStatus

class StatusIndicator(QWidget):
    def __init__(self, size=16, parent=None):
        super().__init__(parent)
        self.setFixedSize(QSize(size, size))
        self.current_status = NodeStatus.UNKNOWN

    def set_status(self, status: NodeStatus):
        self.current_status = status
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Color mapping corresponding to Toss aesthetic
        color_map = {
            NodeStatus.NORMAL: QColor("#3182f6"),   # Toss Blue (or Green for normal, usually Toss uses blue for success, but let's stick to green)
            # Actually, standard dictates green for normal
            NodeStatus.NORMAL: QColor("#00c73c"),   # Toss style vibrance green
            NodeStatus.WARNING: QColor("#f4ab2e"),  # Toss style vibrance orange/yellow
            NodeStatus.DEAD: QColor("#f04452"),     # Toss style vibrance red
            NodeStatus.UNKNOWN: QColor("#b0b8c1")   # Toss style gray
        }
        
        rect = self.rect()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color_map.get(self.current_status, QColor("#b0b8c1"))))
        
        # Draw a perfect circle
        painter.drawEllipse(rect.adjusted(1, 1, -1, -1))
