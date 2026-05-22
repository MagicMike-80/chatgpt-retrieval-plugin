import logging
import os
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

GTTS_LANGS = {
    "no": "Norsk",
    "en": "English",
    "sv": "Svenska",
    "da": "Dansk",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
}

# OpenAI voices kept as option if key is available
OPENAI_VOICES = {
    "nova": "Kvinne, vennlig",
    "shimmer": "Kvinne, myk",
    "alloy": "Nøytral",
    "echo": "Mann, varm",
    "onyx": "Dypt, autoritativt",
    "fable": "Britisk",
}


class VoiceGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self._openai_key = api_key or os.environ.get("OPENAI_API_KEY")

    def generate(
        self,
        text: str,
        output_path: str,
        voice: str = "nova",
        lang: str = "no",
        speed: float = 1.0,
    ) -> str:
        # Prefer OpenAI TTS if key exists (higher quality)
        if self._openai_key:
            result = self._openai_tts(text, output_path, voice, speed)
            if result:
                return result

        # Free fallback: Google TTS (no key needed)
        result = self._gtts(text, output_path, lang)
        if result:
            return result

        # Last resort: silent audio
        logger.warning("All TTS methods failed — using silent audio")
        return self._silent_audio(output_path, len(text) / 13)

    def _openai_tts(self, text: str, output_path: str, voice: str, speed: float) -> Optional[str]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self._openai_key)
            logger.info(f"OpenAI TTS: voice={voice}")
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed,
            )
            response.stream_to_file(output_path)
            return output_path
        except Exception as e:
            logger.warning(f"OpenAI TTS failed: {e}")
            return None

    def _gtts(self, text: str, output_path: str, lang: str = "no") -> Optional[str]:
        try:
            from gtts import gTTS
            logger.info(f"Google TTS (gratis): lang={lang}")
            # gTTS outputs mp3 directly
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            logger.info(f"Voice saved: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"gTTS failed: {e}")
            return None

    def _silent_audio(self, output_path: str, duration: float) -> str:
        duration = max(1.0, duration)
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", str(duration),
            "-q:a", "9", "-acodec", "libmp3lame",
            output_path,
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except Exception:
            open(output_path, "wb").close()
        return output_path

    def generate_per_scene(
        self,
        scenes: list,
        output_dir: str,
        voice: str = "nova",
        lang: str = "no",
    ) -> list[str]:
        paths = []
        for scene in scenes:
            path = os.path.join(output_dir, f"voice_scene_{scene.index:02d}.mp3")
            self.generate(scene.narration, path, voice=voice, lang=lang)
            paths.append(path)
        return paths
