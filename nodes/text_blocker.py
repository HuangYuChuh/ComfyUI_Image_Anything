"""
文本阻塞节点 - 使用HTTP桥接技术

技术方案：
- 前端监听ComfyUI原生的executing事件
- 检测到TextBlocker节点执行时显示编辑模态框
- 通过HTTP POST发送编辑结果
- 后端轮询等待HTTP消息
"""

import time
import uuid
from aiohttp import web
from server import PromptServer


class TextBlockerMessage:
    """
    消息管理器 - 使用HTTP POST通信
    
    关键：不依赖WebSocket自定义事件，使用HTTP桥接
    """
    
    # 存储每个节点的等待状态
    stash = {}
    # 存储每个节点的当前文本（供前端查询）
    current_texts = {}
    
    @classmethod
    def set_current_text(cls, node_id, text):
        """存储节点当前的文本，供前端查询"""
        cls.current_texts[node_id] = text
        print(f"[text_blocker] store text: node={node_id} len={len(text)}")
    
    @classmethod
    def get_current_text(cls, node_id):
        """获取节点当前的文本"""
        return cls.current_texts.get(node_id, "")
    
    @classmethod
    def wait_for_message(cls, node_id, timeout=3600):
        """
        轮询等待前端提交的消息
        
        Args:
            node_id: 节点唯一ID
            timeout: 超时时间（秒），默认1小时
        
        Returns:
            编辑后的文本
        
        Raises:
            TimeoutError: 等待超时
            InterruptedError: 用户取消编辑
        """
        # 创建等待槽位
        if node_id not in cls.stash:
            cls.stash[node_id] = {"waiting": True, "result": None}
        
        # 重置状态
        cls.stash[node_id]["waiting"] = True
        cls.stash[node_id]["result"] = None
        
        print(f"[text_blocker] poll: waiting node={node_id}")
        
        # 轮询等待结果
        start_time = time.time()
        poll_count = 0
        
        while cls.stash[node_id]["waiting"]:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"等待超时 (节点ID: {node_id})")
            
            poll_count += 1
            if poll_count % 50 == 0:  # 每5秒打印一次
                print(f"[text_blocker] poll: {int(time.time() - start_time)}s elapsed")
            
            time.sleep(0.1)
        
        result = cls.stash[node_id]["result"]
        
        # 检查是否被取消
        if result is None or result.get("cancelled", False):
            raise InterruptedError("用户取消了编辑")
        
        return result.get("text", "")
    
    @classmethod
    def receive_message(cls, node_id, text, cancelled=False):
        """
        接收前端POST的消息
        
        Args:
            node_id: 节点唯一ID
            text: 编辑后的文本
            cancelled: 是否被取消
        """
        print(f"[text_blocker] recv: node={node_id} cancelled={cancelled}")
        
        if node_id in cls.stash:
            cls.stash[node_id]["waiting"] = False
            cls.stash[node_id]["result"] = {
                "text": text,
                "cancelled": cancelled
            }
        else:
            print(f"[text_blocker] warn: no slot for {node_id}")


# 注册HTTP API路由
@PromptServer.instance.routes.post("/text_blocker/submit")
async def text_blocker_submit(request):
    """
    接收前端提交的文本
    
    关键：使用HTTP POST而不是WebSocket自定义事件
    
    请求格式:
    {
        "node_id": "节点ID",
        "text": "编辑后的文本",
        "cancelled": false
    }
    """
    try:
        data = await request.json()
        node_id = data.get("node_id")
        text = data.get("text", "")
        cancelled = data.get("cancelled", False)
        
        print(f"[text_blocker] POST /submit node={node_id}")
        
        if not node_id:
            return web.json_response(
                {"error": "缺少 node_id 参数"},
                status=400
            )
        
        # 将结果传递给等待的节点
        TextBlockerMessage.receive_message(node_id, text, cancelled)
        
        return web.json_response({"status": "success"})
        
    except Exception as e:
        print(f"[text_blocker] error: {str(e)}")
        return web.json_response(
            {"error": str(e)},
            status=500
        )


@PromptServer.instance.routes.get("/text_blocker/get_text")
async def text_blocker_get_text(request):
    """
    获取节点当前的文本
    
    前端在显示模态框前调用此API获取实际的文本值
    （因为从连接的节点传入的文本不在widget中）
    """
    try:
        node_id = request.query.get("node_id")
        
        if not node_id:
            return web.json_response(
                {"error": "缺少 node_id 参数"},
                status=400
            )
        
        text = TextBlockerMessage.get_current_text(node_id)
        print(f"[text_blocker] GET /get_text node={node_id} len={len(text)}")
        
        return web.json_response({
            "status": "success",
            "text": text
        })
        
    except Exception as e:
        print(f"[text_blocker] error: {str(e)}")
        return web.json_response(
            {"error": str(e)},
            status=500
        )


class TextBlocker:
    """
    文本阻塞节点 - 中继式文本编辑器
    
    作为上游文本的中转编辑节点，不提供自身的文本输入。
    执行时会弹出编辑框，用户可以修改上游传入的文本后继续执行。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "forceInput": True,  # 强制只接收输入，不显示widget
                }),
            },
            "optional": {
                "enabled": ("BOOLEAN", {
                    "default": True,
                    "label_on": "阻塞编辑",
                    "label_off": "直接通过",
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "block_and_edit"
    OUTPUT_NODE = False
    CATEGORY = "🚦 ComfyUI_Image_Anything/Text"
    DESCRIPTION = "中转编辑上游传入的文本，执行时弹出编辑框"
    
    def block_and_edit(self, text, enabled=True, unique_id=None):
        """
        阻塞并等待用户编辑上游传入的文本
        """
        print(f"[TextBlocker] exec: node={unique_id} enabled={enabled} len={len(text)}")
        
        # 如果未启用，直接返回原文本
        if not enabled:
            print("[TextBlocker] disabled, passthrough")
            return (text,)
        
        # 如果没有unique_id，生成一个临时ID
        if unique_id is None:
            unique_id = str(uuid.uuid4())
            print(f"[TextBlocker] generated tmp_id={unique_id}")
        
        # 存储当前文本，供前端查询
        TextBlockerMessage.set_current_text(unique_id, text)
        
        # 开始轮询等待
        print(f"[TextBlocker] blocking, awaiting frontend...")
        
        try:
            edited_text = TextBlockerMessage.wait_for_message(unique_id)
            print(f"[TextBlocker] done: received len={len(edited_text)}")
            return (edited_text,)
        except InterruptedError:
            print(f"[TextBlocker] cancelled, returning original")
            return (text,)
        except TimeoutError as e:
            print(f"[TextBlocker] timeout: {str(e)}")
            return (text,)
        except Exception as e:
            print(f"[TextBlocker] error: {str(e)}")
            import traceback
            traceback.print_exc()
            return (text,)


# 导出节点类映射
NODE_CLASS_MAPPINGS = {
    "TextBlocker": TextBlocker,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextBlocker": "Text Blocker",
}

