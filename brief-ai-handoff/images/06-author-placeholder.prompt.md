# Image 06 — Author block (placeholder)

**File**: `06-author-placeholder.jpg`
**Status**: **Placeholder.** This is currently a still-life image reused from elsewhere in the project. **Replace before final delivery.**
**Used at**: page 12, left column of the "About the Author" grid (65 mm wide, ~4:5 aspect).
**Aspect ratio**: 1:1 (currently — should be re-cropped to 4:5 when replaced).
**Higgsfield model**: `gpt_image_2`
**Resolution at generation**: 2k

---

## Replacement preference (priority order)

### Option 1 — A real Vincent portrait (strongly preferred)

Match the visual treatment of Vincent's existing Azure brief author page:

- Black-and-white or very desaturated colour.
- Environmental — Vincent in a corridor, in a workspace, against a textured wall — not a studio shot, not a cropped headshot.
- Looking middle-distance, three-quarter angle, not direct-to-camera.
- Crisp focus on the face, slightly soft background.
- 4:5 aspect ratio (portrait), tight enough to read clearly at 65 mm wide in the layout.

Vincent should supply this image himself. The placeholder exists so the layout works in the meantime.

### Option 2 — A non-face editorial still life

If a real portrait is not available and one is needed for delivery, generate an *intentionally non-portrait* still life that signals "the author's desk" rather than "the author's face":

**PROMPT (suggested if regenerating)**:

> Editorial photograph: a writer's desk surface in soft afternoon light. A black-paged notebook open with handwritten cursive notes in faint blue ink, a fountain pen lying diagonally across it, a single empty wine glass at the edge of frame catching warm light, a stack of three printed reports beside the notebook with margin annotations. The composition is balanced left-to-right but slightly asymmetric. Mood: contemplative, working, restrained. No people, no faces, no readable text, no logos. Color palette: clay red, deep olive, navy ink, cream paper, dark walnut. Medium format film, slight grain, soft shadows. Aspect ratio 4:5 portrait.

This works because it preserves the editorial mood and the visual identity without pretending to be a photo of Vincent.

### Option 3 — DO NOT

**Do not generate a fake portrait of a fictional person and present it as Vincent.** The Azure brief uses a real photograph; using a fake face here would be dishonest about the document's authorship.

---

## Iteration notes

- Whichever option is chosen, the image must be 4:5 (portrait orientation). The current placeholder is 1:1 and gets visually cropped in the layout.
- The image should be visually quiet. The right column carries the name, the paragraphs and the meta grid; the left column should not compete.

## Regenerate (Option 2)

```bash
higgsfield generate create gpt_image_2 \
  --prompt "[PROMPT ABOVE]" \
  --aspect_ratio 4:5 --resolution 2k --wait
```
