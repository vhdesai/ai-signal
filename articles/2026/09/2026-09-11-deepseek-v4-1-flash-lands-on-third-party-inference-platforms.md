---
article_id: 2026-09-11-deepseek-v4-1-flash-lands-on-third-party-inference-platforms
title: DeepSeek V4.1-Flash Lands on Third-Party Inference Platforms With 1M-Token
  Context
date: '2026-09-11'
source: Unite.AI
url_original: https://www.unite.ai/baseten-adds-deepseek-v4-1-flash-to-model-apis-with-1m-token-context/
url_canonical: https://www.unite.ai/baseten-adds-deepseek-v4-1-flash-to-model-apis-with-1m-token-context/
url_status: ok
digest_source: digests\raw\2026-09-13_062313_Inbox_Daily AI News Digest - September
  13, 2026.md
content_hash: bcd6c58d456f7edeaaf1dcd9159b6d218987030e4627f7ebc85d460b72f2775d
normalized_title_hash: c09a953eb4979cd9
canonical_url_hash: f0e1e889bed63be1
tags: []
entities:
- DeepSeek
themes:
- model-capabilities
cross_cutting_topics:
- china-compete
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-10-deepseek-releases-v4-1-flash-with-1m-context-fp4-kv-cache-an
- 2026-09-12-deepseek-v4-1-flash-ships-a-new-encoder-decoder-architecture
- 2026-04-23-deepseek-previews-v4-family-1-6t-param-pro-and-1m-token-flas
embedding_id: 2026-09-11-deepseek-v4-1-flash-lands-on-third-party-inference-platforms
event_name: ''
---

# DeepSeek V4.1-Flash Lands on Third-Party Inference Platforms With 1M-Token Context

Baseten added DeepSeek-V4.1-Flash to its model APIs, extending distribution for the 552B-parameter multimodal mixture-of-experts model released under MIT license on Hugging Face. The architecture is the story: a causal encoder-decoder split activates only 8B parameters during prefill and 16B during decode, and FP4 KV caching cuts the global cache footprint to 890 bytes per token — roughly a quarter of the prior generation. That directly attacks cache-hit charges, which dominate spend on long-running agent loops. Reported scores put it at 74.2 on DeepSWE v1.1 and 90.6 on Terminal-Bench 2.1, ahead of DeepSeek's own V4-Pro, which is being retired into it; Baseten itself cautioned that a 54.8 on AutomationBench means roughly half of complex workflows still fail without a human in the loop. Products & Tools DEVELOPER PLATFORM

<!-- graph:start -->
## Connections

**Entities:** [[DeepSeek]]
**Topics:** [[Model Breakthroughs]] · [[Global AI Race]]
**Related:** [[2026-09-10-deepseek-releases-v4-1-flash-with-1m-context-fp4-kv-cache-an]] · [[2026-09-12-deepseek-v4-1-flash-ships-a-new-encoder-decoder-architecture]] · [[2026-04-23-deepseek-previews-v4-family-1-6t-param-pro-and-1m-token-flas]]
<!-- graph:end -->
