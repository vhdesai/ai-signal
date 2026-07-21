---
article_id: 2026-07-11-compromised-jscrambler-npm-release-drops-a-rust-infostealer
title: Compromised jscrambler npm release drops a Rust infostealer targeting AI dev
  tools
date: '2026-07-11'
source: The Hacker News
url_original: null
url_canonical: null
url_status: missing
digest_source: digests\raw\2026-07-12_060557_Inbox_Daily AI News Digest - July 12,
  2026.md
content_hash: 5722d02377c72ef500b8a5c4d4e99479e9b8dd119ec524136dbf9abae695abae
normalized_title_hash: f7f2d9f4caa4d5d6
canonical_url_hash: ''
tags:
- Breaking
entities: []
themes:
- company-storylines
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-07-11-compromised-npm-package-drops-rust-infostealer-targeting-ai
- 2026-04-04-an-npm-packaging-error-exposed-512-000-lines-of-claude-code
- 2026-05-12-mini-shai-hulud-worm-compromises-mistral-ai-pypi-tanstack-np
- 2026-06-27-researchers-turn-agentic-coding-tools-into-malware-vectors-v
embedding_id: 2026-07-11-compromised-jscrambler-npm-release-drops-a-rust-infostealer
event_name: ''
---

# Compromised jscrambler npm release drops a Rust infostealer targeting AI dev tools

The official jscrambler npm package was compromised across several releases; a preinstall hook silently drops and executes a ~7.8 MB cross-platform Rust infostealer (Windows, macOS, Linux) that targets cloud credentials, browser data, and crypto wallets. Notably, it also harvests the configuration files of AI coding tools including Claude Desktop, Cursor, Windsurf, VS Code, and Zed. Socket flagged the release within six minutes of publication, and no fix was available as of July 11 — worth a heads-up to any engineering teams using these tools.

<!-- graph:start -->
## Connections

**Topics:** [[Corporate Moves]]
**Related:** [[2026-07-11-compromised-npm-package-drops-rust-infostealer-targeting-ai]] · [[2026-04-04-an-npm-packaging-error-exposed-512-000-lines-of-claude-code]] · [[2026-05-12-mini-shai-hulud-worm-compromises-mistral-ai-pypi-tanstack-np]] · [[2026-06-27-researchers-turn-agentic-coding-tools-into-malware-vectors-v]]
<!-- graph:end -->
