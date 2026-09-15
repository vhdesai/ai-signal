---
article_id: 2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and
title: 'Perplexity details its GPU embedding stack: how Ivy, Tulip and ROSE serve
  pplx-embed'
date: '2026-09-05'
source: MarkTechPost
url_original: https://www.marktechpost.com/2026/09/05/perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and-rose-serve-pplx-embed/
url_canonical: https://www.marktechpost.com/2026/09/05/perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and-rose-serve-pplx-embed/
url_status: ok
digest_source: digests\raw\2026-09-06_060409_Inbox_Daily AI News Digest - September
  6, 2026.md
content_hash: 8a0e18d6ffe869cd7189680072f7fd8558215d64a073c2426e539a7c5f13d293
normalized_title_hash: ae8354652e0cdef0
canonical_url_hash: f90f59c481ae5ffe
tags: []
entities:
- Anthropic
- Cerebras
- Perplexity
themes:
- company-storylines
- company-investments
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-05-perplexity-details-the-gpu-serving-stack-behind-pplx-embed
- 2026-09-05-perplexity-publishes-the-internals-of-its-gpu-embedding-serv
- 2026-09-05-perplexity-details-the-gpu-embedding-stack-behind-pplx-embed
- 2026-07-17-nvidia-releases-nemotron-3-embed-8b-checkpoint-ranks-1-on-rt
embedding_id: 2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and
event_name: ''
---

# Perplexity details its GPU embedding stack: how Ivy, Tulip and ROSE serve pplx-embed

Perplexity’s engineering team published an account of the serving infrastructure behind its embedding models, covering CUDA graph capture, LazyTensor overlap, and benchmarks against vLLM. Retrieval quality in an AI search product is bounded both by embedding model quality and by the cost of running it across an index; this disclosure addresses the second constraint. It is a useful reference point for teams building retrieval at scale who are weighing custom serving against off-the-shelf inference stacks. Coverage note. Several stories circulating today — Anthropic’s Claude-generated formal proof of Fermat’s Last Theorem, Crusoe’s $3B raise at a $30B valuation, Nscale’s $3.5B pre-IPO financing, and Qwen 3.8 27B on Cerebras — were published September 3–4, 2026 and fall outside the 24-hour window. They are excluded rather than re-dated.

<!-- graph:start -->
## Connections

**Entities:** [[Anthropic]] · [[Cerebras]] · [[Perplexity]]
**Topics:** [[Corporate Moves]] · [[Company Investments]]
**Related:** [[2026-09-05-perplexity-details-the-gpu-serving-stack-behind-pplx-embed]] · [[2026-09-05-perplexity-publishes-the-internals-of-its-gpu-embedding-serv]] · [[2026-09-05-perplexity-details-the-gpu-embedding-stack-behind-pplx-embed]] · [[2026-07-17-nvidia-releases-nemotron-3-embed-8b-checkpoint-ranks-1-on-rt]]
<!-- graph:end -->
