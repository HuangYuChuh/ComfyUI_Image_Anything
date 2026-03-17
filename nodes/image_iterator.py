import os
import json
import hashlib
import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import comfy.model_management

# 支持的图片格式
SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff', '.tif', '.gif'}


class ImageIterator:
    """
    图片文件夹迭代器节点

    功能：
    - 从指定文件夹中逐张加载图片
    - 每次执行加载一张图片，自动递增索引
    - 输出图片、遮罩、文件名（不含扩展名）、当前索引、总数
    - 迭代完成后可选择停止或循环
    - 支持 ComfyUI 的 Auto Queue 模式实现自动迭代
    """

    # 用类变量跟踪每个文件夹的迭代状态
    _counters = {}

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "图片文件夹的绝对路径",
                    "tooltip": "包含图片的文件夹路径（绝对路径）"
                }),
                "sort_by": (["name_asc", "name_desc", "modified_asc", "modified_desc"], {
                    "default": "name_asc",
                    "tooltip": "图片排序方式：按名称/修改时间 升序/降序"
                }),
                "mode": (["sequential", "loop"], {
                    "default": "sequential",
                    "tooltip": "sequential: 迭代完所有图片后停止; loop: 循环迭代"
                }),
            },
            "optional": {
                "start_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999999,
                    "step": 1,
                    "tooltip": "起始索引（从0开始），修改此值可跳转到指定位置"
                }),
                "reset": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Reset",
                    "label_off": "Continue",
                    "tooltip": "重置迭代器到起始位置"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "filename", "filename_with_ext", "current_index", "total_count")
    FUNCTION = "load_next_image"
    OUTPUT_NODE = False
    CATEGORY = "🚦 ComfyUI_Image_Anything/Iterator"
    DESCRIPTION = "从文件夹中逐张迭代加载图片，配合Auto Queue使用可自动遍历整个文件夹"

    @classmethod
    def _get_counter_key(cls, folder_path, sort_by):
        """生成唯一的计数器键"""
        return f"{folder_path}|{sort_by}"

    @classmethod
    def _get_image_list(cls, folder_path, sort_by):
        """获取排序后的图片文件列表"""
        if not os.path.isdir(folder_path):
            return []

        files = []
        for f in os.listdir(folder_path):
            ext = os.path.splitext(f)[1].lower()
            full_path = os.path.join(folder_path, f)
            if ext in SUPPORTED_EXTENSIONS and os.path.isfile(full_path):
                files.append(f)

        if sort_by == "name_asc":
            files.sort()
        elif sort_by == "name_desc":
            files.sort(reverse=True)
        elif sort_by == "modified_asc":
            files.sort(key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
        elif sort_by == "modified_desc":
            files.sort(key=lambda f: os.path.getmtime(os.path.join(folder_path, f)), reverse=True)

        return files

    def load_next_image(self, folder_path, sort_by="name_asc", mode="sequential",
                        start_index=0, reset=False):
        """
        加载文件夹中的下一张图片

        Args:
            folder_path: 图片文件夹路径
            sort_by: 排序方式
            mode: 迭代模式 (sequential/loop)
            start_index: 起始索引
            reset: 是否重置迭代器
        """
        # 验证文件夹路径
        if not folder_path or not os.path.isdir(folder_path):
            raise ValueError(f"无效的文件夹路径: {folder_path}")

        # 获取图片列表
        image_files = self._get_image_list(folder_path, sort_by)
        total_count = len(image_files)

        if total_count == 0:
            raise ValueError(f"文件夹中没有找到支持的图片文件: {folder_path}")

        # 获取/更新计数器
        counter_key = self._get_counter_key(folder_path, sort_by)

        if reset or counter_key not in ImageIterator._counters:
            # 重置或首次运行，使用 start_index
            current_index = start_index
        else:
            current_index = ImageIterator._counters[counter_key]

        # 处理索引越界
        if current_index >= total_count:
            if mode == "loop":
                current_index = 0
            else:
                # sequential 模式，迭代结束，中断处理
                # 重置计数器以便下次使用
                ImageIterator._counters[counter_key] = 0
                comfy.model_management.interrupt_current_processing()
                raise comfy.model_management.InterruptProcessingException()

        # 加载当前图片
        image_filename = image_files[current_index]
        image_path = os.path.join(folder_path, image_filename)

        # 提取文件名（不含扩展名）
        filename_no_ext = os.path.splitext(image_filename)[0]

        # 使用与 ComfyUI LoadImage 一致的方式加载图片
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)

        output_images = []
        output_masks = []

        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)

            if i.mode == 'I':
                i = i.point(lambda x: x * (1 / 255))
            image = i.convert("RGB")

            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            elif i.mode == 'P' and 'transparency' in i.info:
                mask = np.array(i.convert('RGBA').getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

            output_images.append(image_tensor)
            output_masks.append(mask.unsqueeze(0))

            if img.format == "MPO":
                break

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        # 更新计数器为下一张
        ImageIterator._counters[counter_key] = current_index + 1

        return (output_image, output_mask, filename_no_ext, image_filename,
                current_index, total_count)

    @classmethod
    def IS_CHANGED(cls, folder_path, sort_by="name_asc", mode="sequential",
                   start_index=0, reset=False):
        """每次都返回不同的值，确保节点在 Auto Queue 模式下重新执行"""
        counter_key = cls._get_counter_key(folder_path, sort_by)
        current = cls._counters.get(counter_key, start_index)
        # 返回当前索引作为变化标识，确保每次执行都被视为"已变化"
        return f"{current}_{reset}"
