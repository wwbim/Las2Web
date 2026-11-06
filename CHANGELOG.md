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

> ⏱️ **项目累计总工时 / Total Active Development Time**: **1 小时 45 分钟 (1.75 Hours)**  
> 📅 **自然时间跨度 / Total Calendar Span**: **2026-11-05 22:30 至 2026-11-05 23:15**  
> 🔢 **累计交互与执行步骤 / Total Engineering Steps**: **110 Steps**  
> 🔄 **更新机制 / Update Policy**: 每次版本构建打包发布时基于真实日志自动重新精算累计工时。

### 阶段与每日工时分解 / Daily Breakdown
| 日期 / Date | 活跃开发时段 / Active Sprints | 有效工时 / Active Hours | 核心迭代内容 / Milestones |
| :--- | :--- | :---: | :--- |
| **2026-11-05** | 22:30~23:15 | 1h 45m (1.75h) | 项目初始化、PotreeConverter 集成、GUI 双语切换、非 ASCII 路径免疫、全隔离 %TEMP% 打包管线、客户机零运行时依赖与专属点云高程地形图标 / Initial setup, PotreeConverter integration, GUI bilingual toggle, non-ASCII immunity, isolated %TEMP% build pipeline, zero-dependency client bundling & custom terrain icon |

---

## [v1.2611061940] - 2026-11-06 19:40

### 修复独立可执行程序启动缺失 sys 模块导入 / Fix Missing sys Import in Standalone Exe
- **中文**:
  1. **修复 `NameError: name 'sys' is not defined`**: 修复了在 GUI 模式主窗口 `MainWindow.__init__` 动态定位打包图标路径（`sys._MEIPASS`）时遗漏 `import sys` 导致的启动崩溃问题。
  2. **网盘覆盖写入增强**: 优化 `build.py` 交付物分发步骤，采用 `shutil.copytree(..., dirs_exist_ok=True)` 杜绝 Google Drive 在覆写删除占用目录时的 `WinError 183` 竞争异常。
  3. **便携包全量更新**: 重新生成了 `Deliverables/Las2Web/` 及 `Deliverables/Las2Web_win64.zip`。
- **English**:
  1. **Fix `NameError: name 'sys' is not defined`**: Resolved the startup crash when resolving `sys._MEIPASS` icon path in `MainWindow.__init__` due to missing `import sys`.
  2. **Robust Overwrite on Cloud Drives**: Enhanced `build.py` deployment step with `shutil.copytree(..., dirs_exist_ok=True)` to eliminate Google Drive `WinError 183` folder locking during overwrites.
  3. **Deliverables Rebuilt**: Regenerated standalone application directory `Deliverables/Las2Web/` and portable archive `Deliverables/Las2Web_win64.zip`.

---

## [v1.2611052315] - 2026-11-05 23:15

### 独立绿色发行版与全隔离打包管线 / Isolated Temp Packaging & Standalone Deliverables
- **全隔离 %TEMP% 打包构建管线 / 100% Isolated %TEMP% Build Pipeline**
  - **中文**:
    1. **网盘同步锁死根治**: 为避免 Google Drive 等云盘实时同步高频锁死构建临时文件，`build.py` 将整个源码暂存、PyInstaller 编译过程、中间缓存（`workpath`、`specpath`、`distpath`）100% 迁移至本地系统 `%TEMP%` 中执行，构建完毕后自动清空临时工作区。
    2. **标准 Deliverables 输出**: 编译产物自动生成独立免安装便携目录 `Deliverables/Las2Web/` 以及便携分发压缩包 `Deliverables/Las2Web_win64.zip`（体积压缩至仅 49.6 MB）。
  - **English**:
    1. **Google Drive Sync Lock Elimination**: Migrates 100% of staging, PyInstaller compilation, and intermediate caches into the local Windows `%TEMP%` directory, eliminating cloud drive file lockups and sync bottlenecks.
    2. **Standard Deliverables Output**: Emits a self-contained portable folder (`Deliverables/Las2Web/`) and distribution archive (`Deliverables/Las2Web_win64.zip`, compressed to 49.6 MB).

- **目标客户机 100% 零依赖与零运行时要求 / Zero-Dependency Runtime Guarantee**
  - **中文**:
    1. **全套 VC++ 运行库内置打包**: 针对目标客户全新安装或无开发环境的 Windows 电脑，将 PotreeConverter 所需的 Visual C++ 2015-2022 核心运行时库（`msvcp140.dll`、`vcruntime140.dll`、`vcruntime140_1.dll`、`msvcp140_atomic_wait.dll`、`vcomp140.dll` 等）自动提取并打包进应用程序根目录及 `bin/` 目录，彻底杜绝客户机弹出“缺少 VCRUNTIME140.dll”报错。
    2. **纯绿色解压即用**: 客户机无需预装 Python、无需安装 VC++ Redistributable，双击即可直接秒启运行与点云转换。
  - **English**:
    1. **Bundled VC++ 2015-2022 Runtimes**: Bundles all necessary Visual C++ runtime DLLs (`msvcp140.dll`, `vcruntime140.dll`, `vcruntime140_1.dll`, `msvcp140_atomic_wait.dll`, `vcomp140.dll`, etc.) directly into the application distribution. Eliminates "missing VCRUNTIME140.dll" errors on clean Windows PCs.
    2. **100% Portable & Zero-Install**: Clients require no Python installation or administrative VC++ Redistributable setups.

- **专属点云高程地形图标 (las2web.ico) / Custom Point Cloud Elevation Terrain Icon**
  - **中文**:
    1. **高程渐变色调点云起伏地形**: 依据点云真彩色高程渲染规范，生成紫红（低海拔/基底）经过青色渐变至翠绿（山峰起伏）的三维空间起伏地形点云图徽，内嵌多分辨率图标 (`16x16` 至 `256x256`)，深度集成至可执行文件与 GUI 窗口。
  - **English**:
    1. **Hypsometric Tint Elevation Point Cloud Terrain**: Features a 3D undulating terrain surface rendered with point cloud elevation coloring ramping from magenta/purple to vivid green, bundled across resolutions (`16x16` to `256x256`) and integrated into `Las2Web.exe`.

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
