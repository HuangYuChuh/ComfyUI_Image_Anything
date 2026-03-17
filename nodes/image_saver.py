import os
import numpy as np
from PIL import Image
import folder_paths


class ImageSaver:
    """
    图片保存节点

    功能：
    - 接收处理好的图片和文件名（可从 Image Iterator 传入）
    - 支持自定义保存路径
    - 支持选择保存格式和质量
    """

    def __init__(self):
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING", {
                    "default": "image",
                    "forceInput": True,
                    "tooltip": "保存的文件名（不含扩展名），可从 Image Iterator 的 filename 输出连接"
                }),
                "save_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "保存路径（绝对路径），留空则保存到 ComfyUI 输出目录",
                    "tooltip": "图片保存的文件夹路径"
                }),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("save_info",)
    FUNCTION = "save_image"
    OUTPUT_NODE = True
    CATEGORY = "🚦 ComfyUI_Image_Anything/Iterator"
    DESCRIPTION = "保存处理后的图片，支持自定义路径和文件名，可配合 Image Iterator 使用"

    def save_image(self, image, filename, save_path=""):
        # 确定保存目录
        if save_path and save_path.strip():
            output_dir = save_path.strip()
        else:
            output_dir = folder_paths.get_output_directory()

        os.makedirs(output_dir, exist_ok=True)

        # 转换 tensor 为 PIL Image
        # image shape: (batch, height, width, channels)
        i_array = image.cpu().numpy()
        if i_array.ndim == 4:
            i_array = i_array[0]

        i_array = (np.clip(i_array, 0, 1) * 255).astype(np.uint8)
        img = Image.fromarray(i_array)

        # 构建完整文件路径
        full_filename = f"{filename}.png"
        filepath = os.path.join(output_dir, full_filename)

        # 避免覆盖：如果文件已存在则加编号
        if os.path.exists(filepath):
            base = filename
            counter = 1
            while os.path.exists(filepath):
                full_filename = f"{base}_{counter:03d}.png"
                filepath = os.path.join(output_dir, full_filename)
                counter += 1

        # 保存无损 PNG
        img.save(filepath, format="PNG")

        save_info = f"{filepath}"
        return (save_info,)
