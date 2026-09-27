"""
BlastAdmin — Departments tab.
CRUD for the studio's department list.
"""
from widgets.list_editor_tab import ListEditorTab


class DepartmentsTab(ListEditorTab):
    def __init__(self, parent=None):
        super().__init__("department", "departments", "DEPARTMENTS", "departments", parent)
