---
name: document_reader
description: "读取 PDF 和 Office 文档（Word/Excel/PowerPoint），先用 markitdown 转成 Markdown 再阅读。当用户发来文档文件，或要求读取、提取、总结 .pdf、.docx、.xlsx、.pptx 文件内容时使用本技能。本技能只能「读」文档，不能修改或创建文档。"
metadata:
  builtin_skill_version: "1.0"
  qwenpaw:
    emoji: "📑"
    requires: {}
---

# 文档读取

用 `markitdown`（已作为依赖内置）把 PDF / Office 文档转成 Markdown 后阅读。转换后的 Markdown 会保留文档结构——标题、表格、列表、链接。

## 支持格式

- PDF（`.pdf`）
- Word（`.docx`）
- Excel（`.xlsx`、`.xls`）
- PowerPoint（`.pptx`、`.ppt`）

## 读取步骤

### 第一步——转成 Markdown

用 `markitdown` 命令行：

```bash
markitdown "path/to/document.pdf" -o /tmp/document.md
```

小文件可以直接输出到终端：

```bash
markitdown "path/to/document.docx"
```

需要更多控制时可用 Python API：

```python
from markitdown import MarkItDown
result = MarkItDown().convert("path/to/document.xlsx")
print(result.text_content)
```

### 第二步——阅读并总结

用 `read_file` 读取转换后的 Markdown，然后总结或提取用户要的那部分内容。

## 注意事项

- 大文档先转成文件，再只读相关部分（用 `grep_search` 或 `read_file` 指定行范围）。
- 扫描版/纯图片 PDF 没有文字层，可能读不出内容。遇到这种情况要如实告诉用户，不要编造内容。
- 本技能只能**读**文档，不能修改、创建、或转回 `.docx`/`.xlsx`/`.pptx`/`.pdf`。如果用户要求改文档，要说明这个限制。
