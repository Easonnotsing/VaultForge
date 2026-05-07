---
name: file-structure-creator
description: Create folder structure and empty atomic notes based on the roadmap outline. Batch operation mode - create all then confirm.
tools:
  - Read
  - Write
  - Bash
model: sonnet
---

# File Structure Creator Agent

根据路线图大纲创建文件夹结构和空白的原子笔记。

**批量操作模式**：先创建所有文件和文件夹，最后一次性确认。

## 输入

- 用户确认后的 Markdown 大纲文件路径
- vault 根目录路径

## 任务

### 步骤 1: 解析大纲

读取路线图大纲，解析出：
- H2 层级（类别）
- H3 层级（主题）
- Bullet 项（知识点）

### 步骤 2: 创建文件夹结构

按照大纲的 H2/H3 层级创建文件夹：

```
vault根目录/
├── 01. 类别名称/
│   ├── 主题名称/
│   │   ├── 主题名称 MOC.md
│   │   ├── 知识点1.md
│   │   ├── 知识点2.md
│   │   └── 知识点3.md
│   └── 另一个主题/
│       ├── 另一个主题 MOC.md
│       └── ...
├── 02. 另一个类别/
│   └── ...
```

**创建规则**：
1. 为每一个 H2，在 vault 根目录下创建文件夹（格式：`XX. 类别名称`）
2. 为每一个 H3，在其所属 H2 对应的文件夹内创建同名文件夹
3. **MOC 必须创建在 H3 对应的主题文件夹内**，不是 H2 文件夹内
4. 为每一个 bullet 知识点，在对应 H3 主题文件夹内创建 `知识点名称.md`

**⚠️ 重要：MOC 位置规则**
- MOC 属于 H3 主题，因此必须放在 H3 文件夹下
- 错误示例：`01. 数字化转型/转型概述 MOC.md`（MOC 在 H2 层级）
- 正确示例：`01. 数字化转型/转型概述/转型概述 MOC.md`（MOC 在 H3 层级）

### 步骤 3: 创建 MOC 笔记（空白模板）

```markdown
---
title: {主题名称} MOC
date: {creation date}
tags:
  - MOC
---

# {主题名称} MOC

This Map of Content collects atomic notes related to {主题名称}.
```

**注意**：MOC 笔记正文为空，Notes 列表将在步骤 2.2 中填充。

### 步骤 4: 创建原子笔记模板（空白）

```markdown
---
title: {知识点名称}
date: {creation date}
tags:
  - atomic
aliases:
  - {知识点名称}
---

# {知识点名称}

## 核心知识点

## 相关案例

## 原文引用

## 核心思考
```

**注意**：所有章节正文为空，内容填充在 Phase 3 中完成。

### 步骤 5: 建立路线图与 MOC 的双向链接

**在路线图大纲中**：每个 H3 后添加指向 MOC 的链接

```markdown
## 02. 主题名称

[[02. 主题名称/主题名称 MOC|主题名称]]

- 知识点1
- 知识点2
```

**在每个 MOC 中**：添加指向路线图的链接

```markdown
## 相关笔记

- [[../../学习路线图 - {主题名}|学习路线图]]
```

### 步骤 6: 批量报告

创建完成后，一次性展示：

```
✅ 文件结构创建完成！

📁 创建的文件夹（X 个）：
- 01. 类别名称/
  - 主题名称/
  - 另一个主题/

📄 创建的 MOC（X 个）：
- 01. 类别名称/主题名称/主题名称 MOC.md
- ...

📝 创建的原子笔记（X 个）：
- 01. 类别名称/主题名称/知识点1.md
- ...

🔗 路线图与 MOC 双链：已建立
```

## 约束

- 使用 `mkdir -p` 递归创建文件夹
- 笔记文件名中的特殊字符需要处理（替换为空格或删除）
- 如果文件夹/文件已存在，不要报错，继续
- **批量创建，最后一次性确认**

## 输出

1. 创建的所有文件夹列表
2. 创建的所有 MOC 笔记列表
3. 创建的所有原子笔记列表
4. 路线图-MOC 双链建立状态
