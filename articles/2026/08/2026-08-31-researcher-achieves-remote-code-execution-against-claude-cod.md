---
article_id: 2026-08-31-researcher-achieves-remote-code-execution-against-claude-cod
title: Researcher Achieves Remote Code Execution Against Claude Code Opus 5 Auto Mode
date: '2026-08-31'
source: GovInfoSecurity
url_original: null
url_canonical: null
url_status: missing
digest_source: digests\raw\2026-09-01_081735_Inbox_Daily AI News Digest - September
  1, 2026.md
content_hash: 897768b5a7929eb9040dd029d4e4587b58bc05e98f7ae8784ef78022ad74ed34
normalized_title_hash: 15b55856525772c0
canonical_url_hash: ''
tags: []
entities:
- Anthropic
themes:
- model-capabilities
- company-storylines
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-06-27-researchers-turn-agentic-coding-tools-into-malware-vectors-v
- 2026-06-27-mozilla-researchers-show-ai-coding-agents-can-be-coerced-int
- 2026-04-01-anthropic-s-claude-code-platform-experienced-a-significant-s
- 2026-04-04-an-autonomous-ai-agent-leveraging-claude-exploited-kernel-vu
- 2026-08-17-ai-generated-security-fix-introduced-a-shell-injection-in-sn
embedding_id: 2026-08-31-researcher-achieves-remote-code-execution-against-claude-cod
event_name: ''
---

# Researcher Achieves Remote Code Execution Against Claude Code Opus 5 Auto Mode

Security researcher Johann Rehberger demonstrated an RCE attack chain against Anthropic's Claude Code Opus 5 in Auto Mode, exploiting a path from sanctioned fetch to direct curl usage, then leveraging Python module shadowing to execute a poisoned struct.py. The finding directly contradicts a commissioned evaluation reporting a 0.00% prompt-injection success rate. For enterprises piloting autonomous coding agents: this is a concrete argument for sandboxing and egress controls over model-level classifiers.

<!-- graph:start -->
## Connections

**Entities:** [[Anthropic]]
**Topics:** [[Model Breakthroughs]] · [[Corporate Moves]]
**Related:** [[2026-06-27-researchers-turn-agentic-coding-tools-into-malware-vectors-v]] · [[2026-06-27-mozilla-researchers-show-ai-coding-agents-can-be-coerced-int]] · [[2026-04-01-anthropic-s-claude-code-platform-experienced-a-significant-s]] · [[2026-04-04-an-autonomous-ai-agent-leveraging-claude-exploited-kernel-vu]] · [[2026-08-17-ai-generated-security-fix-introduced-a-shell-injection-in-sn]]
<!-- graph:end -->
