# ComfyUI Dynamic Batch Image Saver

[![GitHub stars](https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![GitHub forks](https://img.shields.io/github/forks/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-节点-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

A powerful ComfyUI custom node for dynamic batch image saving with custom save names and automatic organization.

一个支持动态数量图片批量保存的 ComfyUI 扩展节点。

## 🆕 New V2 Modular Design / 新V2模块化设计

**2025年11月更新**：新增模块化设计，支持更灵活的图片收集和保存！

### V2 新功能
- ✅ **完全解耦架构**：图片和文本都可独立模块化
- ✅ **Image Batch子节点**：收集1-5张图片（可选输入）
- ✅ **Text Batch子节点**：接收文件内容（file_content + file_name）
- ✅ **BatchImageSaverV2主节点**：接收多个图片+文本批次，统一保存
- ✅ **无限扩展**：通过复制子节点支持任意数量图片和文本文件
- ✅ **智能重新编号**：全局统一编号，保持顺序
- ✅ **灵活组合**：每个图片批次可配对对应的文本批次
- ✅ **向后兼容**：保留原始版本供选择使用

## ✨ Key Features / 主要功能

### V2 模块化版本
- ✅ **完全解耦**：Image Batch + Text Batch + BatchImageSaverV2
- ✅ **可选输入**：图片和文本子节点都支持可选输入
- ✅ **多批次支持**：主节点可接收多个图片+文本批次
- ✅ **灵活配对**：每个图片批次可配对对应的文本批次
- ✅ **5字段文本**：Text Batch支持5个通用文本字段（text_1到text_5）
- ✅ **动态扩展**：需要更多内容只需复制相应子节点
- ✅ **统一编号**：自动重新编号，保持全局顺序
- ✅ **简洁设计**：主节点移除统一文本输入，完全依赖Text Batch

### 原始版本功能
- ✅ **动态输入**：支持 1-10 张图片的动态输入
- ✅ **独立保存名称**：每张图片可以设置单独的保存名称
- ✅ **文本描述**：可输入关于图片的描述信息，保存到文件
- ✅ **Prompt 保存**：自动保存 ComfyUI 的 Prompt 文本到独立文件
- ✅ **文本保存**：输出文本信息同时保存到 save_info.txt 文件
- ✅ **自动分组**：每次运行自动创建时间戳文件夹
- ✅ **详细文本输出**：输出包含所有图片信息的文本
- ✅ **JSON 元数据**：自动保存完整的元数据信息
- ✅ **灵活路径**：支持自定义输出文件夹路径
- ✅ **启用控制**：可通过 enabled 参数控制节点是否启用

## 节点参数

### 输入参数

- **input_count** (必需): 图片数量（1-5）
- **image_1** (必需): 第一张图片
- **save_name_1** (必需): 第一张图片的保存名称（默认："image"）
- **output_folder** (必需): 输出文件夹名称（默认："batch_saves"）
- **enabled** (可选): 是否启用此节点（默认：true）
- **image_2 到 image_5** (可选): 更多图片输入（根据 input_count 自动扩展）
- **save_name_2 到 save_name_5** (可选): 对应的保存名称
- **description** (可选): 文本描述，会保存到文件中

### 输出结果

- **save_info**: 文本信息（任务ID、时间戳、输出路径、描述信息、所有图片信息）

## 文件组织结构

```
output/
├── batch_saves/                    # 父文件夹（可自定义）
│   ├── task_20241109_143022/       # 任务文件夹（每次运行创建）
│   │   ├── 封面_01.png             # 保存名称_序号.png 格式
│   │   ├── 细节_02.png
│   │   ├── 对比_03.png
│   │   ├── 局部_04.png
│   │   ├── 全图_05.png
│   │   ├── prompt.txt              # ComfyUI Prompt 文本（如果有）
│   │   ├── metadata.json           # 基本元数据（包含格式化文本）
│   │   └── workflow.json           # 完整工作流文件（可直接加载）
│   ├── task_20241109_144035/
│   │   ├── 原图_01.png
│   │   ├── 处理图_02.png
│   │   ├── metadata.json
│   │   └── workflow_metadata.json
│   └── ...
```

## 使用示例

### V2 模块化版本使用方法

#### 基本工作流程（仅图片）

1. **添加图片收集器**：在工作流中添加 `Image Collector` 节点
2. **连接图片**：将1-5张图片连接到子节点的 `image_1` 到 `image_5` 输入
3. **设置保存名称**：为每张图片设置对应的保存名称
4. **添加主节点**：添加 `Dynamic Batch Image Saver (V2)` 节点
5. **连接图片批次**：将子节点的 `image_batch` 输出连接到主节点的 `batch_1` 输入
6. **运行工作流**

> **注意**：如果需要文本信息，必须添加 `Text Collector` 节点并连接到主节点的 `text_batch_1` 输入。

#### 高级工作流程（图片+对应文本）

1. **添加图片收集器**：添加 `Image Collector` 节点（如 Collector A）
2. **添加文本收集器**：添加 `Text Collector` 节点（如 Text A）
3. **配置内容**：
   - 在 Collector A 中连接图片并设置保存名称
   - 在 Text A 中设置5个通用文本字段（text_1到text_5，可输入任意内容）
4. **添加主节点**：添加 `Dynamic Batch Image Saver (V2)` 节点
5. **连接批次**：
   - 将 Collector A 的 `image_batch` 连接到主节点的 `batch_1`
   - 将 Text A 的 `text_batch` 连接到主节点的 `text_batch_1`
6. **运行工作流**

> **注意**：BatchImageSaverV2主节点不再有统一的文本输入字段，所有文本内容必须通过TextCollector提供。

#### 混合工作流程（多组图片+文本）

```
[图片1-5] → [ImageCollector A] → batch_1 → \
[文本A] → [TextCollector A] → text_batch_1 →  → [BatchImageSaverV2]
[图片6-7] → [ImageCollector B] → batch_2 → /
[文本B] → [TextCollector B] → text_batch_2 → /

或者混合模式：

[图片1-5] → [ImageCollector A] → batch_1 → \
                                     → [BatchImageSaverV2] ← 统一文本
[图片6-7] → [ImageCollector B] → batch_2 → /
```

#### 扩展示例（15张图片）

```
[图片1-5] → [Image Batch A] → batch_1 → \
[图片6-10] → [Image Batch B] → batch_2 → → [BatchImageSaverV2] → 保存
[图片11-15] → [Image Batch C] → batch_3 → /
```

#### 灵活组合（7张图片）

```
[图片1-5] → [Image Batch A] → batch_1 → \
[图片6-7] → [Image Batch B] → batch_2 → → [BatchImageSaverV2] → 保存
```

### 原始版本使用方法

#### 基本用法

1. 设置 **input_count** 为需要的图片数量 (1-5)
2. 依次连接相应数量的图片到 `image_1` 到 `image_N`
3. 设置对应的保存名称，如：`封面`、`细节`、`对比`、`局部`、`全图`
4. （可选）在 **description** 框中输入关于这些图片的描述信息
5. （可选）通过 **enabled** 参数控制节点是否启用
6. 运行工作流

### V2版本输出示例

```
任务ID: task_20241129_143022
时间戳: 20241129_143022
输出目录: /output/batch_saves/task_20241129_143022
图片总数: 7

分组统计:
  group_A: 5 张图片
  group_B: 2 张图片

文本信息:
标题: 测试标题
描述: 测试描述
Prompt: 测试prompt

保存的图片:
  [01] 封面_01.png (来源: group_A)
  [02] 细节_02.png (来源: group_A)
  [03] 对比_03.png (来源: group_A)
  [04] 局部_04.png (来源: group_A)
  [05] 全图_05.png (来源: group_A)
  [06] 特写_06.png (来源: group_B)
  [07] 放大_07.png (来源: group_B)
```

### 原始版本输出示例

```
任务ID: task_20241109_143022
时间戳: 20241109_143022
输出目录: /output/batch_saves/task_20241109_143022
图片数量: 5

描述信息:
这是一次测试的图片保存任务，包含封面、细节、对比、局部和全图。

保存的图片:
  [1] 封面_01.png (保存名称: 封面)
  [2] 细节_02.png (保存名称: 细节)
  [3] 对比_03.png (保存名称: 对比)
  [4] 局部_04.png (保存名称: 局部)
  [5] 全图_05.png (保存名称: 全图)
```

### Prompt 文本示例 (prompt.txt)

```
=== ComfyUI Prompt ===

Positive Prompt:
a beautiful cat, sitting on a chair, soft lighting, high quality

Negative Prompt:
blurry, low quality, distorted

=== Full Prompt JSON ===
{
  "3": {
    "inputs": {
      "text": "a beautiful cat, sitting on a chair, soft lighting, high quality",
      "clip": ["4", 0]
    },
    "class_type": "CLIPTextEncode"
  }
}
```

## 🚀 Installation / 安装方法

### Method 1: Clone Repository / 方式一：克隆仓库
```bash
# Clone to your ComfyUI custom_nodes directory / 克隆到 ComfyUI 的 custom_nodes 目录
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/HuangYuChuh/ComfyUI_Image_Anything.git
```

### Method 2: Download ZIP / 方式二：下载 ZIP
1. Download the ZIP from the repository / 从仓库下载 ZIP 文件
2. Extract to ComfyUI's `custom_nodes` directory / 解压到 ComfyUI 的 `custom_nodes` 目录
3. Restart ComfyUI / 重启 ComfyUI

### Method 3: ComfyUI Manager (Recommended) / 方式三：ComfyUI 管理器（推荐）
1. Open ComfyUI Manager in your browser / 在浏览器中打开 ComfyUI 管理器
2. Search for "ComfyUI_Image_Anything" / 搜索 "ComfyUI_Image_Anything"
3. Click Install / 点击安装

---

After installation, find the node in / 安装后，在节点列表中查找：

**V2 模块化版本 / V2 Modular Version**:
- `ComfyUI_Image_Anything` → `Image Collector` (图片收集器 / Image Collector)
- `ComfyUI_Image_Anything` → `Text Collector` (文本收集器 / Text Collector)
- `ComfyUI_Image_Anything` → `Dynamic Batch Image Saver (V2)` (主节点 / Main node)

**原始版本 / Original Version**:
- `ComfyUI_Image_Anything` → `Dynamic Batch Image Saver (V1)`

## 使用说明

### 动态输入操作步骤

1. 首先设置 **input_count** 参数（要保存的图片数量）
2. 点击节点上的 "更新" 按钮或重新加载工作流
3. ComfyUI 会自动显示相应数量的输入接口
4. 连接图片和设置保存名称
5. （可选）设置 **enabled** 参数控制节点启用状态
6. 运行工作流

### 路径说明 / Path Guide

**支持 Windows 和 Linux 绝对路径** / **支持 Windows 和 Linux 绝对路径**

- **相对路径 / Relative Path**：`batch_saves` → 保存到 `ComfyUI/output/batch_saves/`
- **Linux/Mac 绝对路径 / Linux/Mac Absolute Path**：`/home/user/images` → 直接保存到指定目录
- **Windows 绝对路径 / Windows Absolute Path**：`D:\images` 或 `D:/images` → 直接保存到指定目录

**文件组织结构 / File Organization**：
```
输入绝对路径: D:/images
实际保存位置: D:/images/task_20241109_143022/
├── 封面_01.png
├── 细节_02.png
├── save_info.txt
└── metadata.json
```

### 元数据文件

每个任务文件夹包含：
- **`图片文件`**：保存名称_序号.png 格式的图片文件
- **`prompt.txt`**：ComfyUI Prompt 文本（包含正向提示词、负向提示词和完整 JSON）
- **`metadata.json`**：基本元数据（任务ID、时间戳、输出目录、图片数量和图片信息等，不含ComfyUI工作流数据），同时包含格式化的文本信息
- **`workflow.json`**：完整的ComfyUI工作流文件（可以直接拖拽到ComfyUI中加载使用）

## 注意事项

- 每次运行工作流都会创建新的时间戳文件夹
- 文件命名格式：`保存名称_序号.png`（序号为 01, 02, 03...）
- 文本信息（description）会自动保存到 save_info.txt 和 metadata.json 文件
- 只输出文本信息，不输出图片（纯保存节点）
- input_count 范围：1-5
- 未连接的图片输入会被自动跳过
- 通过 enabled 参数可控制节点是否执行保存操作

## 🤝 Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request. / 欢迎贡献！请随时提交拉取请求。

### Development / 开发
1. Fork the repository / 派生仓库
2. Create a feature branch / 创建功能分支
3. Commit your changes / 提交您的更改
4. Push to the branch / 推送到分支
5. Open a Pull Request / 打开拉取请求

## 📜 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. / 本项目采用 MIT 许可证 - 查看许可证文件了解详情。

## ⭐ Show Your Support / 支持我们

If you find this project helpful, please consider:
- ⭐ Starring the repository / 为仓库点星
- 🐛 Reporting issues / 报告问题
- 💡 Suggesting features / 建议功能
- 🤝 Contributing to the code / 贡献代码

---

**Made with ❤️ for the ComfyUI Community / 为 ComfyUI 社区精心制作**
