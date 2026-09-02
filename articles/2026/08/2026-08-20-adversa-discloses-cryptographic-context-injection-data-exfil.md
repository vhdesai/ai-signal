---
article_id: 2026-08-20-adversa-discloses-cryptographic-context-injection-data-exfil
title: Adversa Discloses 'Cryptographic Context Injection' Data-Exfiltration Attack
  on Grok
date: '2026-08-20'
source: The Hacker News
url_original: https://thehackernews.com/2026/08/new-cryptographic-context-injection.html
url_canonical: https://thehackernews.com/2026/08/new-cryptographic-context-injection.html
url_status: found
digest_source: digests\raw\2026-08-21_060810_Inbox_Daily AI News Digest - August 21,
  2026.md
content_hash: 9a85c274a53a463de88610ed12bf8da20db6999def61c785510751bd610c332b
normalized_title_hash: 1d9f95715e486c5a
canonical_url_hash: eaaed4290b794f92
tags:
- Breaking
- Hot
entities:
- xAI
themes:
- policy-regulation
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-08-20-grok-keeps-sending-gibberish-responses-to-users
- 2026-08-21-zero-click-cryptographic-context-injection-attack-steals-gro
- 2026-07-01-investigation-finds-xai-s-grok-bypassing-its-own-safety-guar
- 2026-07-14-security-concern-grok-build-xai-uploads-entire-git-repositor
embedding_id: 2026-08-20-adversa-discloses-cryptographic-context-injection-data-exfil
event_name: ''
---

# Adversa Discloses 'Cryptographic Context Injection' Data-Exfiltration Attack on Grok

Security firm Adversa AI disclosed a technique that can make xAI's Grok exfiltrate a user's name, approximate location, subscription tier and conversation prompts to an attacker's server after being asked to summarize a web page. The attack smuggles instructions as encrypted ciphertext that Grok decrypts inside its own code runtime, bypassing content classifiers with no confirmation step. Adversa reported roughly a 40% success rate when tested against Grok 4.5 Fast. There is no patch or CVE, and the writeup reports no exploitation in the wild.

<!-- graph:start -->
## Connections

**Entities:** [[xAI]]
**Topics:** [[Policy & Regulation]]
**Related:** [[2026-08-20-grok-keeps-sending-gibberish-responses-to-users]] · [[2026-08-21-zero-click-cryptographic-context-injection-attack-steals-gro]] · [[2026-07-01-investigation-finds-xai-s-grok-bypassing-its-own-safety-guar]] · [[2026-07-14-security-concern-grok-build-xai-uploads-entire-git-repositor]]
<!-- graph:end -->
