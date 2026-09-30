---
article_id: 2026-09-05-perplexity-details-the-gpu-embedding-stack-behind-pplx-embed
title: Perplexity details the GPU embedding stack behind pplx-embed
date: '2026-09-05'
source: MarkTechPost · Perplexity
url_original: https://www.marktechpost.com/2026/09/05/perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and-rose-serve-pplx-embed/
url_canonical: https://www.marktechpost.com/2026/09/05/perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and-rose-serve-pplx-embed/
url_status: ok
digest_source: digests\raw\2026-09-06_060643_Inbox_Daily AI News Digest - September
  6, 2026.md
content_hash: ed8b66dc94ebcef859e9bfaf058fa7acaf4044a61e11696b43b57fc214cad7a1
normalized_title_hash: 48de3eba71dadcef
canonical_url_hash: f90f59c481ae5ffe
tags: []
entities:
- Perplexity
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: duplicate
canonical_article_id: 2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and
related_article_ids: []
embedding_id: 2026-09-05-perplexity-details-the-gpu-embedding-stack-behind-pplx-embed
event_name: ''
---

# Perplexity details the GPU embedding stack behind pplx-embed

Rather than standing up a separate embedding engine, Perplexity reuses its LLM prefill/decode kernels and layers three services on top: Ivy (a Rust HTTP gateway handling tokenization and batch splitting), Tulip (a gRPC inference server) and ROSE (a Python runtime managing CUDA graphs). Notable techniques include whole-model CUDA-graph capture with “lazy capture” to reduce launch overhead, and a LazyTensor abstraction that overlaps CPU batch preparation with in-flight GPU work. Benchmarks are run against vLLM v0.22.0 in BF16.

<!-- graph:start -->
## Connections

**Entities:** [[Perplexity]]
**Topics:** [[Model Breakthroughs]]
**Canonical:** [[2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and]]
<!-- graph:end -->
