#!/usr/bin/env python3
"""
测试新的模块化节点功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nodes.batch_image_saver import ImageCollector, BatchImageSaverV2
import torch
import numpy as np
from PIL import Image

def create_test_image(color=(255, 0, 0), size=(64, 64)):
    """创建测试图片"""
    img = Image.new('RGB', size, color)
    # 转换为ComfyUI格式 (batch, height, width, channels)
    img_array = np.array(img).astype(np.float32) / 255.0
    img_tensor = torch.from_numpy(img_array).unsqueeze(0)
    return img_tensor

def test_image_collector():
    """测试ImageCollector节点"""
    print("=== 测试 ImageCollector 节点 ===")

    collector = ImageCollector()

    # 创建测试图片
    img1 = create_test_image((255, 0, 0))  # 红色
    img2 = create_test_image((0, 255, 0))  # 绿色
    img3 = create_test_image((0, 0, 255))  # 蓝色

    # 测试收集3张图片
    batch_data, batch_info = collector.collect_images(
        group_name="test_group",
        image_1=img1,
        save_name_1="red_image",
        image_2=img2,
        save_name_2="green_image",
        image_3=img3,
        save_name_3="blue_image"
    )

    print(f"批次信息: {batch_info}")
    print(f"收集的图片数量: {batch_data['total_count']}")
    print(f"组名: {batch_data['group_name']}")

    # 验证数据格式
    assert isinstance(batch_data, dict)
    assert "images" in batch_data
    assert "group_name" in batch_data
    assert "total_count" in batch_data
    assert batch_data["total_count"] == 3

    print("✓ ImageCollector 测试通过")
    return batch_data

def test_batch_saver_v2():
    """测试BatchImageSaverV2节点"""
    print("\n=== 测试 BatchImageSaverV2 节点 ===")

    saver = BatchImageSaverV2()

    # 创建测试批次数据（模拟ImageCollector的输出）
    batch1 = {
        "images": [
            {
                "image": Image.new('RGB', (64, 64), (255, 0, 0)),
                "save_name": "test_red",
                "original_index": 1
            },
            {
                "image": Image.new('RGB', (64, 64), (0, 255, 0)),
                "save_name": "test_green",
                "original_index": 2
            }
        ],
        "group_name": "batch_1",
        "total_count": 2
    }

    batch2 = {
        "images": [
            {
                "image": Image.new('RGB', (64, 64), (0, 0, 255)),
                "save_name": "test_blue",
                "original_index": 1
            }
        ],
        "group_name": "batch_2",
        "total_count": 1
    }

    # 测试保存功能
    save_info = saver.save_batches(
        title="测试标题",
        description="测试描述",
        text_prompt="测试prompt",
        output_folder="test_output",
        enabled=True,
        batch_1=batch1,
        batch_2=batch2
    )

    print(f"保存信息:\n{save_info[0]}")
    print("✓ BatchImageSaverV2 测试通过")

def test_optional_inputs():
    """测试可选输入功能"""
    print("\n=== 测试可选输入功能 ===")

    collector = ImageCollector()

    # 只连接2张图片
    img1 = create_test_image((255, 255, 0))  # 黄色
    img2 = create_test_image((255, 0, 255))  # 紫色

    batch_data, batch_info = collector.collect_images(
        group_name="partial_test",
        image_1=img1,
        save_name_1="yellow_image",
        image_2=img2,
        save_name_2="purple_image"
        # image_3, image_4, image_5 不连接
    )

    print(f"批次信息: {batch_info}")
    print(f"收集的图片数量: {batch_data['total_count']}")
    assert batch_data["total_count"] == 2
    print("✓ 可选输入测试通过")

if __name__ == "__main__":
    print("开始测试新的模块化节点...")

    try:
        # 运行所有测试
        test_image_collector()
        test_batch_saver_v2()
        test_optional_inputs()

        print("\n🎉 所有测试通过！新节点功能正常。")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)