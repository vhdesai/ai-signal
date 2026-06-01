"""Warm the local embedding-model cache so the index stage never downloads at runtime."""

from __future__ import annotations

import sys


def main() -> int:
    model = sys.argv[1] if len(sys.argv) > 1 else "BAAI/bge-small-en-v1.5"
    from sentence_transformers import SentenceTransformer

    SentenceTransformer(model)
    print(f"cached embedding model: {model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
