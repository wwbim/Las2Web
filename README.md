# Las2Web ☁️

> 🌐 **配套网页端三维查看器 / Companion Web 3D Viewer**: [https://wwbim.github.io/BIM-Scope/](https://wwbim.github.io/BIM-Scope/)  
> 📦 **基于 PotreeConverter 驱动的极简点云切片转换工具**  
> **A Minimal Point Cloud Octree Converter Powered by PotreeConverter for Web Viewers**  
> 即拖即转 • 就地另存 • 纯本地运行 • 中英双语一键无感切换  
> Instant Drag-and-Drop • In-Place Output • 100% Local Execution • Zero-Restart Bilingual Toggle

---

## 🌟 核心特色 / Key Highlights

### 1. 🎯 极简即拖即转交互 / Instant Drag-and-Drop Workflow
- **中文**：无需层层点击繁琐的配置弹窗，直接将 `.las` 或 `.laz` 点云文件拖入主窗口即可瞬间启动转换流水线。
- **English**: No complicated nested configuration wizards. Simply drag and drop `.las` or `.laz` point cloud files into the window to trigger the conversion pipeline immediately.

### 2. 📁 自动就地另存 / In-Place Output Beside Source File
- **中文**：默认在源文件同级目录下自动创建 `<原文件名>_potree` 文件夹，避免同名文件覆盖，同时省去手动挑选输出目录的繁琐步骤。
- **English**: Automatically generates a dedicated `<filename>_potree` folder alongside the original point cloud file, preventing accidental overwrites while eliminating manual directory picking.

### 3. 🌐 网页端规范适配 (Potree 2.x & potree-core) / Full Web Potree 2.x Standard
- **中文**：底层集成官方 PotreeConverter 2.1.5，输出包含 `metadata.json`、`octree.bin` 和 `hierarchy.bin` 的标准八叉树切片结构，天然无缝支持 `potree-core` 与 WebGL 渲染管线。
- **English**: Powered by official PotreeConverter 2.1.5, emitting standard octree chunk structures (`metadata.json`, `octree.bin`, `hierarchy.bin`) natively tailored for `potree-core` and WebGL streaming pipelines.

### 4. 🔗 无缝对接 BIM-Scope 网页查看器 / Seamless BIM-Scope Web Viewer Integration
- **中文**：转换完成后一键唤起内置支持跨域（CORS）与分块（HTTP 206 Range）的轻量本地文件服务器，自动调用系统默认浏览器打开 [BIM-Scope](https://wwbim.github.io/BIM-Scope/) 查看器载入模型。
- **English**: One-click integration with [BIM-Scope](https://wwbim.github.io/BIM-Scope/). Automatically launches an internal CORS & HTTP Range streaming file server and opens the web viewer in your default browser.

### 5. 🌏 中英双语即时无感切换 / Zero-Restart Bilingual Localization
- **中文**：界面右上角提供显眼语言切换按钮，支持在简体中文与英文之间秒级切换，所有状态提示与配置文本即时更新，无需重启程序。
- **English**: Dedicated language toggle button in the top-right corner. Seamlessly switches between English and Simplified Chinese in real time without restarting the application.

### 6. 💻 双模式分流 (GUI & CLI) / Dual Mode: GUI & Headless CLI
- **中文**：双击运行无参启动现代化 PyQt6 桌面界面；在终端或脚本中传参调用即可直接以无头 CLI 模式运行，完美契合批处理自动化工作流。
- **English**: Launch without arguments to enjoy a clean, modern PyQt6 desktop GUI, or supply command-line arguments to execute high-throughput headless batch conversions.

---

## 🚀 快速上手 / Quick Start

### 运行环境 / Requirements
- **操作系统 / OS**: Windows 10 / 11 (x64)
- **Python**: Python 3.10+ (推荐 3.13)
- **依赖库 / Dependencies**: `PyQt6`

### 安装与启动 / Installation & Launch
```powershell
# 1. 克隆或下载本代码库 / Clone or download repository
git clone https://github.com/wwbim/Las2Web.git
cd Las2Web

# 2. 安装 Python 依赖 / Install dependencies
python -m pip install -r requirements.txt

# 3. 启动图形界面 / Launch GUI
python main.py
```

### 命令行 CLI 使用示例 / CLI Usage Examples
```powershell
# 1. 基础转换（默认就地输出至 scan_potree 目录）
# Basic conversion (in-place output to scan_potree/)
python cli.py "C:\path\to\scan.las"

# 2. 指定输出目录与随机采样算法
# Specify custom output path and random sampling
python cli.py "C:\path\to\scan.las" -o "D:\output\potree" -m random

# 3. 开启 Brotli 压缩编码并在转换后自动打开网页查看器预览
# Enable Brotli chunk compression and auto-launch web viewer
python cli.py "C:\path\to\scan.laz" --encoding BROTLI --preview
```

---

## 🛠️ 打包独立单文件 / Standalone Build
使用内置打包脚本即可将 Las2Web 与 PotreeConverter 引擎一键封装为无需 Python 环境的独立 Windows 绿色软件：
```powershell
python build.py
```
构建产物将输出至 `dist/Las2Web/` 目录下。

---

## 📄 开源与版权许可 / License
本项目遵循 MIT 协议开源。核心点云转换模块基于 [PotreeConverter](https://github.com/potree/PotreeConverter)（BSD 2-Clause 许可）。
This project is open-source under the MIT License. Underlying converter engine is powered by [PotreeConverter](https://github.com/potree/PotreeConverter) (BSD 2-Clause License).
