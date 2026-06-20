import json
import csv
import os

output_rows = []

# --- Del 1: MongoDB spørsmål ---
mongodb_file = "mongodb_questions_export.json"
if os.path.exists(mongodb_file):
    with open(mongodb_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    for q in questions:
        qid = q.get("id", "").replace("-", "_")
        question_th = q.get("question", {}).get("th", "")
        explanation_th = q.get("explanation", {}).get("th", "")

        if question_th:
            output_rows.append([f"q_{qid}_question.mp3", question_th])

        for opt in q.get("options", []):
            opt_id = opt.get("id", "")
            opt_th = opt.get("text", {}).get("th", "")
            if opt_th:
                output_rows.append([f"q_{qid}_ans_{opt_id}.mp3", opt_th])

        if explanation_th:
            output_rows.append([f"q_{qid}_explanation.mp3", explanation_th])

    print(f"MongoDB: {len(questions)} spørsmål behandlet.")
else:
    print(f"Fant ikke {mongodb_file} — hopper over.")

# --- Del 2: Teoriboken ---
teoribok_file = "teoribok json skrift til appen.txt"
if os.path.exists(teoribok_file):
    with open(teoribok_file, "r", encoding="utf-8") as f:
        teoribok_data = json.load(f)

    kapitler = teoribok_data.get("teoribok", [])
    for kapittel in kapitler:
        kid = kapittel.get("id", "")
        for i, seksjon in enumerate(kapittel.get("innhold", []), start=1):
            tekst_th = seksjon.get("tekst_th") or seksjon.get("tekst", "")
            if tekst_th:
                output_rows.append([f"teoribok_{kid}_{i}.mp3", tekst_th])

    print(f"Teoriboken: {len(kapitler)} kapitler behandlet.")
else:
    print(f"Fant ikke teoribok-filen — hopper over.")

# --- Skriv CSV ---
output_file = "elevenlabs_input.csv"
with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["filnavn", "thai_tekst"])
    writer.writerows(output_rows)

print(f"\nFerdig! {len(output_rows)} filer skrevet til {output_file}")
