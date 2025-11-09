from .dual_image_saver import BatchImageSaver

NODE_CLASS_MAPPINGS = {
    "BatchImageSaver": BatchImageSaver,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageSaver": "Dynamic Batch Image Saver",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
