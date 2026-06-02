"""
BlastAdmin — Artists tab.
Full CRUD on the artists list.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QLineEdit, QHeaderView, QMessageBox,
    QAbstractItemView, QMenu,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from core import constants
from core import registry
from dialogs.artist_dialog import ArtistDialog


_COLUMNS = ["Username", "Name", "Department", "Role", "Permissions", "Email"]
_PERM_COLORS = {
    "admin":    "#1085d3",
    "reviewer": "#e5a820",
    "basic":    "#a1a1a1",
}


class ArtistsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._artists: list[dict] = []
        self._build_ui()
        self.refresh()

    # ── UI ────────────────────────────────────────────────────────────────── #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Toolbar row
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search artists…")
        self._search.setFixedHeight(30)
        self._search.setMaximumWidth(280)
        self._search.textChanged.connect(self._apply_filter)

        self._count_lbl = QLabel()
        self._count_lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")

        add_btn = QPushButton(" Add Artist")
        add_btn.setIcon(QIcon(str(constants.ICONS_DIR / "plus.png")))
        add_btn.setFixedHeight(30)
        add_btn.setProperty("primary", True)
        add_btn.setStyle(add_btn.style())
        add_btn.clicked.connect(self._on_add)

        toolbar.addWidget(self._search)
        toolbar.addWidget(self._count_lbl)
        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        layout.addLayout(toolbar)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self._table.setShowGrid(True)
        self._table.setWordWrap(False)
        self._table.doubleClicked.connect(self._on_edit)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._table)

        # Bottom action row
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self._edit_btn   = QPushButton("Edit")
        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setProperty("danger", True)
        self._delete_btn.setStyle(self._delete_btn.style())

        self._edit_btn.clicked.connect(self._on_edit)
        self._delete_btn.clicked.connect(self._on_delete)

        action_row.addStretch()
        action_row.addWidget(self._edit_btn)
        action_row.addWidget(self._delete_btn)
        layout.addLayout(action_row)

    # ── Data ──────────────────────────────────────────────────────────────── #

    def refresh(self):
        """Reload from disk and repopulate the table."""
        self._artists = registry.load_artists()
        self._apply_filter(self._search.text())

    def _apply_filter(self, text: str):
        q = text.strip().lower()
        filtered = [
            a for a in self._artists
            if not q or any(
                q in str(v).lower()
                for v in a.values()
            )
        ] if q else list(self._artists)

        self._table.setRowCount(0)
        for row, artist in enumerate(filtered):
            self._table.insertRow(row)
            for col, key in enumerate(["username", "name", "department", "role", "permissions", "email"]):
                val  = artist.get(key, "")
                item = QTableWidgetItem(val)
                item.setData(Qt.UserRole, artist.get("username", ""))
                if key == "permissions":
                    item.setForeground(
                        __import__("PyQt5.QtGui", fromlist=["QColor"]).QColor(
                            _PERM_COLORS.get(val, constants.TEXT_SEC)
                        )
                    )
                self._table.setItem(row, col, item)

        self._table.setRowHeight(0, 36)
        for r in range(self._table.rowCount()):
            self._table.setRowHeight(r, 36)

        total = len(self._artists)
        shown = len(filtered)
        self._count_lbl.setText(
            f"{total} artist{'s' if total != 1 else ''}"
            + (f"  ({shown} shown)" if q else "")
        )

    def _selected_username(self) -> str | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _artist_by_username(self, username: str) -> dict | None:
        for a in self._artists:
            if a.get("username", "").lower() == username.lower():
                return a
        return None

    # ── Slots ─────────────────────────────────────────────────────────────── #

    def _on_context_menu(self, pos):
        menu = QMenu(self)
        item = self._table.itemAt(pos)
        if item is not None:
            self._table.selectRow(item.row())
            menu.addAction("Edit").triggered.connect(self._on_edit)
            menu.addAction("Delete").triggered.connect(self._on_delete)
        else:
            menu.addAction("Add Artist").triggered.connect(self._on_add)
        menu.exec_(self._table.viewport().mapToGlobal(pos))

    def _on_add(self):
        result = ArtistDialog(parent=self).get_artist()
        if result is None:
            return
        # Check for duplicate username
        if any(a.get("username", "").lower() == result["username"] for a in self._artists):
            QMessageBox.warning(
                self, "Duplicate Username",
                f"An artist with username '{result['username']}' already exists."
            )
            return
        self._artists.append(result)
        registry.save_artists(self._artists)
        self._apply_filter(self._search.text())

    def _on_edit(self):
        username = self._selected_username()
        if not username:
            return
        artist = self._artist_by_username(username)
        if not artist:
            return
        result = ArtistDialog(artist=artist, parent=self).get_artist()
        if result is None:
            return
        for i, a in enumerate(self._artists):
            if a.get("username", "").lower() == username.lower():
                self._artists[i] = result
                break
        registry.save_artists(self._artists)
        self._apply_filter(self._search.text())

    def _on_delete(self):
        username = self._selected_username()
        if not username:
            return
        reply = QMessageBox.question(
            self, "Delete Artist",
            f"Remove '{username}' from the registry?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._artists = [a for a in self._artists if a.get("username", "").lower() != username.lower()]
        registry.save_artists(self._artists)
        self._apply_filter(self._search.text())
