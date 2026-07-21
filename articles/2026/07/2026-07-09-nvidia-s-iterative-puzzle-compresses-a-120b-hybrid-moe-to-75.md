---
article_id: 2026-07-09-nvidia-s-iterative-puzzle-compresses-a-120b-hybrid-moe-to-75
title: NVIDIA's “Iterative Puzzle” compresses a 120B hybrid MoE to 75B, roughly doubling
  throughput
date: '2026-07-09'
source: NVIDIA
url_original: https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4
url_canonical: https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4
url_status: found
digest_source: digests\raw\2026-07-10_062836_Inbox_Daily AI News Digest - July 10,
  2026.md
content_hash: 8455f8ebe969a17e4a2607b168fe781f40ec70cba81818fafd436488ed954ec0
normalized_title_hash: e9a5b8e84d04c8ed
canonical_url_hash: e7c13fa05fe678c3
tags: []
entities:
- NVIDIA
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-06-26-nvidia-ships-a-nemotron-3-ultra-nvfp4-checkpoint-that-runs-o
- 2026-03-24-nvidia-open-sources-nemotron-cascade-2-efficient-30b-moe-for
- 2026-07-02-nvidia-releases-nemotron-labs-twotower-a-diffusion-llm-2-42
- 2026-07-01-nvidia-releases-nemotron-labs-twotower-an-open-weight-diffus
- 2026-05-20-nvidia-releases-nemotron-labs-diffusion-a-tri-mode-language
embedding_id: 2026-07-09-nvidia-s-iterative-puzzle-compresses-a-120b-hybrid-moe-to-75
event_name: ''
---

# NVIDIA's “Iterative Puzzle” compresses a 120B hybrid MoE to 75B, roughly doubling throughput

NVIDIA released Nemotron-Labs-3-Puzzle-75B-A9B, a deployment-optimized compression of Nemotron-3-Super (120.7B→75.3B total, 12.8B→9.3B active) that preserves the 88-block Mamba/MoE/attention layout. The “Iterative Puzzle” method alternates hardware-aware structural pruning with distillation, reporting ~2x server throughput on 8×B200 at modest quality cost (−4.2 Arena-Hard-V2, −2.6 SWE-Bench) with long-context benchmarks barely moving. Weights ship on Hugging Face in BF16/FP8/NVFP4.

<!-- graph:start -->
## Connections

**Entities:** [[NVIDIA]]
**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-06-26-nvidia-ships-a-nemotron-3-ultra-nvfp4-checkpoint-that-runs-o]] · [[2026-03-24-nvidia-open-sources-nemotron-cascade-2-efficient-30b-moe-for]] · [[2026-07-02-nvidia-releases-nemotron-labs-twotower-a-diffusion-llm-2-42]] · [[2026-07-01-nvidia-releases-nemotron-labs-twotower-an-open-weight-diffus]] · [[2026-05-20-nvidia-releases-nemotron-labs-diffusion-a-tri-mode-language]]
<!-- graph:end -->
