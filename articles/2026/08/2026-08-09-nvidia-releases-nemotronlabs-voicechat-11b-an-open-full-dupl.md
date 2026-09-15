---
article_id: 2026-08-09-nvidia-releases-nemotronlabs-voicechat-11b-an-open-full-dupl
title: NVIDIA releases NemotronLabs VoiceChat 11B, an open full-duplex speech model
  with tool calling
date: '2026-08-09'
source: '[MarkTechPost]'
url_original: https://www.marktechpost.com/2026/08/09/nvidia-releases-nemotronlabs-voicechat-11b-an-open-full-duplex-speech-to-speech-model-with-450-ms-turn-taking-and-live-tool-calling/
url_canonical: https://www.marktechpost.com/2026/08/09/nvidia-releases-nemotronlabs-voicechat-11b-an-open-full-duplex-speech-to-speech-model-with-450-ms-turn-taking-and-live-tool-calling/
url_status: ok
digest_source: digests\raw\2026-08-10_062245_Inbox_Daily AI News Digest - August 10,
  2026.md
content_hash: 125fe3aff65b22fae42fb0f879c1ca54a488c1c50f768e51819de7a6f467f42a
normalized_title_hash: 2d23b99da85560ec
canonical_url_hash: 2c3323f389b9aa31
tags:
- Launch
entities:
- NVIDIA
themes:
- model-capabilities
cross_cutting_topics: []
dedupe_status: canonical
canonical_article_id: null
related_article_ids:
- 2026-08-09-nvidia-releases-nemotronlabs-voicechat-11b-open-full-duplex
- 2026-08-09-race-to-full-duplex-nvidia-and-bytedance-ship-competing-real
- 2026-07-07-nvidia-releases-audex-a-unified-audio-text-llm-30b-moe
- 2026-07-01-nvidia-releases-nemotron-labs-twotower-an-open-weight-diffus
- 2026-07-02-nvidia-releases-nemotron-labs-twotower-a-diffusion-llm-2-42
embedding_id: 2026-08-09-nvidia-releases-nemotronlabs-voicechat-11b-an-open-full-dupl
event_name: ''
---

# NVIDIA releases NemotronLabs VoiceChat 11B, an open full-duplex speech model with tool calling

NVIDIA published an 11B end-to-end speech-to-speech model that replaces the conventional ASR → LLM → TTS chain with a single hybrid Mamba/Transformer network, measuring 448 ms smooth turn-taking latency on Full-Duplex-Bench 1.0 and a 1.00 take-over rate on user interruption at 480 ms. It is the first open full-duplex model to support tool calling mid-conversation, using a side channel plus operator-defined "on-hold" lines so the agent does not fall silent while an API runs. The weights are permissively licensed (OpenMDW-1.1), but NVIDIA labels the checkpoint research-only and documents real failure modes including a two-minute audio context ceiling and degradation after several turns. Deployment requires a single 80 GB GPU with no hosted API available, which limits near-term contact-center and IVR pilots to teams with their own compute. Products & Tools PRODUCT

<!-- graph:start -->
## Connections

**Entities:** [[NVIDIA]]
**Topics:** [[Model Breakthroughs]]
**Related:** [[2026-08-09-nvidia-releases-nemotronlabs-voicechat-11b-open-full-duplex]] · [[2026-08-09-race-to-full-duplex-nvidia-and-bytedance-ship-competing-real]] · [[2026-07-07-nvidia-releases-audex-a-unified-audio-text-llm-30b-moe]] · [[2026-07-01-nvidia-releases-nemotron-labs-twotower-an-open-weight-diffus]] · [[2026-07-02-nvidia-releases-nemotron-labs-twotower-a-diffusion-llm-2-42]]
<!-- graph:end -->
