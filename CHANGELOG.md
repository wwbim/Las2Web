# 变更记录 / Changelog

本文档记录 Las2Web 从项目创建至今的所有正式版本演进与主要改动记录。  
This document records all formal version iterations and major changes of Las2Web since project initiation.

> **版本号命名规则 / Versioning Convention**:  
> - 主版本号固定为 `v1`（日常对外显示简写为 `v1`）；
> - 完整细版本号格式为 `v1.<YYMMDDHHMM>`，小数点后 10 位数字精确对应具体发布的年月日时分。  
> - Major version is fixed at `v1` (displayed as `v1` in everyday usage);  
> - Full sub-version follows `v1.<YYMMDDHHMM>`, where the 10-digit timestamp represents Year, Month, Day, Hour, Minute.

---

## 项目开发耗时统计 / Development Time Metrics

> ⏱️ **项目累计总工时 / Total Active Development Time**: **1 小时 15 分钟 (1.25 Hours)**  
> 📅 **自然时间跨度 / Total Calendar Span**: **2026-11-05 22:30 至 2026-11-05 23:45**  
> 🔢 **累计交互与执行步骤 / Total Engineering Steps**: **75 Steps**  
> 🔄 **更新机制 / Update Policy**: 每次版本构建打包发布时基于真实日志自动重新精算累计工时。

### 阶段与每日工时分解 / Daily Breakdown
| 日期 / Date | 活跃开发时段 / Active Sprints | 有效工时 / Active Hours | 核心迭代内容 / Milestones |
| :--- | :--- | :---: | :--- |
| **2026-11-05** | 22:30~23:45 | 1h 15m (1.25h) | 项目脚手架初始化、PotreeConverter 2.1.5 集成、极简拖拽就地转换 GUI、中英双语无感切换与 BIM-Scope 查看器无缝对接 / Scaffold setup, PotreeConverter integration, drag-and-drop in-place GUI, bilingual toggle & BIM-Scope integration |

---

## [v1.2611052250] - 2026-11-05 22:50

### 极景点云切片转换工具初版发布 / Initial Release of Las2Web Converter
- **PotreeConverter 2.1.5 引擎集成与自动下载 / PotreeConverter Engine & Auto-Downloader**
  - **中文**:
    1. **依赖自动检测与补全**: 启动时检测 `bin/PotreeConverter/` 是否存在可执行文件；若不存在，自动从官方 GitHub Releases 获取 Windows x64 预编译包并静默解压就位。
    2. **标准八叉树规范输出**: 默认生成符合 `potree-core` 与 Potree 2.x 规范的切片产物（`metadata.json`、`octree.bin`、`hierarchy.bin`）。
  - **English**:
    1. **Automatic Dependency Resolution**: Detects `PotreeConverter.exe` in local `bin/` upon startup and downloads the official Windows x64 release from GitHub if missing.
    2. **Potree 2.x Standard Output**: Generates clean octree data slices (`metadata.json`, `octree.bin`, `hierarchy.bin`) natively compatible with `potree-core`.

- **极简即拖即转 GUI 与就地另存 / Minimal Drag-and-Drop GUI & In-Place Conversion**
  - **中文**:
    1. **无感即拖即转**: 大尺寸交互放置区，支持拖入单个或多个 `.las` / `.laz` 点云文件，松开鼠标立即触发转换流水线。
    2. **就地另存策略**: 默认在原点云同级目录下创建 `<文件名>_potree` 文件夹输出数据，防止重名覆盖并免去繁琐的路径选择。
    3. **多线程异步执行**: 基于 `QThread` 封装底层进程调用，转换时界面保持 100% 顺畅响应，实时回传进度百分比与执行日志。
  - **English**:
    1. **Zero-Friction Drop & Convert**: Large responsive drop target; dropping `.las` or `.laz` files immediately starts background conversion.
    2. **In-Place Output Strategy**: Automatically generates a dedicated `<filename>_potree` folder alongside the source file.
    3. **Asynchronous Multi-Threading**: Encapsulates subprocesses within a non-blocking `QThread` worker, ensuring a responsive GUI with real-time progress and logs.

- **中英双语一键无感即时切换 / Zero-Restart Bilingual Localization**
  - **中文**:
    1. **即时国际化引擎**: 顶部右上角配备一键语言切换按钮，在简体中文与英文之间切换时无需重启应用，所有组件文字即刻动态重译刷新。
  - **English**:
    1. **Live Localization Engine**: Dedicated top-right language button toggling between Simplified Chinese and English in real time without restarting.

- **BIM-Scope 网页查看器无缝对接 / Seamless BIM-Scope Web Viewer Integration**
  - **中文**:
    1. **内置跨域与分块服务**: 转换完成后提供“在 BIM-Scope 中查看 3D”快捷键，自动拉起内置支持 CORS (`Access-Control-Allow-Origin: *`) 与 HTTP Range (`206 Partial Content`) 的微型本地静态服务，并在系统默认浏览器中唤起 `https://wwbim.github.io/BIM-Scope/?pointcloud=http://localhost:<PORT>/metadata.json`。
  - **English**:
    1. **Embedded CORS & Range Server**: Launches an internal static server supporting CORS headers and HTTP 206 Partial Content range requests, streaming local octree chunks directly into `https://wwbim.github.io/BIM-Scope/`.

- **无头 CLI 与独立打包支持 / Headless CLI & Standalone Packaging**
  - **中文**:
    1. 提供完整的 `cli.py` 命令行工具以及 `main.py` 统一分流入口。
    2. 编写 `build.py` 自动化打包脚本，使用 PyInstaller 输出脱机免安装的 Windows 可执行程序。
  - **English**:
    1. Comprehensive `cli.py` and unified `main.py` entry point.
    2. Standalone packaging script `build.py` via PyInstaller.
