---
article_id: 2026-09-19-linkup-releases-sparseup-a-149m-parameter-open-source-sparse
title: Linkup Releases SPARSEUP, a 149M-Parameter Open-Source Sparse Embedding Model
date: '2026-09-19'
source: MarkTechPost
url_original: https://www.marktechpost.com/2026/09/19/linkup-research-releases-sparseup/
url_canonical: https://www.marktechpost.com/2026/09/19/linkup-research-releases-sparseup/
url_status: ok
digest_source: digests\raw\2026-09-20_060444_Inbox_Daily AI News Digest - September
  20, 2026.md
content_hash: c487d2b650ed663d668280657a1f67e2d9b10d8c5b885e501c93fd74a02d6653
normalized_title_hash: 33c2c1e372a11fbe
canonical_url_hash: 2ff0f002c21ca15b
tags:
- New
entities: []
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-05-05-newarxiv-sparse-regression-benchmarks-under-correlation-and
- 2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and
- 2026-07-17-nvidia-releases-nemotron-3-embed-8b-checkpoint-ranks-1-on-rt
embedding_id: 2026-09-19-linkup-releases-sparseup-a-149m-parameter-open-source-sparse
event_name: ''
---

# Linkup Releases SPARSEUP, a 149M-Parameter Open-Source Sparse Embedding Model

SPARSEUP is a learned sparse embedding model on a 149M-parameter ModernBERT backbone, released under Apache 2.0, scoring 56.4 average nDCG@10 on BEIR-13. Three techniques drive it: a logit shift, per-position top-12 expansion, and case folding that cuts output dimensions from roughly 50k to 34k; paired with the Seismic inverted index it reaches over 97% recall in about 380 microseconds per query, single-threaded. Because it shares a backbone and fine-tuning data with DenseOn and LateOn, it completes a rare controlled three-way comparison — and the controlled numbers are less flattering than the headline (LateOn 58.9, DenseOn 57.9, SPARSEUP 56.4). Practical relevance: sparse vectors drop into existing inverted indexes without new infrastructure.

<!-- graph:start -->
## Connections

**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-05-05-newarxiv-sparse-regression-benchmarks-under-correlation-and]] · [[2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and]] · [[2026-07-17-nvidia-releases-nemotron-3-embed-8b-checkpoint-ranks-1-on-rt]]
<!-- graph:end -->
