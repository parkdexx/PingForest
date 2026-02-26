TOSS_STYLE_QSS = """
QWidget {
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    color: #333d4b;
    font-size: 13px;
    background-color: #f9fafb;
}

QMainWindow {
    background-color: #f9fafb;
}

/* TreeView Styling */
QTreeView {
    background-color: #ffffff;
    border: 1px solid #e5e8eb;
    border-radius: 12px;
    padding: 5px;
    outline: none;
}

QTreeView::item {
    padding: 8px 5px;
    border-radius: 6px;
    margin: 2px 5px;
}

QTreeView::item:hover {
    background-color: #f2f4f6;
}

QTreeView::item:selected {
    background-color: #e8f3ff;
    color: #1b64da;
    font-weight: bold;
}

/* Detail Panel Styling */
#detailPanel {
    background-color: #ffffff;
    border: 1px solid #e5e8eb;
    border-radius: 12px;
    padding: 20px;
}

/* Log Panel Styling */
#logPanel {
    background-color: #ffffff;
    border: 1px solid #e5e8eb;
    border-radius: 12px;
    padding: 20px;
}

/* Header Labels */
.PanelTitle {
    font-size: 18px;
    font-weight: bold;
    color: #191f28;
    margin-bottom: 10px;
}

/* Buttons */
QPushButton {
    background-color: #3182f6;
    color: #ffffff;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: bold;
    border: none;
}

QPushButton:hover {
    background-color: #1b64da;
}

QPushButton:pressed {
    background-color: #1551b5;
}

/* Secondary Button */
QPushButton.secondary {
    background-color: #f2f4f6;
    color: #4e5968;
}

QPushButton.secondary:hover {
    background-color: #e5e8eb;
}

/* Inputs */
QLineEdit, QSpinBox {
    background-color: #f2f4f6;
    border: 1px solid #e5e8eb;
    border-radius: 6px;
    padding: 8px;
    color: #333d4b;
}

QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #3182f6;
    background-color: #ffffff;
}
"""
