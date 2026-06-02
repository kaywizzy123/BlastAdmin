"""
BlastAdmin — Studio tab.
Manages studio name and the registry file path only.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal

from core import constants
from core import registry


class StudioTab(QWidget):
    registry_changed = pyqtSignal()   # emitted after a successful save

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
        self._registry_path.textChanged.connect(self._on_path_changed)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedHeight(32)
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_registry)
        path_row.addWidget(self._registry_path)
        path_row.addWidget(browse_btn)
        form.addRow(self._lbl("Registry File"), path_row)

        outer.addLayout(form)

        # ── Registry status indicator ─────────────────────────────────────
        self._status_lbl = QLabel()
        self._status_lbl.setWordWrap(True)
        self._status_lbl.setStyleSheet(
            f"font-size: 11px; color: {constants.TEXT_SEC}; background: transparent;"
        )
        outer.addWidget(self._status_lbl)

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

    def _set_status(self, text: str, ok: bool | None = None):
        """Update the status label. ok=True → green, ok=False → red, None → grey."""
        if ok is True:
            color = constants.SUCCESS
        elif ok is False:
            color = constants.FAIL
        else:
            color = constants.TEXT_SEC
        self._status_lbl.setStyleSheet(
            f"font-size: 11px; color: {color}; background: transparent;"
        )
        self._status_lbl.setText(text)

    def _on_path_changed(self):
        """Live feedback as the user types a path."""
        from pathlib import Path
        raw = self._registry_path.text().strip()
        if not raw:
            # Blank → show default path
            default = registry.registry_path()
            if default.exists():
                data   = registry.load()
                count  = len(data.get("artists", []))
                self._set_status(
                    f"✓  Using default path  ·  {count} artist{'s' if count != 1 else ''} found",
                    ok=True,
                )
            else:
                self._set_status(f"Default path not found: {default}", ok=False)
            return

        p = Path(raw)
        if p.exists():
            try:
                import json
                data  = json.loads(p.read_text(encoding="utf-8"))
                count = len(data.get("artists", []))
                self._set_status(
                    f"✓  File found  ·  {count} artist{'s' if count != 1 else ''}",
                    ok=True,
                )
            except Exception as exc:
                self._set_status(f"⚠  File found but could not be read: {exc}", ok=False)
        else:
            self._set_status("⚠  File not found at this path", ok=False)

    def _load(self):
        self._studio_name.setText(constants.STUDIO_NAME)
        self._registry_path.setText(constants.REGISTRY_PATH)
        # Trigger status display on load
        self._on_path_changed()

    def _save(self):
        name = self._studio_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Studio Name", "Studio name cannot be empty.")
            return

        constants.STUDIO_NAME   = name
        constants.REGISTRY_PATH = self._registry_path.text().strip()

        # ── Only write studio_name into artists.json if the file already exists ──
        # Never create or overwrite a registry file with an empty artists list.
        path = registry.registry_path()
        if path.exists():
            data = registry.load()
            if data.get("studio_name") != constants.STUDIO_NAME:
                data["studio_name"] = constants.STUDIO_NAME
                registry.save(data)

        # Always save the local BlastAdmin config
        registry.save_config()

        # Refresh status label
        self._on_path_changed()

        self.registry_changed.emit()
        QMessageBox.information(self, "Saved", "Studio settings saved.")

    def _browse_registry(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Registry File",
            self._registry_path.text() or constants.STUDIO_ROOT,
            "JSON files (*.json)",
        )
        if path:
            self._registry_path.setText(path)
