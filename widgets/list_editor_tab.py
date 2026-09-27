"""
BlastAdmin — reusable list editor tab.
CRUD for a simple list of names stored on ``core.constants`` and mirrored
into both artists.json and the local config (departments, review types, …).
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QLineEdit, QMessageBox,
    QAbstractItemView, QInputDialog, QMenu,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from core import constants
from core import registry


class ListEditorTab(QWidget):
    """
    Editable list of names.

    *noun* / *plural* are the display words ("department" / "departments").
    *attr* is the list attribute on ``core.constants`` (e.g. "DEPARTMENTS").
    *key* is the top-level key written into artists.json (e.g. "departments").
    """

    def __init__(self, noun: str, plural: str, attr: str, key: str, parent=None):
        super().__init__(parent)
        self._noun   = noun
        self._plural = plural
        self._attr   = attr
        self._key    = key
        self._build_ui()
        self.refresh()

    # ── UI ────────────────────────────────────────────────────────────────── #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._search = QLineEdit()
        self._search.setPlaceholderText(f"Search {self._plural}…")
        self._search.setFixedHeight(30)
        self._search.setMaximumWidth(280)
        self._search.textChanged.connect(self._apply_filter)

        self._count_lbl = QLabel()
        self._count_lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")

        add_btn = QPushButton(f" Add {self._noun.title()}")
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
        self._table.setColumnCount(1)
        self._table.setHorizontalHeaderLabels([self._noun.title()])
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
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

    def _items(self) -> list[str]:
        # Looked up each time — load_config() rebinds the attribute.
        return getattr(constants, self._attr)

    def refresh(self):
        self._apply_filter(self._search.text())

    def _apply_filter(self, text: str):
        q = text.strip().lower()
        items = self._items()
        filtered = [i for i in items if not q or q in i.lower()]

        self._table.setRowCount(0)
        for row, name in enumerate(filtered):
            self._table.insertRow(row)
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, name)
            self._table.setItem(row, 0, item)
            self._table.setRowHeight(row, 36)

        total = len(items)
        shown = len(filtered)
        self._count_lbl.setText(
            f"{total} {self._noun if total == 1 else self._plural}"
            + (f"  ({shown} shown)" if q else "")
        )

    def _selected_name(self) -> str | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _persist(self):
        data = registry.load()
        data[self._key] = self._items()
        registry.save(data)
        registry.save_config()

    # ── Slots ─────────────────────────────────────────────────────────────── #

    def _on_context_menu(self, pos):
        menu = QMenu(self)
        item = self._table.itemAt(pos)
        if item is not None:
            self._table.selectRow(item.row())
            menu.addAction("Edit").triggered.connect(self._on_edit)
            menu.addAction("Delete").triggered.connect(self._on_delete)
        else:
            menu.addAction(f"Add {self._noun.title()}").triggered.connect(self._on_add)
        menu.exec_(self._table.viewport().mapToGlobal(pos))

    def _on_add(self):
        title = f"Add {self._noun.title()}"
        name, ok = QInputDialog.getText(self, title, f"{self._noun.capitalize()} name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self._items():
            QMessageBox.warning(self, "Duplicate", f"'{name}' already exists.")
            return
        self._items().append(name)
        self._persist()
        self._apply_filter(self._search.text())

    def _on_edit(self):
        old = self._selected_name()
        if not old:
            return
        title = f"Edit {self._noun.title()}"
        name, ok = QInputDialog.getText(self, title, f"{self._noun.capitalize()} name:", text=old)
        if not ok or not name.strip() or name.strip() == old:
            return
        name = name.strip()
        items = self._items()
        if name in items:
            QMessageBox.warning(self, "Duplicate", f"'{name}' already exists.")
            return
        items[items.index(old)] = name
        self._persist()
        self._apply_filter(self._search.text())

    def _on_delete(self):
        name = self._selected_name()
        if not name:
            return
        reply = QMessageBox.question(
            self, f"Delete {self._noun.title()}",
            f"Remove '{name}' from the {self._noun} list?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._items().remove(name)
        self._persist()
        self._apply_filter(self._search.text())
