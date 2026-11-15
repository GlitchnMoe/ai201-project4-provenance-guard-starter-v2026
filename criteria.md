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

**Original criterion:** The `/submit` endpoint must reject 3 out of 3 invalid requests — one with no `text` field, one with an empty `text` value, and one with text longer than the allowed maximum — without creating a normal submission record or returning a success response.

**Why this target:**

Invalid input should be rejected before it reaches the detector because missing or unusable text could cause errors or produce meaningless scores. I chose 3 out of 3 because malformed requests should fail safely and consistently instead of being treated as normal submissions.

> **Revised in unit 8:** The `/submit` endpoint must cleanly reject 3 out of 3 invalid requests with a `4xx` response: one request with no `text` field, one where `text` is an empty string, and one where `text` is `null`. None of the three may create a normal decision entry in the audit log.
>
> **Why revised:** The original criterion referred to text being longer than the "allowed maximum," but I had never defined what that maximum was, so that part could not be measured objectively. I replaced that case with `null` and specified a `4xx` response so a server crash would not count as successfully rejecting bad input.
>
> **Revised criterion run:** `results/run_2026-11-08_1546_before.md`
>
> The revised criterion returned `500`, `500`, and `500` in all three trials, so the revised result was `0/3`, `0/3`, and `0/3` — **MISSED**.

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

---

## Unit 9 Capstone — Acceptance Criteria

These five criteria evaluate the operational observability extension added to Provenance Guard. Criteria 1–4 focus on the new instrumentation, while Criterion 5 checks that the existing application continues functioning correctly.

Each criterion will be tested in three independent trials without changing the application between trials.

**Shared test input:** For valid detection submissions, the standard input will be:

"Artificial intelligence is transforming the way people work, learn, and communicate. These systems can automate repetitive tasks, generate written content, and assist with decision making."

This input contains 188 characters. Unique creator IDs will be used to prevent the existing per-creator rate limit from interfering with the evaluation.

### 1. Structured Logging Completeness

**Criterion:** In each trial, ten completed HTTP requests (five valid `/ping` requests and five valid `/submit` requests) must generate exactly ten corresponding records in `logs/operations.jsonl`, with no missing or duplicate records. All ten records must contain a valid UTC timestamp, HTTP method, endpoint, input summary, output summary, status code, numeric nonnegative processing duration, and error field. The logged status code must match the actual HTTP response.

**Target:** 10 of 10 complete and correctly matched records in each of three trials.

**Why this target:** Missing even one request would make it impossible to reconstruct all application activity during that test. Since the extension exists specifically to make the application observable, I chose 100% completeness rather than allowing occasional missing records.

### 2. Failure Logging and Error Visibility

**Criterion:** In each trial, submit three invalid requests to `/submit`: one missing the `text` field, one containing empty text, and one containing numeric text. All three must return HTTP 400 and produce exactly one corresponding operational log record containing the endpoint, input summary, HTTP 400 status, nonempty error information, and processing duration.

**Target:** 3 of 3 failed requests recorded correctly in each of three trials.

**Why this target:** Failed requests are especially important to diagnose because they reveal where the application rejects unexpected input. I chose 100% failure logging because even occasional missing errors would undermine the main purpose of the observability extension.

### 3. Input Privacy in Operational Logs

**Criterion:** In each trial, submit five valid text samples containing different unique private markers. For every request, the operational log must record the correct text length and a 16-character SHA-256 fingerprint without storing the complete submitted text or the private marker. Each request must also return HTTP 200.

**Target:** 5 of 5 requests preserve the expected summary fields without exposing the original text or private markers in each of three trials.

**Why this target:** Provenance Guard processes writing that may contain private information, and operational logs may be retained or committed as evidence. I chose zero plaintext exposure because allowing even one complete submission into the operational log could unnecessarily disclose user content.

### 4. Warm-Model Processing Latency

**Criterion:** After one unmeasured model warm-up request, submit the same fixed 188-character sample ten times sequentially using unique creator IDs. At least nine of the ten successful requests must have a recorded `duration_ms` value of 60 milliseconds or less.

**Target:** At least 9 of 10 requests at or below 60 milliseconds in each of three trials.

**Why this target:** Initial measurements showed an average warm-model processing time of 42.5128 milliseconds. A 60-millisecond target allows approximately 41% additional processing time for normal fluctuations while still detecting meaningful performance degradation. Requiring nine of ten requests to meet the limit allows one occasional slow request without accepting consistently poor performance.

### 5. Existing Application Regression Protection

**Criterion:** In each trial, test five existing API behaviors: a valid `/ping` request returns HTTP 200 with `ok: true`; `/health` returns HTTP 200 with `ok: true`; a valid `/submit` request returns HTTP 200 with `content_id`, `guess`, and `confidence`; an empty `/appeal` request returns HTTP 400 with an error response; and a lookup for a nonexistent content ID returns HTTP 404 with an error response.

**Target:** All 5 of 5 behaviors must return the expected status codes and response fields in each of three trials.

**Why this target:** Adding instrumentation should not break functionality that already worked in previous units. I chose 100% because these are established API behaviors, and failures would mean the operational extension introduced a regression rather than simply adding visibility.