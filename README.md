# ComfyUI Image Anything

[![GitHub stars](https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![GitHub forks](https://img.shields.io/github/forks/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-节点-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

**ComfyUI Image Anything** 让你能在一次任务运行中批量保存不同阶段的图片和文本，自动整理到统一的时间戳文件夹中，方便后期 review 和批量处理。通过模块化设计（Image Batch + Text Batch + BatchImageSaverV2），你可以灵活组合任意数量的图片批次和文本批次，每个批次内的图片可设置独立保存名称，所有内容会自动重新编号并保存完整的元数据和工作流文件。

## 安装方法

### 方式一：克隆仓库
```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/HuangYuChuh/ComfyUI_Image_Anything.git
```

### 方式二：ComfyUI Manager（推荐）
在 ComfyUI Manager 中搜索 "ComfyUI_Image_Anything" 并安装。

## 节点参数详解

### V2 模块化版本参数

#### Image Batch 节点 (`image_batch`)
- **image_1 到 image_5** (可选): 最多5张图片输入
- **save_name_1 到 save_name_5** (可选): 对应每张图片的保存名称

#### Text Batch 节点 (`text_batch`)
- **text_1 到 text_5** (可选): 5个通用文本字段，可输入任意内容
- **name_1 到 name_5** (可选): 对应每个文本的文件名

#### Batch Image Saver V2 主节点
- **output_folder** (必需): 输出文件夹名称（默认："batch_saves"）
- **enabled** (可选): 是否启用此节点（默认：true）
- **batch_1, batch_2, ...** (必需): 连接 Image Batch 节点的输出
- **text_batch_1, text_batch_2, ...** (可选): 连接 Text Batch 节点的输出

### 原始版本参数 (Batch Image Saver V1)
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

## 使用示例

### V2 模块化版本使用方法

#### 基本工作流程（仅图片）
1. **添加图片收集器**：在工作流中添加 `Image Batch` 节点
2. **连接图片**：将1-5张图片连接到子节点的 `image_1` 到 `image_5` 输入
3. **设置保存名称**：为每张图片设置对应的保存名称
4. **添加主节点**：添加 `Batch Image Saver V2 (Dynamic)` 节点
5. **连接图片批次**：将子节点的 `image_batch` 输出连接到主节点的 `batch_1` 输入
6. **运行工作流**

> **注意**：如果需要文本信息，必须添加 `Text Batch` 节点并连接到主节点的 `text_batch_1` 输入。

#### 高级工作流程（图片+对应文本）
1. **添加图片收集器**：添加 `Image Batch` 节点（如 Batch A）
2. **添加文本收集器**：添加 `Text Batch` 节点（如 Text A）
3. **配置内容**：
   - 在 Batch A 中连接图片并设置保存名称
   - 在 Text A 中设置5个通用文本字段（text_1到text_5，可输入任意内容）
4. **添加主节点**：添加 `Batch Image Saver V2 (Dynamic)` 节点
5. **连接批次**：
   - 将 Batch A 的 `image_batch` 连接到主节点的 `batch_1`
   - 将 Text A 的 `text_batch` 连接到主节点的 `text_batch_1`
6. **运行工作流**

> **注意**：BatchImageSaverV2主节点不再有统一的文本输入字段，所有文本内容必须通过Text Batch提供。

#### 多批次组合示例
```
[图片1-5] → [Image Batch A] → batch_1 → \
[文本A] → [Text Batch A] → text_batch_1 →  → [Batch Image Saver V2]
[图片6-7] → [Image Batch B] → batch_2 → /
[文本B] → [Text Batch B] → text_batch_2 → /
```

### 原始版本使用方法
1. 设置 **input_count** 为需要的图片数量 (1-5)
2. 依次连接相应数量的图片到 `image_1` 到 `image_N`
3. 设置对应的保存名称，如：`封面`、`细节`、`对比`、`局部`、`全图`
4. （可选）在 **description** 框中输入关于这些图片的描述信息
5. （可选）通过 **enabled** 参数控制节点是否启用
6. 运行工作流

## 输出文件结构

每次运行都会创建独立的时间戳文件夹：
```
output/
└── batch_saves/
    └── task_20251130_143022/
        ├── 封面_01.png          # 保存名称_序号.png 格式
        ├── 细节_02.png
        ├── 对比_03.png
        ├── 局部_04.png
        ├── 全图_05.png
        ├── prompt.txt           # ComfyUI Prompt 文本（如果有）
        ├── metadata.json        # 基本元数据（包含格式化文本）
        └── workflow.json        # 完整工作流文件（可直接加载）
```

## 节点查找

安装后，在节点列表中查找：

**V2 模块化版本**:
- `ComfyUI_Image_Anything` → `Image Batch`
- `ComfyUI_Image_Anything` → `Text Batch`
- `ComfyUI_Image_Anything` → `Batch Image Saver V2 (Dynamic)`

**原始版本**:
- `ComfyUI_Image_Anything` → `Batch Image Saver V1`

---

**Made with love for the ComfyUI Community**