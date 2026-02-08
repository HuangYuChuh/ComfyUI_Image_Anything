
from .nodes.batch_image_saver import BatchImageSaverV2, ImageCollector, TextCollector
from .nodes.dataset_utils import EditDatasetLoader, EditDatasetSaver
from .nodes.smart_resize import SmartImageResizeForBucket
from .nodes.text_blocker import TextBlocker

# 节点类映射 - ComfyUI 核心注册
NODE_CLASS_MAPPINGS = {
    "BatchImageSaverV2": BatchImageSaverV2,
    "ImageCollector": ImageCollector,
    "TextCollector": TextCollector,
    "EditDatasetLoader": EditDatasetLoader,
    "EditDatasetSaver": EditDatasetSaver,
    "SmartImageResizeForBucket": SmartImageResizeForBucket,
    "TextBlocker": TextBlocker,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageSaverV2": "Batch Image Saver (Dynamic)",
    "ImageCollector": "Image Collector",
    "TextCollector": "Text Collector",
    "EditDatasetLoader": "Edit Dataset Loader",
    "EditDatasetSaver": "Edit Dataset Saver",
    "SmartImageResizeForBucket": "Smart Image Resize for Bucket",
    "TextBlocker": "Text Blocker",
}

# Web 目录路径，用于加载前端JavaScript
import os
WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "web")

# 导出所有必要的变量
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
