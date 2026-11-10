---
article_id: 2026-11-02-zyphra-s-hierarchical-attention-method-aims-to-cut-the-cost
title: Zyphra's hierarchical attention method aims to cut the cost of long-context
  inference
date: '2026-11-02'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/11/02/zyphra-hierarchical-attention-zha-sparse-attention/
url_canonical: https://www.marktechpost.com/2026/11/02/zyphra-hierarchical-attention-zha-sparse-attention/
url_status: broken
digest_source: digests\raw\2026-11-03_061250_Inbox_Daily AI News Digest - November
  3, 2026.md
content_hash: 2648437722989598d0246acb4883b580c4df363da4878df25c8b623b22a877b4
normalized_title_hash: 9875be33ca818935
canonical_url_hash: 78194b95ff03faf5
tags: []
entities: []
themes:
- datacenter-infrastructure
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-05-26-cmu-and-ut-austin-detail-new-methods-for-long-context-retrie
- 2026-04-06-a-georgia-tech-team-published-a-new-sparse-attention-archite
- 2026-04-23-cornell-and-purdue-publish-work-on-energy-efficient-attentio
- 2026-05-27-natural-language-query-to-configuration-for-retrieval-agents
embedding_id: 2026-11-02-zyphra-s-hierarchical-attention-method-aims-to-cut-the-cost
event_name: ''
---

# Zyphra's hierarchical attention method aims to cut the cost of long-context inference

To save compute, many models attend to only some earlier tokens, but they still score every earlier token to decide which ones to use. Near 1 million tokens, that selection step can take 60-90% of the computing time. Zyphra's ZHA method uses a tree search over compressed summaries of the context instead, and it can be added to an existing model with about 4B tokens of extra training. On Qwen3.6-35B-A3B it scores within a few points of standard attention; its SWE-bench Verified score matches at 67.4. However, the speedups are estimated rather than measured, no optimized code is released, and one model dropped 25 points on a long-context retrieval benchmark. It is a promising approach to cheaper long-context inference but is not ready for production. Academic Research No qualifying publication from the monitored universities was verified in this 24-hour window.

<!-- graph:start -->
## Connections

**Topics:** [[Infrastructure & Compute]]
**Related:** [[2026-05-26-cmu-and-ut-austin-detail-new-methods-for-long-context-retrie]] · [[2026-04-06-a-georgia-tech-team-published-a-new-sparse-attention-archite]] · [[2026-04-23-cornell-and-purdue-publish-work-on-energy-efficient-attentio]] · [[2026-05-27-natural-language-query-to-configuration-for-retrieval-agents]]
<!-- graph:end -->
