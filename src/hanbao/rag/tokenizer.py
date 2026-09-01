# -*- coding: utf-8 -*-
# [hanbao modification]
"""CJK-aware tokenizer for the hanbao local knowledge base.

This module is new hanbao code (no upstream counterpart).

Chinese has no whitespace word boundaries, so a naive ``split()`` would
index whole sentences as single tokens and BM25 would degenerate into an
exact-substring match.  CJK runs are therefore emitted as **unigrams plus
bigrams** (e.g. "家庭账单" → 家, 庭, 账, 单, 家庭, 庭账, 账单), which is a
standard cheap approximation that works well for BM25 without pulling in
a segmentation library (and without the bundled dictionaries that would
inflate the image).

Latin text keeps ordinary word tokens; digits are kept as-is so invoice
numbers and dates stay searchable.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import re

# CJK Unified Ideographs (+ Ext A) and Japanese kana.
_CJK_CHARS = (
    "\u3400-\u4dbf"  # CJK Ext A
    "\u4e00-\u9fff"  # CJK Unified Ideographs
    "\u3040-\u30ff"  # Hiragana + Katakana
    "\uac00-\ud7af"  # Hangul syllables
)
_CJK_RUN_RE = re.compile(f"[{_CJK_CHARS}]+")
_LATIN_RE = re.compile(r"[A-Za-z]+|\d+")

# Discard single-character CJK unigrams except these high-signal ones.
_KEEP_SINGLE = frozenset("年月日号元省市县区")


def tokenize(text: str) -> list[str]:
    """Split *text* into BM25 tokens.

    Args:
        text: Raw text (any language mix).

    Returns:
        Lowercased token list.  CJK runs contribute unigrams and bigrams;
        Latin runs contribute whole words; digits are preserved.
    """
    if not text:
        return []
    lowered = text.lower()
    tokens: list[str] = []

    for run in _CJK_RUN_RE.findall(lowered):
        length = len(run)
        if length == 1:
            if run in _KEEP_SINGLE:
                tokens.append(run)
            continue
        tokens.extend(run[i] for i in range(length))
        tokens.extend(run[i : i + 2] for i in range(length - 1))

    for match in _LATIN_RE.findall(lowered):
        tokens.append(match)

    return tokens


def highlight_spans(text: str, tokens: list[str]) -> list[tuple[int, int]]:
    """Return (start, end) spans in *text* covered by any of *tokens*."""
    lowered = text.lower()
    spans: list[tuple[int, int]] = []
    for token in tokens:
        if len(token) < 2 and token not in _KEEP_SINGLE:
            continue
        start = 0
        while True:
            idx = lowered.find(token, start)
            if idx < 0:
                break
            spans.append((idx, idx + len(token)))
            start = idx + 1
            if len(spans) > 200:
                break
    return spans
