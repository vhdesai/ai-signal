---
article_id: 2026-11-13-perplexity-releases-open-weight-decider-v1-3-models-that-ret
title: Perplexity releases open-weight Decider v1.3 models that return probabilities
  instead of text
date: '2026-11-13'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/11/13/perplexity-decider-v1-3-open-weight-decision-models-locate/
url_canonical: https://www.marktechpost.com/2026/11/13/perplexity-decider-v1-3-open-weight-decision-models-locate/
url_status: broken
digest_source: digests\raw\2026-11-14_061857_Inbox_Daily AI News Digest - November
  14, 2026.md
content_hash: afe3fb9ce830037835effe15f15792f1188492c330b216f5cb41a0136d56c65d
normalized_title_hash: d8430890b3343537
canonical_url_hash: 1dffd8e3f80675af
tags: []
entities:
- Perplexity
themes:
- company-storylines
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-11-13-perplexity-open-sources-decider-v1-3-small-models-that-retur
- 2026-11-14-perplexity-shipped-pplx-decider-v1-3-27b-on-qwen3-8-27b-and
- 2026-10-10-microsoft-releases-decision-1-a-qwen3-5-9b-decision-scoring
- 2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and
- 2026-09-24-bottlecap-ai-releases-thinkingcap-qwen3-8-27b-37-2-fewer-rea
embedding_id: 2026-11-13-perplexity-releases-open-weight-decider-v1-3-models-that-ret
event_name: ''
---

# Perplexity releases open-weight Decider v1.3 models that return probabilities instead of text

Perplexity's Decider models answer yes/no, multiple-choice and scoring questions by returning a probability for each option rather than generating text. They come in two sizes: about 27B parameters, built on Qwen3.8-27B, and a 4B Flash version built on Qwen3.5-4B. Version 1.3 adds Locate, which extracts exact text spans, and changes attention so that each question sees only the input and itself. Perplexity says this cuts the rate at which answers flip to 0.27%. All benchmark figures are self-reported, including 91.6% mean accuracy on 63 query-classification tasks. Weights are released under Apache 2.0. Small, cheap decision models like these suit the routing, guardrail and triage steps inside agent pipelines.

<!-- graph:start -->
## Connections

**Entities:** [[Perplexity]]
**Topics:** [[Corporate Moves]]
**Related:** [[2026-11-13-perplexity-open-sources-decider-v1-3-small-models-that-retur]] · [[2026-11-14-perplexity-shipped-pplx-decider-v1-3-27b-on-qwen3-8-27b-and]] · [[2026-10-10-microsoft-releases-decision-1-a-qwen3-5-9b-decision-scoring]] · [[2026-09-05-perplexity-details-its-gpu-embedding-stack-how-ivy-tulip-and]] · [[2026-09-24-bottlecap-ai-releases-thinkingcap-qwen3-8-27b-37-2-fewer-rea]]
<!-- graph:end -->
