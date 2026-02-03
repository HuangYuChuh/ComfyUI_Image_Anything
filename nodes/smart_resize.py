import torch
import numpy as np
from PIL import Image

class SmartImageResizeForBucket:
    """
    智能图像分桶预处理 (Smart Image Resize for Bucket)
    自动将图片裁剪缩放至最接近的 AI-Toolkit/SDXL 标准分桶分辨率，确保训练时零拉伸。
    """
    
    def __init__(self):
        self.type = "smart_image_resize_for_bucket"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mode": ([
                    "Smart (Auto Detect)", 
                    "Force 1024x1024 (1:1)", 
                    "Force 832x1152 (3:4)", 
                    "Force 768x1344 (9:16)",
                    "Force 1152x832 (4:3)",
                    "Force 1344x768 (16:9)"
                ], {"default": "Smart (Auto Detect)"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "width", "height")
    FUNCTION = "resize_image"
    CATEGORY = "ComfyUI_Image_Anything/Preprocess"
    DESCRIPTION = "智能缩放裁剪节点，支持多种标准训练分辨率 (SDXL Buckets)。Smart 模式会自动匹配最佳比例。"

    def resize_image(self, image, mode):
        # Define standard buckets (Width, Height, Aspect Ratio)
        # Using exact buckets from ai-toolkit
        buckets = [
            (1024, 1024, 1.0),   # 1:1
            (832, 1152, 0.72),   # ~3:4 (Portrait)
            (1152, 832, 1.38),   # ~4:3 (Landscape)
            (768, 1344, 0.57),   # ~9:16 (Tall Portrait)
            (1344, 768, 1.75),   # ~16:9 (Wide Landscape)
        ]

        # Determine target resolution for the batch based on the first image or force mode
        start_image = image[0]
        input_h, input_w, _ = start_image.shape
        input_ratio = input_w / input_h
        
        target_w, target_h = 1024, 1024 # Default fallback

        if "Force" in mode:
            # Parse resolution from string like "Force 832x1152 (3:4)"
            dims = mode.split(" ")[1] # "832x1152"
            w_str, h_str = dims.split("x")
            target_w = int(w_str)
            target_h = int(h_str)
        else:
            # Smart Mode: Find closest matching bucket ratio
            min_diff = float('inf')
            best_bucket = (1024, 1024)
            
            for (bw, bh, br) in buckets:
                diff = abs(input_ratio - br)
                if diff < min_diff:
                    min_diff = diff
                    best_bucket = (bw, bh)
            
            target_w, target_h = best_bucket

        result_images = []
        
        for i in range(image.shape[0]):
            img_tensor = image[i]
            img_np = img_tensor.cpu().numpy()
            img_pil = Image.fromarray(np.clip(255. * img_np, 0, 255).astype(np.uint8))
            
            # 1. Scale to cover
            src_w, src_h = img_pil.size
            scale_w = target_w / src_w
            scale_h = target_h / src_h
            scale = max(scale_w, scale_h)
            
            new_w = int(src_w * scale)
            new_h = int(src_h * scale)
            
            # 2. Resize (Lanczos)
            img_resized = img_pil.resize((new_w, new_h), Image.LANCZOS)
            
            # 3. Center Crop
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            
            img_cropped = img_resized.crop((left, top, right, bottom))
            
            out_np = np.array(img_cropped).astype(np.float32) / 255.0
            result_images.append(torch.from_numpy(out_np))

        output_tensor = torch.stack(result_images)
        
        return (output_tensor, target_w, target_h)
