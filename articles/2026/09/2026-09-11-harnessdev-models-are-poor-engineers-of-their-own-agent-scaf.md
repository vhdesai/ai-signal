---
article_id: 2026-09-11-harnessdev-models-are-poor-engineers-of-their-own-agent-scaf
title: 'HarnessDev: models are poor engineers of their own agent scaffolding'
date: '2026-09-11'
source: MarkTechPost
url_original: https://www.marktechpost.com/2026/09/11/can-llms-engineer-their-own-agent-harness-bytedance-seeds-harnessdev-says-only-34-of-64-changes-generalize/
url_canonical: https://www.marktechpost.com/2026/09/11/can-llms-engineer-their-own-agent-harness-bytedance-seeds-harnessdev-says-only-34-of-64-changes-generalize/
url_status: ok
digest_source: digests\raw\2026-09-12_060708_Inbox_Daily AI News Digest - September
  12, 2026.md
content_hash: e3b53cca7e6670a91a62624df6eed07949a80e9bf7c86f2057f3c4b835682822
normalized_title_hash: a96216d0047f6791
canonical_url_hash: b3f6dacab6fd3f6e
tags:
- Hot
entities: []
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-18-an-empirical-study-of-harness-design-for-coding-agents-poste
- 2026-09-06-independent-evaluator-finds-openai-s-astra-agi-benchmark-was
- 2026-08-21-nvidia-research-the-agent-harness-not-the-base-model-drives
embedding_id: 2026-09-11-harnessdev-models-are-poor-engineers-of-their-own-agent-scaf
event_name: ''
---

# HarnessDev: models are poor engineers of their own agent scaffolding

HarnessDev grades the runnable agent harness a model builds rather than the answer it produces, across 2,207 tasks and five benchmarks. Six frontier models fall well short of human-engineered references — Opus 4.8 averages 67.8 against a reference of 86.2, and the best BrowseComp score is 52.6 against a 92.2 reference. Self-improvement is weak and noisy: feedback and held-out scores moved in the same direction only 34 of 64 times, and harness quality does not transfer across executors, with one SWE-Pro score falling from 69.3 to 33.0 on an executor swap. The practical implication is that vendor benchmark claims are not portable to your stack, and letting a model optimize its own agent framework is not yet a reliable cost-reduction strategy.

<!-- graph:start -->
## Connections

**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-09-18-an-empirical-study-of-harness-design-for-coding-agents-poste]] · [[2026-09-06-independent-evaluator-finds-openai-s-astra-agi-benchmark-was]] · [[2026-08-21-nvidia-research-the-agent-harness-not-the-base-model-drives]]
<!-- graph:end -->
