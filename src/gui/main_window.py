"""
Main Application Window for Las2Web.
Features instant in-place drag-and-drop conversion, zero-restart bilingual toggle,
and seamless integration with the online BIM-Scope 3D viewer.
"""

import os
import subprocess
from pathlib import Path
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QComboBox,
    QGroupBox,
    QPlainTextEdit,
    QFrame,
    QMessageBox,
)

from .i18n import i18n
from .drop_zone import DropZoneWidget
from ..core.converter import ConversionTask
from ..core.server import open_in_bim_scope


class ConversionWorker(QThread):
    """Background worker thread executing ConversionTask without blocking UI."""

    progress_updated = pyqtSignal(int, str)
    log_emitted = pyqtSignal(str)
    finished_result = pyqtSignal(dict)

    def __init__(self, task: ConversionTask):
        super().__init__()
        self.task = task

    def run(self):
        result = self.task.run(
            on_progress=lambda pct, msg: self.progress_updated.emit(pct, msg),
            on_log=lambda line: self.log_emitted.emit(line),
        )
        self.finished_result.emit(result)

    def cancel(self):
        self.task.cancel()


class MainWindow(QMainWindow):
    """Las2Web Main Window."""

    def __init__(self):
        super().__init__()
        self.worker: ConversionWorker | None = None
        self.current_output_dir: Path | None = None

        # Set Window Icon
        base_dir = (
            Path(sys._MEIPASS)
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
            else Path(__file__).resolve().parent.parent.parent
        )
        icon_path = base_dir / "assets" / "las2web.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.setWindowTitle(i18n.t("app_title"))
        self.resize(720, 680)
        self.setMinimumSize(600, 560)

        self._init_ui()
        i18n.language_changed.connect(lambda _: self.retranslate_ui())

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. Header with Title & Language Switcher
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_col = QVBoxLayout()
        self.label_app_title = QLabel(i18n.t("app_title"))
        self.label_app_title.setObjectName("appTitle")
        self.label_app_subtitle = QLabel(i18n.t("app_subtitle"))
        self.label_app_subtitle.setObjectName("appSubtitle")
        title_col.addWidget(self.label_app_title)
        title_col.addWidget(self.label_app_subtitle)
        header_layout.addLayout(title_col, stretch=1)

        self.btn_lang = QPushButton(i18n.t("lang_toggle_btn"))
        self.btn_lang.setObjectName("langButton")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.clicked.connect(self._toggle_language)
        header_layout.addWidget(self.btn_lang, alignment=Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(header_widget)

        # 2. Drag & Drop Zone
        self.drop_zone = DropZoneWidget(self)
        self.drop_zone.files_dropped.connect(self.start_conversion)
        main_layout.addWidget(self.drop_zone)

        # 3. Settings Card
        self.options_group = QGroupBox()
        options_layout = QHBoxLayout(self.options_group)
        options_layout.setContentsMargins(14, 14, 14, 14)
        options_layout.setSpacing(16)

        # Method
        self.label_method = QLabel()
        self.combo_method = QComboBox()
        self.combo_method.addItem("Poisson", "poisson")
        self.combo_method.addItem("Random", "random")
        options_layout.addWidget(self.label_method)
        options_layout.addWidget(self.combo_method)

        options_layout.addSpacing(20)

        # Encoding
        self.label_encoding = QLabel()
        self.combo_encoding = QComboBox()
        self.combo_encoding.addItem("UNCOMPRESSED", "UNCOMPRESSED")
        self.combo_encoding.addItem("BROTLI", "BROTLI")
        options_layout.addWidget(self.label_encoding)
        options_layout.addWidget(self.combo_encoding)

        options_layout.addStretch()
        main_layout.addWidget(self.options_group)

        # 4. Status, Progress & Completion Action Card
        self.status_card = QFrame()
        self.status_card.setObjectName("statusCard")
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setSpacing(8)

        status_header_row = QHBoxLayout()
        self.label_status = QLabel(i18n.t("status_idle"))
        self.label_status.setObjectName("statusLabel")
        status_header_row.addWidget(self.label_status, stretch=1)

        self.btn_cancel = QPushButton(i18n.t("btn_cancel"))
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self._cancel_conversion)
        self.btn_cancel.setVisible(False)
        status_header_row.addWidget(self.btn_cancel)
        status_layout.addLayout(status_header_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        status_layout.addWidget(self.progress_bar)

        self.label_output_dir = QLabel()
        self.label_output_dir.setStyleSheet("color: #64748b; font-size: 11px;")
        status_layout.addWidget(self.label_output_dir)

        # Completion Action Buttons
        self.actions_row = QHBoxLayout()
        self.actions_row.setSpacing(10)

        self.btn_open_folder = QPushButton()
        self.btn_open_folder.setObjectName("btnOpenFolder")
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.clicked.connect(self._open_output_folder)
        self.btn_open_folder.setVisible(False)
        self.actions_row.addWidget(self.btn_open_folder)

        self.btn_bim_scope = QPushButton()
        self.btn_bim_scope.setObjectName("btnBIMScope")
        self.btn_bim_scope.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bim_scope.clicked.connect(self._open_in_bim_scope)
        self.btn_bim_scope.setVisible(False)
        self.actions_row.addWidget(self.btn_bim_scope)

        self.actions_row.addStretch()
        status_layout.addLayout(self.actions_row)
        main_layout.addWidget(self.status_card)

        # 5. Log Console
        log_header = QHBoxLayout()
        self.label_log = QLabel(i18n.t("log_title"))
        self.label_log.setStyleSheet("font-weight: 600; color: #475569;")
        log_header.addWidget(self.label_log, stretch=1)

        self.btn_clear_log = QPushButton(i18n.t("btn_clear_log"))
        self.btn_clear_log.setStyleSheet(
            "background: transparent; border: none; color: #64748b; font-size: 11px; text-decoration: underline;"
        )
        self.btn_clear_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_log.clicked.connect(self._clear_logs)
        log_header.addWidget(self.btn_clear_log)
        main_layout.addLayout(log_header)

        self.log_console = QPlainTextEdit()
        self.log_console.setObjectName("logConsole")
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(150)
        main_layout.addWidget(self.log_console)

        self.retranslate_ui()

    def _toggle_language(self):
        i18n.toggle_language()

    def retranslate_ui(self):
        """Update all text components across the window."""
        self.setWindowTitle(i18n.t("app_title"))
        self.label_app_title.setText(i18n.t("app_title"))
        self.label_app_subtitle.setText(i18n.t("app_subtitle"))
        self.btn_lang.setText(i18n.t("lang_toggle_btn"))

        self.options_group.setTitle(i18n.t("options_group"))
        self.label_method.setText(i18n.t("sampling_method"))
        self.label_encoding.setText(i18n.t("encoding"))

        self.combo_method.setItemText(0, i18n.t("method_poisson"))
        self.combo_method.setItemText(1, i18n.t("method_random"))
        self.combo_encoding.setItemText(0, i18n.t("encoding_uncompressed"))
        self.combo_encoding.setItemText(1, i18n.t("encoding_brotli"))

        self.btn_cancel.setText(i18n.t("btn_cancel"))
        self.btn_open_folder.setText(i18n.t("btn_open_folder"))
        self.btn_bim_scope.setText(i18n.t("btn_view_bim_scope"))
        self.label_log.setText(i18n.t("log_title"))
        self.btn_clear_log.setText(i18n.t("btn_clear_log"))

        if not self.worker:
            self.label_status.setText(i18n.t("status_idle"))

    def start_conversion(self, file_paths: list[str]):
        """Triggered immediately when files are dropped or selected."""
        if not file_paths:
            return

        if self.worker and self.worker.isRunning():
            QMessageBox.warning(
                self,
                "Warning",
                "A conversion task is already in progress. Please wait or cancel.",
            )
            return

        # Take first file for immediate conversion
        file_path = file_paths[0]
        method = self.combo_method.currentData() or "poisson"
        encoding = self.combo_encoding.currentData() or "UNCOMPRESSED"

        task = ConversionTask(
            input_file=file_path,
            method=method,
            encoding=encoding,
        )

        self.current_output_dir = task.output_dir
        self.label_output_dir.setText(
            f"{i18n.t('output_dir_label')} {self.current_output_dir}"
        )

        self.label_status.setText(i18n.t("status_converting"))
        self.label_status.setStyleSheet("color: #0284c7; font-weight: 600;")
        self.progress_bar.setValue(0)
        self.btn_cancel.setVisible(True)
        self.btn_open_folder.setVisible(False)
        self.btn_bim_scope.setVisible(False)

        self.log_console.appendPlainText(f"\n--- New Task: {file_path} ---")

        self.worker = ConversionWorker(task)
        self.worker.progress_updated.connect(self._on_worker_progress)
        self.worker.log_emitted.connect(self._on_worker_log)
        self.worker.finished_result.connect(self._on_worker_finished)
        self.worker.start()

    def _on_worker_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)

    def _on_worker_log(self, line: str):
        self.log_console.appendPlainText(line)
        # Auto scroll to bottom
        sb = self.log_console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_worker_finished(self, result: dict):
        self.btn_cancel.setVisible(False)
        self.worker = None

        if result.get("success"):
            self.label_status.setText(
                f"✅ {i18n.t('status_completed')} ({result.get('elapsed_seconds', 0):.1f}s)"
            )
            self.label_status.setStyleSheet("color: #16a34a; font-weight: 700;")
            self.progress_bar.setValue(100)
            self.btn_open_folder.setVisible(True)
            self.btn_bim_scope.setVisible(True)
        else:
            err = result.get("error", "Unknown error")
            self.label_status.setText(f"❌ {i18n.t('status_failed')}")
            self.label_status.setStyleSheet("color: #ef4444; font-weight: 700;")
            self.log_console.appendPlainText(f"[ERROR] {err}")

    def _cancel_conversion(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.btn_cancel.setEnabled(False)

    def _open_output_folder(self):
        if self.current_output_dir and self.current_output_dir.exists():
            os.startfile(str(self.current_output_dir))

    def _open_in_bim_scope(self):
        if self.current_output_dir and self.current_output_dir.exists():
            url = open_in_bim_scope(self.current_output_dir)
            self.log_console.appendPlainText(f"[BIM-Scope] Opened: {url}")

    def _clear_logs(self):
        self.log_console.clear()
