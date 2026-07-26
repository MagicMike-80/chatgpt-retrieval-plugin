#!/usr/bin/env python3
"""Voice-First generator for the Thai Folklore series.

AGENTS.md section 3: "Lyd Foerst-Prinsippet" — audio is produced before image.
This script turns the VO lines in `episodes.py` into ElevenLabs MP3s plus a
MANIFEST.json that SyncFrame consumes to cut the images to the voice.

Usage:
    export ELEVENLABS_API_KEY="..."
    python voice_generator.py --dry-run          # plan only, no API calls, no cost
    python voice_generator.py                    # all 10 episodes
    python voice_generator.py --episode 1        # one episode
    python voice_generator.py --episode 1 --episode 4 --out ./voices

Output:
    episode_voices/
        EP01_S1_L1_Narrator_TH.mp3
        EP01_S1_L2_Narrator_EN.mp3
        ...
        MANIFEST.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from episodes import EPISODES, VOICES, get_episode
except ImportError:  # invoked from the repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from episodes import EPISODES, VOICES, get_episode

API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
MODEL_ID = "eleven_v3"  # AGENTS.md section 2: ElevenLabs V3
PLACEHOLDER = "REPLACE_WITH_VOICE_ID"

# Thai reads better slightly slower and less stable than English; a little
# instability is what keeps a ghost from sounding like a newsreader.
VOICE_SETTINGS = {
    "th": {"stability": 0.45, "similarity_boost": 0.80, "style": 0.35},
    "en": {"stability": 0.55, "similarity_boost": 0.80, "style": 0.25},
}


def slugify(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def plan(episodes):
    """Build the full list of files to generate. No side effects."""
    items = []
    for ep in episodes:
        for scene in ep["scenes"]:
            for idx, line in enumerate(scene["vo"], start=1):
                speaker = line["speaker"]
                filename = "EP{:02d}_S{}_L{}_{}.mp3".format(
                    ep["episode"], scene["scene"], idx, slugify(speaker)
                )
                items.append({
                    "episode": ep["episode"],
                    "episode_title": ep["title"],
                    "scene": scene["scene"],
                    "scene_title": scene["title"],
                    "scene_start": scene["start"],
                    "scene_end": scene["end"],
                    "line": idx,
                    "speaker": speaker,
                    "lang": line["lang"],
                    "text": line["text"],
                    "voice_id": VOICES.get(speaker),
                    "filename": filename,
                })
    return items


def check_voices(items):
    """Fail before spending credits, not after."""
    missing = sorted({i["speaker"] for i in items if not i["voice_id"]})
    placeholder = sorted({i["speaker"] for i in items if i["voice_id"] == PLACEHOLDER})
    problems = []
    if missing:
        problems.append("No entry in VOICES for: " + ", ".join(missing))
    if placeholder:
        problems.append(
            "Still set to {}: {}".format(PLACEHOLDER, ", ".join(placeholder))
        )
    return problems


def synthesize(item, api_key, out_dir):
    import requests  # imported lazily so --dry-run works without it

    resp = requests.post(
        API_URL.format(voice_id=item["voice_id"]),
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text": item["text"],
            "model_id": MODEL_ID,
            "voice_settings": VOICE_SETTINGS.get(item["lang"], VOICE_SETTINGS["en"]),
        },
        timeout=120,
    )
    resp.raise_for_status()
    path = out_dir / item["filename"]
    path.write_bytes(resp.content)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--episode", type=int, action="append",
                    help="episode number, repeatable (default: all)")
    ap.add_argument("--out", default="episode_voices", help="output directory")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and write MANIFEST.json, no API calls")
    args = ap.parse_args()

    episodes = [get_episode(n) for n in args.episode] if args.episode else EPISODES
    items = plan(episodes)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Episodes: {}   VO lines: {}".format(
        ", ".join(str(e["episode"]) for e in episodes), len(items)))
    total_chars = sum(len(i["text"]) for i in items)
    print("Characters to synthesize: {} (ElevenLabs bills on this)\n".format(total_chars))

    for i in items:
        print("  EP{:02d} S{}  {:<14} {:<3} {}".format(
            i["episode"], i["scene"], i["speaker"], i["lang"], i["filename"]))

    manifest_path = out_dir / "MANIFEST.json"

    if args.dry_run:
        manifest_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nDry run. Nothing was generated. Plan written to {}".format(manifest_path))
        return 0

    problems = check_voices(items)
    if problems:
        print("\nRefusing to run — fix VOICES in episodes.py first:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return 1

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("\nELEVENLABS_API_KEY is not set.", file=sys.stderr)
        return 1

    print()
    generated = []
    for n, item in enumerate(items, start=1):
        try:
            path = synthesize(item, api_key, out_dir)
        except Exception as exc:  # keep going; one bad line shouldn't kill the batch
            print("  [{}/{}] FAILED {}: {}".format(n, len(items), item["filename"], exc),
                  file=sys.stderr)
            item["error"] = str(exc)
        else:
            print("  [{}/{}] {}".format(n, len(items), path))
        generated.append(item)

    manifest_path.write_text(
        json.dumps(generated, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [i for i in generated if "error" in i]
    print("\nDone. {} files in {}/".format(len(generated) - len(failed), out_dir))
    if failed:
        print("{} failed — rerun to retry them.".format(len(failed)), file=sys.stderr)
    print("Manifest for SyncFrame: {}".format(manifest_path))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
