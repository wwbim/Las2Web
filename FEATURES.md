# 功能特性清单 / Features Matrix

本文档详细列出 Las2Web 点云转换工具的所有功能特性、技术规范、参数矩阵以及交互体验设计。  
This document provides a comprehensive inventory of all functional capabilities, technical specifications, parameter matrices, and UX designs in Las2Web.

---

## 📋 功能清单一览 / Feature Inventory

| 功能模块 / Module | 中文功能描述 / Chinese Description | 英文功能描述 / English Description | 状态 / Status |
| :--- | :--- | :--- | :---: |
| **拖拽投放区 / Drop Zone** | 支持将单个或多个点云文件直接拖入主窗口，具备悬停高亮动画反馈 | Accepts single or multiple point cloud files with responsive hover animations | ✅ 已实现 / Ready |
| **就地转换 / In-Place Output** | 自动在输入文件同级目录下创建 `<文件名>_potree` 文件夹并生成切片 | Generates `<stem>_potree` directory beside the source file automatically | ✅ 已实现 / Ready |
| **Potree 2.x 输出** | 输出标准 `metadata.json`、`octree.bin` 与 `hierarchy.bin`，兼容 `potree-core` | Outputs standard `metadata.json`, `octree.bin`, and `hierarchy.bin` for `potree-core` | ✅ 已实现 / Ready |
| **双语即时切换 / i18n Toggle** | 顶部右上角一键切换简体中文与英文，无需重启应用，所有文本实时刷新 | Real-time toggle between Simplified Chinese and English without app restart | ✅ 已实现 / Ready |
| **BIM-Scope 查看对接** | 启动内置微型 CORS & HTTP Range 文件服务，一键调起浏览器加载查看 | Spins up local CORS & Range file server and opens BIM-Scope web viewer | ✅ 已实现 / Ready |
| **后台多线程并发 / Async Threading** | 采用 `QThread` 封装子进程调用，转换过程中 GUI 界面保持 100% 顺滑响应 | Subprocess wrapped in `QThread`; GUI remains 100% responsive without UI freezing | ✅ 已实现 / Ready |
| **实时进度与日志 / Progress & Logs** | 实时估算解析转换进度百分比，提供控制台日志窗口与一键清空功能 | Streams percentage progress and detailed PotreeConverter console logs | ✅ 已实现 / Ready |
| **任务取消 / Cancel Support** | 随时安全中止正在执行的底层转换子进程 | Safely terminates underlying PotreeConverter subprocess on demand | ✅ 已实现 / Ready |
| **无头 CLI 模式 / Headless CLI** | 完整的命令行接口，支持脚本批量转换与自动化流水线集成 | Full CLI interface for automation scripts and batch point cloud processing | ✅ 已实现 / Ready |
| **依赖自检自下 / Auto-Dependency** | 启动时自动检查并在初次缺失时自动下载 PotreeConverter 官方二进制包 | Automatically detects and downloads PotreeConverter 2.1.5 binary on demand | ✅ 已实现 / Ready |
| **单文件打包 / Standalone Packaging** | 包含 PyInstaller 打包脚本，可一键输出脱离 Python 环境的独立绿色软件 | Includes PyInstaller build script for creating a self-contained Windows executable | ✅ 已实现 / Ready |

---

## 🎛️ 转换参数与编码对照 / Parameter & Encoding Matrix

### 1. 采样算法 / Point Sampling Methods
- **Poisson 泊松盘采样 (默认 / Default)**:
  - **中文**：生成均匀分布的下采样点云切片，空间结构保真度高，视觉效果最佳。
  - **English**: Generates uniform Poisson-disk sub-sampled point distributions; delivers optimal visual fidelity.
- **Poisson Average 泊松均值采样**:
  - **中文**：对邻近点进行属性平均计算后再行采样，平滑噪点。
  - **English**: Averages point attributes within local Poisson neighborhoods before sampling.
- **Random 随机采样**:
  - **中文**：基于随机概率抽取点云，计算速度极快，适合超大体量点云快速预览。
  - **English**: Randomly selects points based on probability; maximizes conversion throughput.

### 2. 八叉树数据编码 / Chunk Data Encoding
- **UNCOMPRESSED 未压缩 (默认 / Default)**:
  - **中文**：直接输出原始二进制点属性数据流，浏览器端无需额外解压即可极速渲染。
  - **English**: Raw uncompressed binary point stream; enables instant zero-overhead web parsing.
- **BROTLI 压缩**:
  - **中文**：使用 Brotli 强力压缩算法压缩数据块，显著缩小磁盘占用与网络传输体积。
  - **English**: Compresses octree chunks using Brotli to drastically decrease storage footprint and network bandwidth.

---

## 🖥️ 命令行 CLI 参数全量参考 / Complete CLI Reference

```
usage: cli.py [-h] [-o OUTPUT] [-m {poisson,poisson_average,random}]
              [--encoding {UNCOMPRESSED,BROTLI}] [--preview]
              input

Las2Web - Minimal Point Cloud to Potree 2.x Converter CLI

positional arguments:
  input                 Path to point cloud input file (.las or .laz)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Target output directory (defaults to <filename>_potree beside input)
  -m {poisson,poisson_average,random}, --method {poisson,poisson_average,random}
                        Point sampling method (default: poisson)
  --encoding {UNCOMPRESSED,BROTLI}
                        Octree binary chunk encoding (default: UNCOMPRESSED)
  --preview             Automatically launch local CORS server and open BIM-Scope 3D viewer upon completion
```
