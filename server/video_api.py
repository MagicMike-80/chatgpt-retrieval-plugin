"""
Video Agent API Server
Run: uvicorn server.video_api:app --host 0.0.0.0 --port 8080 --reload
"""

import asyncio
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from agents.video_agent.agent import VideoAgent
from agents.video_agent.models import Platform, PLATFORM_CONFIGS

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Video Studio", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory job store (use Redis for production)
JOBS: dict[str, dict] = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path("static/video_studio/index.html")
    if html_path.exists():
        return html_path.read_text()
    return HTMLResponse("<h1>AI Video Studio</h1><p>Static files not found.</p>")


@app.post("/api/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())[:8]
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    saved = []
    for file in files:
        safe_name = Path(file.filename).name
        dest = os.path.join(session_dir, safe_name)
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved.append({"name": safe_name, "path": dest, "size": os.path.getsize(dest)})

    return {"session_id": session_id, "files": saved}


@app.post("/api/jobs")
async def create_job(
    topic: str = Form(...),
    platform: str = Form("youtube"),
    style: str = Form("engaging and modern"),
    voice: str = Form("nova"),
    upload_session: Optional[str] = Form(None),
):
    try:
        plat = Platform(platform)
    except ValueError:
        raise HTTPException(400, f"Unknown platform: {platform}")

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "step": "Queued",
        "topic": topic,
        "platform": platform,
        "result_path": None,
        "error": None,
        "script": None,
    }

    user_assets = []
    if upload_session:
        session_dir = os.path.join(UPLOAD_DIR, upload_session)
        if os.path.isdir(session_dir):
            user_assets = [
                str(p) for p in Path(session_dir).iterdir()
                if p.is_file()
            ]

    asyncio.create_task(_run_job(job_id, topic, plat, style, voice, user_assets))
    return {"job_id": job_id, "status": "pending"}


async def _run_job(
    job_id: str,
    topic: str,
    platform: Platform,
    style: str,
    voice: str,
    user_assets: list[str],
):
    def update(pct: int, msg: str):
        JOBS[job_id]["progress"] = pct
        JOBS[job_id]["step"] = msg
        JOBS[job_id]["status"] = "running"

    JOBS[job_id]["status"] = "running"
    try:
        agent = VideoAgent(output_base=OUTPUT_DIR)
        result = await asyncio.to_thread(
            agent.create_video,
            topic=topic,
            platform=platform,
            style=style,
            user_assets=user_assets or None,
            voice=voice,
            progress_cb=update,
        )

        JOBS[job_id]["status"] = result.status
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["step"] = result.step if result.status == "done" else result.error
        JOBS[job_id]["result_path"] = result.result_path

        if result.script:
            JOBS[job_id]["script"] = {
                "title": result.script.title,
                "hook": result.script.hook,
                "total_duration": result.script.total_duration,
                "hashtags": result.script.hashtags,
                "thumbnail_idea": result.script.thumbnail_idea,
                "music_style": result.script.music_style,
                "scenes": [
                    {"index": s.index, "title": s.title, "duration": s.duration}
                    for s in result.script.scenes
                ],
            }
    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(404, "Job not found")
    return JOBS[job_id]


@app.get("/api/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    """SSE endpoint for real-time progress updates."""
    async def event_gen():
        while True:
            if job_id not in JOBS:
                yield f"data: {json.dumps({'error': 'not found'})}\n\n"
                break
            job = JOBS[job_id]
            yield f"data: {json.dumps(job)}\n\n"
            if job["status"] in ("done", "error"):
                break
            await asyncio.sleep(1.5)

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.get("/api/jobs/{job_id}/download")
async def download_video(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(404, "Job not found")
    job = JOBS[job_id]
    if job["status"] != "done" or not job["result_path"]:
        raise HTTPException(400, "Video not ready")
    path = job["result_path"]
    if not os.path.exists(path):
        raise HTTPException(404, "File not found on disk")
    filename = Path(path).name
    return FileResponse(path, media_type="video/mp4", filename=filename)


@app.get("/api/platforms")
async def list_platforms():
    return [
        {
            "id": p.value,
            "name": cfg.name,
            "resolution": f"{cfg.width}x{cfg.height}",
            "max_duration": cfg.max_duration,
            "description": cfg.description,
        }
        for p, cfg in PLATFORM_CONFIGS.items()
    ]
