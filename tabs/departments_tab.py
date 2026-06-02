"""
BlastAdmin — Departments tab.
CRUD for the studio's department list.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QLineEdit, QHeaderView, QMessageBox,
    QAbstractItemView, QInputDialog, QMenu,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from core import constants
from core import registry


class DepartmentsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self._search.setPlaceholderText("Search departments…")
        self._search.setFixedHeight(30)
        self._search.setMaximumWidth(280)
        self._search.textChanged.connect(self._apply_filter)

        self._count_lbl = QLabel()
        self._count_lbl.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")

        add_btn = QPushButton(" Add Department")
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
        self._table.setHorizontalHeaderLabels(["Department"])
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

    def refresh(self):
        self._apply_filter(self._search.text())

    def _apply_filter(self, text: str):
        q = text.strip().lower()
        depts = constants.DEPARTMENTS
        filtered = [d for d in depts if not q or q in d.lower()]

        self._table.setRowCount(0)
        for row, dept in enumerate(filtered):
            self._table.insertRow(row)
            item = QTableWidgetItem(dept)
            item.setData(Qt.UserRole, dept)
            self._table.setItem(row, 0, item)
            self._table.setRowHeight(row, 36)

        total = len(depts)
        shown = len(filtered)
        self._count_lbl.setText(
            f"{total} department{'s' if total != 1 else ''}"
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
        data["departments"] = constants.DEPARTMENTS
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
            menu.addAction("Add Department").triggered.connect(self._on_add)
        menu.exec_(self._table.viewport().mapToGlobal(pos))

    def _on_add(self):
        name, ok = QInputDialog.getText(self, "Add Department", "Department name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in constants.DEPARTMENTS:
            QMessageBox.warning(self, "Duplicate", f"'{name}' already exists.")
            return
        constants.DEPARTMENTS.append(name)
        self._persist()
        self._apply_filter(self._search.text())

    def _on_edit(self):
        old = self._selected_name()
        if not old:
            return
        name, ok = QInputDialog.getText(self, "Edit Department", "Department name:", text=old)
        if not ok or not name.strip() or name.strip() == old:
            return
        name = name.strip()
        if name in constants.DEPARTMENTS:
            QMessageBox.warning(self, "Duplicate", f"'{name}' already exists.")
            return
        constants.DEPARTMENTS[constants.DEPARTMENTS.index(old)] = name
        self._persist()
        self._apply_filter(self._search.text())

    def _on_delete(self):
        name = self._selected_name()
        if not name:
            return
        reply = QMessageBox.question(
            self, "Delete Department",
            f"Remove '{name}' from the department list?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        constants.DEPARTMENTS.remove(name)
        self._persist()
        self._apply_filter(self._search.text())
