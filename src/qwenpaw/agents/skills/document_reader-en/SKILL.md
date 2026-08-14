---
name: document_reader
description: "Read PDF and Office documents (Word/Excel/PowerPoint) by converting them to Markdown with markitdown. Use this skill when the user shares a document file, or asks to read, extract, or summarize content from a .pdf, .docx, .xlsx, or .pptx file. This skill only READS documents — it cannot edit or create them."
metadata:
  builtin_skill_version: "1.0"
  qwenpaw:
    emoji: "📑"
    requires: {}
---

# Document Reader

Read PDF and Office documents by converting them to Markdown with `markitdown` (bundled as a dependency). The converted Markdown preserves document structure — headings, tables, lists, and links.

## Supported formats

- PDF (`.pdf`)
- Word (`.docx`)
- Excel (`.xlsx`, `.xls`)
- PowerPoint (`.pptx`, `.ppt`)

## How to read a document

### Step 1 — Convert to Markdown

Use the `markitdown` CLI:

```bash
markitdown "path/to/document.pdf" -o /tmp/document.md
```

Or stream to stdout for small files:

```bash
markitdown "path/to/document.docx"
```

Or use the Python API when you need more control:

```python
from markitdown import MarkItDown
result = MarkItDown().convert("path/to/document.xlsx")
print(result.text_content)
```

### Step 2 — Read and summarize

Read the converted Markdown with `read_file`, then summarize or extract the specific part the user asked about.

## Notes

- For large documents, convert to a file first, then read only the relevant sections (use `grep_search` or `read_file` with line ranges).
- Scanned/image-only PDFs without a text layer may return little or no text. If so, tell the user rather than inventing content.
- This skill only **reads** documents. It cannot edit, create, or convert back to `.docx`/`.xlsx`/`.pptx`/`.pdf`. If the user asks to modify a document, explain this limitation.
