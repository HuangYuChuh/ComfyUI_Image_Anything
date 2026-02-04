# ComfyUI Image Anything

[![GitHub stars](https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![GitHub forks](https://img.shields.io/github/forks/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-节点-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

**ComfyUI Image Anything** 提供三大核心功能：

1. **批量保存工作流输出**：在一次任务运行中批量保存不同阶段的图片和文本，自动整理到统一的时间戳文件夹中。通过模块化设计（Image Batch + Text Batch + BatchImageSaverV2），你可以灵活组合任意数量的图片批次和文本批次。

2. **数据集自动标注**：专为制作图像编辑模型（如 Qwen Edit、Kontext）训练数据集设计。提供自动迭代加载、结构化保存、失败重跑等功能，大幅提升数据集制作效率。

3. **分桶图像标准化**：专为 SDXL/Flux 模型训练优化。智能检测图片比例，自动归一化到 `ai-toolkit` 支持的标准训练 Bucket 分辨率，确保零拉伸、无黑边。

## 安装方法

### 方式一：克隆仓库
```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/HuangYuChuh/ComfyUI_Image_Anything.git
```

### 方式二：ComfyUI Manager（推荐）
在 ComfyUI Manager 中搜索 "ComfyUI_Image_Anything" 并安装。

## 节点参数详解

### 1. 智能分桶预处理 (`Preprocess`)
**Smart Image Resize for Bucket**
专为训练准备的图像预处理节点。它会自动将任意比例的图片 Center Crop 到最接近的标准 Bucket 尺寸。

*   **image**: 输入图片
*   **mode**: 处理模式
    *   `Smart (Auto Detect)`: (推荐) 自动计算宽高比，匹配最接近的标准尺寸 (1:1, 3:4, 4:3, 9:16, 16:9)。
    *   `Force 1024x1024 (1:1)`: 强制方形
    *   `Force 832x1152 (3:4)`: 强制标准竖图 (人像常用)
    *   `Force 1152x832 (4:3)`: 强制标准横图
    *   `Force 768x1344 (9:16)`: 强制长竖图 (手机壁纸)
    *   `Force 1344x768 (16:9)`: 强制宽屏横图

> **支持的 SDXL/Flux 标准 Bucket**: 1024x1024, 832x1152, 1152x832, 768x1344, 1344x768.

### 2. 自动数据集标注 (`Edit_Image`)
这些是专为自动化制作模型数据集（如 Qwen Edit、Kontext 等）设计的新节点。

**EditDatasetLoader**:
- **directory** (必需): 图片文件夹路径
- **start_index** (必需): 起始索引（默认：0）
- **auto_next** (可选): 自动递增索引（默认：True），关闭后固定读取 start_index
- **reset_iterator** (可选): 强制重置索引到 start_index（默认：False）
- **index_list** (可选): 逗号分隔的索引列表，如 `"5,12,23"`。用于**重新处理失败的图片**，填写后只加载指定索引的图片。
- **自动停止**: 当遍历完文件夹中所有图片（或指定索引）后，会自动触发停止信号终止工作流。

**EditDatasetSaver**:
- **output_root** (必需): 保存根目录
- **naming_style** (必需): 
    - `Keep Original`: 保持原文件名
    - `Rename (Prefix + Index)`: 使用前缀+自动序号
- **filename_prefix**: 重命名时的前缀（默认："AnyBG"）
- **index**: 重命名时的起始序号（默认：0，会自动跳过已存在文件）
- **allow_overwrite** (新增): 是否允许覆盖已有文件。开启后配合 `index_list` 使用，可自动覆盖错误的数据对。
- **filename_stem**: 原始文件名（可选，连接 Loader 的输出）
- **save_image_control/target**: 输入图片（可选）
- **save_caption**: 输入文本标题（可选）
- **save_format**: 保存格式（可选，支持 jpg/png/webp，默认 jpg）

#### 高级功能：配对数据加载 (Paired Data Loading)
支持加载训练常用的 "Target Image + Control Image" 数据对。

**参数设置**:
- `target_img_suffix`: Target 图片的后缀（如 `_O`）。填写后，通过 `target_img` 端口输出。
- `control_img_suffix`: Control 图片的后缀（如 `_W`）。填写后，通过 `control_img` 端口输出。

**逻辑**:
加载器会自动筛选包含 `target_img_suffix` 的图片，并自动查找对应 `control_img_suffix` 的配对文件。
例如：填 `_O` 和 `_W`。加载 `Dog_O.jpg` 时，自动找到 `Dog_W.png` 并作为 control 输出。

**Outputs**:
- `control_img`: 原图/条件图 (对应 `_W`)，**推荐放在上面**。
- `target_img`: 目标图 (对应 `_O`)。
- `filename_stem`: 文件名（**已自动去除后缀**）。例如加载 `A_O.jpg`，这里输出 `A`。这使得 Saver 可以直接保存为干净的文件名。

**EditDatasetSaver更新**:
无需任何额外设置。只要 `EditDatasetLoader` 获取到了干净的 `filename_stem`，Saver 就会自动以该名字保存所有输出文件（Control/Target/Txt），确保文件名一致。

### 3. V2 模块化批量保存 (`Batch_Save`)

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

### V1 版本 (Batch Image Saver V1)
*(保留用于向后兼容，建议使用 V2)*
- **input_count** (必需): 图片数量（1-5）
- **image_1** (必需): 第一张图片
- **save_name_1** (必需): 第一张图片的保存名称（默认："image"）
- **output_folder** (必需): 输出文件夹名称（默认："batch_saves"）

## 使用示例

### 场景一：自动清洗数据集 (Auto Clean Dataset)
1.  **加载**: 使用 `EditDatasetLoader` 读取原始图片文件夹。
2.  **处理**: 连接 `Smart Image Resize for Bucket` 节点，模式设为 `Smart (Auto Detect)`。
3.  **保存**: 连接 `EditDatasetSaver` (或普通 Save Image)，即可得到完美符合训练标准的数据集。

### 场景二：自动标注数据集流程 (`Edit Dataset Workflow`)
这是一个专门用于构建和标注图像编辑模型数据集的流程：
1. **加载图片**: 使用 `EditDatasetLoader` 指向你的图片文件夹。
2. **处理流程**: 在中间连接任意的处理节点（如图像反推提示词、抠图、风格迁移等）。
3. **保存结果**: 连接 `EditDatasetSaver`。
   - **Output Root**: 设置保存结果的根目录。
   - **Naming Style**: 
     - 想要保持文件名不变？选 `Keep Original` 并连接 loader 的 `filename_stem`。
     - 想要统一重命名？选 `Rename (Prefix + Index)` 并设置前缀（如 `AnyBG`）。
   - **Auto Increment**: 即使中断重启，"Rename" 模式也会自动检测已有文件，从下一个序号开始保存，**不会覆盖旧数据**。

#### 高级技巧：重跑失败图片
当发现某些图片（如索引 5, 12, 23）处理失败时，无需重跑整个数据集：
1. **Loader 设置**：
   - `index_list`: 填入 `"5,12,23"`。
   - `reset_iterator`: 开启（确保从列表第一个开始）。
2. **Saver 设置**：
   - `allow_overwrite`: 开启 `True`（允许覆盖旧的错误结果）。
3. **运行**：节点只处理这 3 张图片，完成后自动停止。

### 场景三：多批次组合保存 (V2)
```
[图片1-5] → [Image Batch A] → batch_1 → \
[文本A] → [Text Batch A] → text_batch_1 →  → [Batch Image Saver V2]
[图片6-7] → [Image Batch B] → batch_2 → /
[文本B] → [Text Batch B] → text_batch_2 → /
```

## 输出文件结构

每次运行都会创建独立的时间戳文件夹：
```
output/
└── batch_saves/
    └── task_20251130_143022/
        ├── 封面_01.png          # 保存名称_序号.png 格式
        ├── 细节_02.png
        ├── prompt.txt           # ComfyUI Prompt 文本（如果有）
        ├── metadata.json        # 基本元数据（包含格式化文本）
        └── workflow.json        # 完整工作流文件（可直接加载）
```

## 节点查找
安装后，在节点列表中查找：

*   **预处理 (`Preprocess`)**: `ComfyUI_Image_Anything` → `Preprocess` → `Smart Image Resize for Bucket`
*   **数据集 (`Edit_Image`)**: `ComfyUI_Image_Anything` → `Edit_Image` → `EditDatasetLoader`, `EditDatasetSaver`
*   **批量保存 (`Batch_Save`)**: `ComfyUI_Image_Anything` → `Batch_Save` → `Batch Image Saver V2 (Dynamic)`

---

**Made with love for the ComfyUI Community**