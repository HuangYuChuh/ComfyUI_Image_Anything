import os
import json
import torch
import numpy as np
from PIL import Image
import folder_paths
from datetime import datetime

class ImageCollector:
    """
    图片批次节点 - 用于收集一组图片及其保存名称

    功能：
    - 收集1-5张图片（可选输入）
    - 为每张图片设置对应的保存名称
    - 打包输出供主节点使用
    """

    def __init__(self):
        self.type = "collector"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                # 5个可选的图片输入
                "image_1": ("IMAGE", {"forceInput": True}),
                "save_name_1": ("STRING", {"default": "image"}),
                "image_2": ("IMAGE", {"forceInput": True}),
                "save_name_2": ("STRING", {"default": "image"}),
                "image_3": ("IMAGE", {"forceInput": True}),
                "save_name_3": ("STRING", {"default": "image"}),
                "image_4": ("IMAGE", {"forceInput": True}),
                "save_name_4": ("STRING", {"default": "image"}),
                "image_5": ("IMAGE", {"forceInput": True}),
                "save_name_5": ("STRING", {"default": "image"}),
            },
        }

    RETURN_TYPES = ("IMAGE_BATCH", "STRING")
    RETURN_NAMES = ("image_batch", "batch_info")
    FUNCTION = "collect_images"
    OUTPUT_NODE = False
    CATEGORY = "🚦 ComfyUI_Image_Anything/Batch_Save"
    DESCRIPTION = "收集1-5张图片及其保存名称，打包输出给主节点"

    def collect_images(self, **kwargs):
        """
        收集图片和对应的保存名称

        Args:
            **kwargs: 包含image_1-5和save_name_1-5的可选参数

        Returns:
            image_batch: 打包的图片批次数据
            batch_info: 批次信息字符串
        """
        collected_images = []
        total_count = 0

        # 检查每个可选的图片输入
        for i in range(1, 6):
            image_key = f"image_{i}"
            save_name_key = f"save_name_{i}"

            # 如果图片输入存在
            if image_key in kwargs and kwargs[image_key] is not None:
                image_tensor = kwargs[image_key]
                save_name = kwargs.get(save_name_key, "image")

                # 转换tensor为numpy数组
                i_array = image_tensor.cpu().numpy()
                if i_array.ndim == 4 and i_array.shape[0] == 1:
                    i_array = i_array[0]

                # 转换为PIL Image
                i_array = 255. * i_array
                img = Image.fromarray(np.clip(i_array, 0, 255).astype(np.uint8))

                collected_images.append({
                    "image": img,
                    "save_name": save_name,
                    "original_index": i
                })
                total_count += 1

        # 构建批次数据
        batch_data = {
            "images": collected_images,
            "total_count": total_count
        }

        # 生成批次信息
        batch_info = f"收集了 {total_count} 张图片"

        return (batch_data, batch_info)


