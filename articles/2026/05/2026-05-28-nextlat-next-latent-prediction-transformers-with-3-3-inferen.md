---
article_id: 2026-05-28-nextlat-next-latent-prediction-transformers-with-3-3-inferen
title: 'NextLat: Next-Latent Prediction Transformers with 3.3× Inference Speedup Hot'
date: '2026-05-28'
source: John Langford (Microsoft Research) at Cornell Tech Frontiers of AI Symposium
url_original: null
url_canonical: null
url_status: missing
digest_source: digests\raw\2026-05-28_071047_Inbox_Daily AI News Digest – May 28,
  2026.md
content_hash: 05e5ed8c37ea09f1eb93404cbd16918522a15066c412997c84dc76c6d724207a
normalized_title_hash: fe9270d0bb71aae7
canonical_url_hash: ''
tags: []
entities: []
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-05-12-meta-stanford-propose-fast-byte-latent-transformer-50-infere
- 2026-05-27-think-before-you-speak-next-gen-llms-with-global-reasoning-a
- 2026-07-08-constrained-decoding-for-diffusion-language-models-via-effic
- 2026-07-08-stanford-proposes-constrained-decoding-for-diffusion-languag
- 2026-05-28-resae-residualized-sparse-autoencoders-for-multi-layer-trans
embedding_id: 2026-05-28-nextlat-next-latent-prediction-transformers-with-3-3-inferen
event_name: ''
---

# NextLat: Next-Latent Prediction Transformers with 3.3× Inference Speedup Hot

Langford introduced NextLat, which extends next-token training with self-supervised predictions in latent space — training transformers to predict the next latent state given the next output token. The architecture enables variable-length self-speculative decoding with up to 3.3× inference acceleration on language tasks, while showing measurable gains in downstream accuracy, representation compression, and lookahead planning. Notably, the recurrent inductive bias is added without changing transformer architecture, parallel training, or inference path.

<!-- graph:start -->
## Connections

**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-05-12-meta-stanford-propose-fast-byte-latent-transformer-50-infere]] · [[2026-05-27-think-before-you-speak-next-gen-llms-with-global-reasoning-a]] · [[2026-07-08-constrained-decoding-for-diffusion-language-models-via-effic]] · [[2026-07-08-stanford-proposes-constrained-decoding-for-diffusion-languag]] · [[2026-05-28-resae-residualized-sparse-autoencoders-for-multi-layer-trans]]
<!-- graph:end -->
