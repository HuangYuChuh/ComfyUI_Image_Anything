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
                "input_count": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "tooltip": "要输入的图片数量（1-5张）"
                }),
                "image_1": ("IMAGE", {"tooltip": "第一张图片"}),
                "prefix_1": ("STRING", {
                    "default": "image",
                    "tooltip": "第一张图片的文件名前缀"
                }),
                "output_folder": ("STRING", {
                    "default": "batch_saves",
                    "tooltip": "输出文件夹名称（可使用相对或绝对路径）"
                }),
            },
            "optional": {
                # 预留的动态输入，ComfyUI 会根据 input_count 自动扩展
                "image_2": ("IMAGE", {"forceInput": True}),
                "prefix_2": ("STRING", {"default": "image"}),
                "image_3": ("IMAGE", {"forceInput": True}),
                "prefix_3": ("STRING", {"default": "image"}),
                "image_4": ("IMAGE", {"forceInput": True}),
                "prefix_4": ("STRING", {"default": "image"}),
                "image_5": ("IMAGE", {"forceInput": True}),
                "prefix_5": ("STRING", {"default": "image"}),
                # 文本输入接口
                "description": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "输入关于这些图片的描述信息（可选）",
                    "tooltip": "输入的文本会保存到文件中"
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
    CATEGORY = "我的工具"
    DESCRIPTION = "动态批量保存多张图片到独立工作流文件夹并输出文本信息"

    def save_batch(self, input_count, output_folder="batch_saves", description="", prompt=None, extra_pnginfo=None, **kwargs):
        """
        批量保存图片到独立文件夹

        Args:
            input_count: 图片数量
            output_folder: 输出文件夹名
            prompt: ComfyUI 提示词（自动传入）
            extra_pnginfo: ComfyUI 额外信息（自动传入）
            **kwargs: 动态图片和前缀输入，格式为 image_1, prefix_1, image_2, prefix_2, ...
        """
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

        print(f"[DEBUG] 输入路径: {output_folder}")
        print(f"[DEBUG] 是否为绝对路径: {is_absolute}")
        print(f"[DEBUG] 父目录: {base_dir}")
        print(f"[DEBUG] 任务目录: {batch_dir}")
        print(f"[DEBUG] 文件将保存到: {batch_dir}")

        # 收集所有图片和前缀
        images_info = []
        saved_files = []

        # 转换并保存图片
        for i in range(1, input_count + 1):
            # 获取图片和前缀
            image_key = f"image_{i}"
            prefix_key = f"prefix_{i}"

            if image_key not in kwargs:
                continue  # 跳过未连接的图片

            image_tensor = kwargs[image_key]
            prefix = kwargs.get(prefix_key, "image")

            # 转换 tensor 为 PIL 并保存
            i_numpy = image_tensor.cpu().numpy()
            original_shape = i_numpy.shape

            # 先尝试与 ComfyUI 核心保持一致的方法
            try:
                i_numpy = 255. * i_numpy
                img = Image.fromarray(np.clip(i_numpy, 0, 255).astype(np.uint8))
            except (TypeError, ValueError):
                # 如果失败，尝试多种备用方案
                i_numpy = np.squeeze(i_numpy)

                # 尝试不同的处理策略
                if i_numpy.ndim == 3:
                    # (H, W, C) 或 (C, H, W)
                    if i_numpy.shape[0] == 3 or i_numpy.shape[0] == 4:
                        # (C, H, W) -> (H, W, C)
                        i_numpy = np.transpose(i_numpy, (1, 2, 0))
                    elif i_numpy.shape[0] == 1:
                        # (1, H, W) -> (H, W)
                        i_numpy = i_numpy.squeeze(0)
                elif i_numpy.ndim == 2:
                    # (H, W) - 保持不变
                    pass
                else:
                    # 异常形状，尝试 reshape
                    total_size = i_numpy.size
                    if total_size == 3 * 512 * 512:
                        i_numpy = i_numpy.reshape(512, 512, 3)
                    elif total_size == 3 * 1024 * 1024:
                        i_numpy = i_numpy.reshape(1024, 1024, 3)
                    elif total_size == 3 * 768 * 768:
                        i_numpy = i_numpy.reshape(768, 768, 3)
                    else:
                        # 最后一个尝试：假设是 (H, W) 格式
                        # 但要确保 W 至少是 3（RGB 通道）
                        h, w = i_numpy.shape
                        if w < h and w <= 4:
                            # 可能是 (W, H) 而不是 (H, W)，交换
                            i_numpy = i_numpy.T
                        # 如果还是不对，就尝试 reshape
                        if i_numpy.ndim == 2 and i_numpy.shape[1] <= 4:
                            # 假设形状是 (H*W, C)，重构
                            img_array = np.zeros((h, 1, 3))
                            img_array[:h, 0, :min(3, w)] = i_numpy[:, :3]
                            i_numpy = img_array

                i_numpy = 255. * i_numpy
                img = Image.fromarray(np.clip(i_numpy, 0, 255).astype(np.uint8))

            # 生成文件名：前缀_序号.png
            filename = f"{prefix}_{i:02d}.png"
            filepath = os.path.join(batch_dir, filename)
            img.save(filepath)

            # 记录信息
            images_info.append({
                "index": i,
                "prefix": prefix,
                "filename": filename,
                "filepath": filepath
            })
            saved_files.append(filepath)

        # 保存元数据文件
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

        if prompt is not None:
            metadata["prompt"] = prompt
        if extra_pnginfo is not None:
            metadata["extra_pnginfo"] = extra_pnginfo

        metadata_path = os.path.join(batch_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # 创建文本信息
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
            save_info_lines.append(f"  [{img_info['index']}] {img_info['filename']} (前缀: {img_info['prefix']})")

        save_info = "\n".join(save_info_lines)

        # 保存文本信息到文件
        save_info_path = os.path.join(batch_dir, "save_info.txt")
        with open(save_info_path, 'w', encoding='utf-8') as f:
            f.write(save_info)

        # 返回文本信息
        return (save_info,)
