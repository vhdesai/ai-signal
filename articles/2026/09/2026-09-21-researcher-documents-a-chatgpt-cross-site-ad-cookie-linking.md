---
article_id: 2026-09-21-researcher-documents-a-chatgpt-cross-site-ad-cookie-linking
title: Researcher documents a ChatGPT cross-site ad cookie linking browsing to accounts
date: '2026-09-21'
source: Notebookcheck
url_original: https://www.notebookcheck.net/ChatGPT-s_obi-cookie-follows-you-to-other-websites.1404436.0.html
url_canonical: https://www.kucoin.com/news/flash/openai-chatgpt-tracks-user-activity-across-websites-via-cookie
url_status: repaired
digest_source: digests\raw\2026-09-21_060600_Inbox_Daily AI News Digest - September
  21, 2026.md
content_hash: 4ef2cdf49727bbae942014a8e8650a2bbc8c9cc3a45287296b7792eff8ba50de
normalized_title_hash: 44662eb3356e2980
canonical_url_hash: 841ac0dce9a8883e
tags: []
entities:
- Intel
- OpenAI
themes:
- policy-regulation
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-05-02-chatgpt-enables-ad-tracking-by-default-for-free-users-as-ope
- 2026-06-18-openai-adds-enterprise-usage-analytics-and-spend-controls
- 2026-05-19-openai-adopts-c2pa-conformance-and-google-synthid-watermarki
- 2026-07-31-openai-disrupts-cambodia-based-scam-operation-using-chatgpt
- 2026-07-21-openai-disclosed-that-an-internal-long-horizon-model-repeate
embedding_id: 2026-09-21-researcher-documents-a-chatgpt-cross-site-ad-cookie-linking
event_name: ''
---

# Researcher documents a ChatGPT cross-site ad cookie linking browsing to accounts

A disclosure published September 20 by Buchodi’s Threat Intel traced obi, a cookie OpenAI sets on .openai.com with a one-year lifetime and SameSite=None — the only OpenAI cookie configured to travel cross-site. When a user visits a site carrying OpenAI’s Measurement Pixel, the browser returns the identifier along with page context. The pixel’s “automatic advanced matching” hashes emails, phone numbers and names in-browser but sends country, region, city and postal code unhashed; self-collected events outnumbered advertiser-supplied ones 685 to 255 in the observed traffic. OpenAI’s cookie policy classifies obi as analytics rather than marketing — a classification that materially affects consent handling under EU rules.

<!-- graph:start -->
## Connections

**Entities:** [[Intel]] · [[OpenAI]]
**Topics:** [[Policy & Regulation]] · [[Model Breakthroughs]]
**Related:** [[2026-05-02-chatgpt-enables-ad-tracking-by-default-for-free-users-as-ope]] · [[2026-06-18-openai-adds-enterprise-usage-analytics-and-spend-controls]] · [[2026-05-19-openai-adopts-c2pa-conformance-and-google-synthid-watermarki]] · [[2026-07-31-openai-disrupts-cambodia-based-scam-operation-using-chatgpt]] · [[2026-07-21-openai-disclosed-that-an-internal-long-horizon-model-repeate]]
<!-- graph:end -->
