"""
BlastAdmin — PIN authentication dialogs.
"""
import hashlib

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from core import constants


class PinAuthDialog(QDialog):
    """Shown on launch when a PIN is set — must enter it to open BlastAdmin."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BlastAdmin — Authentication")
        self.setFixedWidth(380)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(0)

        # Icon
        icon_lbl = QLabel()
        pix = QPixmap(str(constants.ICONS_DIR / "lock.png"))
        if not pix.isNull():
            icon_lbl.setPixmap(pix.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)
        layout.addSpacing(10)

        title = QLabel("Admin Authentication")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {constants.TEXT_PRI};"
        )
        layout.addWidget(title)
        layout.addSpacing(6)

        sub = QLabel("Enter the admin PIN to open BlastAdmin.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size: 11px; color: {constants.TEXT_SEC};")
        layout.addWidget(sub)
        layout.addSpacing(18)

        pin_lbl = QLabel("PIN")
        pin_lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")
        layout.addWidget(pin_lbl)
        layout.addSpacing(4)

        self._pin_field = QLineEdit()
        self._pin_field.setEchoMode(QLineEdit.Password)
        self._pin_field.setPlaceholderText("Enter PIN…")
        self._pin_field.setFixedHeight(34)
        self._pin_field.returnPressed.connect(self._on_confirm)
        layout.addWidget(self._pin_field)

        self._error_lbl = QLabel()
        self._error_lbl.setAlignment(Qt.AlignCenter)
        self._error_lbl.setFixedHeight(18)
        self._error_lbl.setStyleSheet(f"color: {constants.FAIL}; font-size: 11px;")
        self._error_lbl.setVisible(False)
        layout.addSpacing(6)
        layout.addWidget(self._error_lbl)
        layout.addSpacing(14)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        unlock_btn = QPushButton("Unlock")
        unlock_btn.setProperty("primary", True)
        unlock_btn.setStyle(unlock_btn.style())
        unlock_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(unlock_btn)
        layout.addLayout(btn_row)

    def _on_confirm(self):
        pin = self._pin_field.text()
        if not pin:
            self._error_lbl.setText("Please enter your PIN.")
            self._error_lbl.setVisible(True)
            return
        if hashlib.sha256(pin.encode()).hexdigest() != constants.ADMIN_PIN_HASH:
            self._error_lbl.setText("Incorrect PIN — please try again.")
            self._error_lbl.setVisible(True)
            self._pin_field.clear()
            self._pin_field.setFocus()
            return
        self.accept()


class PinSetupDialog(QDialog):
    """Two-field dialog for creating or changing the admin PIN."""

    def __init__(self, title="Set Admin PIN", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(380)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._new_hash = ""
        self._build_ui(title)

    def _build_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(0)

        icon_lbl = QLabel()
        pix = QPixmap(str(constants.ICONS_DIR / "lock.png"))
        if not pix.isNull():
            icon_lbl.setPixmap(pix.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)
        layout.addSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {constants.TEXT_PRI};"
        )
        layout.addWidget(title_lbl)
        layout.addSpacing(18)

        def _field(placeholder):
            f = QLineEdit()
            f.setEchoMode(QLineEdit.Password)
            f.setPlaceholderText(placeholder)
            f.setFixedHeight(34)
            return f

        new_lbl = QLabel("New PIN")
        new_lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")
        layout.addWidget(new_lbl)
        layout.addSpacing(4)
        self._new_field = _field("New PIN…")
        layout.addWidget(self._new_field)
        layout.addSpacing(10)

        confirm_lbl = QLabel("Confirm PIN")
        confirm_lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")
        layout.addWidget(confirm_lbl)
        layout.addSpacing(4)
        self._confirm_field = _field("Confirm PIN…")
        layout.addWidget(self._confirm_field)

        self._new_field.returnPressed.connect(self._confirm_field.setFocus)
        self._confirm_field.returnPressed.connect(self._on_confirm)

        self._error_lbl = QLabel()
        self._error_lbl.setAlignment(Qt.AlignCenter)
        self._error_lbl.setFixedHeight(18)
        self._error_lbl.setStyleSheet(f"color: {constants.FAIL}; font-size: 11px;")
        self._error_lbl.setVisible(False)
        layout.addSpacing(6)
        layout.addWidget(self._error_lbl)
        layout.addSpacing(14)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Set PIN")
        save_btn.setProperty("primary", True)
        save_btn.setStyle(save_btn.style())
        save_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_confirm(self):
        pin     = self._new_field.text()
        confirm = self._confirm_field.text()
        if not pin:
            self._error_lbl.setText("Please enter a PIN.")
            self._error_lbl.setVisible(True)
            return
        if pin != confirm:
            self._error_lbl.setText("PINs do not match — please try again.")
            self._error_lbl.setVisible(True)
            self._confirm_field.clear()
            self._confirm_field.setFocus()
            return
        self._new_hash = hashlib.sha256(pin.encode()).hexdigest()
        self.accept()

    def get_hash(self) -> str | None:
        """Run dialog. Returns SHA-256 hex hash on accept, None on cancel."""
        if self.exec_() == QDialog.Accepted:
            return self._new_hash
        return None
