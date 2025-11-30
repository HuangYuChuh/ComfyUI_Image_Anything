# ComfyUI Dynamic Batch Image Saver

[![GitHub stars](https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![GitHub forks](https://img.shields.io/github/forks/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-节点-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

**一次任务，完整记录** - 在单次 ComfyUI 工作流运行中，批量保存不同阶段、不同结构的图片和文本，自动组织到统一的时间戳文件夹中，方便后期 review 和批量处理。

## 🆕 核心价值 / Core Value

这个扩展节点解决了 ComfyUI 社区用户的实际痛点：

### 🎯 **为什么需要它？**
- **传统方式限制**：标准保存节点只能保存单张图片，无法在一次任务中保存多个不同阶段的结果
- **手动操作繁琐**：需要多次运行工作流或手动复制粘贴来保存不同结果
- **文件管理混乱**：不同阶段的图片分散在不同位置，难以关联和对比

### 💡 **我们的解决方案**
- **一次运行，完整记录**：在单次工作流执行中，同时保存所有阶段的图片和对应的文本信息
- **智能分组**：支持将相关图片和文本组织成批次（如：正面图+背面图+细节图 = 一个产品批次）
- **自动整理**：所有内容自动保存到带时间戳的独立文件夹，保持整洁有序
- **灵活扩展**：通过复制子节点，轻松支持任意数量的图片和文本组合

### 🚀 **典型使用场景**
- **AI绘画工作流**：保存提示词生成的多张不同构图图片 + 对应的提示词文本
- **图像处理流水线**：原始图 → 处理图 → 最终图 + 每个阶段的参数说明
- **批量产品展示**：同一产品的多角度视图 + 产品描述文本
- **实验对比**：不同参数设置下的结果对比 + 实验配置说明

## V2 模块化架构

### 架构设计
```
[Image Batch A] → batch_1 ─┐
[Text Batch A] → text_batch_1 ─┤
                              ├──→ [BatchImageSaverV2] → 统一保存到 task_时间戳/
[Image Batch B] → batch_2 ─┤
[Text Batch B] → text_batch_2 ─┘
```

### 节点组成
- **Image Batch** (`image_batch`)：收集1-5张相关图片，可为每张设置独立保存名称
- **Text Batch** (`text_batch`)：收集结构化文本内容（支持5个自定义文本字段）
- **BatchImageSaverV2**：主节点，接收多个图片+文本批次，统一保存到时间戳文件夹

### 核心优势
- **完全解耦**：图片和文本独立处理，灵活组合
- **动态扩展**：需要更多内容？只需复制相应的子节点
- **智能编号**：自动全局重新编号，保持顺序一致性
- **向后兼容**：保留 V1 版本供简单场景使用

## 使用示例

### 场景1：AI绘画多结果保存
```
[提示词A生成的5张图] → [Image Batch A] → batch_1 ─┐
[提示词A的详细参数] → [Text Batch A] → text_batch_1 ─┤
                                                     ├──→ [BatchImageSaverV2]
[提示词B生成的3张图] → [Image Batch B] → batch_2 ─┤
[提示词B的详细参数] → [Text Batch B] → text_batch_2 ─┘
```
**结果**：`task_20251130_143022/` 文件夹包含：
- 8张图片（自动编号 01-08）
- 2组文本信息（提示词A和B的参数）
- 完整的工作流文件和元数据

### 场景2：图像处理流水线
```
[原始图, 增强图, 最终图] → [Image Batch] → batch_1
[处理步骤说明] → [Text Batch] → text_batch_1 → [BatchImageSaverV2]
```
**结果**：清晰记录整个处理过程，方便后期分析和优化

## 安装方法

### 方式一：克隆仓库
```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/HuangYuChuh/ComfyUI_Image_Anything.git
```

### 方式二：ComfyUI Manager（推荐）
1. 在 ComfyUI Manager 中搜索 "ComfyUI_Image_Anything"
2. 点击安装

## 节点查找

安装后，在节点列表中查找：

**V2 模块化版本**:
- `ComfyUI_Image_Anything` → `Image Batch`
- `ComfyUI_Image_Anything` → `Text Batch`
- `ComfyUI_Image_Anything` → `Batch Image Saver V2 (Dynamic)`

**原始版本**:
- `ComfyUI_Image_Anything` → `Batch Image Saver V1`

## 输出文件结构

每次运行都会创建独立的时间戳文件夹：
```
output/
└── batch_saves/
    └── task_20251130_143022/
        ├── 图片_01.png          # 自动编号的图片
        ├── 细节_02.png
        ├── 对比_03.png
        ├── prompt.txt           # ComfyUI 提示词
        ├── metadata.json        # 完整元数据
        └── workflow.json        # 可直接加载的工作流
```

## 项目愿景

为 ComfyUI 社区提供一个**高效、灵活、易用**的批量保存解决方案，让创作者能够：
- ✨ **专注创作**：无需担心保存问题，一次运行完成所有记录
- 🔍 **方便回顾**：所有相关素材集中管理，便于对比和分析
- 🚀 **批量处理**：支持大规模实验和生产，提高工作效率
- 📊 **结构化输出**：图片和文本完美配对，便于后续处理

---

**Made with love for the ComfyUI Community / 为 ComfyUI 社区精心制作**