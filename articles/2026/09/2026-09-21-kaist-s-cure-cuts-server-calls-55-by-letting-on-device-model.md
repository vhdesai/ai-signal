---
article_id: 2026-09-21-kaist-s-cure-cuts-server-calls-55-by-letting-on-device-model
title: KAIST's CURE Cuts Server Calls 55% by Letting On-Device Models Reuse Prior
  Answers
date: '2026-09-21'
source: Tech Xplore
url_original: https://techxplore.com/news/2026-09-smartphone-ai-solutions-tackle-similar.html
url_canonical: https://techxplore.com/news/2026-09-smartphone-ai-solutions-tackle-similar.html
url_status: ok
digest_source: digests\raw\2026-09-22_060336_Inbox_Daily AI News Digest - September
  22, 2026.md
content_hash: a88e6eb0c95e2638db9a7c42146b9cc4a59e7f8e2cb7bb4339e8afa6a3641ec2
normalized_title_hash: 8de79c387d767c5b
canonical_url_hash: 2a23b3b71591ac92
tags:
- New
entities: []
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-02-gigapath-flash-and-gigatime-flash-toward-population-scale-di
- 2026-09-13-princeton-researcher-proposes-the-recurrent-looped-transform
- 2026-08-25-liquid-ai-open-sources-pipette-a-reproducible-benchmarking-s
- 2026-05-28-new-causal-explanation-method-targets-llm-jailbreaks
embedding_id: 2026-09-21-kaist-s-cure-cuts-server-calls-55-by-letting-on-device-model
event_name: ''
---

# KAIST's CURE Cuts Server Calls 55% by Letting On-Device Models Reuse Prior Answers

A KAIST team led by Prof. Jae-Gil Lee developed CURE (Cumulative Knowledge Reuse), which lets a small on-device vision-language model store and reuse knowledge previously obtained from a large server model rather than re-querying it. Pairing MobileCLIP2 on-device with an 18B-parameter EVA-CLIP server model, CURE made 55.61% fewer server calls than a non-cumulative hybrid baseline at near-server accuracy, running up to 2.80× faster end-to-end and 3.67× faster than always-server. It stores feature summaries rather than original images, which matters for privacy-sensitive deployments, and requires no retraining of either model. Published in Lecture Notes in Computer Science (DOI 10.1007/978-3-032-37627-5_21).

<!-- graph:start -->
## Connections

**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-09-02-gigapath-flash-and-gigatime-flash-toward-population-scale-di]] · [[2026-09-13-princeton-researcher-proposes-the-recurrent-looped-transform]] · [[2026-08-25-liquid-ai-open-sources-pipette-a-reproducible-benchmarking-s]] · [[2026-05-28-new-causal-explanation-method-targets-llm-jailbreaks]]
<!-- graph:end -->
