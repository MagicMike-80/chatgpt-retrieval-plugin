import json
import logging
import re
from typing import Optional

import anthropic

from .models import Platform, PlatformConfig, PLATFORM_CONFIGS, Scene, VideoScript

logger = logging.getLogger(__name__)

GRADIENT_PALETTES = [
    ("#0f0c29", "#302b63"),
    ("#134e5e", "#71b280"),
    ("#1a1a2e", "#e94560"),
    ("#0d324d", "#7f5a83"),
    ("#1d1d1d", "#dd5e89"),
    ("#141e30", "#243b55"),
    ("#200122", "#6f0000"),
    ("#000428", "#004e92"),
]

SCRIPT_PROMPT = """You are a professional video content creator and scriptwriter.

Create a compelling video script for the following:

Topic: {topic}
Platform: {platform_name} ({platform_desc})
Style preference: {style}
User provided files: {user_files}

The video should be engaging, professional, and optimized for {platform_name}.
Maximum duration: {max_duration} seconds.

Return a JSON object with exactly this structure:
{{
  "title": "Video title (catchy, SEO-friendly)",
  "hook": "First 3 seconds hook sentence to grab attention",
  "scenes": [
    {{
      "index": 0,
      "title": "Scene title",
      "narration": "Exact spoken text for this scene",
      "duration": 5.0,
      "visual_description": "What should be shown visually — describe colors, mood, subject",
      "gradient_colors": ["#hex1", "#hex2"]
    }}
  ],
  "call_to_action": "End CTA — what should viewers do (like, subscribe, visit, etc.)",
  "music_style": "upbeat/emotional/cinematic/corporate/energetic",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "thumbnail_idea": "Description of ideal thumbnail"
}}

Rules:
- Total narration duration must not exceed {max_duration} seconds (average 130 words/min)
- For vertical platforms (TikTok, Reels, Shorts): fast-paced, 3-8 sec per scene, hook in first 2 sec
- For YouTube/Facebook: can be slower, more detailed, 5-15 sec per scene
- Make narration natural and conversational, not stiff
- Each scene gradient_colors should match the visual mood
- Minimum 4 scenes, maximum 12 scenes
- Return ONLY valid JSON, no markdown
"""


class ScriptGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def generate(
        self,
        topic: str,
        platform: Platform,
        style: str = "engaging and modern",
        user_files: list[str] | None = None,
    ) -> VideoScript:
        config = PLATFORM_CONFIGS[platform]
        files_desc = ", ".join(user_files) if user_files else "none"

        prompt = SCRIPT_PROMPT.format(
            topic=topic,
            platform_name=config.name,
            platform_desc=config.description,
            style=style,
            user_files=files_desc,
            max_duration=config.max_duration,
        )

        logger.info(f"Generating script for '{topic}' on {config.name}...")
        message = self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)

        scenes = []
        for i, s in enumerate(data.get("scenes", [])):
            gc = s.get("gradient_colors", GRADIENT_PALETTES[i % len(GRADIENT_PALETTES)])
            if isinstance(gc, list) and len(gc) >= 2:
                gc = (gc[0], gc[1])
            else:
                gc = GRADIENT_PALETTES[i % len(GRADIENT_PALETTES)]
            scenes.append(Scene(
                index=i,
                title=s.get("title", f"Scene {i+1}"),
                narration=s.get("narration", ""),
                duration=float(s.get("duration", 5.0)),
                visual_description=s.get("visual_description", ""),
                gradient_colors=gc,
            ))

        full_narration = " ".join(s.narration for s in scenes)
        if data.get("call_to_action"):
            full_narration += " " + data["call_to_action"]

        total = sum(s.duration for s in scenes)

        return VideoScript(
            title=data.get("title", topic),
            hook=data.get("hook", ""),
            scenes=scenes,
            call_to_action=data.get("call_to_action", ""),
            full_narration=full_narration,
            music_style=data.get("music_style", "upbeat"),
            platform=platform,
            total_duration=total,
            hashtags=data.get("hashtags", []),
            thumbnail_idea=data.get("thumbnail_idea", ""),
        )
