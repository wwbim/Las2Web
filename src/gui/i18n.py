"""
Internationalization (i18n) manager for Las2Web.
Provides zero-restart instant toggling between Simplified Chinese and English.
"""

from typing import Callable
from PyQt6.QtCore import QObject, pyqtSignal

STRINGS = {
    "app_title": {
        "zh": "Las2Web - 极景点云格式转换工具 (Potree 2.x)",
        "en": "Las2Web - Minimal Point Cloud Converter (Potree 2.x)",
    },
    "app_subtitle": {
        "zh": "拖入点云直接就地转换并适配网页端 potree-core / BIM-Scope 查看",
        "en": "Drag & drop point clouds for instant in-place conversion for web potree-core & BIM-Scope",
    },
    "lang_toggle_btn": {
        "zh": "English",
        "en": "简体中文",
    },
    "drop_prompt_title": {
        "zh": "拖入点云文件立即开始转换",
        "en": "Drop Point Cloud Files to Convert Immediately",
    },
    "drop_prompt_sub": {
        "zh": "支持 .las, .laz 文件 • 拖入后将自动就地转换并在同级创建 _potree 目录",
        "en": "Supports .las, .laz • In-place conversion will create a _potree folder beside your file",
    },
    "drop_active_prompt": {
        "zh": "松开鼠标立即开始转换！",
        "en": "Release to start conversion immediately!",
    },
    "btn_select_file": {
        "zh": "或点击选择点云文件",
        "en": "Or Click to Select File",
    },
    "options_group": {
        "zh": "转换选项",
        "en": "Conversion Options",
    },
    "sampling_method": {
        "zh": "采样方式:",
        "en": "Sampling Method:",
    },
    "method_poisson": {
        "zh": "泊松盘采样 (Poisson - 均匀高品质，推荐)",
        "en": "Poisson Sampling (Uniform High Quality, Recommended)",
    },
    "method_random": {
        "zh": "随机采样 (Random - 速度较快)",
        "en": "Random Sampling (Faster)",
    },
    "encoding": {
        "zh": "数据编码:",
        "en": "Encoding:",
    },
    "encoding_uncompressed": {
        "zh": "未压缩 (UNCOMPRESSED - 兼容性最高)",
        "en": "Uncompressed (Default, Highest Compatibility)",
    },
    "encoding_brotli": {
        "zh": "Brotli 压缩 (体积更小，需浏览器解压支持)",
        "en": "Brotli Compressed (Smaller Size)",
    },
    "status_idle": {
        "zh": "就绪 - 等待拖入点云文件",
        "en": "Ready - Waiting for point cloud files",
    },
    "status_converting": {
        "zh": "正在转换中，请稍候...",
        "en": "Converting, please wait...",
    },
    "status_completed": {
        "zh": "转换已完成！",
        "en": "Conversion Completed Successfully!",
    },
    "status_failed": {
        "zh": "转换失败，请检查日志",
        "en": "Conversion Failed. Please inspect logs.",
    },
    "btn_open_folder": {
        "zh": "打开输出文件夹",
        "en": "Open Output Folder",
    },
    "btn_view_bim_scope": {
        "zh": "在 BIM-Scope 中查看 3D",
        "en": "View in BIM-Scope 3D",
    },
    "btn_cancel": {
        "zh": "取消转换",
        "en": "Cancel Conversion",
    },
    "log_title": {
        "zh": "运行日志",
        "en": "Process Logs",
    },
    "btn_clear_log": {
        "zh": "清空日志",
        "en": "Clear Logs",
    },
    "err_unsupported_file": {
        "zh": "不支持的文件格式！仅支持 .las 或 .laz 格式点云。",
        "en": "Unsupported file format! Only .las or .laz point cloud files are supported.",
    },
    "output_dir_label": {
        "zh": "输出位置:",
        "en": "Output Directory:",
    },
    "potree_engine_ready": {
        "zh": "PotreeConverter 引擎已就绪",
        "en": "PotreeConverter Engine Ready",
    },
    "file_dialog_filter": {
        "zh": "点云文件 (*.las *.laz);;所有文件 (*.*)",
        "en": "Point Cloud Files (*.las *.laz);;All Files (*.*)",
    },
}


class I18nManager(QObject):
    """Singleton language controller emitting signals upon locale toggle."""

    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._current_lang = "zh"  # Default to Simplified Chinese

    @property
    def current_lang(self) -> str:
        return self._current_lang

    def set_language(self, lang: str):
        if lang in ("zh", "en") and lang != self._current_lang:
            self._current_lang = lang
            self.language_changed.emit(self._current_lang)

    def toggle_language(self):
        new_lang = "en" if self._current_lang == "zh" else "zh"
        self.set_language(new_lang)

    def t(self, key: str) -> str:
        """Translate key into current language."""
        entry = STRINGS.get(key)
        if not entry:
            return key
        return entry.get(self._current_lang, entry.get("en", key))


# Global singleton instance
i18n = I18nManager()
