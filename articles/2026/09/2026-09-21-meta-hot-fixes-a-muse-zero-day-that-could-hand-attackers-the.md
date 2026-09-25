---
article_id: 2026-09-21-meta-hot-fixes-a-muse-zero-day-that-could-hand-attackers-the
title: Meta hot-fixes a Muse zero-day that could hand attackers the agent's privileges
date: '2026-09-21'
source: Ars Technica
url_original: https://arstechnica.com/security/2026/09/muse-metas-extraordinarily-privileged-ai-assistant-has-a-serious-0-day/
url_canonical: https://arstechnica.com/security/2026/09/muse-metas-extraordinarily-privileged-ai-assistant-has-a-serious-0-day/
url_status: ok
digest_source: digests\raw\2026-09-22_060727_Inbox_Daily AI News Digest - September
  22, 2026.md
content_hash: 8ab05f98251f093e66d2000d3ab6e6cd78a752c69300fb44168cefe885200fc0
normalized_title_hash: 558de10da0c6dfe0
canonical_url_hash: 6af58b306bcd0e6e
tags:
- Breaking
entities:
- Amazon
- Meta
themes:
- policy-regulation
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-18-meta-s-muse-assistant-lands-on-mac-with-computer-use-actions
- 2026-09-19-meta-launches-muse-for-mac-with-a-separate-agent-gating-all
- 2026-09-21-meta-s-muse-outpaces-chatgpt-s-early-mobile-launch-in-the-us
- 2026-09-22-amazon-blocks-meta-s-muse-agent-opening-the-platform-permiss
embedding_id: 2026-09-21-meta-hot-fixes-a-muse-zero-day-that-could-hand-attackers-the
event_name: ''
---

# Meta hot-fixes a Muse zero-day that could hand attackers the agent's privileges

Researcher Patrick Wardle disclosed that Muse, Meta's month-old macOS personal agent, exposed an undocumented setting controlling where dictation is transcribed; any unprivileged local process could redirect it to an attacker-controlled endpoint and capture the user's Muse authentication token. Because Muse holds broad delegated access to files, mail, calendar, browser and connected accounts, the flaw functions as access amplification rather than remote code execution. Wardle published a proof-of-concept and confirmed on September 22 that Meta had hot-fixed the issue within roughly a day; Meta characterized it as local privilege escalation. The disclosure lands alongside Amazon's decision to block Muse from its shopping platform. Academic Research RESEARCH MATHEMATICS

<!-- graph:start -->
## Connections

**Entities:** [[Amazon]] · [[Meta]]
**Topics:** [[Policy & Regulation]] · [[Model Breakthroughs]]
**Related:** [[2026-09-18-meta-s-muse-assistant-lands-on-mac-with-computer-use-actions]] · [[2026-09-19-meta-launches-muse-for-mac-with-a-separate-agent-gating-all]] · [[2026-09-21-meta-s-muse-outpaces-chatgpt-s-early-mobile-launch-in-the-us]] · [[2026-09-22-amazon-blocks-meta-s-muse-agent-opening-the-platform-permiss]]
<!-- graph:end -->
