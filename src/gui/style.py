"""
Modern, flat UI stylesheet (QSS) for Las2Web.
"""

APP_STYLESHEET = """
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    font-size: 13px;
}

/* Header */
#headerWidget {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 10px 16px;
}

#appTitle {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
}

#appSubtitle {
    font-size: 12px;
    color: #64748b;
}

#langButton {
    background-color: #f1f5f9;
    color: #0284c7;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}

#langButton:hover {
    background-color: #e0f2fe;
    border-color: #7dd3fc;
    color: #0369a1;
}

/* Drop Zone */
#dropZone {
    background-color: #ffffff;
    border: 2px dashed #94a3b8;
    border-radius: 12px;
    min-height: 180px;
}

#dropZone.hover {
    background-color: #f0fdf4;
    border: 2px dashed #22c55e;
}

#dropTitle {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
}

#dropSubtitle {
    font-size: 12px;
    color: #64748b;
}

#btnSelectFile {
    background-color: #0284c7;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
}

#btnSelectFile:hover {
    background-color: #0369a1;
}

/* Options Card */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: #334155;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
}

QComboBox {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 10px;
    min-height: 26px;
}

QComboBox:hover {
    border-color: #94a3b8;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

/* Status & Progress */
#statusCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
}

#statusLabel {
    font-weight: 600;
    font-size: 14px;
    color: #0f172a;
}

QProgressBar {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #f1f5f9;
    text-align: center;
    height: 18px;
    font-weight: 600;
    color: #1e293b;
    font-size: 11px;
}

QProgressBar::chunk {
    background-color: #0284c7;
    border-radius: 5px;
}

/* Action Buttons */
#btnOpenFolder {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

#btnOpenFolder:hover {
    background-color: #e2e8f0;
    color: #0f172a;
}

#btnBIMScope {
    background-color: #16a34a;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
}

#btnBIMScope:hover {
    background-color: #15803d;
}

#btnCancel {
    background-color: #ef4444;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

#btnCancel:hover {
    background-color: #dc2626;
}

/* Console Log */
QPlainTextEdit#logConsole {
    background-color: #0f172a;
    color: #38bdf8;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 8px;
}
"""
