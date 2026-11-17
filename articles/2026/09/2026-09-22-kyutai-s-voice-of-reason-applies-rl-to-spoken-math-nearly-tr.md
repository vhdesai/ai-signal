---
article_id: 2026-09-22-kyutai-s-voice-of-reason-applies-rl-to-spoken-math-nearly-tr
title: Kyutai's Voice of Reason applies RL to spoken math, nearly tripling speech-native
  accuracy
date: '2026-09-22'
source: MarkTechPost / Kyutai
url_original: https://www.marktechpost.com/2026/09/22/kyutai-releases-voice-of-reason-a-speech-native-model-that-solves-spoken-math-with-reinforcement-learning/
url_canonical: https://www.marktechpost.com/2026/09/22/kyutai-releases-voice-of-reason-a-speech-native-model-that-solves-spoken-math-with-reinforcement-learning/
url_status: ok
digest_source: digests\raw\2026-09-23_060328_Inbox_Daily AI News Digest - September
  23, 2026.md
content_hash: 0c929adeab351e6574e975d4f2b79a20f04dbd8fbea1e0ae8d1e89a46dee34e3
normalized_title_hash: 174cd47e4841730e
canonical_url_hash: dcc32713a8001b14
tags:
- New
entities: []
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-05-03-mit-researchers-explain-why-llm-scaling-laws-work-the-superp
- 2026-08-03-openai-s-gpt-live-update-combines-full-duplex-voice-interact
- 2026-07-07-llm-as-a-verifier-scaling-verification-as-a-new-axis-for-lar
embedding_id: 2026-09-22-kyutai-s-voice-of-reason-applies-rl-to-spoken-math-nearly-tr
event_name: ''
---

# Kyutai's Voice of Reason applies RL to spoken math, nearly tripling speech-native accuracy

Kyutai released two open-weight 9B speech-to-speech checkpoints built on GLM-4-Voice, trained with supervised fine-tuning on 150,616 Orca-Math problems plus group-relative REINFORCE on 16 H100s. Spoken GSM8K accuracy rises from 27.3% for the base model to 77.1%, beating the prior STITCH result of 58.7%. The team claims this is the first application of reinforcement learning to math reasoning in speech-native models. Two implementation details proved load-bearing — temperature correction and audio-token merging — with accuracy collapsing to 12.3% when the former was removed.

<!-- graph:start -->
## Connections

**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-05-03-mit-researchers-explain-why-llm-scaling-laws-work-the-superp]] · [[2026-08-03-openai-s-gpt-live-update-combines-full-duplex-voice-interact]] · [[2026-07-07-llm-as-a-verifier-scaling-verification-as-a-new-axis-for-lar]]
<!-- graph:end -->
