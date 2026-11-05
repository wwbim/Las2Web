"""
Drag and Drop zone widget with visual hover state and instant conversion trigger.
"""

from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
)

from .i18n import i18n
from ..core.converter import is_supported_file, SUPPORTED_EXTENSIONS


class DropZoneWidget(QFrame):
    """Visual drop target for point cloud files."""

    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        # Large Icon
        self.icon_label = QLabel("☁️")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 42px;")
        layout.addWidget(self.icon_label)

        # Title
        self.title_label = QLabel()
        self.title_label.setObjectName("dropTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("dropSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle_label)

        # Browse button
        self.btn_select = QPushButton()
        self.btn_select.setObjectName("btnSelectFile")
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.clicked.connect(self._on_browse_click)
        layout.addWidget(self.btn_select, alignment=Qt.AlignmentFlag.AlignCenter)

        self.retranslate_ui()
        i18n.language_changed.connect(lambda _: self.retranslate_ui())

    def retranslate_ui(self):
        """Update strings on locale change."""
        self.title_label.setText(i18n.t("drop_prompt_title"))
        self.subtitle_label.setText(i18n.t("drop_prompt_sub"))
        self.btn_select.setText(i18n.t("btn_select_file"))

    def _on_browse_click(self):
        """File open dialog fallback."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            i18n.t("drop_prompt_title"),
            "",
            i18n.t("file_dialog_filter"),
        )
        if files:
            valid_files = [f for f in files if is_supported_file(f)]
            if valid_files:
                self.files_dropped.emit(valid_files)

    def dragEnterEvent(self, event):
        """Check if dragged content contains valid point cloud files."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            has_supported = any(
                Path(u.toLocalFile()).suffix.lower() in SUPPORTED_EXTENSIONS
                for u in urls
                if u.isLocalFile()
            )
            if has_supported:
                self.setProperty("hover", True)
                self.style().polish(self)
                self.title_label.setText(i18n.t("drop_active_prompt"))
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        """Reset hover styling."""
        self.setProperty("hover", False)
        self.style().polish(self)
        self.retranslate_ui()
        event.accept()

    def dropEvent(self, event):
        """Handle dropped files and forward to conversion queue."""
        self.setProperty("hover", False)
        self.style().polish(self)
        self.retranslate_ui()

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            paths = []
            for u in urls:
                if u.isLocalFile():
                    p = Path(u.toLocalFile())
                    if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
                        paths.append(str(p))

            if paths:
                event.acceptProposedAction()
                self.files_dropped.emit(paths)
                return

        event.ignore()
