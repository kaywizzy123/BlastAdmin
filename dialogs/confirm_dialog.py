"""BlastAdmin — Reusable styled confirmation dialog."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PyQt5.QtCore import Qt

from core import constants


class ConfirmDialog(QDialog):
    """
    Styled yes/no confirmation dialog.

    Usage:
        dlg = ConfirmDialog("Delete Artist", "Remove 'jdoe'?\nThis cannot be undone.", danger=True, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            ...
    """

    def __init__(self, title: str, message: str, confirm_label: str = "Confirm",
                 danger: bool = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(380)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {constants.TEXT_PRI};"
        )
        layout.addWidget(title_lbl)

        # Message
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"font-size: 12px; color: {constants.TEXT_SEC};")
        layout.addWidget(msg_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(32)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton(confirm_label)
        confirm_btn.setFixedHeight(32)
        confirm_btn.setFixedWidth(100)
        if danger:
            confirm_btn.setProperty("danger", True)
        else:
            confirm_btn.setProperty("primary", True)
        confirm_btn.setStyle(confirm_btn.style())
        confirm_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)
