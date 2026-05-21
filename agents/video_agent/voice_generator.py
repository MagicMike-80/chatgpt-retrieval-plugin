import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

VOICES = {
    "alloy": "Neutral, balanced",
    "echo": "Male, warm",
    "fable": "British, expressive",
    "onyx": "Deep, authoritative",
    "nova": "Female, friendly",
    "shimmer": "Female, soft",
}


class VoiceGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")

    def generate(
        self,
        text: str,
        output_path: str,
        voice: str = "nova",
        speed: float = 1.0,
    ) -> str:
        if not self._api_key:
            logger.warning("No OpenAI API key — generating silent audio placeholder")
            return self._silent_audio(output_path, len(text) / 13)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self._api_key)
            logger.info(f"Generating voice-over ({voice}, speed={speed})...")
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed,
            )
            response.stream_to_file(output_path)
            logger.info(f"Voice saved to {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"TTS failed ({e}) — using silent placeholder")
            return self._silent_audio(output_path, len(text) / 13)

    def _silent_audio(self, output_path: str, duration: float) -> str:
        import subprocess
        duration = max(1.0, duration)
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
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
    ) -> list[str]:
        paths = []
        for scene in scenes:
            path = os.path.join(output_dir, f"voice_scene_{scene.index:02d}.mp3")
            self.generate(scene.narration, path, voice=voice)
            paths.append(path)
        return paths
