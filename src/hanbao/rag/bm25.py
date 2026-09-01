# -*- coding: utf-8 -*-
# [hanbao modification]
"""Minimal BM25 index (pure Python, no external dependencies).

This module is new hanbao code (no upstream counterpart).

Why BM25 instead of a vector store: a vector database (Chroma, Qdrant,
…) would either add a heavy dependency or force an embedding API call,
and an embedding call would push family documents off the NAS.  BM25 over
a CJK-aware tokenizer keeps the index **local, tiny and auditable**.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Sequence

K1 = 1.5
B = 0.75


class BM25Index:
    """Okapi BM25 over a fixed corpus of tokenized documents."""

    def __init__(self) -> None:
        self.doc_count = 0
        self.avgdl = 0.0
        self.doc_lens: list[int] = []
        self.doc_freq: dict[str, int] = {}
        self.term_freqs: list[dict[str, int]] = []

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def build(self, documents: Iterable[Sequence[str]]) -> "BM25Index":
        """(Re)build the index from *documents* (one token list each)."""
        self.doc_lens = []
        self.doc_freq = {}
        self.term_freqs = []
        for tokens in documents:
            tf: dict[str, int] = {}
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
            self.term_freqs.append(tf)
            self.doc_lens.append(len(tokens))
            for term in tf:
                self.doc_freq[term] = self.doc_freq.get(term, 0) + 1
        self.doc_count = len(self.doc_lens)
        self.avgdl = (
            sum(self.doc_lens) / self.doc_count if self.doc_count else 0.0
        )
        return self

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def idf(self, term: str) -> float:
        """Return the Robertson/Sparck-Jones IDF for *term*."""
        df = self.doc_freq.get(term, 0)
        # BM25+ style floor: a term present in more than half the corpus
        # would otherwise produce a negative IDF.
        return math.log(
            1.0
            + (self.doc_count - df + 0.5) / (max(df, 0) + 0.5),
        )

    def score(self, query_tokens: Sequence[str]) -> list[float]:
        """Return a BM25 score per document for *query_tokens*."""
        if not self.doc_count or not query_tokens:
            return [0.0] * self.doc_count
        terms = [
            t for t in dict.fromkeys(query_tokens) if t in self.doc_freq
        ]
        scores = [0.0] * self.doc_count
        idfs = {t: self.idf(t) for t in terms}
        for i, (tf, dl) in enumerate(
            zip(self.term_freqs, self.doc_lens),
        ):
            total = 0.0
            for term in terms:
                freq = tf.get(term, 0)
                if not freq:
                    continue
                denom = freq + K1 * (
                    1.0 - B + B * (dl / self.avgdl if self.avgdl else 0.0)
                )
                total += idfs[term] * ((freq * (K1 + 1.0)) / denom)
            scores[i] = total
        return scores

    def top(
        self,
        query_tokens: Sequence[str],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[tuple[int, float]]:
        """Return ``(doc_index, score)`` pairs, best first."""
        scores = self.score(query_tokens)
        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )
        return [
            (idx, score)
            for idx, score in ranked[: max(1, top_k)]
            if score >= min_score
        ]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize the index (JSON-safe)."""
        return {
            "doc_count": self.doc_count,
            "avgdl": self.avgdl,
            "doc_lens": self.doc_lens,
            "doc_freq": self.doc_freq,
            # Compact form: [[term, count], ...] per document.
            "term_freqs": [sorted(tf.items()) for tf in self.term_freqs],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BM25Index":
        """Restore an index serialized by :meth:`to_dict`."""
        index = cls()
        index.doc_count = int(data.get("doc_count") or 0)
        index.avgdl = float(data.get("avgdl") or 0.0)
        index.doc_lens = list(data.get("doc_lens") or [])
        index.doc_freq = dict(data.get("doc_freq") or {})
        index.term_freqs = [
            {term: count for term, count in pairs}
            for pairs in (data.get("term_freqs") or [])
        ]
        return index
