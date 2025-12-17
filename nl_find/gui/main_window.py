"""Main window for NL-Find GUI."""

import sys
from pathlib import Path

from loguru import logger
from PyQt6.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from nl_find.config.settings import get_settings
from nl_find.core.executor import SearchExecutor
from nl_find.core.models import SearchParams, SearchQuery, SearchResult
from nl_find.gui.widgets.dir_tree import DirectoryTree
from nl_find.gui.widgets.file_list import FileListWidget
from nl_find.gui.widgets.search_bar import SearchBar


class SearchWorker(QThread):
    """Background worker for executing searches."""

    finished = pyqtSignal(SearchResult)
    error = pyqtSignal(str)

    def __init__(self, params: SearchParams):
        super().__init__()
        self.params = params

    def run(self) -> None:
        """Execute the search in background."""
        try:
            executor = SearchExecutor()
            result = executor.execute(self.params)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window with file manager layout."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NL-Find - Natural Language File Search")
        self.setMinimumSize(1000, 600)

        self.settings = get_settings()
        self.current_path = Path.cwd()
        self.search_worker: SearchWorker | None = None

        self._setup_ui()
        self._connect_signals()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Search bar at top
        self.search_bar = SearchBar()
        main_layout.addWidget(self.search_bar)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Directory tree on the left
        self.dir_tree = DirectoryTree()
        splitter.addWidget(self.dir_tree)

        # File list on the right
        self.file_list = FileListWidget()
        splitter.addWidget(self.file_list)

        # Set initial splitter sizes (1:3 ratio)
        splitter.setSizes([250, 750])
        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.search_bar.search_requested.connect(self._on_search)
        self.dir_tree.path_selected.connect(self._on_path_selected)
        self.file_list.file_double_clicked.connect(self._on_file_double_clicked)

    def _apply_styles(self) -> None:
        """Apply dark theme styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: "Segoe UI", sans-serif;
                font-size: 13px;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
            }
            QStatusBar {
                background-color: #252526;
                color: #808080;
                border-top: 1px solid #3c3c3c;
            }
        """)

    def _on_search(self, query_text: str, use_llm: bool) -> None:
        """Handle search request.

        Args:
            query_text: Search query text.
            use_llm: Whether to use LLM for parsing.
        """
        if not query_text.strip():
            return

        self.status_bar.showMessage("Searching...")
        self.search_bar.set_loading(True)

        if use_llm:
            # Use LLM parsing (requires API key)
            try:
                from nl_find.core.llm_parser import LLMParser

                parser = LLMParser()
                search_query = parser.parse(query_text)
                search_query.path = self.current_path
            except Exception as e:
                QMessageBox.warning(self, "LLM Error", str(e))
                self.search_bar.set_loading(False)
                self.status_bar.showMessage("Search failed")
                return
        else:
            # Direct pattern search
            search_query = SearchQuery(
                path=self.current_path,
                pattern=query_text,
                recursive=True,
            )

        params = SearchParams(query=search_query, limit=self.settings.search.max_results)

        # Run search in background
        self.search_worker = SearchWorker(params)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.error.connect(self._on_search_error)
        self.search_worker.start()

    def _on_search_finished(self, result: SearchResult) -> None:
        """Handle search completion.

        Args:
            result: Search result.
        """
        self.search_bar.set_loading(False)
        self.file_list.set_files(result.files)
        self.status_bar.showMessage(
            f"Found {result.total_count} files in {result.search_time:.2f}s"
        )

    def _on_search_error(self, error_msg: str) -> None:
        """Handle search error.

        Args:
            error_msg: Error message.
        """
        self.search_bar.set_loading(False)
        self.status_bar.showMessage(f"Error: {error_msg}")
        QMessageBox.warning(self, "Search Error", error_msg)

    def _on_path_selected(self, path: Path) -> None:
        """Handle directory selection from tree.

        Args:
            path: Selected directory path.
        """
        self.current_path = path
        self.status_bar.showMessage(f"Current: {path}")

    def _on_file_double_clicked(self, path: Path) -> None:
        """Handle file double click - open with default application.

        Args:
            path: Path to the file to open.
        """
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


def main() -> None:
    """Run the GUI application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
