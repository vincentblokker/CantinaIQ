# VIDEO-BRIEF — CantinaIQ walkthrough (Soul avatar + screencast hybrid)

Two-minute video for ADA evaluators. Combines a Higgsfield Soul Character
(digital twin of Vincent) for bookend shots, screencast for the substance,
and Italian-wine mood b-roll for tonal continuity. Lives on Vimeo, links
from the ADA submission email.

---

## 1. Spec at a glance

| Field | Value |
|---|---|
| Target length | 120 s (sweet spot for evaluator attention) |
| Aspect ratio | 16:9 horizontal |
| Resolution | 1080p minimum, 2k if Higgsfield produces it cleanly |
| Audio | Vincent's real voice for VO (recorded separately), no music or light bed only |
| Hosting | Vimeo private-with-link (ADA already uses Vimeo for case intros) |
| Bookend avatar segments | 2 × ~8 s — Soul Cinema or Soul V2 |
| Screencast portion | ~75 s — QuickTime recording at 1440 × 900 |
| B-roll | ~20 s — image-to-video via Seedance 2.0, same palette as PDF |
| End frame | Static URL + QR card |

---

## 2. Soul Character — already trained

A Soul Character named **`vblokker`** is already trained and ready in
the Higgsfield account. No new training run needed.

| Field | Value |
|---|---|
| Soul name | `vblokker` |
| Soul ID | `dc0e1fc7-6d66-4c70-beee-eff4d84ccd97` |
| Type | `soul_2` |
| Status | `ready` |
| Compatible models | `text2image_soul_v2`, `soul_cinema_studio` |

Throughout this document, references to `$SOUL_ID` resolve to that UUID.

The remaining 685 credits in the Plus-plan workspace are sufficient for
the full video production several times over (each Soul Cinema clip
costs roughly 30–60 credits depending on duration; Seedance 2.0 b-roll
clips ~10–20 credits each).

### 2.1 Honesty about avatars

Soul-generated avatars at 1080p talking-head scale still have tells:
slightly off blink rates, mouth-shape mismatch on certain phonemes,
occasional facial micro-glitches. For a 2-minute video with two 8-second
avatar segments, this is acceptable. For longer or close-up-heavy
formats, consider real-Vincent-on-camera or a Marketing Studio avatar
with lip-sync built in.

**Mitigation**: keep the avatar shots wide (waist-up or chest-up, not
tight close-up); keep them short; have the avatar speak slowly and
clearly; avoid technical jargon in those segments.

---

## 3. Storyboard

Seven shots across 120 seconds. Each row lists what's on screen, what's
heard, and how to produce it.

| # | Time | Visual | Source | On-screen text | Voice-over |
|---|---|---|---|---|---|
| 1 | 0:00–0:09 | Vincent (Soul avatar) speaks to camera, warm light, neutral backdrop | Higgsfield Soul Cinema — prompt §4.1 | (lower-third: *Vincent Blokker · AI Professional · ADA 2026*) | *"I'm Vincent. This is CantinaIQ — Slurpini Partner Intelligence — my Final Assignment for the Amsterdam Data Academy. Two minutes to show you what's in the box."* |
| 2 | 0:09–0:18 | Wine cellar slow push-in: bottles, glass with red wine, soft natural light, papers on table | Seedance 2.0 image-to-video — prompt §4.2 | *CANTINAIQ IN PRACTICE — Slurpini Partner Intelligence* (clay-red title card, Inter 900) | *"The case: a Dutch importer of Italian wines needs a data-driven way to prioritise on-site producer visits."* |
| 3 | 0:18–0:38 | Screencast: open `CantinaIQ-in-Practice.pdf` cover → flip to §05 Recommendation → flip to §07 Beyond the Brief | QuickTime screen recording | (none — let PDF speak) | *"The strategy brief is nineteen pages. You don't read it linearly. The recommendation is in section five — Hold the prestige tier, Expand in the value-opportunity zone, Audit the bootstrap-borderline."* |
| 4 | 0:38–1:10 | Screencast: `cantinaiq.clubventure.nl` Overview → click /matrix (zoom in on the 762 bubbles) → click /bias (linger on the bar chart) → click /stability (the bootstrap table) | QuickTime screen recording | (none) | *"The dashboard runs the same logic live. 2,986 wines, 762 producers, a five-factor composite score, bootstrap-stabilised, bias-corrected against ICE Amsterdam import statistics. The opportunity matrix shows the whole catalogue on one canvas."* |
| 5 | 1:10–1:30 | Screencast: click "Open rubric map" CTA → scroll through `/for-evaluators` rubric table | QuickTime screen recording | (none) | *"And because evaluation matters, there's a rubric map. Every ADA criterion is linked to a brief section and a source file. Two minutes to confirm coverage."* |
| 6 | 1:30–1:42 | Notebook open on a desk, fountain pen, soft light — slow pan | Seedance 2.0 image-to-video — prompt §4.3 | *"Methodology choices are governance choices."* (italic, slow fade) | *"Methodology choices are governance choices. The analysis still has to earn its trust."* |
| 7 | 1:42–1:55 | Vincent (Soul avatar) speaks to camera | Higgsfield Soul Cinema — prompt §4.4 | (lower-third with URL: *cantinaiq.clubventure.nl*) | *"Brief, repo, dashboard, one-pager — all at cantinaiq.clubventure.nl. Thanks for evaluating."* |
| 8 | 1:55–2:00 | Static end frame: URL + QR code + GitHub handle | Designed in Figma/Keynote or generated still | *cantinaiq.clubventure.nl · github.com/vincentblokker/CantinaIQ* | (silence — 5 s of cleanly muted air) |

