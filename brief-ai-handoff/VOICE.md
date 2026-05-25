# VOICE.md — Vincent Blokker's authorial voice

This is the voice the document must keep. It is observable in
[reference/Azure-AI-in-Practice.pdf](reference/Azure-AI-in-Practice.pdf), Vincent's
template for ADA submissions, and it is what every section of the current brief
imitates.

If you cannot read the reference PDF, read at least the page-by-page PNGs in
`reference/azure-template-pages/`. Three pages of context is the minimum before
editing.

---

## The shape of the voice

| Trait | What it sounds like | What it never sounds like |
|---|---|---|
| Measured | "Azure earns its place in several situations." | "Azure is amazing for…" |
| Comparative | "The Azure route provides faster setup; the local route provides more control." | "The Azure route is best." |
| Governance-aware | "Where data lives matters. Which legal regime applies matters." | "Data should be secure." |
| Honest about scope | "This document is not a summary of the course material. It is an evaluation." | "This document covers everything you need to know." |
| Concrete, named | "ClubDuty runs on Hetzner with PostgreSQL." | "We use modern infrastructure." |
| Limitations as features | "The architecture is sound. The privacy position is stronger. The remaining challenge is hardware, not feasibility." | "Some limitations may apply." |
| First-person, no hedge | "I completed the Whizlabs labs in my own subscription." | "It is generally recommended that…" |
| Closing zoom-out | "Technology choices are governance choices." | "In conclusion, Azure is one option." |

---

## Sentence-level rules

1. **Lead with the verdict.** "Azure earns its place when…" not "Let's now consider when Azure may be appropriate."
2. **One claim per sentence.** Compound sentences with three claims are dilution.
3. **No padding verbs.** "is" beats "is fundamentally"; "shows" beats "clearly demonstrates".
4. **Numbers are statements.** "88 % recall on exact match" — full stop. Not "an impressive 88 %".
5. **Sceptical asides land hard.** "That immediately changes the nature of the solution." Used sparingly, they steer the argument.
6. **Allow short paragraphs.** A single sentence is a paragraph if it carries weight.

---

## The signature moves

These appear in both the Azure brief and the CantinaIQ brief. They are not optional. They are the connective tissue.

### Move 1 — The "right question" reframe

> *"The right question is not 'can Azure do this?' The right question is what Azure gives you that the next-best option does not."*

Used in §02 of both briefs. Reframes a yes/no choice into a comparative one. Always introduces a section, never closes it.

### Move 2 — The two-route comparison table

A literal `Area | /bare route | /supercharged route` table (in this brief) or `Area | Azure route | Local route` (in the original). The left column is red, bold, lowercase. Rows are honest about both sides.

### Move 3 — The italicised pull-quote between sections

> ***Technology choices are governance choices.***
>
> ***Methodology choices are governance choices.***
>
> ***Infrastructure choice is a governance choice.***

Always italicised, always one short sentence, always full-stop. Pattern: `[NOUN] choices are governance choices.`

### Move 4 — The closing principle

The Azure brief closes with *"But it should still have to earn its place."* The CantinaIQ brief closes with *"But the analysis should still have to earn its trust."* Same shape: a "but" clause that doesn't undo what came before but adds a quiet ethical weight.

### Move 5 — Named concrete projects

Vincent's voice gets its grip from real projects. Use them as touchstones, not as flexes:

- **ClubDuty** — Vincent's basketball-club SaaS (Hetzner, PostgreSQL, Node).
- **BV Hoofddorp** — the youth basketball club where the player-tracking case lives.
- **Scoupy** — Vincent's 2019 receipt-scanning work (used as the "Document Intelligence is not a new problem" anchor).
- **Slurpini** — the Italian-wine importer at the heart of CantinaIQ.

If you add a new section, find a concrete project anchor. Without one, the voice goes generic.

### Move 6 — Limitations stated, not hidden

> *"The current limitation is compute economics rather than capability."*
>
> *"The supercharged track does not claim to have solved the problem. It claims to have made the limitations measurable."*

Limitations are surfaced inside the argument, not relegated to an appendix. They strengthen the work, they don't apologise for it.

---

## Words to avoid

Marked-up examples — left column is wrong, right column is the Vincent way.

| Avoid | Prefer |
|---|---|
| "powerful and intuitive" | "useful in these situations" |
| "leveraging" | "using" |
| "robust" | "stable" or "reliable" |
| "seamlessly" | (cut) |
| "best-in-class" | (cut, or replace with a comparison) |
| "really matters" | "matters" |
| "very significant" | (cut, or give a number) |
| "extremely" | (cut) |
| "in today's fast-paced world" | (cut, always) |
| "It is worth noting that" | (cut, just state the thing) |

---

## Tense and person

- **First-person singular** in the introduction and the "About the Author" page only.
- **Third-person neutral** in the body. "The supercharged track" not "I built the supercharged track".
- **Present tense** for what the document and the system do. Past tense only for the historical anecdote (Scoupy 2019, the Toeslagenaffaire reference).

---

## Argument architecture (per section)

Each section follows a predictable rhythm:

1. **What the thing is.** One paragraph, neutral description.
2. **What it is good at.** One short paragraph, specific.
3. **What it is not / where it fails.** One short paragraph, honest.
4. **The comparative claim.** One paragraph that puts it next to the next-best alternative.
5. **The closing pivot.** One sentence that earns the next section.

Sections 02 and 04 follow this most cleanly. Sections 03 and 05 use a slightly looser version — case narrative for 03, governance pivot for 05.

---

## The litmus test

After editing, read three sentences aloud at random. If any of them sound like a LinkedIn post, a marketing brochure, or a textbook, rewrite them. The target is a *Financial Times Saturday* tone — declarative, specific, restrained, occasionally wry.
