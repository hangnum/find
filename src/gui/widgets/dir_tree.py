"""Directory tree widget for NL-Find GUI."""

from pathlib import Path

from PyQt6.QtCore import QDir, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView


class DirectoryTree(QTreeView):
    """Tree view for navigating directories."""

    path_selected = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the directory tree."""
        # Use file system model
        self.model = QFileSystemModel()
        self.model.setRootPath("")

        # Only show directories
        self.model.setFilter(
            self.model.filter()
            | self.model.Filter.NoDotAndDotDot
        )

        self.setModel(self.model)

        # Hide all columns except name
        for i in range(1, self.model.columnCount()):
            self.hideColumn(i)

        # Set root to home directory
        home = Path.home()
        self.setRootIndex(self.model.index(str(home.parent)))

        # Expand to current directory
        self.setCurrentIndex(self.model.index(str(Path.cwd())))

        # Connect selection
        self.clicked.connect(self._on_clicked)

    def _apply_styles(self) -> None:
        """Apply dark theme styles."""
        self.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                border: 1px solid #3c3c3c;
            }
            QTreeView::item {
                padding: 4px;
            }
            QTreeView::item:selected {
                background-color: #094771;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
        """)

    def _on_clicked(self, index) -> None:
        """Handle item click."""
        path = Path(self.model.filePath(index))
        if path.is_dir():
            self.path_selected.emit(path)
