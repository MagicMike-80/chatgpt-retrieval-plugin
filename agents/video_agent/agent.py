import logging
import os
import uuid
from pathlib import Path
from typing import Callable, Optional

from .models import Platform, PLATFORM_CONFIGS, VideoJob, VideoScript
from .script_generator import ScriptGenerator
from .video_assembler import VideoAssembler
from .voice_generator import VoiceGenerator

logger = logging.getLogger(__name__)


class VideoAgent:
    """
    AI Video Agent — generates professional videos from a topic + optional assets.

    Pipeline:
        1. Generate script (Claude)
        2. Generate voice-over (OpenAI TTS)
        3. Assemble video (FFmpeg + PIL)
        4. Export platform-ready MP4
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        output_base: str = "output/videos",
    ):
        self.anthropic_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.openai_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.output_base = output_base
        self.script_gen = ScriptGenerator(api_key=self.anthropic_key)
        self.voice_gen = VoiceGenerator(api_key=self.openai_key)

    def create_video(
        self,
        topic: str,
        platform: Platform = Platform.YOUTUBE,
        style: str = "engaging and modern",
        user_assets: list[str] | None = None,
        voice: str = "nova",
        lang: str = "no",
        music_path: Optional[str] = None,
        progress_cb: Optional[Callable[[int, str], None]] = None,
    ) -> VideoJob:
        job_id = str(uuid.uuid4())[:8]
        job = VideoJob(
            job_id=job_id,
            status="running",
            progress=0,
            step="Starting...",
            topic=topic,
            platform=platform,
        )

        def _progress(pct: int, msg: str):
            job.progress = pct
            job.step = msg
            logger.info(f"[{pct}%] {msg}")
            if progress_cb:
                progress_cb(pct, msg)

        try:
            output_dir = os.path.join(self.output_base, job_id)
            os.makedirs(output_dir, exist_ok=True)

            _progress(5, "Generating script with AI...")
            script = self.script_gen.generate(topic, platform, style, user_assets)
            job.script = script
            logger.info(f"Script: '{script.title}' — {len(script.scenes)} scenes, {script.total_duration:.0f}s")

            _progress(30, "Generating voice-over...")
            voice_path = os.path.join(output_dir, "voice.mp3")
            self.voice_gen.generate(script.full_narration, voice_path, voice=voice, lang=lang)

            _progress(55, "Assembling video frames...")
            config = PLATFORM_CONFIGS[platform]
            assembler = VideoAssembler(config)

            asset_map: dict[int, str] = {}
            if user_assets:
                for i, asset_path in enumerate(user_assets):
                    if os.path.exists(asset_path):
                        scene_idx = i % len(script.scenes)
                        asset_map[scene_idx] = asset_path

            output_path = os.path.join(output_dir, f"{self._safe_name(script.title)}.mp4")

            _progress(65, "Rendering scenes...")
            assembler.assemble(
                script=script,
                voice_path=voice_path,
                output_path=output_path,
                music_path=music_path,
                user_assets=asset_map,
            )

            _progress(100, "Done!")
            job.status = "done"
            job.result_path = output_path

        except Exception as e:
            logger.error(f"Video creation failed: {e}", exc_info=True)
            job.status = "error"
            job.error = str(e)

        return job

    def _safe_name(self, title: str) -> str:
        safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        return safe[:60].strip().replace(" ", "_")
