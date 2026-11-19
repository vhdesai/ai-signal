---
article_id: 2026-11-14-stanford-s-open-source-memorilla-compresses-a-whole-document
title: Stanford's open-source Memorilla compresses a whole document collection into
  16 tokens a frozen LLM can read
date: '2026-11-14'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/11/14/stanford-memorilla-memory-system-16-memory-tokens/
url_canonical: https://www.marktechpost.com/2026/11/14/stanford-memorilla-memory-system-16-memory-tokens/
url_status: broken
digest_source: digests\raw\2026-11-14_061857_Inbox_Daily AI News Digest - November
  14, 2026.md
content_hash: 630a5b41dc57dec3e1779f8e0e7629a511faf6ef30dd93193b694dee200eb134
normalized_title_hash: b6a6c884cd48c5c6
canonical_url_hash: 9397e3a3601313b3
tags: []
entities: []
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: duplicate
canonical_article_id: 2026-11-14-jure-leskovec-s-snap-group-at-stanford-released-memorilla-a
related_article_ids: []
embedding_id: 2026-11-14-stanford-s-open-source-memorilla-compresses-a-whole-document
event_name: ''
---

# Stanford's open-source Memorilla compresses a whole document collection into 16 tokens a frozen LLM can read

Jure Leskovec's SNAP group at Stanford, with co-authors from Toronto, Penn and MIT, trained a 194M-parameter memory module that sits in front of an unchanged Qwen3-8B model. For each question, the module reads the whole document collection and condenses it into 16 "memory tokens" the model can use. The authors report 84.33% on the FactKG benchmark, versus 80.43% when every document is placed in the prompt, while using 108x fewer document tokens. It had the best average across eight benchmarks but lost on short-document tasks such as PubMedQA. Code and checkpoints are released under Apache 2.0, giving enterprise retrieval teams a practical alternative to ever-longer prompts.

<!-- graph:start -->
## Connections

**Topics:** [[Model Breakthroughs]]
**Canonical:** [[2026-11-14-jure-leskovec-s-snap-group-at-stanford-released-memorilla-a]]
<!-- graph:end -->
