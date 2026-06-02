"""
BlastAdmin — Studio tab.
Manages studio name and the registry file path only.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt

from core import constants
from core import registry


class StudioTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(16)

        outer.addWidget(self._section("Studio Settings"))

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Studio name
        self._studio_name = QLineEdit()
        self._studio_name.setFixedHeight(32)
        self._studio_name.setPlaceholderText("e.g. indie Animation Studio")
        form.addRow(self._lbl("Studio Name"), self._studio_name)

        # Registry file path
        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self._registry_path = QLineEdit()
        self._registry_path.setFixedHeight(32)
        self._registry_path.setPlaceholderText(
            r"e.g. Z:\SHOWS\artists.json  (leave blank to use Studio Root default)"
        )
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedHeight(32)
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_registry)
        path_row.addWidget(self._registry_path)
        path_row.addWidget(browse_btn)
        form.addRow(self._lbl("Registry File"), path_row)

        outer.addLayout(form)

        # Info note
        note = QLabel(
            "The registry file is shared across all machines on the network.\n"
            "Changes here take effect on every machine the next time BlastVault launches."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")
        outer.addWidget(note)

        outer.addStretch()

        # Save button
        save_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setProperty("primary", True)
        save_btn.setStyle(save_btn.style())
        save_btn.setFixedHeight(34)
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(self._save)
        save_row.addStretch()
        save_row.addWidget(save_btn)
        outer.addLayout(save_row)

    def _lbl(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")
        return lbl

    def _section(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {constants.TEXT_PRI};"
        )
        return lbl

    def _load(self):
        data = registry.load()
        self._studio_name.setText(data.get("studio_name", constants.STUDIO_NAME))
        self._registry_path.setText(constants.REGISTRY_PATH)

    def _save(self):
        name = self._studio_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Studio Name", "Studio name cannot be empty.")
            return

        constants.STUDIO_NAME   = name
        constants.REGISTRY_PATH = self._registry_path.text().strip()

        data = registry.load()
        data["studio_name"] = constants.STUDIO_NAME
        registry.save(data)
        registry.save_config()

        QMessageBox.information(self, "Saved", "Studio settings saved.")

    def _browse_registry(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Select Registry File",
            self._registry_path.text() or constants.STUDIO_ROOT,
            "JSON files (*.json)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if path:
            self._registry_path.setText(path)