class TextCollector:
    """
    文本批次节点 - 用于收集多个可自定义名称的文本内容

    功能：
    - 支持5个文本输入（text_1 到 text_5），每个都是可选的
    - 每个文本都有对应的文件名（name_1 到 name_5）
    - 用户可以为每个文本指定自定义的保存名称
    - 完全灵活，适应不同使用场景
    """

    def __init__(self):
        self.type = "text_collector"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                # 5个可选的文本输入 + 对应的文件名
                "text_1": ("STRING", {"forceInput": True, "tooltip": "第一个文本内容"}),
                "name_1": ("STRING", {
                    "default": "text_1",
                    "multiline": False,
                    "placeholder": "文件名1",
                    "tooltip": "第一个文本的保存文件名"
                }),
                "text_2": ("STRING", {"forceInput": True, "tooltip": "第二个文本内容"}),
                "name_2": ("STRING", {
                    "default": "text_2",
                    "multiline": False,
                    "placeholder": "文件名2",
                    "tooltip": "第二个文本的保存文件名"
                }),
                "text_3": ("STRING", {"forceInput": True, "tooltip": "第三个文本内容"}),
                "name_3": ("STRING", {
                    "default": "text_3",
                    "multiline": False,
                    "placeholder": "文件名3",
                    "tooltip": "第三个文本的保存文件名"
                }),
                "text_4": ("STRING", {"forceInput": True, "tooltip": "第四个文本内容"}),
                "name_4": ("STRING", {
                    "default": "text_4",
                    "multiline": False,
                    "placeholder": "文件名4",
                    "tooltip": "第四个文本的保存文件名"
                }),
                "text_5": ("STRING", {"forceInput": True, "tooltip": "第五个文本内容"}),
                "name_5": ("STRING", {
                    "default": "text_5",
                    "multiline": False,
                    "placeholder": "文件名5",
                    "tooltip": "第五个文本的保存文件名"
                }),
            },
        }

    RETURN_TYPES = ("TEXT_BATCH", "STRING")
    RETURN_NAMES = ("text_batch", "text_info")
    FUNCTION = "collect_text"
    OUTPUT_NODE = False
    CATEGORY = "🚦 ComfyUI_Image_Anything/Batch_Save"
    DESCRIPTION = "收集多个可自定义名称的文本内容，打包输出给主节点"

    def collect_text(self, **kwargs):
        """
        收集多个文本内容和对应的文件名

        Args:
            **kwargs: 包含text_1-5和name_1-5的可选参数

        Returns:
            text_batch: 打包的文本批次数据
            text_info: 文本信息字符串
        """
        text_files = []

        # 处理5个文本输入
        for i in range(1, 6):
            text_key = f"text_{i}"
            name_key = f"name_{i}"

            # 检查文本输入是否存在且非空
            if text_key in kwargs and kwargs[text_key] is not None:
                text_content = kwargs[text_key]
                if text_content.strip():  # 只处理非空文本
                    file_name = kwargs.get(name_key, f"text_{i}")
                    # 清理文件名
                    import re
                    clean_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
                    if not clean_file_name:
                        clean_file_name = f"text_{i}"

                    text_files.append({
                        "content": text_content,
                        "file_name": clean_file_name
                    })

        text_data = {"files": text_files}

        # 生成文本信息
        if text_files:
            file_names = [f"{tf['file_name']}.txt" for tf in text_files]
            text_info = f"收集了 {len(text_files)} 个文本文件: {', '.join(file_names)}"
        else:
            text_info = "未收集到任何文本内容"

        return (text_data, text_info)

