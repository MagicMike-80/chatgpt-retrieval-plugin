import logging
import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .models import PlatformConfig, Scene, VideoScript

logger = logging.getLogger(__name__)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class VideoAssembler:
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.w = config.width
        self.h = config.height

    def assemble(
        self,
        script: VideoScript,
        voice_path: str,
        output_path: str,
        music_path: Optional[str] = None,
        user_assets: dict[int, str] | None = None,
    ) -> str:
        user_assets = user_assets or {}

        with tempfile.TemporaryDirectory() as tmp:
            frame_dir = os.path.join(tmp, "frames")
            os.makedirs(frame_dir)

            scene_clips: list[tuple[str, float]] = []

            for scene in script.scenes:
                asset = user_assets.get(scene.index) or scene.user_asset
                if asset and self._is_video(asset):
                    clip_path = self._trim_video(asset, scene.duration, tmp)
                elif asset and self._is_image(asset):
                    img = self._load_user_image(asset)
                    img = self._add_text_overlay(img, scene)
                    clip_path = self._image_to_clip(img, scene.duration, tmp, scene.index)
                else:
                    img = self._render_scene_frame(scene)
                    clip_path = self._image_to_clip(img, scene.duration, tmp, scene.index)

                scene_clips.append((clip_path, scene.duration))
                logger.debug(f"Scene {scene.index} clip ready: {clip_path}")

            concat_path = os.path.join(tmp, "concat.mp4")
            self._concat_clips(scene_clips, concat_path)

            srt_path = os.path.join(tmp, "subtitles.srt")
            self._write_srt(script.scenes, srt_path)

            self._mix_audio(concat_path, voice_path, srt_path, output_path, music_path)

        logger.info(f"Video assembled: {output_path}")
        return output_path

    def _render_scene_frame(self, scene: Scene) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h))
        draw = ImageDraw.Draw(img)

        c1 = _hex_to_rgb(scene.gradient_colors[0])
        c2 = _hex_to_rgb(scene.gradient_colors[1])
        for y in range(self.h):
            t = y / self.h
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            draw.line([(0, y), (self.w, y)], fill=(r, g, b))

        return self._add_text_overlay(img, scene)

    def _add_text_overlay(self, img: Image.Image, scene: Scene) -> Image.Image:
        img = img.copy().convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        padding = int(self.w * 0.08)
        max_w = self.w - padding * 2

        title_font = self._get_font(size=int(self.h * 0.055))
        body_font = self._get_font(size=int(self.h * 0.028))
        small_font = self._get_font(size=int(self.h * 0.022))

        # Title
        title_lines = self._wrap(scene.title, title_font, max_w)
        title_h = len(title_lines) * int(self.h * 0.065)
        y = int(self.h * 0.3)

        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
            x = (self.w - tw) // 2
            draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 160))
            draw.text((x, y), line, font=title_font, fill=(255, 255, 255, 255))
            y += int(self.h * 0.065)

        # Narration text (partial, first 100 chars)
        short_narr = scene.narration[:120] + ("..." if len(scene.narration) > 120 else "")
        narr_lines = self._wrap(short_narr, body_font, max_w)
        y += int(self.h * 0.03)

        bar_top = y - 10
        bar_h = len(narr_lines) * int(self.h * 0.034) + 20
        draw.rectangle([(padding - 10, bar_top), (self.w - padding + 10, bar_top + bar_h)],
                       fill=(0, 0, 0, 120))

        for line in narr_lines:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            tw = bbox[2] - bbox[0]
            x = (self.w - tw) // 2
            draw.text((x, y), line, font=body_font, fill=(230, 230, 230, 240))
            y += int(self.h * 0.034)

        # Scene number badge
        badge_text = f"{scene.index + 1}"
        bx, by = int(self.w * 0.05), int(self.h * 0.05)
        draw.ellipse([(bx, by), (bx + 44, by + 44)], fill=(255, 255, 255, 40))
        draw.text((bx + 8, by + 6), badge_text, font=small_font, fill=(255, 255, 255, 200))

        result = Image.alpha_composite(img, overlay)
        return result.convert("RGB")

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _wrap(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        words = text.split()
        lines, line = [], []
        tmp_img = Image.new("RGB", (1, 1))
        tmp_draw = ImageDraw.Draw(tmp_img)
        for word in words:
            test = " ".join(line + [word])
            bb = tmp_draw.textbbox((0, 0), test, font=font)
            if bb[2] - bb[0] <= max_width:
                line.append(word)
            else:
                if line:
                    lines.append(" ".join(line))
                line = [word]
        if line:
            lines.append(" ".join(line))
        return lines or [""]

    def _image_to_clip(self, img: Image.Image, duration: float, tmp: str, idx: int) -> str:
        frame_path = os.path.join(tmp, f"frame_{idx:02d}.jpg")
        img.save(frame_path, quality=95)
        clip_path = os.path.join(tmp, f"clip_{idx:02d}.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", frame_path,
            "-t", str(duration),
            "-vf", f"scale={self.w}:{self.h}:force_original_aspect_ratio=decrease,"
                   f"pad={self.w}:{self.h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-r", str(self.config.fps),
            clip_path,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return clip_path

    def _trim_video(self, video_path: str, duration: float, tmp: str) -> str:
        out = os.path.join(tmp, f"trimmed_{Path(video_path).stem}.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-t", str(duration),
            "-vf", f"scale={self.w}:{self.h}:force_original_aspect_ratio=decrease,"
                   f"pad={self.w}:{self.h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-r", str(self.config.fps),
            "-an",
            out,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return out

    def _load_user_image(self, path: str) -> Image.Image:
        img = Image.open(path).convert("RGB")
        ratio = max(self.w / img.width, self.h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - self.w) // 2
        top = (new_h - self.h) // 2
        return img.crop((left, top, left + self.w, top + self.h))

    def _concat_clips(self, clips: list[tuple[str, float]], output: str) -> None:
        list_file = output + ".txt"
        with open(list_file, "w") as f:
            for clip_path, _ in clips:
                f.write(f"file '{clip_path}'\n")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output,
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    def _write_srt(self, scenes: list[Scene], path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            t = 0.0
            for i, scene in enumerate(scenes, 1):
                start = self._ts(t)
                end = self._ts(t + scene.duration)
                f.write(f"{i}\n{start} --> {end}\n{scene.narration}\n\n")
                t += scene.duration

    def _ts(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    def _mix_audio(
        self,
        video: str,
        voice: str,
        srt: str,
        output: str,
        music: Optional[str],
    ) -> None:
        inputs = ["-i", video, "-i", voice]
        filter_parts = []
        audio_map = "[1:a]"

        if music and os.path.exists(music):
            inputs += ["-i", music]
            filter_parts.append(
                "[2:a]volume=0.12,aloop=loop=-1:size=2e+09[bg];"
                f"[1:a][bg]amix=inputs=2:duration=first:dropout_transition=3[aout]"
            )
            audio_map = "[aout]"

        vf = (
            f"subtitles={srt}:force_style="
            "'FontName=DejaVu Sans,FontSize=18,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
            "BackColour=&H80000000,BorderStyle=4,Outline=1,Shadow=0,"
            f"MarginV=30,Alignment=2'"
        )

        cmd = ["ffmpeg", "-y"] + inputs
        if filter_parts:
            cmd += ["-filter_complex", "".join(filter_parts), "-map", "0:v", "-map", audio_map]
        else:
            cmd += ["-map", "0:v", "-map", "1:a"]

        cmd += [
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output,
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Subtitle burn failed ({e.stderr.decode()[-300:]}), trying without subs")
            cmd_nosub = ["ffmpeg", "-y"] + inputs + [
                "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p", "-shortest",
                output,
            ]
            subprocess.run(cmd_nosub, capture_output=True, check=True)

    def _is_video(self, path: str) -> bool:
        return Path(path).suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm"}

    def _is_image(self, path: str) -> bool:
        return Path(path).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
