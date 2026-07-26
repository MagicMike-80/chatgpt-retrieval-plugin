# STYLE LOCK — paste this into Flow AI before every batch

This is the constitution for the look. It is derived from the reference image
(white stick figure with torch, black long-haired entity behind him, hallway).
Paste **this whole block first**, attach the reference image, then paste a batch
of 20 numbered prompts.

---

## THE FLOW AI PROMPT

```
Generate a set of images based on the provided scene-specific prompts. Strictly
adhere to the visual style, character designs, and metaphorical translation rules
established in the provided reference image. All scenes designated as "CLIPS" must
be generated as STILL images.

STYLE: Pure black background. Minimalist 2D hand-drawn illustration. The human
characters are simple WHITE LINE-ART STICK FIGURES: thin uniform white stroke,
oval head, large round expressive eyes, simple drawn mouth, thin noodle limbs,
simple hands. The supernatural entities are the opposite: SOLID BLACK INK
SILHOUETTES with no interior detail, long straight black hair, elongated spindly
arms and long fingers, and two glowing white eyes. Never draw an entity as line
art. Never draw a human as a solid silhouette.

LIGHTING: One single practical light source per image (flashlight, oil lamp,
candle, moon, doorway). It throws a hard white pool or cone across the floor.
Everything outside that pool falls to pure black. Heavy vignette. High contrast,
no midtones, no grey wash.

ENVIRONMENT: Sparse white line-art architecture with a slight hand-drawn wobble
in every straight line — floorboards in perspective, doorframes, walls with
hairline cracks. Draw only what the light touches. Empty black space is correct
and wanted.

SHADOWS: Long and distorted, drawn as flat black shapes. A human's shadow may
have more arms, more hair, or a different posture than the human casting it.

COLOR: Strictly monochrome. Black and white only. No colour of any kind.

FORMAT: 16:9 landscape. Clean, standalone 2D illustration.

CRITICAL NEGATIVE CONSTRAINTS — ensure that NO external UI elements or video
overlays are included in any generated image, specifically: no play buttons, no
red progress bars, no video player controls, no timestamps, no watermarks, no
logos, no subtitles, no captions, no title text in the corners of the scenes, no
speech bubbles, no on-screen writing of any kind. No 3D rendering, no photoreal
texture, no gradients, no colour.
```

---

## Recurring cast — visual descriptors

Reuse these exact words whenever a character appears, so prompt 3 and prompt 57
render the same person.

| Character | Fixed descriptor |
| --- | --- |
| **Mae Nak** | black ink silhouette woman, floor-length black hair, glowing white eyes, one arm drawn far too long |
| **Mak** | white stick figure man, short cropped hair scratched in, soldier's satchel strap across chest |
| **Village Elder** | white stick figure, bent spine, thin wispy hair lines, walking stick |
| **Thai Old Man** | white stick figure, round spectacles drawn as two circles, apron |
| **Lucy** | white stick figure young woman, shoulder-length hair drawn in loose white strokes |
| **Gummi-Face** | black ink silhouette with a smooth featureless head that sags and drips like wax, no hair |
| **Krasue** | floating black ink head with glowing white eyes, long hair, trailing entrails drawn as thin black ribbons below |
| **Nuan** | white stick figure woman, hair tied in a bun drawn as a small circle |
| **Somchai** | white stick figure man, wide-brimmed farmer's hat |
| **Phra Sombat** | white stick figure monk, robe drawn as a single draped white outline over one shoulder, shaved head |
| **Nang Tani** | black ink silhouette woman, very long hair, feet not touching the ground, banana-leaf shapes at her edges |
| **Mor Tham** | white stick figure, sacred thread lines around wrists, small satchel |
| **Bua** | white stick figure woman, hollow black-filled eyes (the only human ever drawn with filled eyes) |
| **Khun Anan** | white stick figure man, buttoned shirt lines, wristwatch as a small circle |
| **Kuman** | small black ink silhouette child, round head, glowing white eyes, always seated |
| **Ploy** | white stick figure young woman, long hair spread across a pillow |
| **Ranger Wit** | white stick figure, cap, torch always in hand |
| **Foreman Krit** | white stick figure, hard hat drawn as a half-circle, clipboard |
| **Nang Ta-khian** | black ink silhouette woman, hair merging into tree-bark lines, ribbons trailing from her arms |

## Entity escalation ladder

Use this to pace the horror across the 6 scenes of any episode. It is why the
episodes feel like they build instead of just repeating.

| Scene | How much of the entity is visible |
| --- | --- |
| S1 | A shape in the black. Eyes only, or a hand at the frame edge. |
| S2 | Not present, or present only as a wrong shadow. |
| S3 | Partial — behind the character, unnoticed, cut off by the frame. |
| S4 | Full body, still at distance, clearly aware of the character. |
| S5 | Close. Same pool of light as the character. Touching or nearly touching. |
| S6 | Withdrawn — or occupying the frame alone, facing the viewer. |

## Sequencing rules

- **One light source per image.** Two lights kills the look instantly.
- **The entity is never lit.** Light passes over it without revealing detail.
- **Humans stay line-art even in terror.** Only the ending of Episode 3 breaks
  this, and it breaks it on purpose.
- **Seamless links:** the last prompt of a scene and the first prompt of the next
  share the same camera framing, so SyncFrame's cut lands on a match.
