"""
BlastAdmin — Add / Edit Artist dialog.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
)
from PyQt5.QtCore import Qt

from core import constants


class ArtistDialog(QDialog):
    """Dialog for adding or editing a single artist record."""

    def __init__(self, artist: dict | None = None, parent=None):
        super().__init__(parent)
        self._artist = artist or {}
        self._is_edit = bool(artist)

        self.setWindowTitle("Edit Artist" if self._is_edit else "Add Artist")
        self.setFixedWidth(400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Edit Artist" if self._is_edit else "Add Artist")
        title.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {constants.TEXT_PRI};"
        )
        layout.addWidget(title)

        # Form
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def _label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")
            return lbl

        def _field(placeholder="", value=""):
            f = QLineEdit()
            f.setPlaceholderText(placeholder)
            f.setText(value)
            f.setFixedHeight(32)
            return f

        self._username_field   = _field("e.g. jsmith",           self._artist.get("username", ""))
        self._name_field       = _field("e.g. Jane Smith",        self._artist.get("name", ""))
        self._email_field      = _field("e.g. jsmith@studio.com", self._artist.get("email", ""))

        # Department combobox
        self._dept_combo = QComboBox()
        self._dept_combo.setFixedHeight(32)
        self._dept_combo.addItems(constants.DEPARTMENTS)
        dept = self._artist.get("department", "")
        idx  = self._dept_combo.findText(dept)
        if idx >= 0:
            self._dept_combo.setCurrentIndex(idx)

        # Role combobox
        self._role_combo = QComboBox()
        self._role_combo.setFixedHeight(32)
        self._role_combo.addItems(constants.ROLE_OPTIONS)
        role = self._artist.get("role", "Artist")
        ridx = self._role_combo.findText(role)
        if ridx >= 0:
            self._role_combo.setCurrentIndex(ridx)

        # Permissions combobox
        self._perm_combo = QComboBox()
        self._perm_combo.setFixedHeight(32)
        self._perm_combo.addItems(constants.PERMISSION_OPTIONS)
        perm = self._artist.get("permissions", "basic")
        pidx = self._perm_combo.findText(perm)
        if pidx >= 0:
            self._perm_combo.setCurrentIndex(pidx)

        if self._is_edit:
            self._username_field.setToolTip(
                "Changing the username will break any existing filename matches\n"
                "and session history linked to the old username."
            )

        form.addRow(_label("Username *"), self._username_field)

        # Warning shown under username field when editing
        if self._is_edit:
            username_warn = QLabel("⚠  Changing username breaks existing filename links")
            username_warn.setStyleSheet(
                f"color: {constants.FAIL}; font-size: 10px; background: transparent;"
            )
            form.addRow("", username_warn)
        form.addRow(_label("Display Name"), self._name_field)
        form.addRow(_label("Email"), self._email_field)
        form.addRow(_label("Department"), self._dept_combo)
        form.addRow(_label("Role"), self._role_combo)
        form.addRow(_label("Permissions *"), self._perm_combo)
        layout.addLayout(form)

        # Error label
        self._error_lbl = QLabel()
        self._error_lbl.setStyleSheet(f"color: {constants.FAIL}; font-size: 11px;")
        self._error_lbl.setVisible(False)
        layout.addWidget(self._error_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        self._save_btn = QPushButton("Save" if self._is_edit else "Add Artist")
        self._save_btn.setProperty("primary", True)
        self._save_btn.setStyle(self._save_btn.style())
        self._save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        username = self._username_field.text().strip().lower()
        if not username:
            self._error_lbl.setText("Username is required.")
            self._error_lbl.setVisible(True)
            return

        self._result = {
            "username":   username,
            "name":       self._name_field.text().strip() or username,
            "email":      self._email_field.text().strip(),
            "department": self._dept_combo.currentText(),
            "role":       self._role_combo.currentText(),
            "permissions": self._perm_combo.currentText(),
        }
        self.accept()

    def get_artist(self) -> dict | None:
        """Run dialog. Returns artist dict on accept, None on cancel."""
        if self.exec_() == QDialog.Accepted:
            return self._result
        return None