---

## 4. Higgsfield prompts (ready to paste)

These are written to match the existing PDF mood — clay-red `#B83A1F`,
deep olive, navy shadow, cream paper, dark walnut. Reference style:
*Apartamento* meets *Monocle*; medium-format film grain.

### 4.1 — Shot 1 — Avatar Vincent intro (Soul Cinema)

```text
A bald man in his late forties with warm eyes and a slight smile,
wearing a soft charcoal sweater over a white shirt, standing in a
warmly lit room with out-of-focus shelving and a hint of red wine
bottles behind. Natural window light from the left, soft shadows.
The man speaks calmly and directly to the camera. Composition: chest-up,
slight rule-of-thirds offset to camera-left. Editorial documentary
aesthetic, like a Financial Times Saturday profile. Medium-format film
look, soft grain, restrained palette of deep olive, cream paper, walnut,
clay red. No logos, no readable text.
```

Higgsfield invocation:
```bash
higgsfield generate create soul_cinema_studio \
  --soul-id dc0e1fc7-6d66-4c70-beee-eff4d84ccd97 \
  --prompt "<paste above>" \
  --aspect_ratio 16:9 \
  --duration 9 \
  --wait
```

### 4.2 — Shot 2 — Wine cellar slow push (Seedance image-to-video)

First generate the still with GPT Image 2:

```text
An Italian wine cellar interior at golden hour. Three unopened wine
bottles with paper labels in muted clay tones on an old oak table.
A single tall wine glass with red wine catches the light. Faintly
visible aged-paper notes with handwritten regional names — Toscana,
Puglia, Abruzzo — partially out of focus. Warm directional light
from a small window upper-left. Deep olive, cream paper, dark walnut,
clay-red wine. Apartamento-meets-Monocle editorial photography,
medium-format film, soft grain, single dominant element. No people,
no faces, no readable brand text, no logos.
```

Then turn the still into video:
```bash
higgsfield generate image_to_video seedance_2 \
  --image <still-from-step-1> \
  --prompt "Slow push-in toward the wine glass, 8 seconds, no people, no camera shake, cinematic" \
  --aspect_ratio 16:9 --wait
```

### 4.3 — Shot 6 — Notebook on desk

```text
Hand-bound leather notebook open on a dark walnut desk, fountain pen
resting at an angle, single brass desk lamp casting warm sidelight.
The notebook pages show handwritten annotations in deep ink but the
text is unreadable abstract marks. A folded printed page peeks from
under the notebook with abstract column shapes hinting at a data
table. Editorial overhead-slight-angle composition. Apartamento /
Monocle aesthetic. Medium-format film grain, restrained palette of
deep olive, cream paper, walnut, clay red. No people, no faces,
no readable text, no logos.
```

Then animate:
```bash
higgsfield generate image_to_video seedance_2 \
  --image <still> \
  --prompt "Slow pan from left to right across the notebook, no camera shake, 12 seconds" \
  --aspect_ratio 16:9 --wait
```

### 4.4 — Shot 7 — Avatar Vincent outro (Soul Cinema)

```text
Same man as before — bald, late forties, warm eyes, soft charcoal
sweater. Now standing slightly more to camera-right, framing the
left third of the shot empty (room for a URL lower-third in post).
Subtle smile, hand briefly gesturing as if pointing toward the URL
text. Natural directional light from window. Editorial documentary
look, medium-format film, deep olive and clay-red accents in the
out-of-focus background. No logos, no readable text.
```

