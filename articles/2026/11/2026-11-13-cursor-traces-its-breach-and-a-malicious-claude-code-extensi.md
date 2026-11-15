---
article_id: 2026-11-13-cursor-traces-its-breach-and-a-malicious-claude-code-extensi
title: Cursor traces its breach and a malicious Claude Code extension build to an
  access key leaked by Fireworks
date: '2026-11-13'
source: '[Cursor Blog]'
url_original: https://cursor.com/blog/security-incident-update
url_canonical: https://cursor.com/blog/security-incident-update
url_status: ok
digest_source: digests\raw\2026-11-14_061857_Inbox_Daily AI News Digest - November
  14, 2026.md
content_hash: 18cb6c84d2be2418b7e1db33b35dcad23b697faf7d655fa86168c9ed14e4621a
normalized_title_hash: 305f5da02218b06c
canonical_url_hash: 6f83cc8ccaf2e246
tags: []
entities:
- Anthropic
themes:
- policy-regulation
cross_cutting_topics: []
dedupe_status: duplicate
canonical_article_id: 2026-11-13-cursor-traces-a-malicious-claude-code-extension-to-a-key-lea
related_article_ids: []
embedding_id: 2026-11-13-cursor-traces-its-breach-and-a-malicious-claude-code-extensi
event_name: ''
---

# Cursor traces its breach and a malicious Claude Code extension build to an access key leaked by Fireworks

An attacker used a Cursor access key that its vendor Fireworks had exposed to copy coding-agent session logs (traces), mostly from 2025, collected from sessions not in Privacy Mode. A few of those logs contained credentials that had not been redacted, affecting fewer than 0.01% of customers. The attacker used them to reach Cursor's SaaS tools and archived code repositories. They then placed malicious builds of Anthropic's Claude Code extension on the cache serving Cursor's extension marketplace, where up to 5,000 users may have received them during an 11-hour window. Cursor says production systems, release-signing keys and data from Privacy Mode sessions were not affected, and that the last attacker activity was on November 1. The incident shows that agent session logs kept for model training can contain credentials and become an attack path. POLICY WHITE HOUSE CYBER

<!-- graph:start -->
## Connections

**Entities:** [[Anthropic]]
**Topics:** [[Policy & Regulation]]
**Canonical:** [[2026-11-13-cursor-traces-a-malicious-claude-code-extension-to-a-key-lea]]
<!-- graph:end -->
