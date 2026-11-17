---
article_id: 2026-11-13-google-open-sources-tpu-sync-to-move-kv-caches-and-weights-b
title: Google open-sources TPU Sync to move KV caches and weights between memory,
  storage, and network
date: '2026-11-13'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/11/13/google-tpu-sync-kv-cache-transfer-library/
url_canonical: https://www.marktechpost.com/2026/11/13/google-tpu-sync-kv-cache-transfer-library/
url_status: ok
digest_source: digests\raw\2026-11-13_061529_Inbox_Daily AI News Digest - November
  13, 2026.md
content_hash: d792d9b514f09fb276443bf7736710f36e68cfe5cfcb6a6af785d6349b4c298b
normalized_title_hash: 251259bafc1e7524
canonical_url_hash: dab0b7fbc2e835d3
tags: []
entities:
- Google
themes:
- datacenter-infrastructure
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-11-13-open-inference-plumbing-matures-google-open-sources-tpu-sync
- 2026-11-08-google-adds-confidential-computing-and-long-context-tpus-as
- 2026-10-27-openai-plans-to-buy-google-tpus-as-google-expands-ai-chips-b
embedding_id: 2026-11-13-google-open-sources-tpu-sync-to-move-kv-caches-and-weights-b
event_name: ''
---

# Google open-sources TPU Sync to move KV caches and weights between memory, storage, and network

TPU Sync is an open-source C++ library that moves KV caches and model weights between TPU high-bandwidth memory, host DRAM, storage, and the network. Google reports more than 90% lower KV-transfer latency on mixture-of-experts models with 235B to 480B parameters. Fast KV movement is what makes disaggregated serving (running prefill and decode on separate hardware) and long-context caching economical. Open-sourcing it strengthens TPUs as an inference platform as Hydrogen-style execution models increase token volume. Academic Research MIT ENGINEERING DESIGN HUMAN-IN-THE-LOOP

<!-- graph:start -->
## Connections

**Entities:** [[Google]]
**Topics:** [[Infrastructure & Compute]]
**Related:** [[2026-11-13-open-inference-plumbing-matures-google-open-sources-tpu-sync]] · [[2026-11-08-google-adds-confidential-computing-and-long-context-tpus-as]] · [[2026-10-27-openai-plans-to-buy-google-tpus-as-google-expands-ai-chips-b]]
<!-- graph:end -->
