import os
import torch
import numpy as np
from PIL import Image, ImageOps

# Global counter to track iteration progress per directory
_LOADER_COUNTERS = {}
_SAVER_COUNTERS = {}

class EditDatasetLoader:
    """
    Generic Folder Image Loader (Iterator)
    
    Logic:
    1. Scans `directory` for images.
    2. Returns image at `start_index` (or auto-incremented index).
    3. Returns filename stem for downstream use.
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": ("STRING", {"default": "", "multiline": False, "tooltip": "Path to image folder"}),
                "start_index": ("INT", {"default": 0, "min": 0, "max": 999999, "step": 1}),
                "auto_next": ("BOOLEAN", {"default": True, "label_on": "Auto Next", "label_off": "Fixed Index"}),
                "reset_iterator": ("BOOLEAN", {"default": False, "label_on": "Reset Index", "label_off": "Continue"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "filename_stem")
    FUNCTION = "load_data"
    CATEGORY = "ComfyUI_Image_Anything/Edit_Image"

    @classmethod
    def IS_CHANGED(s, directory, start_index, auto_next, reset_iterator, **kwargs):
        if reset_iterator:
            return float("NaN")
        if not auto_next:
            return float("nan")
        return float("NaN")

    def load_data(self, directory, start_index, auto_next, reset_iterator):
        global _LOADER_COUNTERS
        
        if not os.path.exists(directory):
            print(f"EditDatasetLoader: Directory {directory} not found.")
            return (self._empty_image(), "")

        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        
        # Scan images
        files = [f for f in os.listdir(directory) 
                 if os.path.splitext(f)[1].lower() in valid_extensions]
        files.sort()
        
        if not files:
            print(f"EditDatasetLoader: No images found in {directory}")
            return (self._empty_image(), "")

        # Manage counter
        key = directory
        if reset_iterator or key not in _LOADER_COUNTERS:
            _LOADER_COUNTERS[key] = start_index
            if reset_iterator:
                 print(f"EditDatasetLoader: Iterator reset to {start_index} for {directory}")

        final_index = start_index
        if auto_next:
            final_index = _LOADER_COUNTERS[key]

        if final_index >= len(files):
            print(f"EditDatasetLoader: Index {final_index} out of range (Total: {len(files)}). Stopping.")
            return (self._empty_image(), "")

        # Get Image
        filename = files[final_index]
        image_path = os.path.join(directory, filename)
        current_stem = os.path.splitext(filename)[0]
        
        # Update counter
        if auto_next:
            _LOADER_COUNTERS[key] += 1
            print(f"EditDatasetLoader: Processed {current_stem} ({final_index}). Next: {final_index + 1}")

        # Load image
        tensor = self._load_img(image_path)

        return (tensor, current_stem)

    def _load_img(self, path):
        if not path or not os.path.exists(path):
            return self._empty_image()
        try:
            i = Image.open(path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            return image
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return self._empty_image()

    def _empty_image(self):
        return torch.zeros((1, 512, 512, 3), dtype=torch.float32)


class EditDatasetSaver:
    """
    Split Directory Dataset Saver
    
    Structure:
    Output_Root/
    ├── control_images/
    └── target_images/
    
    Naming Logic:
    - Keep Original: Uses filename_stem
    - Rename (Prefix + Index): Uses filename_prefix + index
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "output_root": ("STRING", {"default": "", "tooltip": "Root directory for saving"}),
                "naming_style": (["Keep Original", "Rename (Prefix + Index)"],),
                "filename_prefix": ("STRING", {"default": "AnyBG"}),
                "index": ("INT", {"default": 0, "min": 0, "max": 999999}),
            },
            "optional": {
                "filename_stem": ("STRING", {"default": "", "forceInput": True}),
                "save_image_control": ("IMAGE",),
                "save_image_target": ("IMAGE",),
                "save_caption": ("STRING", {"forceInput": True}),
                "save_format": (["jpg", "png", "webp"],),
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save_dataset"
    CATEGORY = "ComfyUI_Image_Anything/Edit_Image"

    def save_dataset(self, output_root, naming_style, filename_prefix, index,
                     filename_stem="", save_image_control=None, save_image_target=None, save_caption=None,
                     save_format="jpg"):

        if not output_root:
            print("EditDatasetSaver: No output_root provided.")
            return {}

        # Prepare subfolders
        control_dir = os.path.join(output_root, "control_images")
        target_dir = os.path.join(output_root, "target_images")
        os.makedirs(control_dir, exist_ok=True)
        os.makedirs(target_dir, exist_ok=True)

        # Determine filename
        if naming_style == "Rename (Prefix + Index)":
            global _SAVER_COUNTERS
            key = f"{output_root}_{filename_prefix}"
            
            if key not in _SAVER_COUNTERS:
                max_idx = -1
                # Scan directories to find max index
                dirs_to_check = [control_dir, target_dir]
                for d in dirs_to_check:
                    if os.path.exists(d):
                        for f in os.listdir(d):
                            if f.startswith(filename_prefix):
                                # expect format: prefix_00000.ext
                                try:
                                    # strip extension
                                    base = os.path.splitext(f)[0]
                                    # strip prefix
                                    remain = base[len(filename_prefix):]
                                    if remain.startswith('_') and remain[1:].isdigit():
                                        idx = int(remain[1:])
                                        if idx > max_idx:
                                            max_idx = idx
                                except:
                                    continue
                _SAVER_COUNTERS[key] = max_idx + 1
            
            # Use the greater of global counter or user input
            current_idx = max(_SAVER_COUNTERS[key], index)
            final_name = f"{filename_prefix}_{current_idx:04d}"
            
            # Update global counter
            _SAVER_COUNTERS[key] = current_idx + 1

        else:
            final_name = filename_stem if filename_stem else f"unknown_{index}"

        print(f"EditDatasetSaver: Saving {final_name} (Style: {naming_style})...")

        quality = 95 # Hardcoded high quality

        # Save Control Image
        if save_image_control is not None:
            filename = f"{final_name}.{save_format}"
            path = os.path.join(control_dir, filename)
            self._save_image(save_image_control, path, save_format, quality)

        # Save Target Image
        if save_image_target is not None:
            filename = f"{final_name}.{save_format}"
            path = os.path.join(target_dir, filename)
            self._save_image(save_image_target, path, save_format, quality)

        # Save Caption
        if save_caption is not None:
            filename = f"{final_name}.txt"
            path = os.path.join(target_dir, filename)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(save_caption)
            except Exception as e:
                print(f"Error saving caption {path}: {e}")

        return {}

    def _save_image(self, tensor, path, format, quality):
        try:
            img_tensor = tensor[0]
            i = 255. * img_tensor.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Handle JPG transparency
            if format == 'jpg' and img.mode == 'RGBA':
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
                
            img.save(path, optimize=True, quality=quality)
        except Exception as e:
            print(f"Error saving image {path}: {e}")
