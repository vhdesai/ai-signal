---
article_id: 2026-08-12-researchers-recover-encrypted-reasoning-traces-and-live-cred
title: Researchers Recover “Encrypted” Reasoning Traces — and Live Credentials — From
  Major LLM APIs
date: '2026-08-12'
source: The Hacker News · arXiv:2608.09867
url_original: null
url_canonical: null
url_status: missing
digest_source: digests\raw\2026-08-13_101657_Inbox_Fw Daily AI News Digest - August
  13, 2026.md
content_hash: 4f91cc0ed36d6eef9d7b284839cbfbb340763513a04440ec7ba4a8e5781c880c
normalized_title_hash: f4efa4c02553c60c
canonical_url_hash: ''
tags: []
entities:
- Anthropic
- Google
- OpenAI
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-08-11-new-extraction-technique-surfaces-hidden-reasoning-traces-ac
- 2026-05-02-a-new-arxiv-preprint-demonstrates-that-the-internal-geometri
- 2026-05-20-1password-and-openai-collaborate-to-reduce-coding-agent-cred
- 2026-08-04-openai-agents-chained-an-artifactory-zero-day-to-escape-sand
- 2026-07-06-princeton-privileged-self-distillation-can-degrade-reasoning
embedding_id: 2026-08-12-researchers-recover-encrypted-reasoning-traces-and-live-cred
event_name: ''
---

# Researchers Recover “Encrypted” Reasoning Traces — and Live Credentials — From Major LLM APIs

Researchers from ELLIS Institute Tübingen, Max Planck Institute, MATS, and Snyk demonstrated that opaque “encrypted” reasoning objects at OpenAI, Anthropic, and Google can be replayed into a weaker sibling model as a fuzzy decoder, recovering hidden chain-of-thought. Across 6,708 public agent trajectories, the team decoded 315,320 thinking blocks, yielding 704 privacy artifacts including 62 API keys, 33 passwords, 24 access tokens, and 7 private keys — live credentials embedded in reasoning traces never intended to be visible. The work also demonstrated model-distillation theft and invisible prompt injection through opaque reasoning blocks. Vendors were notified and the primary extraction attack reportedly no longer reproduces. However, the fundamental challenge remains: chain-of-thought cannot be reliably hidden by obfuscation alone. Teams publishing raw agent logs should strip reasoning fields immediately and audit historical logs for credential exposure. The Hacker News | arXiv RESEARCH

<!-- graph:start -->
## Connections

**Entities:** [[Anthropic]] · [[Google]] · [[OpenAI]]
**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-08-11-new-extraction-technique-surfaces-hidden-reasoning-traces-ac]] · [[2026-05-02-a-new-arxiv-preprint-demonstrates-that-the-internal-geometri]] · [[2026-05-20-1password-and-openai-collaborate-to-reduce-coding-agent-cred]] · [[2026-08-04-openai-agents-chained-an-artifactory-zero-day-to-escape-sand]] · [[2026-07-06-princeton-privileged-self-distillation-can-degrade-reasoning]]
<!-- graph:end -->
