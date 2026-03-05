# Voice AI Platform Comparison: Vapi vs Bland.ai vs Retell

## Overview

| | Vapi | Bland.ai | Retell |
|---|---|---|---|
| **Founded** | 2023 | 2023 | 2023 |
| **Focus** | Developer platform | Outbound automation | Enterprise voice |
| **API Style** | REST + WebSocket | REST | REST + WebSocket |
| **Open Source** | Partially | No | No |

## Pricing (as of 2026)

| | Vapi | Bland.ai | Retell |
|---|---|---|---|
| **Per-minute cost** | $0.05/min base + provider | $0.09/min all-inclusive | $0.07-0.15/min |
| **LLM cost** | Pass-through (your keys) | Included | Pass-through |
| **STT cost** | Pass-through | Included | Included |
| **TTS cost** | Pass-through | Included | Pass-through |
| **Phone cost** | ~$2/mo per number | ~$2/mo per number | ~$2-6/mo per number |
| **Free tier** | $10 credit | Limited testing | $10 credit |

### Cost Analysis
- **Cheapest for low volume:** Vapi (you control provider costs)
- **Cheapest for high volume:** Bland.ai (flat rate, predictable)
- **Most expensive but premium:** Retell (enterprise features justify cost)

## Features

| Feature | Vapi | Bland.ai | Retell |
|---|---|---|---|
| **Latency** | 600-1000ms | 400-700ms | 400-600ms |
| **Custom LLM** | ✅ Any OpenAI-compatible | ✅ Limited options | ✅ Via API |
| **BYO Keys** | ✅ Full control | ❌ | ✅ |
| **Function Calling** | ✅ Native | ✅ Via pathways | ✅ |
| **Knowledge Base** | ✅ Built-in RAG | ✅ | ✅ |
| **Call Transfer** | ✅ Warm/cold | ✅ | ✅ |
| **DTMF (keypad)** | ✅ | ✅ | ✅ |
| **Voicemail Detection** | ✅ | ✅ | ✅ |
| **Batch Calling** | Via API loop | ✅ Native campaigns | Via API |
| **Webhooks** | ✅ Rich events | ✅ | ✅ |
| **WebSocket Streaming** | ✅ | ❌ | ✅ |
| **Multi-language** | 100+ via providers | 30+ | 30+ |
| **Custom Voices** | ✅ ElevenLabs clones | ✅ Limited | ✅ |
| **Analytics** | ✅ Dashboard | ✅ Dashboard | ✅ Dashboard |
| **SOC 2** | In progress | No | Yes |
| **HIPAA** | BAA available | No | BAA available |

## Voice Provider Support

| Provider | Vapi | Bland.ai | Retell |
|---|---|---|---|
| ElevenLabs | ✅ | ❌ (own voices) | ✅ |
| PlayHT | ✅ | ❌ | ✅ |
| Deepgram TTS | ✅ | ❌ | ✅ |
| Azure TTS | ✅ | ❌ | ❌ |
| OpenAI TTS | ✅ | ❌ | ✅ |
| Custom/Cloned | ✅ | ✅ | ✅ |

## Best Use Cases

### Choose Vapi When:
- You want **maximum control** over the stack
- Building **complex conversational flows** with function calling
- Need **custom LLM integration** (fine-tuned models, local LLMs)
- Developer-first team comfortable with APIs
- Need **web-based voice** (browser SDK) + phone
- Want to use your own API keys to control costs

### Choose Bland.ai When:
- Running **high-volume outbound campaigns** (1000+ calls/day)
- Need **simple setup** — don't want to manage multiple providers
- **Predictable pricing** is important (flat per-minute)
- Building **appointment setting** or **lead qualification** flows
- Less technical team, want a more managed solution
- Pathways visual builder for call flows

### Choose Retell When:
- **Enterprise requirements** (SOC 2, HIPAA, SLAs)
- Need the **lowest latency** possible
- Building **customer support** or **IVR replacement**
- Need **on-prem deployment** option
- Want the most natural-sounding conversations
- High reliability and uptime requirements

## Integration Comparison

### CRM Integration
- **Vapi:** Webhook → your server → CRM API (most flexible)
- **Bland.ai:** Native Zapier, webhook support
- **Retell:** Webhook → your server → CRM API

### Calendar Booking
- **Vapi:** Function calling → calendar API (real-time)
- **Bland.ai:** Pathway nodes → Cal.com, Calendly
- **Retell:** Function calling → calendar API

### Knowledge Base
- **Vapi:** Upload docs, auto-RAG during calls
- **Bland.ai:** Upload docs or connect URLs
- **Retell:** Upload docs, knowledge base API

## Migration Considerations

Moving between platforms is relatively easy since all use similar concepts:
1. **Prompts** transfer directly (minor adjustments for voice style)
2. **Phone numbers** can usually be ported
3. **Webhooks** need endpoint updates
4. **Function calling** schemas are similar but not identical

## Recommendation

**For most OpenClaw users:** Start with **Vapi**. It offers the best developer experience, most flexibility, and the ability to use any LLM. The community is the largest, and docs are excellent.

Scale to Bland.ai if you need high-volume outbound campaigns with simple flows.
Consider Retell for enterprise deployments where compliance and latency are critical.
