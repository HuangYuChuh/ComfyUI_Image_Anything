/**
 * text_blocker.js - 使用桥接技术的前端实现
 * 
 * 核心技术：
 * 1. 监听ComfyUI原生的executing事件
 * 2. 检测到TextBlocker节点执行时显示编辑框
 * 3. 通过HTTP POST发送编辑结果（不是WebSocket）
 */

import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

console.log("[text_blocker] init: loading module");
console.log("[text_blocker] app:", !!app, "api:", !!api);

// CSS样式 - 完全遵循ComfyUI设计规范
const modalStyles = `
.text-blocker-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    justify-content: flex-end;
    z-index: 10000;
}

.text-blocker-modal {
    background: var(--comfy-menu-bg, #353535);
    color: var(--fg-color, #fff);
    border-left: 1px solid var(--border-color, #4e4e4e);
    box-shadow: -4px 0 16px rgba(0, 0, 0, 0.4);
    width: 360px;
    max-width: 90vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    animation: slideLeft 0.2s ease-out;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

@keyframes slideLeft {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}

@keyframes slideRight {
    from { transform: translateX(0); }
    to { transform: translateX(100%); }
}

@keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
}

/* Header */
.text-blocker-header {
    padding: 14px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color, #4e4e4e);
}

.text-blocker-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--fg-color, #fff);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.text-blocker-badge {
    font-size: 10px;
    padding: 2px 6px;
    background: var(--comfy-menu-secondary-bg, #292929);
    border-radius: 4px;
    color: var(--descrip-text, #999);
    font-weight: 500;
}

/* Close Button - 使用 ComfyUI button-surface */
.text-blocker-close {
    background: var(--comfy-menu-secondary-bg, #292929);
    border: none;
    color: var(--descrip-text, #999);
    width: 28px;
    height: 28px;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: background-color 0.15s, color 0.15s;
}

.text-blocker-close:hover {
    background: var(--content-bg, #4e4e4e);
    color: var(--fg-color, #fff);
}

/* Body */
.text-blocker-body {
    padding: 16px;
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

/* Textarea - 遵循 comfy-input 风格 */
.text-blocker-textarea {
    width: 100%;
    flex: 1;
    padding: 10px 12px;
    background: var(--comfy-input-bg, #222);
    color: var(--input-text, #ddd);
    border: 1px solid var(--border-color, #4e4e4e);
    border-radius: 4px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 13px;
    line-height: 1.5;
    resize: none;
    box-sizing: border-box;
    outline: none;
}

.text-blocker-textarea:focus {
    border-color: var(--primary-bg, #236692);
}

/* Footer */
.text-blocker-footer {
    padding: 12px 16px;
    border-top: 1px solid var(--border-color, #4e4e4e);
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.text-blocker-stats {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: var(--descrip-text, #999);
}

.text-blocker-buttons {
    display: flex;
    gap: 8px;
}

/* Button Base - 遵循 ComfyUI button 样式 */
.text-blocker-button {
    flex: 1;
    height: 32px;
    padding: 0 16px;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    cursor: pointer;
    transition: background-color 0.15s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    white-space: nowrap;
}

/* Secondary Button (Cancel) - content-bg */
.text-blocker-button-cancel {
    background: var(--content-bg, #4e4e4e);
    color: var(--content-fg, #fff);
}

.text-blocker-button-cancel:hover {
    background: var(--content-hover-bg, #222);
}

/* Primary Button (Confirm) - primary-bg */
.text-blocker-button-confirm {
    background: var(--primary-bg, #236692);
    color: var(--primary-fg, #fff);
}

.text-blocker-button-confirm:hover {
    background: var(--primary-hover-bg, #3485bb);
}

/* Disabled state */
.text-blocker-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
`;

// 创建模态框
class TextBlockerModal {
    constructor(nodeId, initialText) {
        this.nodeId = nodeId;
        this.initialText = initialText || "";
        this.overlay = null;
        this.textarea = null;
        this.onConfirm = null;
        this.onCancel = null;

        console.log(`[text_blocker] modal: create node=${nodeId}`);
    }

