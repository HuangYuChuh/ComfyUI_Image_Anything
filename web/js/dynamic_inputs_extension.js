/**
 * ComfyUI Image Anything - 动态输入扩展注册
 * 确保动态输入JavaScript被正确加载
 */

import { app } from "../../../scripts/app.js";

// 添加文件加载日志
console.log("[DynamicInput] JavaScript 文件已加载");

/**
 * 动态输入管理器 - 简化的核心实现
 */
class DynamicInputManager {
    constructor() {
        this.minEmptyPorts = 1; // 最少保持1个空端口
    }

    /**
     * 为节点设置动态输入管理
     */
    setupNode(node) {
        if (node.type !== "BatchImageSaverV2") return;

        console.log(`[DynamicInput] 设置节点 ${node.id} 的动态输入管理`);

        // 初始化属性
        node.properties = node.properties || {};
        node.properties.dynamic_input_manager = {
            next_image_index: 2,  // 从2开始，因为初始有1个
            next_text_index: 2,   // 从2开始，因为初始有1个
            initialized: true
        };

        // 确保初始端口存在
        this.ensureInitialPorts(node);

        // 设置连接监听
        this.setupConnectionMonitoring(node);
    }

    /**
     * 确保初始端口存在
     */
    ensureInitialPorts(node) {
        let hasImageBatch = false;
        let hasTextBatch = false;

        // 检查现有端口
        if (node.inputs) {
            for (let input of node.inputs) {
                if (input.name === "image_batch_1") hasImageBatch = true;
                if (input.name === "text_batch_1") hasTextBatch = true;
            }
        }

        // 如果缺少初始端口，添加它们
        if (!hasImageBatch) {
            node.addInput("image_batch_1", "IMAGE_BATCH", { label: "Image Batch 1" });
            console.log("[DynamicInput] 添加了初始图片批次端口");
        }
        if (!hasTextBatch) {
            node.addInput("text_batch_1", "TEXT_BATCH", { label: "Text Batch 1" });
            console.log("[DynamicInput] 添加了初始文本批次端口");
        }
    }

    /**
     * 设置连接监控
     */
    setupConnectionMonitoring(node) {
        const original_onConnectionsChange = node.onConnectionsChange;

        node.onConnectionsChange = function(type, index, connected, link_info) {
            // 调用原始方法
            if (original_onConnectionsChange) {
                original_onConnectionsChange.apply(this, arguments);
            }

            // 处理动态输入逻辑
            if (type === LiteGraph.INPUT) {
                const input = this.inputs[index];
                if (input && (input.name.startsWith("image_batch_") || input.name.startsWith("text_batch_"))) {
                    console.log(`[DynamicInput] 检测到 ${connected ? '连接' : '断开'}: ${input.name}`);

                    // 延迟执行，确保状态稳定
                    setTimeout(() => {
                        this.adjustDynamicPorts();
                    }, 10);
                }
            }
        }.bind(node);

        // 添加端口调整方法
        node.adjustDynamicPorts = function() {
            console.log(`[DynamicInput] 调整节点 ${this.id} 的动态端口`);

            // 处理图片批次端口
            this.adjustPortGroup("image_batch_", "IMAGE_BATCH", "Image Batch");

            // 处理文本批次端口
            this.adjustPortGroup("text_batch_", "TEXT_BATCH", "Text Batch");
        }.bind(node);

        // 添加端口组调整方法
        node.adjustPortGroup = function(prefix, type, label) {
            const manager = this.properties.dynamic_input_manager;
            const connectedPorts = [];
            const emptyPorts = [];

            // 分类端口
            this.inputs.forEach((input, index) => {
                if (input.name.startsWith(prefix)) {
                    if (input.link) {
                        connectedPorts.push({input, index});
                    } else {
                        emptyPorts.push({input, index});
                    }
                }
            });

            console.log(`[DynamicInput] ${prefix}: 已连接=${connectedPorts.length}, 空=${emptyPorts.length}`);

            // 确保至少有一个空端口
            if (emptyPorts.length === 0) {
                const nextIndex = prefix === "image_batch_" ? manager.next_image_index : manager.next_text_index;
                const inputName = `${prefix}${nextIndex}`;

                this.addInput(inputName, type, { label: `${label} ${nextIndex}` });

                // 更新索引
                if (prefix === "image_batch_") {
                    manager.next_image_index++;
                } else {
                    manager.next_text_index++;
                }

                console.log(`[DynamicInput] 添加了新端口: ${inputName}`);
            }
            // 如果空端口太多，保留一个，移除多余的
            else if (emptyPorts.length > this.minEmptyPorts) {
                // 保留最后一个空端口，移除其他的
                for (let i = 0; i < emptyPorts.length - this.minEmptyPorts; i++) {
                    const portToRemove = emptyPorts[i];
                    this.removeInput(portToRemove.index);
                    console.log(`[DynamicInput] 移除了空端口: ${portToRemove.input.name}`);
                }
            }
        }.bind(node);
    }
}

// 创建全局实例
const dynamicInputManager = new DynamicInputManager();

/**
 * 注册扩展到 ComfyUI
 */
app.registerExtension({
    name: "ComfyUI_Image_Anything.DynamicInputs",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(`[DynamicInput] 处理节点定义: ${nodeData.name}`);

        if (nodeData.name === "BatchImageSaverV2") {
            console.log(`[DynamicInput] 注册动态输入管理到 ${nodeData.name}`);

            const original_onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const result = original_onNodeCreated ? original_onNodeCreated.apply(this, arguments) : undefined;
                dynamicInputManager.setupNode(this);
                return result;
            };
        }
    },

    async nodeCreated(node) {
        console.log(`[DynamicInput] 节点创建: ${node.type} (ID: ${node.id})`);

        if (node.type === "BatchImageSaverV2") {
            console.log(`[DynamicInput] 节点创建完成: ${node.id}`);
        }
    }
});

console.log("[DynamicInput] ComfyUI Image Anything 动态输入扩展已注册");