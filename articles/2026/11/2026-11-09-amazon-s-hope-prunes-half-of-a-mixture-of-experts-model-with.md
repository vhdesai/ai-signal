---
article_id: 2026-11-09-amazon-s-hope-prunes-half-of-a-mixture-of-experts-model-with
title: Amazon's HOPE prunes half of a mixture-of-experts model without retraining
date: '2026-11-09'
source: Hugging Face Blog
url_original: null
url_canonical: https://www.explainx.ai/blog/amazon-hope-moe-expert-pruning-second-order-awslabs-2026
url_status: repaired
digest_source: digests\raw\2026-11-09_084913_Inbox_Daily AI News Digest - November
  9, 2026.md
content_hash: 9bfdf1455cbb5743cb008c9d2d55e927978ed7ac6db05c552a6d2c57dfacfde4
normalized_title_hash: 451320b88300f8df
canonical_url_hash: ''
tags: []
entities:
- Amazon
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-10-12-amazon-science-reports-priming-method-to-alter-model-archite
- 2026-05-16-allen-institute-uc-berkeley-emo-architecture-cuts-moe-infere
- 2026-09-06-meta-fair-introduces-research-preference-models-to-rank-expe
embedding_id: 2026-11-09-amazon-s-hope-prunes-half-of-a-mixture-of-experts-model-with
event_name: ''
---

# Amazon's HOPE prunes half of a mixture-of-experts model without retraining

Amazon researchers introduced Higher-Order Pruning of Experts, which accounts for how experts cooperate when deciding which to remove from mixture-of-experts models. Expert layers make up about 95% of Qwen3.5-122B's roughly 250 GB memory footprint, even though only a handful of its 256 experts per layer fire for any token. At 50% pruning, HOPE posts the best average rank of the methods tested, with gains of up to 6.1% on agentic coding tasks over the next-best approach, pointing to cheaper MoE serving without a retraining cycle. Sources - Hugging Face Blog: Higher-Order Pruning of Experts Academic Research RESEARCH ROBOTICS

<!-- graph:start -->
## Connections

**Entities:** [[Amazon]]
**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-10-12-amazon-science-reports-priming-method-to-alter-model-archite]] · [[2026-05-16-allen-institute-uc-berkeley-emo-architecture-cuts-moe-infere]] · [[2026-09-06-meta-fair-introduces-research-preference-models-to-rank-expe]]
<!-- graph:end -->
