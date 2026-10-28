# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives

<!-- Your criterion. It must name a number. -->

Of 10 pieces of writing known to be written by humans, no more than 1 may be labeled high-confidence AI.

**Why this target:**

A false positive could wrongly accuse a real writer of using AI, so I want the system to be conservative before giving its strongest AI label. I chose at most 1 out of 10 because a 10% false-positive rate is already a meaningful cost to real writers, and anything higher would make the high-confidence AI label too risky to trust.

---

## 2. Score spread

<!-- Your criterion. -->

Across a test set containing clearly human and clearly AI-generated writing, the average combined score for the AI-generated group should be at least 0.30 higher than the average combined score for the human-written group.

**Why this target:**

If the two groups score almost the same, then the combined detector is not separating them well enough to make the confidence score meaningful. I chose a minimum average gap of 0.30 because it requires a noticeable separation without assuming that human and AI writing can be perfectly distinguished.

---

## 3. Label coverage

<!-- Your criterion. -->

All three reader-facing labels — high-confidence human, unsure, and high-confidence AI — must each be produced by at least 1 test input.

**Why this target:**

If one of the labels can never be reached, then the score thresholds are not covering the full range of possible outcomes correctly. I chose at least one example for each label because the minimum requirement is that every label is actually reachable and can be shown to a user.

---

## 4. Appeal path

<!-- Your criterion. -->

For 5 valid appeals submitted with an existing `content_id`, all 5 must change the submission status to `under_review` and all 5 must be recorded in the audit log with the writer's reasoning.

**Why this target:**

The appeal path exists to give writers a reliable way to challenge a decision, so it should work every time for a valid submission. I chose 5 out of 5 because an appeal failing silently would leave a writer with no way to contest a possible false positive.

---

## 5. Bad input

<!-- Your criterion. -->

The `/submit` endpoint must reject 3 out of 3 invalid requests — one with no `text` field, one with an empty `text` value, and one with text longer than the allowed maximum — without creating a normal submission record or returning a success response.

**Why this target:**

Invalid input should be stopped before it reaches the detector because missing or unusable text could produce misleading scores or unnecessary work. I chose 3 out of 3 because these are basic validation cases that the service should handle consistently every time.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
