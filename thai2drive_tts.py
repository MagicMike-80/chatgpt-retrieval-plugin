import json
import os
import time
from pathlib import Path
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_DIR = Path("output")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_mp3(text: str, filename: str):
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        print(f"  Hopper over (finnes): {filename}")
        return

    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format="mp3_44100_128",
        )
        with open(filepath, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print(f"  OK: {filename}")
        time.sleep(0.3)  # unngå rate limiting
    except Exception as e:
        print(f"  FEIL {filename}: {e}")


def process_questions(json_file: str):
    if not os.path.exists(json_file):
        print(f"Finner ikke {json_file} — hopper over.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"\n--- MongoDB: {len(questions)} spørsmål ---")
    for q in questions:
        qid = q.get("id", "").replace("-", "_")
        q_th = q.get("question", {}).get("th", "")
        exp_th = q.get("explanation", {}).get("th", "")

        if q_th:
            generate_mp3(q_th, f"q_{qid}_question.mp3")

        for opt in q.get("options", []):
            opt_id = opt.get("id", "")
            opt_th = opt.get("text", {}).get("th", "")
            if opt_th:
                generate_mp3(opt_th, f"q_{qid}_ans_{opt_id}.mp3")

        if exp_th:
            generate_mp3(exp_th, f"q_{qid}_explanation.mp3")


def process_teoribok(txt_file: str):
    if not os.path.exists(txt_file):
        print(f"Finner ikke {txt_file} — hopper over.")
        return

    with open(txt_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    kapitler = data.get("teoribok", [])
    print(f"\n--- Teoriboken: {len(kapitler)} kapitler ---")
    for kapittel in kapitler:
        kid = kapittel.get("id", "")
        for i, seksjon in enumerate(kapittel.get("innhold", []), start=1):
            tekst_th = seksjon.get("tekst_th") or seksjon.get("tekst", "")
            if tekst_th:
                generate_mp3(tekst_th, f"teoribok_{kid}_{i}.mp3")


if __name__ == "__main__":
    print("Thai2Drive TTS generator startet...")
    process_questions("mongodb_questions_export.json")
    process_teoribok("teoribok json skrift til appen.txt")
    print(f"\nFerdig! MP3-filer lagret i: {OUTPUT_DIR.resolve()}")
