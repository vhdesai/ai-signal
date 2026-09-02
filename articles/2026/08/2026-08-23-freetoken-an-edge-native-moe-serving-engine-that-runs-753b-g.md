---
article_id: 2026-08-23-freetoken-an-edge-native-moe-serving-engine-that-runs-753b-g
title: 'FreeToken: an edge-native MoE serving engine that runs 753B GLM-5.2 on a single
  workstation GPU'
date: '2026-08-23'
source: MarkTechPost
url_original: https://www.marktechpost.com/2026/08/23/meet-freetoken-an-edge-native-moe-serving-engine-that-runs-753b-glm-5-2-on-a-single-workstation-gpu/
url_canonical: https://www.marktechpost.com/2026/08/23/meet-freetoken-an-edge-native-moe-serving-engine-that-runs-753b-glm-5-2-on-a-single-workstation-gpu/
url_status: found
digest_source: digests\raw\2026-08-24_060708_Inbox_Daily AI News Digest - August 24,
  2026.md
content_hash: f1ec3b16db4728be01b62da56d7f5bedb3e562b139b85f6a4ac5ecf6fd081623
normalized_title_hash: d0a10ac350bd9102
canonical_url_hash: 328a3992caf48f39
tags: []
entities:
- DeepSeek
themes:
- datacenter-infrastructure
cross_cutting_topics:
- china-compete
dedupe_status: duplicate
canonical_article_id: 2026-08-23-freetoken-an-edge-native-moe-serving-engine-running-a-753b-m
related_article_ids: []
embedding_id: 2026-08-23-freetoken-an-edge-native-moe-serving-engine-that-runs-753b-g
event_name: ''
---

# FreeToken: an edge-native MoE serving engine that runs 753B GLM-5.2 on a single workstation GPU

Researchers from UC Berkeley and UT Austin released FreeToken, an Apache-2.0 mixture-of-experts serving engine that splits each step's expert cache misses between PCIe fills and in-place CPU execution using profiled bandwidths, with bit-exact outputs and no router modification. Reported throughput is 77-83 tokens/sec on Qwen3.6-35B-A3B and 22-25 tokens/sec on DeepSeek-V4-Flash on an RTX 5090 (1.5-2.3x the best baseline), 39.3 tokens/sec for a 35B model on an 8GB RTX 4060 laptop, and 14.9 tokens/sec for 753B GLM-5.2 on a single RTX PRO 6000 versus 7.3 for llama.cpp. Worst-case time-to-first-token stayed under 44 seconds against 232s (llama.cpp), 179s (Ollama) and 946s (KTransformers). If it holds up, it materially lowers the hardware floor for running very large open models on-premises. AI Safety & Policy REGULATORYBREAKING

<!-- graph:start -->
## Connections

**Entities:** [[DeepSeek]]
**Topics:** [[Infrastructure & Compute]] · [[Global AI Race]]
**Canonical:** [[2026-08-23-freetoken-an-edge-native-moe-serving-engine-running-a-753b-m]]
<!-- graph:end -->
