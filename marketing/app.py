import os
import json
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="thai2drive Marketing Tools")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
CAMPAIGNS_FILE = os.path.join(os.path.dirname(__file__), "campaigns.json")
BASE_URL = os.environ.get("APP_BASE_URL", "https://thai2drive.no")


class UTMRequest(BaseModel):
    platform: str
    campaign_name: str
    content_description: Optional[str] = None
    medium: Optional[str] = None


class ContentRequest(BaseModel):
    topic: str
    platform: str
    language: str   # thai | norwegian | both
    post_type: str  # tip | promotion | quiz


def load_campaigns() -> list:
    if os.path.exists(CAMPAIGNS_FILE):
        with open(CAMPAIGNS_FILE) as f:
            return json.load(f)
    return []


def save_campaigns(campaigns: list) -> None:
    with open(CAMPAIGNS_FILE, "w") as f:
        json.dump(campaigns, f, indent=2, ensure_ascii=False)


def ai_generate(messages: list) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "(OPENAI_API_KEY er ikkje satt — set miljøvariabelen og prøv igjen)"
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model="gpt-4o", messages=messages)
    return resp.choices[0].message.content.strip()


@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(STATIC_DIR, "index.html"), encoding="utf-8") as f:
        return f.read()


@app.post("/api/utm/generate")
async def generate_utm(req: UTMRequest):
    medium_map = {
        "facebook": "social", "instagram": "social", "tiktok": "social",
        "youtube": "video", "email": "email", "sms": "sms",
    }
    medium = req.medium or medium_map.get(req.platform.lower(), "social")
    params = {"utm_source": req.platform.lower(), "utm_medium": medium, "utm_campaign": req.campaign_name}
    if req.content_description:
        params["utm_content"] = req.content_description

    url = f"{BASE_URL}?{urlencode(params)}"
    campaigns = load_campaigns()
    campaign_id = f"{req.platform}_{req.campaign_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    campaigns.append({
        "id": campaign_id, "name": req.campaign_name, "platform": req.platform,
        "url": url, "created_at": datetime.now().isoformat(), "clicks": 0,
    })
    save_campaigns(campaigns)
    return {"url": url, "campaign_id": campaign_id}


@app.post("/api/content/generate")
async def generate_content(req: ContentRequest):
    lang_instruction = {
        "thai": "Write ONLY in Thai language.",
        "norwegian": "Write ONLY in Norwegian (Bokmål).",
        "both": "Write in BOTH Thai and Norwegian. Thai first, then a separator line ---, then Norwegian.",
    }
    platform_notes = {
        "facebook": "Facebook post, 150–200 words, use 3–5 emojis",
        "instagram": "Instagram caption, 80–120 words, 5–8 emojis, 8–10 relevant hashtags at the end",
        "tiktok": "TikTok caption, 50–80 words, very casual and energetic tone, 3–5 hashtags",
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a marketing assistant for thai2drive.no — a driving theory app for Thai people living in Norway. "
                "The app helps Thai speakers pass the Norwegian driving theory test. It has 3 languages: Thai, Norwegian and English. "
                "The creator is a certified Norwegian driving instructor since 2010.\n\n"
                f"{lang_instruction.get(req.language, lang_instruction['both'])}\n"
                f"Format: {platform_notes.get(req.platform.lower(), platform_notes['facebook'])}\n"
                f"Post type: {req.post_type}\n\n"
                "Always end with a call-to-action to visit thai2drive.no or download the app."
            ),
        },
        {"role": "user", "content": f"Create a {req.post_type} post about: {req.topic}"},
    ]
    content = ai_generate(messages)
    return {"content": content}


@app.get("/api/campaigns")
async def get_campaigns():
    return load_campaigns()


@app.get("/track/{campaign_id}")
async def track_click(campaign_id: str):
    campaigns = load_campaigns()
    for c in campaigns:
        if c["id"] == campaign_id:
            c["clicks"] = c.get("clicks", 0) + 1
            save_campaigns(campaigns)
            return RedirectResponse(c["url"])
    return RedirectResponse(BASE_URL)


def start():
    uvicorn.run("marketing.app:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    start()