class BatchImageSaverV2:
    """
    重构的批量图片保存节点 - 支持真正的动态输入

    功能：
    - 支持动态添加/移除图片批次输入
    - 支持动态添加/移除文本批次输入
    - 前端JavaScript管理动态端口
    - 统一保存到时间戳文件夹
    """

    def __init__(self):
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        inputs = {
            "required": {
                # 移除了固定的 input_count，改为真正的动态输入
            },
            "optional": {
                # 输出设置
                "output_folder": ("STRING", {
                    "default": "batch_saves",
                    "tooltip": "输出文件夹名称（可使用相对或绝对路径）"
                }),
                "enabled": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Enabled",
                    "label_off": "Disabled",
                    "tooltip": "启用或禁用此节点"
                }),
                # 初始各定义一个输入端口，其余由前端动态添加
                "image_batch_1": ("IMAGE_BATCH", {"forceInput": True}),
                "text_batch_1": ("TEXT_BATCH", {"forceInput": True}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

        return inputs

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("save_info",)
    FUNCTION = "save_batches"
    OUTPUT_NODE = True
    CATEGORY = "🚦 ComfyUI_Image_Anything/Batch_Save"
    DESCRIPTION = "支持动态输入的批量图片保存节点"

    def save_batches(self, output_folder="batch_saves", enabled=True, prompt=None, extra_pnginfo=None, **kwargs):
        """
        批量保存多个图片批次到独立文件夹 - 支持真正的动态输入

        Args:
            output_folder: 输出文件夹名
            enabled: 是否启用此节点
            prompt: ComfyUI 提示词元数据（自动传入）
            extra_pnginfo: ComfyUI 额外信息（自动传入）
            **kwargs: 动态包含image_batch_1-N和text_batch_1-N的批次输入
        """
        # 检查是否启用
        if not enabled:
            return ("Node is disabled",)

        # 生成唯一时间戳和文件夹名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"task_{timestamp}"
        batch_folder = task_id

        # 确定保存目录
        is_absolute = (
            os.path.isabs(output_folder) or
            (len(output_folder) >= 3 and output_folder[1] == ':')
        )

        if is_absolute:
            base_dir = output_folder
        else:
            base_dir = os.path.join(folder_paths.get_output_directory(), output_folder)

        # 创建主保存目录
        os.makedirs(base_dir, exist_ok=True)

        # 创建批次特定文件夹（时间戳子文件夹）
        batch_dir = os.path.join(base_dir, batch_folder)
        os.makedirs(batch_dir, exist_ok=True)

        # 收集所有图片（重新编号）
        all_images = []
        saved_files = []
        global_index = 1

        # 动态处理所有图片批次输入
        image_batch_count = 0
        for key, value in kwargs.items():
            if key.startswith("image_batch_") and value is not None:
                batch_data = value

                # 验证批次数据格式
                if not isinstance(batch_data, dict) or "images" not in batch_data:
                    continue

                batch_images = batch_data["images"]
                batch_idx = int(key.replace("image_batch_", ""))

                # 处理批次中的每张图片（重新编号）
                for img_data in batch_images:
                    img = img_data["image"]
                    save_name = img_data["save_name"]
                    original_index = img_data["original_index"]

                    # 清理保存名称
                    clean_save_name = save_name.replace('/', '_').replace('\\', '_')

                    # 生成新文件名（全局编号）
                    filename = f"{clean_save_name}_{global_index:02d}.png"
                    filepath = os.path.join(batch_dir, filename)

                    # 保存图片
                    img.save(filepath)

                    # 记录信息
                    all_images.append({
                        "global_index": global_index,
                        "save_name": save_name,
                        "filename": filename,
                        "filepath": filepath,
                        "source_batch": batch_idx,
                        "source_index": original_index
                    })
                    saved_files.append(filepath)
                    global_index += 1

                image_batch_count += 1

        # 如果没有保存任何图片，返回提示信息
        if not all_images:
            return ("No images to save",)

        # 处理文本批次 - 动态收集所有文本文件
        text_files = []  # 存储 {content: "...", file_name: "..."} 的列表
        text_batch_count = 0

        # 动态处理所有文本批次输入
        for key, value in kwargs.items():
            if key.startswith("text_batch_") and value is not None:
                text_batch = value
                if isinstance(text_batch, dict) and "files" in text_batch:
                    # 添加所有文本文件
                    text_files.extend(text_batch["files"])
                    text_batch_count += 1

        # 保存元数据文件
        metadata = {
            "task_id": task_id,
            "timestamp": timestamp,
            "output_folder": output_folder,
            "batch_dir": batch_dir,
            "total_images": len(all_images),
            "images": all_images
        }

        # 构建输出信息
        save_info_lines = [
            f"任务ID: {task_id}",
            f"时间戳: {timestamp}",
            f"输出目录: {batch_dir}",
            f"图片总数: {len(all_images)}",
            f"图片批次数: {image_batch_count}",
            f"文本批次数: {text_batch_count}",
        ]

        # 按批次显示统计（基于实际的批次索引）
        batch_stats = {}
        for img in all_images:
            batch = img["source_batch"]
            batch_stats[batch] = batch_stats.get(batch, 0) + 1

        if len(batch_stats) > 0:
            save_info_lines.append("")
            save_info_lines.append("批次统计:")
            for batch, count in sorted(batch_stats.items()):
                save_info_lines.append(f"  图片批次{batch}: {count} 张图片")

        # 添加文本文件信息
        if text_files:
            save_info_lines.append("")
            save_info_lines.append("文本文件:")
            for text_file in text_files:
                save_info_lines.append(f"  {text_file['file_name']}.txt")

        # 添加保存的图片列表
        save_info_lines.append("")
        save_info_lines.append("保存的图片:")
        for img_info in all_images:
            save_info_lines.append(f"  [{img_info['global_index']:02d}] {img_info['filename']}")

        save_info = "\n".join(save_info_lines)
        metadata["save_info_text"] = save_info

        # 保存ComfyUI工作流文件
        if extra_pnginfo is not None and "workflow" in extra_pnginfo:
            workflow_path = os.path.join(batch_dir, "workflow.json")
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump(extra_pnginfo["workflow"], f, indent=2, ensure_ascii=False)

        # 保存元数据文件
        metadata_path = os.path.join(batch_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # 保存文本文件
        for text_file in text_files:
            text_path = os.path.join(batch_dir, f"{text_file['file_name']}.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_file["content"])

        return (save_info,)


class BatchImageSaver:
    """
    动态批量保存图片到独立工作流文件夹的节点

    功能：
    - 支持动态数量的图片输入
    - 每张图片可以设置独立的文件名前缀
    - 创建独立的时间戳文件夹
    - 输出包含所有图片信息的文本
    """

    def __init__(self):
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_1": ("IMAGE", {"tooltip": "第一张图片"}),
                # 文本输入接口 - 来自上游节点的单行文本输入
                "title": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "标题文本（来自上游节点）",
                    "tooltip": "接收上游节点的标题文本输出"
                }),
                "description": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "描述文本（来自上游节点）",
                    "tooltip": "接收上游节点的描述文本输出"
                }),
                "text_prompt": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Prompt文本（来自上游节点）",
                    "tooltip": "接收上游节点的Prompt文本输出"
                }),
                "save_name_1": ("STRING", {
                    "default": "image",
                    "tooltip": "第一张图片的保存名称"
                }),
            },
            "optional": {
                # 预定义的图片输入端口
                "image_2": ("IMAGE", {"forceInput": True}),
                "save_name_2": ("STRING", {"default": "image"}),
                "image_3": ("IMAGE", {"forceInput": True}),
                "save_name_3": ("STRING", {"default": "image"}),
                "image_4": ("IMAGE", {"forceInput": True}),
                "save_name_4": ("STRING", {"default": "image"}),
                "image_5": ("IMAGE", {"forceInput": True}),
                "save_name_5": ("STRING", {"default": "image"}),
                "image_6": ("IMAGE", {"forceInput": True}),
                "save_name_6": ("STRING", {"default": "image"}),
                "image_7": ("IMAGE", {"forceInput": True}),
                "save_name_7": ("STRING", {"default": "image"}),
                "image_8": ("IMAGE", {"forceInput": True}),
                "save_name_8": ("STRING", {"default": "image"}),
                "image_9": ("IMAGE", {"forceInput": True}),
                "save_name_9": ("STRING", {"default": "image"}),
                "image_10": ("IMAGE", {"forceInput": True}),
                "save_name_10": ("STRING", {"default": "image"}),
                # 将 output_folder 和 enabled 放在最后
                "output_folder": ("STRING", {
                    "default": "batch_saves",
                    "tooltip": "输出文件夹名称（可使用相对或绝对路径）"
                }),
                "enabled": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Enabled",
                    "label_off": "Disabled",
                    "tooltip": "启用或禁用此节点"
                }),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("save_info",)
    FUNCTION = "save_batch"
    OUTPUT_NODE = True
    CATEGORY = "🚦 ComfyUI_Image_Anything/Batch_Save"
    DESCRIPTION = "动态批量保存多张图片到独立工作流文件夹并输出文本信息"

    def save_batch(self, image_1, title="", description="", text_prompt="", save_name_1="image", output_folder="batch_saves", enabled=True, prompt=None, extra_pnginfo=None, **kwargs):
        """
        批量保存图片到独立文件夹

        Args:
            image_1: 第一张图片
            title: 标题文本（来自上游节点）
            description: 描述文本（来自上游节点）
            text_prompt: Prompt文本（来自上游节点）
            save_name_1: 第一张图片的保存名称
            output_folder: 输出文件夹名
            enabled: 是否启用此节点
            prompt: ComfyUI 提示词元数据（自动传入）
            extra_pnginfo: ComfyUI 额外信息（自动传入）
            **kwargs: 图片和保存名称输入，格式为 image_2, save_name_2, image_3, save_name_3, ...
        """
        # 检查是否启用
        if not enabled:
            # 如果未启用，返回空信息
            return ("Node is disabled",)
        
        # 生成唯一时间戳和文件夹名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"task_{timestamp}"
        batch_folder = task_id

        # 确定保存目录
        # 检查是否为绝对路径（支持 Windows 和 Linux）
        # Windows: C:\, D:\, E:\ 等
        # Linux/Mac: /path/to/dir
        is_absolute = (
            os.path.isabs(output_folder) or  # 标准绝对路径
            (len(output_folder) >= 3 and output_folder[1] == ':')  # Windows 盘符路径 (C:\, D:\, 等)
        )

        if is_absolute:
            base_dir = output_folder
        else:
            base_dir = os.path.join(folder_paths.get_output_directory(), output_folder)

        # 创建主保存目录
        os.makedirs(base_dir, exist_ok=True)

        # 创建批次特定文件夹（时间戳子文件夹）
        batch_dir = os.path.join(base_dir, batch_folder)
        os.makedirs(batch_dir, exist_ok=True)

        # 收集所有图片和前缀
        images_info = []
        saved_files = []

        # 首先处理 image_1 和 prefix_1 (必需参数)
        # 转换 tensor 为 PIL 并保存
        # ComfyUI 图片是 (batch, height, width, channels) 格式
        # 需要去掉 batch 维度才能传给 PIL
        i_array = image_1.cpu().numpy()  # (1, height, width, 3)

        # 去掉 batch 维度（ComfyUI LoadImage 添加的）
        if i_array.ndim == 4 and i_array.shape[0] == 1:
            i_array = i_array[0]  # 变成 (height, width, 3)

        # 现在 i_array 是 (height, width, 3)，可以传给 PIL
        i_array = 255. * i_array
        img = Image.fromarray(np.clip(i_array, 0, 255).astype(np.uint8))

        # 清理保存名称中的路径分隔符，避免被解释为子目录
        clean_save_name_1 = save_name_1.replace('/', '_').replace('\\', '_')
        # 生成文件名：保存名称_序号.png
        filename = f"{clean_save_name_1}_01.png"
        filepath = os.path.join(batch_dir, filename)
        img.save(filepath)

        # 记录信息
        images_info.append({
            "index": 1,
            "save_name": save_name_1,
            "filename": filename,
            "filepath": filepath
        })
        saved_files.append(filepath)

        # 转换并保存图片 - 最多处理10个预定义的输入 (从 image_2 开始)
        for idx in range(2, 11):  # 处理 image_2 到 image_10
            # 获取图片和保存名称
            image_key = f"image_{idx}"
            save_name_key = f"save_name_{idx}"

            # 检查是否提供了相应的图片输入
            if image_key not in kwargs:
                # 如果没有提供相应的图片输入，跳过该索引
                continue

            image_tensor = kwargs[image_key]
            save_name = kwargs.get(save_name_key, "image")

            # 转换 tensor 为 PIL 并保存
            # ComfyUI 图片是 (batch, height, width, channels) 格式
            # 需要去掉 batch 维度才能传给 PIL
            i_array = image_tensor.cpu().numpy()  # (1, height, width, 3)

            # 去掉 batch 维度（ComfyUI LoadImage 添加的）
            if i_array.ndim == 4 and i_array.shape[0] == 1:
                i_array = i_array[0]  # 变成 (height, width, 3)

            # 现在 i_array 是 (height, width, 3)，可以传给 PIL
            i_array = 255. * i_array
            img = Image.fromarray(np.clip(i_array, 0, 255).astype(np.uint8))

            # 清理保存名称中的路径分隔符，避免被解释为子目录
            clean_save_name = save_name.replace('/', '_').replace('\\', '_')
            # 生成文件名：保存名称_序号.png
            filename = f"{clean_save_name}_{idx:02d}.png"
            filepath = os.path.join(batch_dir, filename)
            img.save(filepath)

            # 记录信息
            images_info.append({
                "index": idx,
                "save_name": save_name,
                "filename": filename,
                "filepath": filepath
            })
            saved_files.append(filepath)

        # 保存元数据文件（不包含ComfyUI工作流信息以避免混淆）
        metadata = {
            "task_id": task_id,
            "timestamp": timestamp,
            "output_folder": output_folder,
            "batch_dir": batch_dir,
            "image_count": len(images_info),
            "images": images_info
        }

        # 添加所有文本内容到元数据中
        if title:
            metadata["title"] = title
        if description:
            metadata["description"] = description
        if text_prompt:
            metadata["prompt"] = text_prompt

        # 将save_info内容也添加到metadata中，以便在metadata.json中保留格式化文本
        save_info_lines = [
            f"任务ID: {task_id}",
            f"时间戳: {timestamp}",
            f"输出目录: {batch_dir}",
            f"图片数量: {len(images_info)}",
        ]

        # 添加所有文本信息到输出中
        text_sections = []
        if title:
            text_sections.append(f"标题: {title}")
        if description:
            text_sections.append(f"描述: {description}")
        if text_prompt:
            text_sections.append(f"Prompt: {text_prompt}")

        if text_sections:
            save_info_lines.append("")
            save_info_lines.append("文本信息:")
            save_info_lines.extend(text_sections)

        save_info_lines.append("")
        save_info_lines.append("保存的图片:")
        for img_info in images_info:
            save_info_lines.append(f"  [{img_info['index']}] {img_info['filename']} (保存名称: {img_info['save_name']})")

        save_info = "\n".join(save_info_lines)
        metadata["save_info_text"] = save_info  # 添加格式化文本到metadata

        # 保存可直接加载的完整ComfyUI工作流文件
        if extra_pnginfo is not None and "workflow" in extra_pnginfo:
            workflow_path = os.path.join(batch_dir, "workflow.json")
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump(extra_pnginfo["workflow"], f, indent=2, ensure_ascii=False)

        metadata_path = os.path.join(batch_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # 保存各个文本到对应的文件
        if title:
            title_path = os.path.join(batch_dir, "title.txt")
            with open(title_path, 'w', encoding='utf-8') as f:
                f.write(title)

        if description:
            description_path = os.path.join(batch_dir, "description.txt")
            with open(description_path, 'w', encoding='utf-8') as f:
                f.write(description)

        if text_prompt:
            prompt_path = os.path.join(batch_dir, "prompt.txt")
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(text_prompt)

        # 返回文本信息
        return (save_info,)
