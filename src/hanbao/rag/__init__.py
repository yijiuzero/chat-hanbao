# -*- coding: utf-8 -*-
# [hanbao modification]
"""hanbao local knowledge base (RAG) — data never leaves this device.

This package is new hanbao code (no upstream counterpart).

Retrieval is BM25 over a CJK-aware tokenizer; document conversion reuses
the existing ``markitdown`` dependency.  **No new third-party package is
introduced and no network call is made during indexing or search**, which
is what keeps the "家庭数据不出 NAS" guarantee true and the slim image
intact.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""

from .config import KnowledgeConfig
from .service import KnowledgeService, get_knowledge_service

__all__ = [
    "KnowledgeConfig",
    "KnowledgeService",
    "get_knowledge_service",
]