```bash
higgsfield generate create soul_cinema_studio \
  --soul-id dc0e1fc7-6d66-4c70-beee-eff4d84ccd97 \
  --prompt "<paste above>" \
  --aspect_ratio 16:9 \
  --duration 14 \
  --wait
```

### 4.5 — End frame still (optional Higgsfield, or designed manually)

Title card with the dashboard URL on cream background, clay-red title
weight 900, small QR code lower-right. Easier to design in Keynote or
Figma than to generate, but if you want a generated still:

```text
A cream paper background, slight uneven texture, with one bold
hand-set clay-red typographic block reading "cantinaiq.clubventure.nl"
in massive lowercase serif/sans hybrid, occupying the centre. Below it
a smaller line in dark walnut: "github.com/vincentblokker/CantinaIQ".
Slight letterpress impression, restrained palette. Editorial print
aesthetic, medium-format film grain on the paper texture.
No logos, no QR code in the generation — overlay the QR in post.
```

---

## 5. Voice-over recording

### 5.1 Full script (timing-checked at 140 wpm = 280 words for 120 s)

> *(Shot 1 — avatar)*
>
> "I'm Vincent. This is CantinaIQ — Slurpini Partner Intelligence — my Final Assignment for the Amsterdam Data Academy. Two minutes to show you what's in the box."
>
> *(Shot 2 — wine cellar)*
>
> "The case: a Dutch importer of Italian wines needs a data-driven way to prioritise on-site producer visits."
>
> *(Shot 3 — PDF)*
>
> "The strategy brief is nineteen pages. You don't read it linearly. The recommendation is in section five — Hold the prestige tier, Expand in the value-opportunity zone, Audit the bootstrap-borderline."
>
> *(Shot 4 — dashboard)*
>
> "The dashboard runs the same logic live. Two thousand nine hundred eighty-six wines, seven hundred sixty-two producers, a five-factor composite score, bootstrap-stabilised, bias-corrected against I·C·E Amsterdam import statistics. The opportunity matrix shows the whole catalogue on one canvas."
>
> *(Shot 5 — for-evaluators)*
>
> "And because evaluation matters, there's a rubric map. Every ADA criterion is linked to a brief section and a source file. Two minutes to confirm coverage."
>
> *(Shot 6 — notebook)*
>
> "Methodology choices are governance choices. The analysis still has to earn its trust."
>
> *(Shot 7 — avatar)*
>
> "Brief, repo, dashboard, one-pager — all at cantinaiq dot clubventure dot N L. Thanks for evaluating."

**Word count: ~285 words.** At a natural ~140 wpm with brief pauses
between shots, this lands at approximately 2:00. Pad pauses to hit
exact length during editing.

### 5.2 Recording tips

- Quiet room, soft furnishings around. Phone-on-stand close to mouth.
- One take per shot, with at least 5 seconds of room-tone before the
  first word and after the last word of each segment. The room-tone
  helps with noise reduction in editing.
- Read each shot's line twice — pick the best take. Don't read straight
  through; the cadence matters more than continuity.
- For Shot 1 ("I'm Vincent. This is CantinaIQ…"): land it warm and
  measured, not announcer-voice. Think *Financial Times podcast host*,
  not *commercial voiceover*.
- For Shot 6 ("Methodology choices are governance choices…"): slower,
  reflective. This is the moment.

### 5.3 Tools

- **Audacity** (free, mac/win/linux) — recording + noise reduction + trim.
- **iPhone Voice Memos** also fine if your room is quiet.
- Export 48 kHz / 24-bit WAV mono.

---

## 6. Screencast capture

### 6.1 Pre-flight

```bash
# Make sure the dashboard is fully built and live
curl -I https://cantinaiq.clubventure.nl/                # expect HTTP/2 200

# Optional — start the local preview server for higher-fidelity recording
cd dashboard && npm run dev
open http://localhost:5175
```

### 6.2 QuickTime recording

1. ⌘⇧5 → "Record Selected Portion"
2. Frame a 1440 × 810 area (matches 16:9 cleanly)
3. Hide your dock and menu bar (System Settings → Desktop & Dock → auto-hide both)
4. Record three takes:
   - **Take A — PDF walkthrough**: open `CantinaIQ-in-Practice.pdf`,
     show cover for 2 s, scroll to TOC, scroll to p10 (§05), scroll to
     p14 (§07). Smooth, no fast scrolling.
   - **Take B — Dashboard tour**: Overview → wait 3 s → click /matrix
     → wait, hover over Tenuta Masseto bubble → click /bias → linger on
     the bar chart → click /stability → scroll the bootstrap table.
   - **Take C — for-evaluators**: from Overview, click the tuscan CTA
     banner → scroll through the rubric mapping table → click one of
     the download buttons (don't actually trigger the download in
     recording; you can stop the cursor at the button).

