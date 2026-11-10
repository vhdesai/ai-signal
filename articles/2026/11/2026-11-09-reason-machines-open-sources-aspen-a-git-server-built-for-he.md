---
article_id: 2026-11-09-reason-machines-open-sources-aspen-a-git-server-built-for-he
title: Reason Machines open-sources Aspen, a Git server built for heavy agent traffic
date: '2026-11-09'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/11/09/reason-machines-aspen-open-source-git-server-ai-agents/
url_canonical: https://www.marktechpost.com/2026/11/09/reason-machines-aspen-open-source-git-server-ai-agents/
url_status: ok
digest_source: digests\raw\2026-11-09_061126_Inbox_Daily AI News Digest - November
  9, 2026.md
content_hash: b28ca896100387fdcacc1e60b1c9650564687f4aa723d83b26d4d4891b1b469f
normalized_title_hash: a21553487168b89c
canonical_url_hash: 33785ca66bbf6af1
tags: []
entities:
- OpenAI
themes:
- company-storylines
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-11-09-agent-operations-get-their-own-plumbing-and-a-cautionary-tal
- 2026-09-21-google-open-sources-ax-an-agentic-orchestrator-for-kubernete
- 2026-08-08-shepherd-an-open-source-substrate-that-lets-meta-agents-fork
embedding_id: 2026-11-09-reason-machines-open-sources-aspen-a-git-server-built-for-he
event_name: ''
---

# Reason Machines open-sources Aspen, a Git server built for heavy agent traffic

Aspen is a single program written in Rust that stores branches in PostgreSQL or SQLite and stores code in object storage. It updates each branch independently, so pushes to different branches never wait on each other, following the design OpenAI described for its internal Pando server. Reason Machines reports 567 pushes per second sustained for five minutes on one 8-core server, with a median push latency of 208 ms. Pushes to main run at only about four per second, and the project is pre-alpha with no releases. Source control is becoming a bottleneck as companies run hundreds of coding agents at once.

<!-- graph:start -->
## Connections

**Entities:** [[OpenAI]]
**Topics:** [[Corporate Moves]]
**Related:** [[2026-11-09-agent-operations-get-their-own-plumbing-and-a-cautionary-tal]] · [[2026-09-21-google-open-sources-ax-an-agentic-orchestrator-for-kubernete]] · [[2026-08-08-shepherd-an-open-source-substrate-that-lets-meta-agents-fork]]
<!-- graph:end -->
