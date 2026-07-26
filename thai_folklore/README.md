# Thai Folklore — Master Prompts (Episodes 1–10)

Copy-paste-ready prompt packs for the pipeline:

```
Ideation → Voice-First (ElevenLabs V3) → TurboScribe (timestamps)
        → Google Flow + ZAPI FLOW (still image batch) → Meta AI / Grok (animation)
        → SyncFrame (auto-cut on voice) → YouTube Studio
```

**Format:** 16:9 landscape, ~11 minutes, 6 scenes per episode.
**Look:** black-and-white 2D — white line-art stick figures, solid black ink spirits.
**Rule from AGENTS.md §3:** voice first, scene second. Always.

## Files

| File | Use it for |
| --- | --- |
| `STYLE_LOCK.md` | **Paste this into Flow before every batch.** The header prompt, the cast descriptors, the negative constraints. |
| `master_prompts/EP01..EP10_*.md` | One file = one full 6-scene episode = 60 numbered image prompts in 3 batches of 20, plus VO and SEO. |
| `episodes.py` | Machine-readable: scenes, timing, characters, VO lines (Thai + English). |
| `voice_generator.py` | Reads `episodes.py`, calls ElevenLabs, writes MP3s + `MANIFEST.json` for SyncFrame. |

## Episode order

| # | Title | Creature | File |
| --- | --- | --- | --- |
| 1 | Mae Nak — The Wife Who Would Not Leave | แม่นาคพระโขนง | `EP01_MAE_NAK.md` |
| 2 | The Last Emotion | Gummi-Face (original) | `EP02_THE_LAST_EMOTION.md` |
| 3 | The Mirror Drip | Gummi-Face (original) | `EP03_THE_MIRROR_DRIP.md` |
| 4 | Krasue — The Hunger Below the Head | กระสือ | `EP04_KRASUE.md` |
| 5 | Nang Tani — The Woman in the Banana Grove | นางตานี | `EP05_NANG_TANI.md` |
| 6 | Phi Pop — The Thing That Wears You | ผีปอบ | `EP06_PHI_POP.md` |
| 7 | Kuman Thong — The Golden Child | กุมารทอง | `EP07_KUMAN_THONG.md` |
| 8 | Phi Am — The Weight on Your Chest | ผีอำ | `EP08_PHI_AM.md` |
| 9 | Kong Koi — One Leg, One Thirst | กองกอย | `EP09_KONG_KOI.md` |
| 10 | Nang Ta-khian — The Tree That Screamed | นางตะเคียน | `EP10_NANG_TAKHIAN.md` |

Episodes 2 and 3 are reconstructed from the voice manifest (`EP2_S1_Thai_Old_Man`,
`EP3_S2_Lucy_Eng_Girl`) because the original Python files live in another sandbox.
Drop your exact dialogue into `episodes.py` — the visual prompts are written
against the beats, not the lines, so they still hold.

## The 6-scene / 11-minute grid

Identical across all ten, so SyncFrame, chapters and thumbnails stay mechanical.

| Scene | Timing | Function | Prompts |
| --- | --- | --- | --- |
| S1 | 00:00 – 01:30 | Cold open. The image that makes them stay. | 1–10 |
| S2 | 01:30 – 03:30 | Setup. Who, where, what is normal. | 11–20 |
| S3 | 03:30 – 05:30 | First contact. Something is wrong. | 21–30 |
| S4 | 05:30 – 07:30 | Escalation. The rules of the haunting reveal themselves. | 31–40 |
| S5 | 07:30 – 09:30 | Confrontation. Face to face. | 41–50 |
| S6 | 09:30 – 11:00 | Resolution + hook into the next episode. | 51–60 |

Batch 1 = prompts 1–20 (S1+S2) · Batch 2 = 21–40 (S3+S4) · Batch 3 = 41–60 (S5+S6).

## Workflow, in order

**1. Voice first.** Fill in the voice IDs in `episodes.py`, then:

```bash
export ELEVENLABS_API_KEY="..."
python thai_folklore/voice_generator.py --dry-run     # check the plan, costs nothing
python thai_folklore/voice_generator.py --episode 1   # generate
```

**2. Timestamps.** Run the MP3s through TurboScribe. The real runtime is now known
— the 11-minute grid was only ever a target.

**3. Images.** Open Flow AI. Paste `STYLE_LOCK.md`'s **THE FLOW AI PROMPT** block,
attach your reference image, then paste Batch 1 (prompts 1–20). Batch generate.
Repeat for batches 2 and 3. 60 stills per episode.

**4. Animation.** Push selected stills through Meta AI / Grok for subtle motion —
hair drift, light flicker, the entity's slow lean. Most stills stay still; the
Ken Burns push in the edit does the rest.

**5. Cut.** Feed the stills + `MANIFEST.json` into SyncFrame. It cuts to the voice.

**6. Publish.** Each episode file ends with a YOUTUBE SEO block — title options,
description, tags, chapters, thumbnail prompt.

### Why 60 stills

60 stills across ~11 minutes is roughly an 11-second hold each, which is right for
this style with a slow push. Want faster cutting? Generate the batch twice with
small framing variations and interleave, or write 20 extra prompts for the scenes
that need them. Don't go below 60 — it starts to feel like a slideshow.

## Before you burn credits

The Thai lines are written to be spoken, not as a translation exercise. Have a
native speaker read them once before generating — especially Episode 6, which is
written in Isan. Fix them in `episodes.py`, never in the markdown.

## Cultural note

Mae Nak, Krasue, Nang Tani, Phi Pop, Kuman Thong and Nang Ta-khian are living
beliefs, not just monsters — there are shrines to Mae Nak in Phra Khanong, and
people leave offerings at takhian trees today. These scripts treat the spirits as
grieving or hungry rather than evil, and the humans as respectful rather than
comic. Keep that if you rewrite it: it's also what separates this from the
thousand other AI horror channels.
