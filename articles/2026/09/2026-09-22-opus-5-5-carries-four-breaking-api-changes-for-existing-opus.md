---
article_id: 2026-09-22-opus-5-5-carries-four-breaking-api-changes-for-existing-opus
title: Opus 5.5 carries four breaking API changes for existing Opus 5 code
date: '2026-09-22'
source: Claude Platform Docs
url_original: https://platform.claude.com/docs/en/models/opus-5-5/overview
url_canonical: https://platform.claude.com/docs/en/models/opus-5-5/overview
url_status: ok
digest_source: digests\raw\2026-09-23_062038_Inbox_Daily AI News Digest - September
  23, 2026.md
content_hash: 22cb077d80e9c3bd439da5e6eeb33da7d64e4bb077c0ac3dce398f4e5d62f0ce
normalized_title_hash: cda6644b423bc3c6
canonical_url_hash: 4d070c5c8c674d4e
tags: []
entities:
- Amazon
- Anthropic
- Google
- Microsoft
themes:
- model-capabilities
- infrastructure-investments
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-07-11-claude-opus-4-7-is-now-generally-available
- 2026-05-17-anthropic-released-claude-opus-4-7-fast-this-week-an-inferen
- 2026-05-02-anthropic-releases-claude-opus-4-7-with-improved-software-en
- 2026-08-11-anthropic-confirms-it-will-watermark-text-generated-by-claud
embedding_id: 2026-09-22-opus-5-5-carries-four-breaking-api-changes-for-existing-opus
event_name: ''
---

# Opus 5.5 carries four breaking API changes for existing Opus 5 code

Migration is not a drop-in swap. Anthropic's platform documentation lists four changes that break code running on Opus 5: adaptive thinking cannot be disabled, forced tool use returns an error, thinking blocks are now bound to the model and conversation so replays fail, and the earlier computer-use tool is rejected on the Claude API and Google Cloud. A fifth change alters response shape without failing requests — text between tool calls returns in thinking blocks that are empty at the default display setting, which silently breaks applications that stream that text as progress updates. The model is live on the Claude API, Amazon Bedrock, Google Cloud and Microsoft Foundry with a 1M-token context and 128K max output. Industry News FUNDING

<!-- graph:start -->
## Connections

**Entities:** [[Amazon]] · [[Anthropic]] · [[Google]] · [[Microsoft]]
**Topics:** [[Model Breakthroughs]] · [[Infrastructure Investments]]
**Related:** [[2026-07-11-claude-opus-4-7-is-now-generally-available]] · [[2026-05-17-anthropic-released-claude-opus-4-7-fast-this-week-an-inferen]] · [[2026-05-02-anthropic-releases-claude-opus-4-7-with-improved-software-en]] · [[2026-08-11-anthropic-confirms-it-will-watermark-text-generated-by-claud]]
<!-- graph:end -->
