"""BlastAdmin — global stylesheet (matches BlastVault dark theme)."""
import sys
from core import constants as c


def stylesheet() -> str:
    return f"""
    QMainWindow, QDialog, QWidget {{
        background-color: {c.BG};
        color: {c.TEXT_PRI};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 12px;
    }}
    QTabWidget::pane {{
        border: 1px solid {c.SPLITTER_COLOR};
        background: {c.BG};
    }}
    QTabBar::tab {{
        background: {c.BORDER};
        color: {c.TEXT_SEC};
        padding: 8px 20px;
        border: none;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{
        color: {c.TEXT_PRI};
        border-bottom: 2px solid {c.ACCENT_HI};
        background: {c.BG};
    }}
    QTabBar::tab:hover:!selected {{
        color: {c.TEXT_PRI};
        background: {c.ACCENT};
    }}
    QLineEdit, QTextEdit {{
        background-color: {c.BORDER};
        color: {c.TEXT_PRI};
        border: 1px solid {c.SPLITTER_COLOR};
        border-radius: 4px;
        padding: 5px 8px;
        selection-background-color: {c.ACCENT_HI};
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {c.ACCENT_HI};
    }}
    QComboBox {{
        background-color: {c.BORDER};
        color: {c.TEXT_PRI};
        border: 1px solid {c.SPLITTER_COLOR};
        border-radius: 4px;
        padding: 5px 8px;
    }}
    QComboBox:focus {{
        border: 1px solid {c.ACCENT_HI};
    }}
    QComboBox QAbstractItemView {{
        background-color: {c.BORDER};
        color: {c.TEXT_PRI};
        border: 1px solid {c.SPLITTER_COLOR};
        selection-background-color: {c.ACCENT};
        outline: none;
    }}
    QPushButton {{
        background-color: {c.ACCENT};
        color: {c.TEXT_PRI};
        border: none;
        border-radius: 4px;
        padding: 6px 16px;
    }}
    QPushButton:hover {{
        background-color: {c.SPLITTER_COLOR};
    }}
    QPushButton:pressed {{
        background-color: {c.BORDER};
    }}
    QPushButton[primary="true"] {{
        background-color: {c.ACCENT_HI};
        color: white;
        font-weight: bold;
    }}
    QPushButton[primary="true"]:hover {{
        background-color: #1a95e8;
    }}
    QPushButton[danger="true"] {{
        background-color: {c.FAIL};
        color: white;
    }}
    QPushButton[danger="true"]:hover {{
        background-color: #cc0000;
    }}
    QTableWidget {{
        background-color: {c.BORDER};
        color: {c.TEXT_PRI};
        border: 1px solid {c.SPLITTER_COLOR};
        gridline-color: {c.SPLITTER_COLOR};
        border-radius: 4px;
        outline: none;
    }}
    QTableWidget::item {{
        padding: 6px 10px;
        border: none;
    }}
    QTableWidget::item:selected {{
        background-color: {c.ACCENT};
        color: {c.TEXT_PRI};
    }}
    QHeaderView::section {{
        background-color: {c.BG};
        color: {c.TEXT_SEC};
        border: none;
        border-bottom: 1px solid {c.SPLITTER_COLOR};
        padding: 6px 10px;
        font-weight: bold;
        font-size: 11px;
        text-transform: uppercase;
    }}
    QListWidget {{
        background-color: {c.BORDER};
        color: {c.TEXT_PRI};
        border: 1px solid {c.SPLITTER_COLOR};
        border-radius: 4px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 5px 8px;
    }}
    QListWidget::item:selected {{
        background-color: {c.ACCENT};
        color: {c.TEXT_PRI};
    }}
    QScrollBar:vertical {{
        background-color: {c.BG};
        width: 10px;
        border: 1px solid {c.SPLITTER_COLOR};
    }}
    QScrollBar::handle:vertical {{
        background-color: {c.BORDER};
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {c.ACCENT};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background-color: {c.BG};
        height: 10px;
        border: 1px solid {c.SPLITTER_COLOR};
    }}
    QScrollBar::handle:horizontal {{
        background-color: {c.BORDER};
        min-width: 20px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {c.ACCENT};
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    QLabel {{
        background: transparent;
        color: {c.TEXT_PRI};
    }}
    QSplitter::handle {{
        background-color: {c.SPLITTER_COLOR};
    }}
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    QMessageBox {{
        background-color: {c.BG};
    }}
    QMessageBox QLabel {{
        color: {c.TEXT_PRI};
    }}
    """


def qt_argv():
    """Return argv list with HiDPI flags pre-inserted."""
    import sys
    return sys.argv
