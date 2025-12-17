"""File list widget for NL-Find GUI."""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
)

from src.core.models import FileInfo


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


class FileListWidget(QTableWidget):
    """Table widget displaying file search results."""

    file_double_clicked = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: list[FileInfo] = []
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the table UI."""
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Path"])

        # Configure header
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(1, 80)
        header.resizeSection(2, 140)

        # Configure selection
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Enable sorting
        self.setSortingEnabled(True)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Double click
        self.doubleClicked.connect(self._on_double_click)

    def _apply_styles(self) -> None:
        """Apply dark theme styles."""
        self.setStyleSheet("""
            QTableWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                gridline-color: #3c3c3c;
            }
            QTableWidget::item {
                padding: 4px 8px;
            }
            QTableWidget::item:selected {
                background-color: #094771;
            }
            QTableWidget::item:hover {
                background-color: #2a2d2e;
            }
            QHeaderView::section {
                background-color: #333;
                color: #d4d4d4;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #3c3c3c;
                border-right: 1px solid #3c3c3c;
            }
        """)

    def set_files(self, files: list[FileInfo]) -> None:
        """Update the file list.

        Args:
            files: List of FileInfo objects to display.
        """
        self._files = files
        self.setRowCount(len(files))

        for row, file in enumerate(files):
            self.setItem(row, 0, QTableWidgetItem(file.name))
            self.setItem(row, 1, QTableWidgetItem(format_size(file.size)))
            self.setItem(row, 2, QTableWidgetItem(
                file.modified.strftime("%Y-%m-%d %H:%M")
            ))
            self.setItem(row, 3, QTableWidgetItem(str(file.path.parent)))

    def _show_context_menu(self, pos) -> None:
        """Show right-click context menu."""
        menu = QMenu(self)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self._open_selected)
        menu.addAction(open_action)

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self._open_folder)
        menu.addAction(open_folder_action)

        menu.addSeparator()

        copy_path_action = QAction("Copy Path", self)
        copy_path_action.triggered.connect(self._copy_path)
        menu.addAction(copy_path_action)

        menu.exec(self.mapToGlobal(pos))

    def _get_selected_file(self) -> Optional[FileInfo]:
        """Get the currently selected file."""
        row = self.currentRow()
        if 0 <= row < len(self._files):
            return self._files[row]
        return None

    def _on_double_click(self) -> None:
        """Handle double click on file."""
        file = self._get_selected_file()
        if file:
            self.file_double_clicked.emit(file.path)

    def _open_selected(self) -> None:
        """Open selected file with default application."""
        import os

        file = self._get_selected_file()
        if file:
            os.startfile(file.path)

    def _open_folder(self) -> None:
        """Open containing folder in file explorer."""
        import subprocess

        file = self._get_selected_file()
        if file:
            subprocess.run(["explorer", "/select,", str(file.path)])

    def _copy_path(self) -> None:
        """Copy file path to clipboard."""
        from PyQt6.QtWidgets import QApplication

        file = self._get_selected_file()
        if file:
            clipboard = QApplication.clipboard()
            clipboard.setText(str(file.path))
