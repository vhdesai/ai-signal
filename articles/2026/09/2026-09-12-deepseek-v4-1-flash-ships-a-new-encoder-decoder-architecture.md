---
article_id: 2026-09-12-deepseek-v4-1-flash-ships-a-new-encoder-decoder-architecture
title: DeepSeek V4.1-Flash ships a new encoder-decoder architecture and a 60% cut
  to cached-input pricing
date: '2026-09-12'
source: Martin Cid Magazine
url_original: https://www.martincid.com/technology-sv/deepseek-v4-1-flash-new-architecture-8b-active-60-price-cut/
url_canonical: https://www.martincid.com/technology-sv/deepseek-v4-1-flash-new-architecture-8b-active-60-price-cut/
url_status: ok
digest_source: digests\raw\2026-09-12_062305_Inbox_Daily AI News Digest - September
  12, 2026.md
content_hash: 1f35ca5eccda7aae80cd99577e3789b83992b29b6450e08880b8e0af4aa9f2b4
normalized_title_hash: b894448a46e25ce6
canonical_url_hash: 1856c1b537e9ad67
tags:
- Launch
- Hot
entities:
- DeepSeek
themes:
- model-capabilities
- infrastructure-investments
cross_cutting_topics:
- china-compete
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-10-deepseek-releases-v4-1-flash-with-1m-context-fp4-kv-cache-an
- 2026-09-11-deepseek-v4-1-flash-lands-on-third-party-inference-platforms
- 2026-09-11-deepseek-v4-1-flash-resets-inference-price-performance-with
- 2026-08-03-deepseek-s-v4-flash-update-surpasses-its-own-flagship-on-age
embedding_id: 2026-09-12-deepseek-v4-1-flash-ships-a-new-encoder-decoder-architecture
event_name: ''
---

# DeepSeek V4.1-Flash ships a new encoder-decoder architecture and a 60% cut to cached-input pricing

DeepSeek's V4.1-Flash uses a "Causal Encoder-Decoder" design: a 552B-parameter MoE backbone that activates only 8B parameters on input and 16B on output, with a 1M-token context. KV cache falls to about 890 bytes per token — roughly a quarter of the prior generation's HBM and an eighth of its SSD footprint — and cached input now costs $0.003 per million tokens off-peak, down 60%. Self-reported DeepSWE v1.1 is 74.2 against Opus 5 at 74.0, though Terminal-Bench 3.0 shows a real gap (30.0 vs 43.3). From September 14, all deepseek-v4-pro API traffic routes to Flash at Flash pricing — a one-day migration notice that drew criticism from production teams.

<!-- graph:start -->
## Connections

**Entities:** [[DeepSeek]]
**Topics:** [[Model Breakthroughs]] · [[Infrastructure Investments]] · [[Global AI Race]]
**Related:** [[2026-09-10-deepseek-releases-v4-1-flash-with-1m-context-fp4-kv-cache-an]] · [[2026-09-11-deepseek-v4-1-flash-lands-on-third-party-inference-platforms]] · [[2026-09-11-deepseek-v4-1-flash-resets-inference-price-performance-with]] · [[2026-08-03-deepseek-s-v4-flash-update-surpasses-its-own-flagship-on-age]]
<!-- graph:end -->
