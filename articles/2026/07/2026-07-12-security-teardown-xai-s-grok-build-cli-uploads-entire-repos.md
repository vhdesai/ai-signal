---
article_id: 2026-07-12-security-teardown-xai-s-grok-build-cli-uploads-entire-repos
title: 'Security Teardown: xAI''s Grok Build CLI Uploads Entire Repos — Including
  .env Secrets — to xAI Cloud'
date: '2026-07-12'
source: byteiota**
url_original: https://byteiota.com/grok-build-cli-uploads-repo-xai-servers/
url_canonical: https://byteiota.com/grok-build-cli-uploads-repo-xai-servers/
url_status: found
digest_source: digests\raw\2026-07-13_065032_Final-Daily-AI-News-Digest.md
content_hash: 703fb4ea26944e374c279f79ac369f1a5dee149eecd24c5e244639a1c1be290e
normalized_title_hash: 1db02ed636d5be3f
canonical_url_hash: cffd999087782316
tags:
- Breaking
- Security
entities:
- Google
- xAI
themes:
- company-storylines
cross_cutting_topics: []
dedupe_status: duplicate
canonical_article_id: 2026-07-12-security-teardown-says-xai-s-grok-build-cli-uploads-entire-r
related_article_ids: []
embedding_id: 2026-07-12-security-teardown-xai-s-grok-build-cli-uploads-entire-repos
event_name: ''
---

# Security Teardown: xAI's Grok Build CLI Uploads Entire Repos — Including .env Secrets — to xAI Cloud

A wire-level analysis found xAI's Grok Build CLI (v0.2.93) transmits a user's full repository — not just files the agent reads — to a Google Cloud Storage bucket. In one test a 12 GB repo generated 5.1 GB of uploads, with an unredacted .env file sent verbatim, and the opt-out reportedly did not stop transfers despite "local-first" marketing. Enterprises piloting agentic coding tools should audit egress before wider deployment.

<!-- graph:start -->
## Connections

**Entities:** [[Google]] · [[xAI]]
**Topics:** [[Corporate Moves]]
**Canonical:** [[2026-07-12-security-teardown-says-xai-s-grok-build-cli-uploads-entire-r]]
<!-- graph:end -->
