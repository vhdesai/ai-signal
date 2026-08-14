---
article_id: 2026-06-26-nvidia-ships-a-nemotron-3-ultra-nvfp4-checkpoint-that-runs-o
title: NVIDIA ships a Nemotron 3 Ultra NVFP4 checkpoint that runs on both Hopper and
  Blackwell
date: '2026-06-26'
source: NVIDIA Developer Blog
url_original: https://developer.nvidia.com/blog/creating-the-nvidia-nemotron-3-ultra-nvfp4-checkpoint-with-nvidia-model-optimizer/
url_canonical: https://developer.nvidia.com/blog/creating-the-nvidia-nemotron-3-ultra-nvfp4-checkpoint-with-nvidia-model-optimizer/
url_status: found
digest_source: digests\raw\2026-06-27_092146_Inbox_Daily AI News Digest - June 27,
  2026.md
content_hash: 52716923775d870fd03fa3915f9259201b56f87010b4963668abf8f40d4ff043
normalized_title_hash: 8ce16a98764cf1de
canonical_url_hash: cd278d56ab374f39
tags: []
entities:
- NVIDIA
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-07-09-nvidia-s-iterative-puzzle-compresses-a-120b-hybrid-moe-to-75
- 2026-06-05-nvidia-ships-nemotron-3-ultra-its-largest-open-weights-reaso
- 2026-08-11-nvidia-is-developing-a-1-trillion-parameter-nemotron-4-open
- 2026-08-12-nvidia-reportedly-developing-nemotron-4-a-1-trillion-paramet
- 2026-07-17-nvidia-releases-nemotron-3-embed-an-open-embedding-collectio
embedding_id: 2026-06-26-nvidia-ships-a-nemotron-3-ultra-nvfp4-checkpoint-that-runs-o
event_name: ''
---

# NVIDIA ships a Nemotron 3 Ultra NVFP4 checkpoint that runs on both Hopper and Blackwell

NVIDIA detailed how it quantized its 550B-parameter Nemotron 3 Ultra to the 4-bit NVFP4 format using its Model Optimizer, shrinking the model from 1,121 GB to 352 GB (a 3.2× reduction) while matching BF16 accuracy on nearly every benchmark. A single checkpoint adapts to the hardware it runs on — W4A16 on Hopper, native W4A4 on Blackwell — and reports up to 5.9× higher decode-heavy throughput than a comparable competing FP4 model. The work targets the rising cost of moving large model weights as context windows lengthen. Research Breakthroughs RESEARCH AGENTS

<!-- graph:start -->
## Connections

**Entities:** [[NVIDIA]]
**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-07-09-nvidia-s-iterative-puzzle-compresses-a-120b-hybrid-moe-to-75]] · [[2026-06-05-nvidia-ships-nemotron-3-ultra-its-largest-open-weights-reaso]] · [[2026-08-11-nvidia-is-developing-a-1-trillion-parameter-nemotron-4-open]] · [[2026-08-12-nvidia-reportedly-developing-nemotron-4-a-1-trillion-paramet]] · [[2026-07-17-nvidia-releases-nemotron-3-embed-an-open-embedding-collectio]]
<!-- graph:end -->
