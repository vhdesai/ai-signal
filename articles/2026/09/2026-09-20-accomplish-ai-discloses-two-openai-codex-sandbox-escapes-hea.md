---
article_id: 2026-09-20-accomplish-ai-discloses-two-openai-codex-sandbox-escapes-hea
title: 'Accomplish AI discloses two OpenAI Codex sandbox escapes: Heapjack and Overpatch'
date: '2026-09-20'
source: BleepingComputer
url_original: https://www.bleepingcomputer.com/news/security/openai-codex-heapjack-overpatch-sandbox-escapes-2026
url_canonical: https://www.bleepingcomputer.com/news/security/openai-codex-heapjack-overpatch-sandbox-escapes-2026
url_status: broken
digest_source: digests\raw\2026-09-20_070031_Inbox_Daily AI News Digest - September
  20, 2026.md
content_hash: de1a710eeea1fde49b391dcdb1400cc260360461ce85c7005070867f185bfb3e
normalized_title_hash: 1090c9e1e0ac99de
canonical_url_hash: fea0c82c272e23f9
tags:
- Breaking
- Hot
entities:
- OpenAI
themes:
- policy-regulation
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-09-12-context-engineering-inside-the-agent-harness-four-mechanisms
- 2026-07-20-openai-disclosed-that-an-internal-long-horizon-model-repeate
- 2026-07-21-openai-disclosed-that-an-internal-long-horizon-model-repeate
embedding_id: 2026-09-20-accomplish-ai-discloses-two-openai-codex-sandbox-escapes-hea
event_name: ''
---

# Accomplish AI discloses two OpenAI Codex sandbox escapes: Heapjack and Overpatch

BleepingComputer details a technical writeup from Oren Yomtov of Accomplish AI on two OpenAI Codex sandbox escapes. Heapjack turns a routine "open someone else's repo and ask about the code" workflow into unsandboxed RCE on a developer's machine by reading a trust token from V8 heap memory shared between trusted and untrusted contexts. Overpatch abuses Codex's apply_patch tool to expand write permissions by naming /tmp in a patch, then symlinking into $HOME to modify .zshrc. Both were reported August 12 and patched within eight days. Sandbox-escape risk is now systematic across coding agents — not specific to any one model.

<!-- graph:start -->
## Connections

**Entities:** [[OpenAI]]
**Topics:** [[Policy & Regulation]]
**Related:** [[2026-09-12-context-engineering-inside-the-agent-harness-four-mechanisms]] · [[2026-07-20-openai-disclosed-that-an-internal-long-horizon-model-repeate]] · [[2026-07-21-openai-disclosed-that-an-internal-long-horizon-model-repeate]]
<!-- graph:end -->
