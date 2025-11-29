# ComfyUI_Image_Anything - 开发待办事项

## 当前状态
已完成完全解耦的模块化架构（V2版本）：
- ✅ ImageCollector 子节点（1-5张可选图片）
- ✅ TextCollector 子节点（3个文本字段：title/description/prompt）
- ✅ BatchImageSaverV2 主节点（支持图片+文本批次输入）
- ✅ 智能文本优先级逻辑
- ✅ 向后兼容（保留V1版本）

## 待办事项（需要进一步迭代）

### 1. 扩展TextCollector文本字段
**问题**: 当前TextCollector只有3个固定字段（title/description/prompt）
**需求**:
- 支持5个可自定义的文本字段
- 字段名称统称为 `text_1` 到 `text_5`（而不是固定的语义名称）
- 用户可以输入任意内容，不局限于特定类型（标题、描述等）
- 提供更大的灵活性，适应不同的使用场景

**实现要点**:
- 修改TextCollector的INPUT_TYPES
- 更新collect_text函数参数
- 调整数据结构为通用文本字段
- 更新文档说明新的设计理念

### 2. 简化主节点文本输入
**问题**: BatchImageSaverV2主节点同时有统一文本输入和文本批次输入
**需求**:
- 完全移除主节点中的统一文本输入字段（title, description, text_prompt）
- 所有文本内容都必须通过TextCollector子节点提供
- 实现彻底的解耦设计，避免功能重复

**实现要点**:
- 从BatchImageSaverV2的INPUT_TYPES中移除统一文本字段
- 简化save_batches函数的文本处理逻辑
- 更新向后兼容策略（可能需要考虑现有工作流）

### 3. 优化输入接口布局
**问题**: 图片批次和文本批次交叉排列，影响用户体验
**当前布局**:
```
batch_1, text_batch_1, batch_2, text_batch_2, batch_3, text_batch_3...
```

**目标布局**:
```
// 图片批次集中在一起
batch_1, batch_2, batch_3, batch_4, batch_5, batch_6, batch_7, batch_8

// 文本批次集中在一起
text_batch_1, text_batch_2, text_batch_3, text_batch_4, text_batch_5, text_batch_6, text_batch_7, text_batch_8
```

**实现要点**:
- 重新组织BatchImageSaverV2的optional输入顺序
- 保持功能不变，只改变UI显示顺序
- 确保ComfyUI正确解析新的输入顺序

### 4. 更新相关文档和示例
**需要更新的内容**:
- README.md 中的V2功能说明
- 使用示例和工作流程说明
- 节点参数说明
- 创建新的示例工作流文件

### 5. 测试计划
- 测试5字段TextCollector功能
- 验证主节点简化后的兼容性
- 确认新布局在ComfyUI中的显示效果
- 测试各种组合场景（多图片+多文本）

## 开发优先级建议
1. **高优先级**: 扩展TextCollector到5个字段（核心功能需求）
2. **中优先级**: 优化输入接口布局（用户体验改进）
3. **中优先级**: 简化主节点文本输入（架构清理）
4. **低优先级**: 文档和示例更新（配套工作）

## 注意事项
- 保持向后兼容性，确保现有工作流不受影响
- 考虑用户迁移成本，提供清晰的升级指南
- 测试各种边界情况（空输入、部分连接等）
- 确保元数据结构能够正确保存所有新字段

---
*最后更新: 2025年11月29日*