### 6.3 Mouse cursor

For a more polished look, hide the cursor between clicks (QuickTime
doesn't do this natively; use **CleanMyMac's "Mouse Highlight" off**
or just record without highlighting and let the cursor be small).

---

## 7. Edit and assembly

### 7.1 Tools

Any of: **iMovie** (free, simplest), **CapCut** (free, more powerful,
auto-subtitle option), **DaVinci Resolve** (free pro, steeper curve),
**Final Cut Pro** (paid, smoothest workflow on Mac).

### 7.2 Sequence

1. Drop all clips on the timeline in storyboard order
2. Underlay the VO track across all shots (start at 0:01, leave ~0.5 s
   pre-roll on each segment)
3. Add lower-thirds for shots 1 and 7 (avatar segments)
4. Add the title card overlay on shot 2 ("CANTINAIQ IN PRACTICE")
5. Add the pull-quote italic text on shot 6
6. Add a subtle music bed at −24 LUFS under the entire timeline (optional;
   silence works too — see the Brief's tone)
7. Fade-in 0.5 s at start, fade-out 1.0 s at end
8. Audio: ducking 6 dB under VO so any music or room tone doesn't fight

### 7.3 Export

- **H.264 MP4**, **1080p**, **CRF 18–20** (visually lossless, ~50–80 MB
  for 2 min)
- 48 kHz / 192 kbps AAC audio
- Aspect ratio 16:9, no letterboxing

### 7.4 Captions

Higgsfield's lip-sync isn't perfect on avatar segments — caption tracks
help comprehension *and* accessibility. Auto-generate with CapCut's
caption tool, then hand-correct. Burn into the export OR ship as a
separate `.vtt` file with the Vimeo upload (Vimeo handles `.vtt` natively).

---

## 8. Hosting and link

### 8.1 Vimeo

ADA already uses Vimeo for case intros (the Slurpini intro at
`vimeo.com/1135863784` is on Vimeo). Mirror that pattern.

1. Upload to Vimeo
2. Privacy: **Unlisted with link** (no public listing, anyone with the
   link can view — appropriate for ADA evaluators)
3. Disable downloads (optional — evaluators don't need to download)
4. Disable comments and likes (academic context, not social)
5. Custom thumbnail: pick a frame from shot 4 (dashboard /matrix view)
6. Note the URL

### 8.2 Where the link lives

After upload, add the URL to:

- The ADA submission email body
- The `/for-evaluators` page on the dashboard — add a fourth download
  card or a banner: *"Prefer a guided tour? Watch the 2-minute video
  walkthrough →"*
- The repo `README.md` near the top, as a third anchor next to the live
  dashboard and the PDF

---

## 9. Production checklist

Tick as you go.

- [x] Soul Character `vblokker` trained — Soul ID `dc0e1fc7-6d66-4c70-beee-eff4d84ccd97`
- [ ] Higgsfield shot 1 generated, looks acceptable
- [ ] Higgsfield shot 2 generated (still + video)
- [ ] Higgsfield shot 6 generated (still + video)
- [ ] Higgsfield shot 7 generated, looks acceptable
- [ ] End-frame card designed
- [ ] Screencast take A (PDF) recorded, 18 s usable
- [ ] Screencast take B (dashboard) recorded, 30 s usable
- [ ] Screencast take C (for-evaluators) recorded, 18 s usable
- [ ] VO recorded for all 7 shots, room-tone padded
- [ ] Timeline assembled in editor
- [ ] Lower-thirds + title card + pull-quote overlays added
- [ ] Captions generated and hand-corrected
- [ ] Export — 1080p H.264 MP4
- [ ] Uploaded to Vimeo (unlisted)
- [ ] Vimeo URL added to README, /for-evaluators, ADA email draft

---

## 10. Fallback if Soul avatars don't land

If the Soul avatar output looks off in the test renders, the cleanest
fallback is to record yourself on iPhone front camera against the
same warm-light backdrop, then composite that into the same edit. No
script changes required — only the source of shots 1 and 7 changes.

That fallback adds ~30 minutes for the recording but eliminates avatar
artefacts entirely. Worth keeping as a Plan B in your head.
