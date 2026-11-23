---
article_id: 2026-11-21-columbia-and-certik-s-tensorlean-formally-verifies-the-gpu-k
title: Columbia and CertiK's TensorLean formally verifies the GPU kernels behind production
  AI
date: '2026-11-21'
source: '[MarkTechPost]'
url_original: null
url_canonical: null
url_status: missing
digest_source: digests\raw\2026-11-22_070553_Inbox_Daily AI News Digest - November
  22, 2026.md
content_hash: c11a251f350a3b1fb10fd451a07cec883091de981e8d939bf8fb9c31ad6990af
normalized_title_hash: 54e1f568bc1d37a2
canonical_url_hash: ''
tags: []
entities: []
themes:
- company-storylines
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-07-25-developer-guide-to-high-performance-gpu-kernels-with-tilelan
- 2026-08-28-nvidia-tensorrt-model-connect-simplifies-open-model-deployme
- 2026-05-07-new-zaya1-8b-competitive-open-reasoning-model-trained-entire
embedding_id: 2026-11-21-columbia-and-certik-s-tensorlean-formally-verifies-the-gpu-k
event_name: ''
---

# Columbia and CertiK's TensorLean formally verifies the GPU kernels behind production AI

Researchers from Columbia University and CertiK introduced TensorLean, a Lean-based framework that proves compiled GPU kernels match a tensor-level math specification at the PTX level, checking for data races, termination, numerical correctness and untouched memory. Applied to 149 kernel instances, including every FlashAttention-2, -3 and -4 kernel plus DeepGEMM, it proved 83 correct, and the remaining 66 led to 38 correctness bugs across six projects. One find was a FlashAttention-4 data race that never surfaced in 17,760 test runs, a strong case for formal methods in the low-level code that training and inference depend on. MarkTechPost: TensorLean formal verification of GPU kernels<https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fwww.marktechpost.com%2F2026%2F11%2F21%2Fcolumbia-certik-tensorlean-formal-verification-gpu-kernels%2F&data=05%7C02%7Cvdesai%40microsoft.com%7C2c29963662a140e7713f08df48aa165a%7C72f988bf86f141af91ab2d7cd011db47%7C1%7C0%7C639309567532216142%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=bbD9TRfnWZCQ%2BJnxh05c%2BmEU2sMDmshUFvtCm%2BpNUm4%3D&reserved=0>

<!-- graph:start -->
## Connections

**Topics:** [[Corporate Moves]]
**Related:** [[2026-07-25-developer-guide-to-high-performance-gpu-kernels-with-tilelan]] · [[2026-08-28-nvidia-tensorrt-model-connect-simplifies-open-model-deployme]] · [[2026-05-07-new-zaya1-8b-competitive-open-reasoning-model-trained-entire]]
<!-- graph:end -->
