"""Search bar widget for NL-Find GUI."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class SearchBar(QWidget):
    """Search bar with input field and options."""

    search_requested = pyqtSignal(str, bool)  # query, use_llm

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the search bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "输入自然语言搜索，如：找出最近修改的Python文件..."
        )
        self.search_input.returnPressed.connect(self._on_search)
        layout.addWidget(self.search_input, stretch=1)

        # LLM toggle
        self.llm_checkbox = QCheckBox("Use LLM")
        self.llm_checkbox.setChecked(True)
        self.llm_checkbox.setToolTip("Use AI to parse natural language query")
        layout.addWidget(self.llm_checkbox)

        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._on_search)
        layout.addWidget(self.search_btn)

    def _apply_styles(self) -> None:
        """Apply styles to the search bar."""
        self.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 12px;
                color: #d4d4d4;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cc1;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QCheckBox {
                color: #d4d4d4;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)

    def _on_search(self) -> None:
        """Emit search request signal."""
        query = self.search_input.text()
        use_llm = self.llm_checkbox.isChecked()
        self.search_requested.emit(query, use_llm)

    def set_loading(self, loading: bool) -> None:
        """Set loading state.

        Args:
            loading: Whether search is in progress.
        """
        self.search_btn.setEnabled(not loading)
        self.search_input.setEnabled(not loading)
        self.search_btn.setText("Searching..." if loading else "Search")
