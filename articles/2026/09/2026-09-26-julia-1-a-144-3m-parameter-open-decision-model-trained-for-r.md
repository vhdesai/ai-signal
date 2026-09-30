---
article_id: 2026-09-26-julia-1-a-144-3m-parameter-open-decision-model-trained-for-r
title: 'Julia 1: a 144.3M-parameter open decision model trained for roughly $104'
date: '2026-09-26'
source: MarkTechPost
url_original: https://www.marktechpost.com/2026/09/26/supersonic-labs-releases-julia-1-a-144-3m-parameter-open-decision-model-that-runs-on-a-cpu/
url_canonical: https://www.marktechpost.com/2026/09/26/supersonic-labs-releases-julia-1-a-144-3m-parameter-open-decision-model-that-runs-on-a-cpu/
url_status: ok
digest_source: digests\raw\2026-09-27_060139_Inbox_Daily AI News Digest - September
  27, 2026.md
content_hash: 304f689244e141d41a7728c82ff6a1d94245512887f1a40106f0ae4eb5c85562
normalized_title_hash: 1e95b14a45a031c0
canonical_url_hash: c42e813e348967bf
tags:
- New
entities:
- Apple
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-26-supersonic-labs-releases-julia-1-a-144-3m-parameter-open-dec
- 2026-06-29-meituan-open-sources-longcat-2-0-a-1-6t-model-reportedly-tra
- 2026-06-30-meituan-open-sources-longcat-2-0-a-trillion-parameter-model
embedding_id: 2026-09-26-julia-1-a-144-3m-parameter-open-decision-model-trained-for-r
event_name: ''
---

# Julia 1: a 144.3M-parameter open decision model trained for roughly $104

Brazilian lab Supersonic Labs released Julia 1, a 144.3M-parameter Apache 2.0 model that classifies, scores and routes rather than generating text, built on Johns Hopkins CLSP’s mmBERT-small encoder with an added decision head. It selects among 2–20 supplied options and returns full softmax probabilities, running on plain CPU with an ONNX/WebGPU browser build at a median 33.15 ms per decision on an Apple M4. Reported results beat the TypeSafe Jev reference on three of four pilots (Typed Decisions 73.15%, AG News 94%, DAIR Emotion 86%) but trailed badly on 72-label Banking77 (64% vs 87%). Total cloud GPU training spend was approximately US$104 — the datapoint worth noting for routing-layer economics.

<!-- graph:start -->
## Connections

**Entities:** [[Apple]]
**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-09-26-supersonic-labs-releases-julia-1-a-144-3m-parameter-open-dec]] · [[2026-06-29-meituan-open-sources-longcat-2-0-a-1-6t-model-reportedly-tra]] · [[2026-06-30-meituan-open-sources-longcat-2-0-a-trillion-parameter-model]]
<!-- graph:end -->
