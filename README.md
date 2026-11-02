# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

A writer submits text to POST /submit along with a creator_id. The service creates a unique content_id for the submission

The text then moves through the detection pipeline:

1. `detector.py` analyzes how predictable the writing is to a local language model and produces a model score from 0 to 1.
2. `stylometry.py` measures the shape of the writing using sentence-length variation, vocabulary variety, and punctuation density and produces a second score from 0 to 1.
3. `scoring.py::combine_signals` combines the model score and style score using a 65% model / 35% style weighted average.
4. `scoring.py::score_to_label` maps the combined score to one of three outcomes: high-confidence human, unsure, or high-confidence AI.
5. The service writes the decision, both signal scores, combined score, label, creator ID, content ID, and status to `logs/audit.jsonl`.
6. The response returned to the caller includes the `content_id`, guess, confidence score, reader-facing label, model score, and style score.
7. If the writer believes the result is incorrect, they can send the `content_id` and their reasoning to `POST /appeal`. The appeal is appended to the audit log and the submission is marked `under_review`.
8. A caller can use `GET /content/<id>` with a submission's `content_id` to retrieve the original decision, both signal scores, combined confidence, reader-facing label, and the item's current status. If an appeal has been filed, the current status is returned as `under_review`.



---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**

`detector.py` uses a local language model to read the submitted text and produce a score representing how AI-like the writing appears based on language patterns the model learned during training.

**Why that might differ between human and AI writing:**

AI-generated writing can contain patterns in phrasing, structure, and word choice that differ from naturally written human text. A model trained to distinguish the two may be able to recognize some of those patterns.

**What it can't see:**

The model cannot actually know who wrote the text. A polished or formal human writer could produce language that resembles patterns associated with AI, while AI-generated text that has been edited by a person could appear more human and avoid detection.

### Signal two — the style signal

**What it measures:**

`stylometry.py` measures surface-level characteristics of the text rather than its meaning, such as sentence-length variation, vocabulary variety, and punctuation density.

**Why that might differ between human and AI writing:**

Human writing can contain irregularities and variation in sentence length, vocabulary, and punctuation, while AI-generated writing may sometimes be more uniform or consistent in these areas.

**What it can't see:**

Stylometry does not understand what the text means or know who created it. A human writer may naturally have a very consistent style, while AI-generated text can be prompted or edited to deliberately vary sentence length, vocabulary, and punctuation.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**  
I combine the two signals using a weighted average. The model signal receives 65% of the weight and the style signal receives 35%. Both signals use the same direction, where a higher score means more likely AI.

**The numbers:**  
`combined_score = (0.65 × model_score) + (0.35 × style_score)`

I gave the model signal more weight because it separated the clearly AI-written example more strongly in my initial tests. The style signal still has enough weight to act as a second opinion when the two signals disagree. This helps prevent one signal by itself from producing an overly confident result.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:**  
For the clearly human-style example, the model signal returned `0.6499` while the style signal returned `0.2556`. The model signal leaned AI while the style signal leaned human. With my 65/35 weighting, the combined score becomes approximately `0.5119`, which moves the result toward uncertainty instead of allowing the model signal alone to strongly accuse the writing of being AI-generated.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| High-confidence human | 0.00 – 0.35 | We think this was probably written by a person. |
| Unsure | 0.35 – 0.65 | We cannot confidently tell whether this was written by a person or generated by AI. |
| High-confidence AI | 0.65 – 1.00 | We think this was probably generated by AI. |

**Why I worded the "unsure" one this way:**  
I wanted the label to clearly admit uncertainty without accusing the writer of using AI. It tells the reader that the system does not have enough evidence to make a confident decision and leaves open both possibilities.


---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

Submission with the first signal

Request:

```bash
curl.exe --% -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d "{\"text\":\"Artificial intelligence is transforming the way people work and communicate. It can automate repetitive tasks, generate written content, and assist with decision making. These systems are becoming increasingly common in schools, businesses, and everyday software.\",\"creator_id\":\"user123\"}"
```
Response:

```json
{
  "confidence": 0.0,
  "content_id": "8a2acba7-135a-4bd7-914b-f87658022044",
  "guess": "ai",
  "label": "placeholder",
  "model_score": 0.7242,
  "style_score": 0.0
}
```

**A submission**

Submission with both signals and combined scoring.

**Request**

```bash
curl.exe --% -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d "{\"text\":\"Artificial intelligence is transforming the way people work, learn, and communicate. It offers numerous benefits, including increased efficiency, improved decision-making, and the automation of repetitive tasks.\",\"creator_id\":\"test_ai\"}"
```

**Response**

```json
{
  "confidence": 0.6792,
  "content_id": "be7d1efa-4cf1-4078-a8f3-b0227e278e1f",
  "guess": "ai",
  "label": "placeholder",
  "model_score": 0.8577,
  "style_score": 0.3476
}
```

At this stage, both signal scores and the combined confidence score are real. The reader-facing label is still a placeholder because the three final label variants are implemented in Milestone 5.

**An appeal**

```bash
$ curl.exe --% -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" -d "{\"content_id\":\"1d6fec38-573d-4365-abf9-e10c5e1f3707\",\"reasoning\":\"I wrote this myself and believe the classification is incorrect.\"}"
```

