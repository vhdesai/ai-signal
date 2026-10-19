---
article_id: 2026-09-22-cisco-talos-documents-first-autonomous-ai-command-and-contro
title: Cisco Talos Documents First Autonomous AI Command-and-Control Implant
date: '2026-09-22'
source: The Register
url_original: https://www.theregister.com/security/2026/09/22/windows-closedquorum-malware-uses-ai-models-to-autonomously-select-post-compromise-actions/5298435
url_canonical: https://www.theregister.com/security/2026/09/22/windows-closedquorum-malware-uses-ai-models-to-autonomously-select-post-compromise-actions/5298435
url_status: ok
digest_source: digests\raw\2026-09-23_062154_Inbox_Daily AI News Digest - September
  23, 2026.md
content_hash: dec2fd42854505e7428289c06742055c884b09c546a550e1b5c1b57f0b1727b3
normalized_title_hash: 6e8670995898d6c2
canonical_url_hash: 1ccedf36f3068dce
tags: []
entities:
- DeepSeek
- Mistral
themes:
- datacenter-infrastructure
cross_cutting_topics:
- china-compete
dedupe_status: duplicate
canonical_article_id: 2026-09-22-cisco-talos-discloses-closedquorum-the-first-reported-autono
related_article_ids: []
embedding_id: 2026-09-22-cisco-talos-documents-first-autonomous-ai-command-and-contro
event_name: ''
---

# Cisco Talos Documents First Autonomous AI Command-and-Control Implant

Cisco Talos disclosed CLOSEDQUORUM, a Go-based Windows implant that queries four commercial LLM providers — Gemini, DeepSeek, Qwen and Mistral — which vote on the malware's next post-compromise action, with DeepSeek breaking ties. It requires no continued human operator and no attacker-run C2 server, targeting browser credentials and cryptocurrency wallets. Talos released it alongside CAIRN, an open-source metadata-first toolkit for hunting AI-integrated malware, and has not observed in-the-wild deployment, though artifacts link the developer to carding forum postings dating to 2025. The structural point for security leaders is "effort displacement": an attack phase that continues running when the operator is offline, and a multi-provider design that no single vendor cutoff defeats.

<!-- graph:start -->
## Connections

**Entities:** [[DeepSeek]] · [[Mistral]]
**Topics:** [[Infrastructure & Compute]] · [[Global AI Race]]
**Canonical:** [[2026-09-22-cisco-talos-discloses-closedquorum-the-first-reported-autono]]
<!-- graph:end -->
