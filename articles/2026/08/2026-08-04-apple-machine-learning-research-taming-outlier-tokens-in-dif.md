---
article_id: 2026-08-04-apple-machine-learning-research-taming-outlier-tokens-in-dif
title: 'Apple Machine Learning Research: Taming Outlier Tokens in Diffusion Transformers'
date: '2026-08-04'
source: Apple Machine Learning Research
url_original: https://machinelearning.apple.com/research/taming-outlier-tokens
url_canonical: https://machinelearning.apple.com/research/taming-outlier-tokens
url_status: ok
digest_source: digests\raw\2026-08-06_061721_Inbox_Daily AI News Digest - August 6,
  2026.md
content_hash: 720e9e8b110254969417f858123578c4964388de206f230226bd63a0de84a73d
normalized_title_hash: a29ac4d244b143e4
canonical_url_hash: bf8f6a60ac502b75
tags: []
entities:
- Apple
themes:
- datacenter-infrastructure
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-08-05-apple-research-targets-outlier-token-artifacts-in-diffusion
- 2026-06-27-bytedance-and-renmin-university-release-illada-an-8b-diffusi
- 2026-08-07-apple-compares-diffusion-and-autoregressive-language-model-p
- 2026-08-03-apple-researchers-study-alignment-methods-for-multimodal-llm
- 2026-05-28-resae-residualized-sparse-autoencoders-for-multi-layer-trans
embedding_id: 2026-08-04-apple-machine-learning-research-taming-outlier-tokens-in-dif
event_name: ''
---

# Apple Machine Learning Research: Taming Outlier Tokens in Diffusion Transformers

Apple (with Rice University collaborators) published research on "outlier tokens" — anomalously high-norm tokens that degrade image quality in Diffusion Transformers. The paper shows masking such tokens does not resolve the issue, since the root cause is corrupted local patch semantics, and introduces Dual-Stage Registers (DSR), a register-based intervention applied at both encoder and denoiser stages. Evaluated on ImageNet and large-scale text-to-image generation, DSR reduces artifacts and improves output quality — a reliability fix relevant to production image-generation systems. Academic Research ACADEMIC

<!-- graph:start -->
## Connections

**Entities:** [[Apple]]
**Topics:** [[Infrastructure & Compute]]
**Related:** [[2026-08-05-apple-research-targets-outlier-token-artifacts-in-diffusion]] · [[2026-06-27-bytedance-and-renmin-university-release-illada-an-8b-diffusi]] · [[2026-08-07-apple-compares-diffusion-and-autoregressive-language-model-p]] · [[2026-08-03-apple-researchers-study-alignment-methods-for-multimodal-llm]] · [[2026-05-28-resae-residualized-sparse-autoencoders-for-multi-layer-trans]]
<!-- graph:end -->
