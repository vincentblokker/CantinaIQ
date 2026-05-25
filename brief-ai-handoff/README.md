# brief-ai-handoff — package for the next AI

This folder is a self-contained handoff so another AI can improve the *CantinaIQ in Practice — Strategy Brief* without ever needing the parent repository.

**Start with [`HANDOFF.md`](HANDOFF.md).** It tells you what to read, what to change, what not to change, and how to render the PDF.

---

## Contents

| File / folder | Purpose |
|---|---|
| **[HANDOFF.md](HANDOFF.md)** | The AI brief. Start here. Explains the job, the priority order, the success criteria. |
| **[VOICE.md](VOICE.md)** | Vincent's authorial voice with examples. Read before touching any prose. |
| **[TEMPLATE.md](TEMPLATE.md)** | Visual identity — colours, typography, layout patterns. Read before touching the HTML. |
| [`content/`](content) | All six section texts as standalone markdown, with per-section editor notes. |
| [`images/`](images) | All six images plus a `.prompt.md` sidecar per image with the exact Higgsfield prompt and iteration notes. |
| [`reference/`](reference) | Vincent's original *Azure-AI-in-Practice* PDF + page-by-page PNGs for visual reference. |
| [`source/`](source) | The editable HTML source and the current rendered PDF. |
| [`render.sh`](render.sh) | One-liner to re-render the PDF from source. |

---

## Three-step quickstart

```bash
# 1. Read the brief
open HANDOFF.md

# 2. Make your edits
$EDITOR source/brief.html

# 3. Re-render and verify
./render.sh
pdfinfo source/brief.pdf | grep Pages   # must say 12
```

If the page count drifts, see HANDOFF.md §3.5 ("Pagination must stay at 12").

---

## When you hand the work back

Update `source/brief.pdf` (re-render) and bump the version line in HANDOFF.md if you have made substantive changes. Re-zip the folder if the package is being shared as a single artefact.

The parent CantinaIQ repository is at https://github.com/vincentblokker/CantinaIQ — but you do not need to touch it. Everything you need is in this folder.