```json
{
  "content_id": "1d6fec38-573d-4365-abf9-e10c5e1f3707",
  "message": "Appeal recorded.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 1,
  "entries": [
    {
      "combined_score": null,
      "content_id": "8a2acba7-135a-4bd7-914b-f87658022044",
      "creator_id": "user123",
      "guess": "ai",
      "label": "placeholder",
      "model_score": 0.7242,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-10-28T23:47:32+00:00"
    }
  ]
}
```
After second style added:

```bash
$ curl "http://127.0.0.1:5000/log?limit=6"
```

```json
{
  "count": 6,
  "entries": [
    {
      "combined_score": null,
      "content_id": "8a2acba7-135a-4bd7-914b-f87658022044",
      "creator_id": "user123",
      "guess": "ai",
      "label": "placeholder",
      "model_score": 0.7242,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-10-28T23:47:32+00:00"
    },
    {
      "combined_score": 0.6792,
      "content_id": "9f0ac538-9dc1-42a5-a971-a131cde7d68f",
      "creator_id": "user123",
      "guess": "ai",
      "label": "placeholder",
      "model_score": 0.8577,
      "status": "decided",
      "style_score": 0.3476,
      "timestamp": "2026-11-01T21:21:29+00:00"
    },
    {
      "combined_score": 0.6792,
      "content_id": "be7d1efa-4cf1-4078-a8f3-b0227e278e1f",
      "creator_id": "test_ai",
      "guess": "ai",
      "label": "placeholder",
      "model_score": 0.8577,
      "status": "decided",
      "style_score": 0.3476,
      "timestamp": "2026-11-01T21:22:52+00:00"
    },
    {
      "combined_score": 0.5119,
      "content_id": "243632cb-afcb-4f5f-a74e-064f4fda88d4",
      "creator_id": "test_human",
      "guess": "ai",
      "label": "placeholder",
      "model_score": 0.6499,
      "status": "decided",
      "style_score": 0.2556,
      "timestamp": "2026-11-01T21:22:58+00:00"
    },
    {
      "combined_score": 0.6388,
      "content_id": "cc55033d-b151-483f-a2da-b6660c2fcce7",
      "creator_id": "test_formal_human",
      "guess": "ai",
      "label": "placeholder",
      "model_score": 0.6489,
      "status": "decided",
      "style_score": 0.62,
      "timestamp": "2026-11-01T21:23:05+00:00"
    },
    {
      "combined_score": 0.3871,
      "content_id": "bf4fd371-6297-4a6b-a9d1-601cdec03943",
      "creator_id": "test_edited_ai",
      "guess": "human",
      "label": "placeholder",
      "model_score": 0.4541,
      "status": "decided",
      "style_score": 0.2628,
      "timestamp": "2026-11-01T21:23:12+00:00"
    }
  ]
}
```
After appeal completed:

Original decision before appeal made:

```json
{
  "combined_score": 0.6792,
  "content_id": "1d6fec38-573d-4365-abf9-e10c5e1f3707",
  "creator_id": "label_ai",
  "guess": "ai",
  "label": "We think this was probably generated by AI.",
  "model_score": 0.8577,
  "status": "decided",
  "style_score": 0.3476,
  "timestamp": "2026-11-02T01:30:32+00:00"
}
```

After appeal made:

```json
{
  "content_id": "1d6fec38-573d-4365-abf9-e10c5e1f3707",
  "creator_id": "label_ai",
  "event": "appeal",
  "reasoning": "I wrote this myself and believe the classification is incorrect.",
  "status": "under_review",
  "timestamp": "2026-11-02T01:32:18+00:00"
}
```

### Content status lookup

**Request**

```bash
curl.exe http://127.0.0.1:5000/content/1d6fec38-573d-4365-abf9-e10c5e1f3707
```

```json
{
  "confidence": 0.6792,
  "content_id": "1d6fec38-573d-4365-abf9-e10c5e1f3707",
  "guess": "ai",
  "label": "We think this was probably generated by AI.",
  "status": "under_review"
}
```

---

## How I Used AI

**Moment 1**

- **What I asked for:** I asked AI to help me design a second stylometric signal using the starter functions for sentence-length spread, type-token ratio, and punctuation density.
- **What came back:** It suggested normalizing the three measures so they all pointed in the same direction, where higher meant more AI-like, and combining them with weights of 50% sentence-length spread, 30% vocabulary repetition, and 20% punctuation density.
- **What I changed:** I implemented the functions in `stylometry.py` and then tested them myself on AI-like, human-like, and borderline writing. The tests showed that the style signal sometimes disagreed strongly with the model signal, so I did not treat it as equally reliable when I later combined the two signals.

**Moment 2**

- **What I asked for:** I asked AI to help reason about how the two signals should be combined after I collected real scores from both of them.
- **What came back:** It recommended a weighted average with 65% weight on the model signal and 35% on the style signal because the model signal separated the clearly AI example more strongly, while the style signal could still act as a second opinion when the two disagreed.
- **What I changed:** I tested that rule against clearly AI, clearly human, formal human, and lightly edited AI text before keeping it. The results exposed weaknesses rather than perfectly separating every case: formal human writing scored `0.6388`, while lightly edited AI scored only `0.3871`. I kept the rule instead of changing it just to make the examples look better because those failures are useful evidence for the next unit.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