    create() {
        // 创建遮罩层
        this.overlay = document.createElement('div');
        this.overlay.className = 'text-blocker-overlay';

        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'text-blocker-modal';

        // 头部
        const header = document.createElement('div');
        header.className = 'text-blocker-header';
        header.innerHTML = `
            <h3 class="text-blocker-title">
                编辑文本
                <span class="text-blocker-badge">阻塞</span>
            </h3>
            <button class="text-blocker-close" aria-label="关闭">×</button>
        `;

        // 内容区域
        const body = document.createElement('div');
        body.className = 'text-blocker-body';

        this.textarea = document.createElement('textarea');
        this.textarea.className = 'text-blocker-textarea';
        this.textarea.value = this.initialText;
        this.textarea.placeholder = "在此编辑文本...";

        body.appendChild(this.textarea);

        // 底部
        const footer = document.createElement('div');
        footer.className = 'text-blocker-footer';
        footer.innerHTML = `
            <div class="text-blocker-stats">
                <span class="text-blocker-char-count">字符数: ${this.initialText.length}</span>
                <span style="opacity: 0.5">ID: ${this.nodeId}</span>
            </div>
            <div class="text-blocker-buttons">
                <button class="text-blocker-button text-blocker-button-cancel">
                    取消
                </button>
                <button class="text-blocker-button text-blocker-button-confirm">
                    确认
                </button>
            </div>
        `;

        modal.appendChild(header);
        modal.appendChild(body);
        modal.appendChild(footer);
        this.overlay.appendChild(modal);

        // 绑定事件
        this.bindEvents(header, footer);

        return this.overlay;
    }

    bindEvents(header, footer) {
        // 关闭按钮
        const closeBtn = header.querySelector('.text-blocker-close');
        closeBtn.onclick = () => {
            console.log("[text_blocker] user: close");
            this.cancel();
        };

        // 取消按钮
        const cancelBtn = footer.querySelector('.text-blocker-button-cancel');
        cancelBtn.onclick = () => {
            console.log("[text_blocker] user: cancel");
            this.cancel();
        };

        // 确认按钮
        const confirmBtn = footer.querySelector('.text-blocker-button-confirm');
        confirmBtn.onclick = () => {
            console.log("[text_blocker] user: confirm");
            this.confirm();
        };

        // 点击遮罩层关闭
        this.overlay.onclick = (e) => {
            if (e.target === this.overlay) {
                console.log("[text_blocker] user: overlay_click");
                this.cancel();
            }
        };

        // 快捷键支持
        this.textarea.onkeydown = (e) => {
            // Ctrl+Enter 确认
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                console.log("[text_blocker] user: ctrl+enter");
                this.confirm();
            }
            // Esc 取消
            if (e.key === 'Escape') {
                e.preventDefault();
                console.log("[text_blocker] user: esc");
                this.cancel();
            }
        };

        // 更新字符数
        const charCount = footer.querySelector('.text-blocker-char-count');
        this.textarea.oninput = () => {
            charCount.textContent = `字符数: ${this.textarea.value.length}`;
        };

        // 自动聚焦
        setTimeout(() => {
            this.textarea.focus();
            this.textarea.select();
        }, 100);
    }

    show() {
        // 添加样式表
        if (!document.getElementById('text-blocker-styles')) {
            const style = document.createElement('style');
            style.id = 'text-blocker-styles';
            style.textContent = modalStyles;
            document.head.appendChild(style);
            console.log("[text_blocker] styles: injected");
        }

        // 显示模态框
        document.body.appendChild(this.create());
        console.log("[text_blocker] modal: shown");
    }

    hide() {
        if (this.overlay && this.overlay.parentNode) {
            // 侧边栏滑出动画
            const modal = this.overlay.querySelector('.text-blocker-modal');
            if (modal) {
                modal.style.animation = 'slideRight 0.2s ease-in forwards';
            }
            // 遮罩淡出
            this.overlay.style.animation = 'fadeOut 0.2s ease-out forwards';

            setTimeout(() => {
                if (this.overlay.parentNode) {
                    this.overlay.parentNode.removeChild(this.overlay);
                }
            }, 200);
            console.log("[text_blocker] modal: hidden");
        }
    }

    confirm() {
        const text = this.textarea.value;
        console.log(`[text_blocker] submit: len=${text.length}`);
        if (this.onConfirm) {
            this.onConfirm(text);
        }
        this.hide();
    }

    cancel() {
        console.log("[text_blocker] submit: cancelled");
        if (this.onCancel) {
            this.onCancel();
        }
        this.hide();
    }
}

// 跟踪当前正在编辑的节点
let currentEditingNode = null;
let pendingNodes = new Set();  // 等待处理的节点

// 核心：监听executing事件（桥接WebSocket）
console.log("[text_blocker] init: registering executing listener...");

