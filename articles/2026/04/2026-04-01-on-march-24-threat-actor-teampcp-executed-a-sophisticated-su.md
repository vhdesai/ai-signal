---
article_id: 2026-04-01-on-march-24-threat-actor-teampcp-executed-a-sophisticated-su
title: On March 24, threat actor TeamPCP executed a sophisticated supply chain attack
  against LiteLLM — the Python package…
date: '2026-04-01'
source: Daily AI News Digest
url_original: null
url_canonical: null
url_status: missing
digest_source: digests\raw\2026-04-01_084004_Inbox_Daily AI News Digest – April 1,
  2026.md
content_hash: 7d18042fddc55e2fe3102b4b1cec3deff12af38ab5d9beae988c3ee8fedac5e4
normalized_title_hash: bb6e36c54f369992
canonical_url_hash: ''
tags: []
entities:
- Amazon
themes:
- policy-regulation
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-04-01-litellm-supply-chain-attack-exposes-ai-developer-ecosystem-t
- 2026-04-04-mercor-the-10b-ai-startup-serving-anthropic-openai-and-meta
- 2026-04-04-mercor-data-breach-supply-chain-attack-on-litellm-exposes-ai
- 2026-05-22-wired-reported-that-the-group-behind-a-recent-github-reposit
- 2026-04-01-mercor-a-10b-ai-recruiting-platform-serving-openai-and-anthr
embedding_id: 2026-04-01-on-march-24-threat-actor-teampcp-executed-a-sophisticated-su
event_name: ''
---

# On March 24, threat actor TeamPCP executed a sophisticated supply chain attack against LiteLLM — the Python package…

On March 24, threat actor TeamPCP executed a sophisticated supply chain attack against LiteLLM — the Python package with 97 million monthly downloads that acts as a universal adapter for over 100 LLM APIs. Attackers compromised LiteLLM's CI/CD pipeline via a poisoned version of the Trivy open-source security scanner, stealing PyPI publishing credentials and uploading two backdoored versions (1.82.7 and 1.82.8) that harvested SSH keys, AWS/GCP/Azure credentials, Kubernetes secrets, and environment files. Despite a 46-minute exposure window, the blast radius is estimated at 500,000+ corporate identities and 300GB+ of compressed credentials, given LiteLLM's deep integration into frameworks including CrewAI, DSPy, and Mem0. Virtually any enterprise building AI agents in Python is potentially affected.

<!-- graph:start -->
## Connections

**Entities:** [[Amazon]]
**Topics:** [[Policy & Regulation]]
**Related:** [[2026-04-01-litellm-supply-chain-attack-exposes-ai-developer-ecosystem-t]] · [[2026-04-04-mercor-the-10b-ai-startup-serving-anthropic-openai-and-meta]] · [[2026-04-04-mercor-data-breach-supply-chain-attack-on-litellm-exposes-ai]] · [[2026-05-22-wired-reported-that-the-group-behind-a-recent-github-reposit]] · [[2026-04-01-mercor-a-10b-ai-recruiting-platform-serving-openai-and-anthr]]
<!-- graph:end -->
