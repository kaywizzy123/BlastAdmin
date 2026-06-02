"""
BlastAdmin — Security tab.
Manages the admin PIN that protects BlastAdmin itself and BlastVault status editing.
"""
import hashlib

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

from core import constants
from core import registry
from dialogs.auth_dialog import PinSetupDialog


class SecurityTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._refresh_status()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)

        # ── Top panel: status card + action buttons ───────────────────────
        top = QWidget()
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 12)
        top_layout.setSpacing(20)

        card = QWidget()
        card.setStyleSheet(
            f"background: {constants.BORDER}; border-radius: 8px;"
        )
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(16)

        icon_lbl = QLabel()
        pix = QPixmap(str(constants.ICONS_DIR / "lock.png"))
        if not pix.isNull():
            icon_lbl.setPixmap(pix.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setFixedSize(32, 32)
        card_layout.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        self._pin_title = QLabel()
        self._pin_title.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {constants.TEXT_PRI};"
        )
        self._pin_sub = QLabel()
        self._pin_sub.setStyleSheet(f"font-size: 11px; color: {constants.TEXT_SEC};")
        text_col.addWidget(self._pin_title)
        text_col.addWidget(self._pin_sub)
        card_layout.addLayout(text_col)
        card_layout.addStretch()

        top_layout.addWidget(card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._set_pin_btn = QPushButton("Set PIN")
        self._set_pin_btn.setProperty("primary", True)
        self._set_pin_btn.setStyle(self._set_pin_btn.style())
        self._set_pin_btn.setFixedHeight(34)
        self._set_pin_btn.clicked.connect(self._on_set_pin)

        self._change_pin_btn = QPushButton("Change PIN")
        self._change_pin_btn.setFixedHeight(34)
        self._change_pin_btn.clicked.connect(self._on_change_pin)

        self._remove_pin_btn = QPushButton("Remove PIN")
        self._remove_pin_btn.setProperty("danger", True)
        self._remove_pin_btn.setStyle(self._remove_pin_btn.style())
        self._remove_pin_btn.setFixedHeight(34)
        self._remove_pin_btn.clicked.connect(self._on_remove_pin)

        btn_row.addWidget(self._set_pin_btn)
        btn_row.addWidget(self._change_pin_btn)
        btn_row.addWidget(self._remove_pin_btn)
        btn_row.addStretch()
        top_layout.addLayout(btn_row)
        top_layout.addStretch()

        # ── Bottom panel: info text ───────────────────────────────────────
        bottom = QWidget()
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 12, 0, 0)
        bottom_layout.setSpacing(0)

        info = QLabel(
            "The admin PIN is shared across all machines via artists.json.\n"
            "Artists need this PIN to temporarily unlock status editing in BlastVault.\n"
            "BlastAdmin itself also requires this PIN on every launch."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {constants.TEXT_SEC}; font-size: 11px; line-height: 160%;"
        )
        bottom_layout.addWidget(info)
        bottom_layout.addStretch()

        splitter.addWidget(top)
        splitter.addWidget(bottom)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter, 1)

    def _refresh_status(self):
        has_pin = bool(constants.ADMIN_PIN_HASH)
        if has_pin:
            self._pin_title.setText("PIN is set")
            self._pin_sub.setText("Artists can use this PIN to unlock status editing in BlastVault.")
            self._pin_title.setStyleSheet(
                f"font-size: 14px; font-weight: bold; color: {constants.SUCCESS};"
            )
            self._set_pin_btn.setVisible(False)
            self._change_pin_btn.setVisible(True)
            self._remove_pin_btn.setVisible(True)
        else:
            self._pin_title.setText("No PIN set")
            self._pin_sub.setText("Without a PIN, artists cannot unlock status editing in BlastVault.")
            self._pin_title.setStyleSheet(
                f"font-size: 14px; font-weight: bold; color: {constants.TEXT_SEC};"
            )
            self._set_pin_btn.setVisible(True)
            self._change_pin_btn.setVisible(False)
            self._remove_pin_btn.setVisible(False)

    def _save_pin(self, pin_hash: str):
        constants.ADMIN_PIN_HASH = pin_hash
        data = registry.load()
        data["admin_pin_hash"] = pin_hash
        registry.save(data)
        registry.save_config()
        self._refresh_status()

    def _on_set_pin(self):
        new_hash = PinSetupDialog("Set Admin PIN", parent=self).get_hash()
        if new_hash:
            self._save_pin(new_hash)
            QMessageBox.information(self, "PIN Set", "Admin PIN has been set and saved to the registry.")

    def _on_change_pin(self):
        new_hash = PinSetupDialog("Change Admin PIN", parent=self).get_hash()
        if new_hash:
            self._save_pin(new_hash)
            QMessageBox.information(self, "PIN Changed", "Admin PIN has been updated.")

    def _on_remove_pin(self):
        reply = QMessageBox.question(
            self, "Remove PIN",
            "Remove the admin PIN?\n\n"
            "Artists will be able to unlock status editing in BlastVault without a PIN.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._save_pin("")
            QMessageBox.information(self, "PIN Removed", "Admin PIN has been removed.")
