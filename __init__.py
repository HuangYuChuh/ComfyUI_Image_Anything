from .nodes.batch_image_saver import BatchImageSaver, BatchImageSaverV2, ImageCollector, TextCollector

NODE_CLASS_MAPPINGS = {
    "BatchImageSaver": BatchImageSaver,        # 原始版本（向后兼容）
    "BatchImageSaverV2": BatchImageSaverV2,    # 新版本（模块化设计）
    "ImageCollector": ImageCollector,          # 图片收集器子节点
    "TextCollector": TextCollector,            # 文本收集器子节点
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageSaver": "Dynamic Batch Image Saver (V1)",
    "BatchImageSaverV2": "Dynamic Batch Image Saver (V2)",
    "ImageCollector": "Image Collector",
    "TextCollector": "Text Collector",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
