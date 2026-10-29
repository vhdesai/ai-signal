---
article_id: 2026-09-10-deepseek-ships-v4-1-flash-and-retires-its-flagship-behind-it
title: DeepSeek Ships V4.1-Flash and Retires Its Flagship Behind It
date: '2026-09-10'
source: DeepSeek**
url_original: https://www.deepseek.com/en/news/deepseek-v4-1-flash/
url_canonical: https://www.deepseek.com/en/news/deepseek-v4-1-flash/
url_status: found
digest_source: digests\raw\2026-09-11_065100_Final-Daily-AI-News-Digest.md
content_hash: 9af5c81cfebb40ad8368f236d91b69075f3e76ae7e97cb329bedb314a9443233
normalized_title_hash: c0d04c4301cf1c02
canonical_url_hash: 6e725a73dc7669f7
tags:
- Launch
- Open weights
entities:
- DeepSeek
themes:
- model-capabilities
cross_cutting_topics:
- china-compete
dedupe_status: duplicate
canonical_article_id: 2026-09-10-deepseek-releases-v4-1-flash-with-1m-context-fp4-kv-cache-an
related_article_ids: []
embedding_id: 2026-09-10-deepseek-ships-v4-1-flash-and-retires-its-flagship-behind-it
event_name: ''
---

# DeepSeek Ships V4.1-Flash and Retires Its Flagship Behind It

V4.1-Flash is a 552B-parameter multimodal MoE model with a 1M-token context window, activating 8B parameters during prefill and 16B during decode. The engineering emphasis is memory: a causal encoder-decoder split, cross-layer attention reuse, and FP4 cache quantization cut the global KV cache to 890 bytes per token — about a quarter the HBM and an eighth the SSD footprint of the prior generation. Weights ship on Hugging Face under MIT, and from September 14 all V4-Pro API traffic reroutes to V4.1-Flash at the smaller model's rates — an effective ~70% output-price cut. DeepSeek's own tables put it narrowly ahead of Claude Opus 5 and GPT-5.6 Sol on Terminal-Bench 2.1, while trailing both on GPQA Diamond.

<!-- graph:start -->
## Connections

**Entities:** [[DeepSeek]]
**Topics:** [[Model Breakthroughs]] · [[Global AI Race]]
**Canonical:** [[2026-09-10-deepseek-releases-v4-1-flash-with-1m-context-fp4-kv-cache-an]]
<!-- graph:end -->
