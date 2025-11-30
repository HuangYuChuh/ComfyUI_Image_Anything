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

## 节点使用

- **V2 模块化版本**: `Image Batch` + `Text Batch` + `Batch Image Saver V2 (Dynamic)`
- **原始版本**: `Batch Image Saver V1`

**输出结构**:
```
task_时间戳/
├── 图片_01.png, 图片_02.png, ...
├── prompt.txt
├── metadata.json
└── workflow.json
```

---

**Made with love for the ComfyUI Community**