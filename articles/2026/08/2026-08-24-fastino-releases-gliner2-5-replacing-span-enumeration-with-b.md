---
article_id: 2026-08-24-fastino-releases-gliner2-5-replacing-span-enumeration-with-b
title: Fastino releases GLiNER2.5, replacing span enumeration with boundary predictionNew
date: '2026-08-24'
source: MarkTechPost
url_original: https://www.marktechpost.com/2026/08/24/fastino-releases-gliner2-5-a-boundary-prediction-architecture-that-removes-span-enumeration-from-information-extraction/
url_canonical: https://www.marktechpost.com/2026/08/24/fastino-releases-gliner2-5-a-boundary-prediction-architecture-that-removes-span-enumeration-from-information-extraction/
url_status: found
digest_source: digests\raw\2026-08-25_060359_Inbox_Daily AI News Digest - August 25,
  2026.md
content_hash: 9e13e07e9d64c6b50317b38b5edc469d9e22e58979aa9c927c3c6b56f85330a6
normalized_title_hash: 3ce8445a259ba98e
canonical_url_hash: d0a14f438f560d26
tags: []
entities: []
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-08-14-z-ai-glm-5-3-all-gains-from-post-training-no-new-base
- 2026-05-06-may-2026-frontier-snapshot-leadership-is-now-category-by-cat
- 2026-05-13-fastino-labs-open-sources-gliguard-300m-param-safety-moderat
embedding_id: 2026-08-24-fastino-releases-gliner2-5-replacing-span-enumeration-with-b
event_name: ''
---

# Fastino releases GLiNER2.5, replacing span enumeration with boundary predictionNew

GLiNER2.5 scores where an entity starts and ends rather than scoring every candidate span, removing the maximum-entity-width ceiling and keeping compute linear in sequence length while enabling a 4,096-word context. Across 16 zero-shot benchmarks the multilingual checkpoint reaches 56.17 macro F1 versus 56.09 for GLiNER2, with a 24.75-point gain on XNLI. Three checkpoints (74M/194M/287M parameters) ship on Hugging Face under Apache 2.0 and run on CPU. For enterprise extraction workloads this is a meaningful cost-per-document lever.

<!-- graph:start -->
## Connections

**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-08-14-z-ai-glm-5-3-all-gains-from-post-training-no-new-base]] · [[2026-05-06-may-2026-frontier-snapshot-leadership-is-now-category-by-cat]] · [[2026-05-13-fastino-labs-open-sources-gliguard-300m-param-safety-moderat]]
<!-- graph:end -->
