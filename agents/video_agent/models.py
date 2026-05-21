from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Platform(str, Enum):
    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


@dataclass
class PlatformConfig:
    name: str
    width: int
    height: int
    max_duration: int   # seconds
    fps: int
    description: str


PLATFORM_CONFIGS: dict[Platform, PlatformConfig] = {
    Platform.YOUTUBE: PlatformConfig(
        "YouTube", 1920, 1080, 900, 30,
        "Landscape 16:9, up to 15 min"
    ),
    Platform.YOUTUBE_SHORTS: PlatformConfig(
        "YouTube Shorts", 1080, 1920, 60, 30,
        "Vertical 9:16, up to 60 sec"
    ),
    Platform.TIKTOK: PlatformConfig(
        "TikTok", 1080, 1920, 180, 30,
        "Vertical 9:16, up to 3 min"
    ),
    Platform.INSTAGRAM: PlatformConfig(
        "Instagram Reels", 1080, 1920, 90, 30,
        "Vertical 9:16, up to 90 sec"
    ),
    Platform.FACEBOOK: PlatformConfig(
        "Facebook", 1280, 720, 600, 30,
        "Landscape 16:9, up to 10 min"
    ),
}


@dataclass
class Scene:
    index: int
    title: str
    narration: str
    duration: float         # seconds
    visual_description: str
    user_asset: Optional[str] = None  # path to user-provided image/video
    gradient_colors: tuple[str, str] = ("#1a1a2e", "#16213e")


@dataclass
class VideoScript:
    title: str
    hook: str
    scenes: list[Scene]
    call_to_action: str
    full_narration: str
    music_style: str
    platform: Platform
    total_duration: float
    hashtags: list[str] = field(default_factory=list)
    thumbnail_idea: str = ""


@dataclass
class VideoJob:
    job_id: str
    status: str          # pending | running | done | error
    progress: int        # 0–100
    step: str
    topic: str
    platform: Platform
    result_path: Optional[str] = None
    error: Optional[str] = None
    script: Optional[VideoScript] = None
