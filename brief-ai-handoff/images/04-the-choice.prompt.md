# Image 04 — The Choice

**File**: `04-the-choice.jpg`
**Used at**: page 9, inline (16 mm margins), ~62 mm tall.
**Aspect ratio**: 16:9
**Higgsfield model**: `gpt_image_2`
**Resolution at generation**: 2k

---

## PROMPT

Editorial photograph: two identical stemmed wine glasses on a dark walnut table, side by side under directional light. The left glass holds a smaller pour of deep ruby wine; the right glass holds the same wine but a noticeably larger pour. Between them, a single folded cream linen napkin and a small handwritten note card. Tight horizontal composition, conceptually evoking "two equivalent options, one is the right choice". Mood: editorial, contemplative, restrained. No people, no faces, no readable text, no logos. Color palette: clay red, navy shadow, cream paper, dark walnut. Medium format film, slight grain, shallow depth of field.

---

## Why this image

The section is "The Choice — when the heavyweight earns its place and when it does not". The two-glass composition is a visual analogy: two valid options, the right answer depends on context. The asymmetric pour (smaller / larger) gestures at "the right size for the question" without spelling it out.

The image's narrow vertical band — short and wide — matches the section opener's compressed layout (one decorative band before the "right choice / wrong choice" grids).

## Iteration notes

- The two glasses must be **identical in shape**. Different glasses break the analogy (it would suggest "different glass for different wine", which is a different point).
- The asymmetric pour (one small, one large) is the whole concept. Don't equalise.
- Lighting should be **directional from one side**, not flat. The contrast on the curve of the glasses is what gives the image its presence at the small render size.
- The note card between them is a small editorial touch. Keep it; don't enlarge it.

## What does NOT belong

- A wine bottle anywhere in frame — the image is about the choice, not the producer.
- Symmetric pours — destroys the concept.
- A vineyard or window in the background. The setting is interior, intimate.
- Two different wines — the wine is the same; the choice is about the pour, not the bottle.

## Regenerate

```bash
higgsfield generate create gpt_image_2 \
  --prompt "[PROMPT ABOVE]" \
  --aspect_ratio 16:9 --resolution 2k --wait
```
