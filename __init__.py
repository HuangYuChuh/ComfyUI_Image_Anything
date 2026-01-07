from .nodes.batch_image_saver import BatchImageSaver, BatchImageSaverV2, ImageCollector, TextCollector
from .nodes.dataset_utils import EditDatasetLoader, EditDatasetSaver

# 节点类映射 - ComfyUI 核心注册
NODE_CLASS_MAPPINGS = {
    "BatchImageSaver": BatchImageSaver,        # 原始版本（向后兼容）
    "BatchImageSaverV2": BatchImageSaverV2,    # 新版本（真正的动态输入）
    "ImageCollector": ImageCollector,          # 图片批次子节点
    "TextCollector": TextCollector,            # 文本批次子节点
    "EditDatasetLoader": EditDatasetLoader,
    "EditDatasetSaver": EditDatasetSaver,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageSaver": "Batch Image Saver V1",
    "BatchImageSaverV2": "Batch Image Saver V2 (Dynamic)",
    "ImageCollector": "image_batch",
    "TextCollector": "text_batch",
    "EditDatasetLoader": "Edit Dataset Loader",
    "EditDatasetSaver": "Edit Dataset Saver",
}

# Web 目录路径，用于加载前端JavaScript
WEB_DIRECTORY = "./web"

# 导出所有必要的变量
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