api.addEventListener("executing", (event) => {
    console.log("=".repeat(60));
    console.log("[text_blocker] event: executing");

    console.log("   event:", event);
    console.log("   detail:", event.detail);

    // executing事件的detail直接就是nodeId，不是对象
    const nodeId = event.detail;

    console.log("   node:", nodeId);

    // 如果nodeId为null，表示执行结束
    if (nodeId === null || nodeId === undefined) {
        console.log("[text_blocker] event: workflow_complete");
        console.log("=".repeat(60));
        currentEditingNode = null;
        pendingNodes.clear();
        return;
    }

    console.log("[text_blocker] check: node_type...");
    console.log("   graph:", !!app.graph);
    console.log("   _nodes_by_id:", !!app.graph?._nodes_by_id);

    // 检查是否是TextBlocker节点
    if (app.graph && app.graph._nodes_by_id) {
        const node = app.graph._nodes_by_id[nodeId];

        console.log(`   lookup[${nodeId}]:`, node);
        console.log(`   type:`, node?.type);

        if (node && node.type === "TextBlocker") {
            console.log(`[text_blocker] match: TextBlocker node`);
            console.log(`   id: ${nodeId}`);
            console.log(`   type: ${node.type}`);

            // 检查是否启用
            const enabledWidget = node.widgets?.find(w => w.name === "enabled");
            const isEnabled = enabledWidget ? enabledWidget.value : true;

            console.log(`   enabled:`, enabledWidget);
            console.log(`   value:`, isEnabled);

            if (!isEnabled) {
                console.log(`[text_blocker] skip: disabled`);
                console.log("=".repeat(60));
                return;
            }

            // 获取节点的当前文本
            const textWidget = node.widgets?.find(w => w.name === "text");
            const currentText = textWidget ? textWidget.value : "";

            console.log(`   text:`, textWidget);
            console.log(`   len: ${currentText.length}`);
            console.log(`   preview:`, currentText.substring(0, 50) + "...");

            // 防止重复显示
            if (currentEditingNode === nodeId) {
                console.log(`[text_blocker] skip: already_editing`);
                console.log("=".repeat(60));
                return;
            }

            // 显示编辑模态框
            console.log(`[text_blocker] modal: preparing...`);
            currentEditingNode = nodeId;

            // 异步获取实际的文本值
            showEditorModal(nodeId);
        } else {
            console.log(`   [text_blocker] skip: not_blocker`);
        }
    } else {
        console.error("[text_blocker] error: no graph!");
    }
    console.log("=".repeat(60));
});

async function showEditorModal(nodeId) {
    console.log(`[text_blocker] modal: show node=${nodeId}`);

    // 从后端获取实际的文本值（因为从连接节点传入的文本不在widget中）
    console.log(`[text_blocker] api: get_text...`);
    let actualText = "";

    try {
        const response = await api.fetchApi(`/text_blocker/get_text?node_id=${nodeId}`);
        const data = await response.json();

        if (data.status === "success") {
            actualText = data.text;
            console.log(`[text_blocker] api: got_text，长度: ${actualText.length}`);
            console.log(`   preview: ${actualText.substring(0, 100)}...`);
        } else {
            console.error(`[text_blocker] api: get_text failed:`, data.error);
        }
    } catch (error) {
        console.error(`[text_blocker] api: get_text error:`, error);
    }

    console.log(`[text_blocker] modal: create...`);
    const modal = new TextBlockerModal(nodeId, actualText);

    modal.onConfirm = (editedText) => {
        console.log(`[text_blocker] user: confirmed node=${nodeId}`);

        // 发送HTTP POST（不是WebSocket）
        console.log(`[text_blocker] api: POST /text_blocker/submit`);
        api.fetchApi('/text_blocker/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                node_id: String(nodeId),  // 确保是字符串
                text: editedText,
                cancelled: false
            })
        }).then(response => {
            console.log("[text_blocker] api: success:", response);
            currentEditingNode = null;
        }).catch(error => {
            console.error("[text_blocker] api: failed:", error);
            currentEditingNode = null;
        });
    };

    modal.onCancel = () => {
        console.log(`[text_blocker] user: cancelled - Node: ${nodeId}`);

        // 发送取消信号
        api.fetchApi('/text_blocker/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                node_id: String(nodeId),  // 确保是字符串
                text: actualText,
                cancelled: true
            })
        }).then(response => {
            console.log("[text_blocker] cancel: notified", response);
            currentEditingNode = null;
        }).catch(error => {
            console.error("[text_blocker] cancel: failed", error);
            currentEditingNode = null;
        });
    };

    modal.show();
}

// 注册ComfyUI扩展
app.registerExtension({
    name: "ComfyUI_Image_Anything.TextBlocker.Bridge",

    async setup() {
        console.log("[text_blocker] init: extension setup");
        console.log("[text_blocker] init: listener registered");
    }
});

console.log("🎉 Text Blocker (桥接版) 加载完成!");
