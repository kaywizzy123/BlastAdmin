"""
BlastAdmin — Review Types tab.
CRUD for the studio's review types (Director Dailies, Final Review, …).
"""
from widgets.list_editor_tab import ListEditorTab


class ReviewTypesTab(ListEditorTab):
    def __init__(self, parent=None):
        super().__init__("review type", "review types", "REVIEW_TYPES", "review_types", parent)
