---
article_id: 2026-11-07-buoyant-open-sources-kinference-a-routing-layer-for-running
title: Buoyant open-sources Kinference, a routing layer for running vLLM on Kubernetes
date: '2026-11-07'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/11/07/buoyant-kinference-open-source-inference-control-plane-kubernetes-vllm/
url_canonical: https://www.marktechpost.com/2026/11/07/buoyant-kinference-open-source-inference-control-plane-kubernetes-vllm/
url_status: ok
digest_source: digests\raw\2026-11-07_061155_Inbox_Daily AI News Digest - November
  7, 2026.md
content_hash: 04e2084791ead84139fa0506b5001c5a7d53a448e32e8ed68fb100dc02c98a44
normalized_title_hash: 1d94f702ffaf0bd1
canonical_url_hash: daa5b2afd1c7092c
tags: []
entities:
- Google
themes:
- company-storylines
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-11-06-november-7-2026-marktechpost
- 2026-11-07-inference-plumbing-matures-buoyant-open-sources-kinference-a
- 2026-10-11-vllm-semantic-router-releases-decision-3-0-open-decision-mod
embedding_id: 2026-11-07-buoyant-open-sources-kinference-a-routing-layer-for-running
event_name: ''
---

# Buoyant open-sources Kinference, a routing layer for running vLLM on Kubernetes

Buoyant, the maker of Linkerd, released Kinference, an early alpha written in Rust under the Apache 2.0 license. It sits in front of fleets of vLLM model servers and decides where each request goes. Teams write rules such as routing simple prompts to cheaper models, sending overflow to cloud providers, keeping prompts with personal data on local servers, and sending each request to a server that already holds its prompt in cache. In Buoyant's own benchmark, median time to first token fell 95% on prompts that share the same opening text and did not improve on prompts that don't. For companies running open-weight models in-house, cost-aware routing is becoming its own layer of the platform. Infrastructure GOOGLE DATA CENTERS

<!-- graph:start -->
## Connections

**Entities:** [[Google]]
**Topics:** [[Corporate Moves]]
**Related:** [[2026-11-06-november-7-2026-marktechpost]] · [[2026-11-07-inference-plumbing-matures-buoyant-open-sources-kinference-a]] · [[2026-10-11-vllm-semantic-router-releases-decision-3-0-open-decision-mod]]
<!-- graph:end -->
