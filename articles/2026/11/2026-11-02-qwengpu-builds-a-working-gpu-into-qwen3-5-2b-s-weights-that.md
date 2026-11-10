---
article_id: 2026-11-02-qwengpu-builds-a-working-gpu-into-qwen3-5-2b-s-weights-that
title: qwenGPU builds a working GPU into Qwen3.5-2B's weights that runs real CUDA
  code
date: '2026-11-02'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/11/01/qwengpu-simt-gpu-compiled-into-qwen3-5-2b-weights-runs-cuda/
url_canonical: https://www.marktechpost.com/2026/11/01/qwengpu-simt-gpu-compiled-into-qwen3-5-2b-weights-runs-cuda/
url_status: broken
digest_source: digests\raw\2026-11-02_061330_Inbox_Daily AI News Digest - November
  2, 2026.md
content_hash: 4bf4cf4ff15439d172a99ffb5548e32e89603c1692b44edb64523a5b8f330206
normalized_title_hash: 6adfd4f2f195fee8
canonical_url_hash: cb91a6f21f786858
tags: []
entities:
- NVIDIA
- OpenAI
themes:
- datacenter-infrastructure
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-11-02-an-independent-developer-released-qwengpu-mit-license-which
- 2026-08-12-nvidia-details-serving-alibaba-s-2-4t-parameter-qwen3-8-mode
- 2026-05-17-an-open-source-project-called-orthrus-qwen3-claims-up-to-7-8
- 2026-08-23-27b-open-model-reverse-engineered-a-licensed-app-in-30-minut
- 2026-08-15-alibaba-releases-qwen3-8-27b-open-weights-with-long-context
embedding_id: 2026-11-02-qwengpu-builds-a-working-gpu-into-qwen3-5-2b-s-weights-that
event_name: ''
---

# qwenGPU builds a working GPU into Qwen3.5-2B's weights that runs real CUDA code

An independent developer added 45 untrained layers, with weights calculated by a compiler, to Qwen3.5-2B. The layers implement a small four-lane GPU that executes real CUDA code inside the model's forward passes. In the developer's tests, every program launch produced exact results, the reference interpreter matched an NVIDIA T4 on 49 of 49 programs, and the model's normal text output changed only negligibly. Throughput is about 10 to 15 tokens per second, so this is a research demonstration of exact computation inside an LLM, not a practical tool. Academic Research No qualifying publication from the monitored universities was verified in this 24-hour window. AI Safety & Policy OPENAI POLICY MIDTERMS

<!-- graph:start -->
## Connections

**Entities:** [[NVIDIA]] · [[OpenAI]]
**Topics:** [[Infrastructure & Compute]]
**Related:** [[2026-11-02-an-independent-developer-released-qwengpu-mit-license-which]] · [[2026-08-12-nvidia-details-serving-alibaba-s-2-4t-parameter-qwen3-8-mode]] · [[2026-05-17-an-open-source-project-called-orthrus-qwen3-claims-up-to-7-8]] · [[2026-08-23-27b-open-model-reverse-engineered-a-licensed-app-in-30-minut]] · [[2026-08-15-alibaba-releases-qwen3-8-27b-open-weights-with-long-context]]
<!-- graph:end -->
