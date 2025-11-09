# ComfyUI Dynamic Batch Image Saver

[![GitHub stars](https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![GitHub forks](https://img.shields.io/github/forks/HuangYuChuh/ComfyUI_Image_Anything?style=social)](https://github.com/HuangYuChuh/ComfyUI_Image_Anything)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-节点-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

A powerful ComfyUI custom node for dynamic batch image saving with custom prefixes and automatic organization.

一个支持动态数量图片批量保存的 ComfyUI 扩展节点。

## ✨ Key Features / 主要功能

- ✅ **动态输入**：支持 1-5 张图片的动态输入
- ✅ **独立前缀**：每张图片可以设置单独的文件名前缀
- ✅ **文本描述**：可输入关于图片的描述信息，保存到文件
- ✅ **文本保存**：输出文本信息同时保存到 save_info.txt 文件
- ✅ **自动分组**：每次运行自动创建时间戳文件夹
- ✅ **详细文本输出**：输出包含所有图片信息的文本
- ✅ **JSON 元数据**：自动保存完整的元数据信息
- ✅ **灵活路径**：支持自定义输出文件夹路径

## 节点参数

### 输入参数

- **input_count** (必需): 图片数量（1-5）
- **image_1** (必需): 第一张图片
- **prefix_1** (必需): 第一张图片的文件名前缀（默认："image"）
- **output_folder** (必需): 输出文件夹名称（默认："batch_saves"）
- **image_2 到 image_5** (可选): 更多图片输入（根据 input_count 自动扩展）
- **prefix_2 到 prefix_5** (可选): 对应的文件名前缀
- **description** (可选): 文本描述，会保存到文件中

### 输出结果

- **save_info**: 文本信息（任务ID、时间戳、输出路径、描述信息、所有图片信息）

## 文件组织结构

```
output/
├── batch_saves/                    # 父文件夹（可自定义）
│   ├── task_20241109_143022/       # 任务文件夹（每次运行创建）
│   │   ├── 封面_01.png             # 前缀_序号.png 格式
│   │   ├── 细节_02.png
│   │   ├── 对比_03.png
│   │   ├── save_info.txt           # 文本信息文件
│   │   └── metadata.json           # 完整元数据
│   ├── task_20241109_144035/
│   │   ├── 原图_01.png
│   │   ├── 处理图_02.png
│   │   ├── save_info.txt
│   │   └── metadata.json
│   └── ...
```

## 使用示例

### 基本用法

1. 设置 **input_count** 为 3
2. 依次连接 3 张图片到 `image_1`, `image_2`, `image_3`
3. 设置前缀：`封面`、`细节`、`对比`
4. （可选）在 **description** 框中输入关于这些图片的描述信息
5. 运行工作流

### 输出文本示例

```
任务ID: task_20241109_143022
时间戳: 20241109_143022
输出目录: /output/batch_saves/task_20241109_143022
图片数量: 3

描述信息:
这是一次测试的图片保存任务，包含封面、细节和对比图。

保存的图片:
  [1] 封面_01.png (前缀: 封面)
  [2] 细节_02.png (前缀: 细节)
  [3] 对比_03.png (前缀: 对比)
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
**Category / 分类**: `我的工具` → `Dynamic Batch Image Saver`

## 使用说明

### 动态输入操作步骤

1. 首先设置 **input_count** 参数（要保存的图片数量）
2. 点击节点上的 "更新" 按钮或重新加载工作流
3. ComfyUI 会自动显示相应数量的输入接口
4. 连接图片和设置前缀
5. 运行工作流

### 路径说明

- **相对路径**：如 "batch_saves" → 保存到 `ComfyUI/output/batch_saves/`
- **绝对路径**：如 "/home/user/images" → 直接保存到指定目录

### 元数据文件

每个任务文件夹包含：
- **`save_info.txt`**：文本输出信息（任务ID、时间戳、输出路径、所有图片信息）
- **`metadata.json`**：完整元数据（任务ID、时间戳、所有图片的完整信息、ComfyUI的prompt和extra_pnginfo等）

## 注意事项

- 每次运行工作流都会创建新的时间戳文件夹
- 文件命名格式：`前缀_序号.png`（序号为 01, 02, 03...）
- 文本信息（description）会自动保存到 save_info.txt 和 metadata.json 文件
- 只输出文本信息，不输出图片（纯保存节点）
- input_count 范围：1-5
- 未连接的图片输入会被自动跳过

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
