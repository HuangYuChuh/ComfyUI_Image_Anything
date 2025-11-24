import os
import json
import torch
import numpy as np
from PIL import Image
import folder_paths
from datetime import datetime

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
                # 文本输入接口 - 放在 image_1 下方
                "description": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "输入关于这些图片的描述信息（可选）",
                    "tooltip": "输入的文本会保存到文件中"
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
    CATEGORY = "ComfyUI_Image_Anything"
    DESCRIPTION = "动态批量保存多张图片到独立工作流文件夹并输出文本信息"

    def save_batch(self, image_1, description="", save_name_1="image", output_folder="batch_saves", enabled=True, prompt=None, extra_pnginfo=None, **kwargs):
        """
        批量保存图片到独立文件夹

        Args:
            image_1: 第一张图片
            description: 描述文本
            save_name_1: 第一张图片的保存名称
            output_folder: 输出文件夹名
            enabled: 是否启用此节点
            prompt: ComfyUI 提示词（自动传入）
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

        # 转换并保存图片 - 最多处理5个预定义的输入 (从 image_2 开始)
        for idx in range(2, 6):  # 处理 image_2 到 image_5
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

        # 如果有描述文本，添加到元数据中
        if description:
            metadata["description"] = description

        # 将save_info内容也添加到metadata中，以便在metadata.json中保留格式化文本
        save_info_lines = [
            f"任务ID: {task_id}",
            f"时间戳: {timestamp}",
            f"输出目录: {batch_dir}",
            f"图片数量: {len(images_info)}",
        ]

        # 如果有描述文本，添加到输出中
        if description:
            save_info_lines.append("")
            save_info_lines.append("描述信息:")
            save_info_lines.append(description)

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

        # 保存 Prompt 文本到单独文件（使用 description 参数的纯文本）
        if description:
            prompt_path = os.path.join(batch_dir, "prompt.txt")
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(description)

        # 返回文本信息
        return (save_info,)
