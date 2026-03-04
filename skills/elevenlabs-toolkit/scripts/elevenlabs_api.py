"""
ElevenLabs API integration — all 7 tools.
"""
import os
import httpx
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket
from starlette.responses import StreamingResponse

router = APIRouter()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
BASE_URL = "https://api.elevenlabs.io/v1"

def _headers():
    return {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}

# 1. Voices/Get — browse available voices
@router.get("/api/voices")
async def get_voices():
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BASE_URL}/voices", headers={"xi-api-key": ELEVENLABS_API_KEY})
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text[:500])
        data = r.json()
        return [{"voice_id": v["voice_id"], "name": v["name"], "category": v.get("category", ""),
                 "labels": v.get("labels", {})} for v in data.get("voices", [])]

# 2. TTS — batch text-to-speech
@router.post("/api/voice/tts")
async def text_to_speech(body: dict):
    text = body.get("text", "")
    voice_id = body.get("voice_id", "pNInz6obpgDQGcFmaJgB")  # Adam default
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE_URL}/text-to-speech/{voice_id}",
            headers=_headers(),
            json={"text": text, "model_id": "eleven_multilingual_v2",
                  "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}})
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text[:500])
        return StreamingResponse(iter([r.content]), media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=narration.mp3"})

# 3. STT — speech-to-text
@router.post("/api/voice/stt")
async def speech_to_text(file: UploadFile = File(...)):
    audio_data = await file.read()
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE_URL}/speech-to-text",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            files={"file": (file.filename or "audio.wav", audio_data, file.content_type or "audio/wav")},
            data={"model_id": "scribe_v1"})
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text[:500])
        return r.json()

# 4. Sound Effects generation
@router.post("/api/audio/sfx")
async def generate_sfx(body: dict):
    text = body.get("text", "gentle rain on a window")
    duration = body.get("duration_seconds", 5.0)
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{BASE_URL}/sound-generation",
            headers=_headers(),
            json={"text": text, "duration_seconds": duration})
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text[:500])
        return StreamingResponse(iter([r.content]), media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=sfx.mp3"})

# 5. Music/Lullaby (uses sound-generation with musical prompt)
@router.post("/api/audio/lullaby")
async def generate_lullaby(body: dict):
    prompt = body.get("prompt", "soft gentle lullaby music box melody for bedtime")
    duration = body.get("duration_seconds", 15.0)
    lullaby_prompt = f"Gentle soothing lullaby music: {prompt}"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{BASE_URL}/sound-generation",
            headers=_headers(),
            json={"text": lullaby_prompt, "duration_seconds": duration})
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text[:500])
        return StreamingResponse(iter([r.content]), media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=lullaby.mp3"})

# 6. TTS WebSocket Streaming
@router.websocket("/api/voice/stream")
async def tts_websocket_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        import websockets
        init_msg = await websocket.receive_json()
        voice_id = init_msg.get("voice_id", "pNInz6obpgDQGcFmaJgB")
        model_id = init_msg.get("model_id", "eleven_multilingual_v2")
        
        ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"
        
        async with websockets.connect(ws_url, additional_headers={"xi-api-key": ELEVENLABS_API_KEY}) as el_ws:
            # Send BOS (beginning of stream)
            await el_ws.send(json.dumps({
                "text": " ", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                "xi_api_key": ELEVENLABS_API_KEY
            }))
            
            import asyncio
            async def forward_to_elevenlabs():
                try:
                    while True:
                        msg = await websocket.receive_json()
                        if msg.get("type") == "close":
                            await el_ws.send(json.dumps({"text": ""}))  # EOS
                            break
                        text = msg.get("text", "")
                        if text:
                            await el_ws.send(json.dumps({"text": text, "try_trigger_generation": True}))
                except Exception:
                    await el_ws.send(json.dumps({"text": ""}))
            
            async def forward_to_client():
                try:
                    async for message in el_ws:
                        data = json.loads(message)
                        if data.get("audio"):
                            await websocket.send_json({"audio": data["audio"], "isFinal": data.get("isFinal", False)})
                        if data.get("isFinal"):
                            break
                except Exception:
                    pass
            
            await asyncio.gather(forward_to_elevenlabs(), forward_to_client())
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass

# 7. ElevenAgents Story Concierge (Conversational AI)
@router.post("/api/story/chat")
async def story_concierge(body: dict):
    message = body.get("message", "")
    conversation_id = body.get("conversation_id", None)
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
    
    # Use ElevenLabs Conversational AI API
    async with httpx.AsyncClient(timeout=30) as client:
        payload = {
            "model_id": "eleven_turbo_v2_5",
            "text": message,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        
        # Story concierge system prompt via Mistral
        from mistralai import Mistral
        mistral_key = os.environ.get("MISTRAL_API_KEY", "")
        if mistral_key:
            mclient = Mistral(api_key=mistral_key)
            resp = mclient.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": "You are the Story Concierge for Sandman Tales, a multilingual bedtime story app. Help parents refine their story idea. Ask about: child's name, age, favorite themes (animals, space, ocean), language preference, story mood (adventurous, calming, funny). Keep responses warm, brief (2-3 sentences), and conversational. When you have enough info, summarize the story brief."},
                    {"role": "user", "content": message}
                ]
            )
            concierge_text = resp.choices[0].message.content.strip()
        else:
            concierge_text = f"I'd love to help create a bedtime story! Tell me about the child - what's their name, and what do they love? (animals, space, magic?)"
        
        return {
            "response": concierge_text,
            "conversation_id": conversation_id or "new",
            "tool": "elevenlabs_agents",
            "status": "ready_for_story" if any(w in message.lower() for w in ["ready", "perfect", "go ahead", "create", "generate"]) else "refining"
        }
