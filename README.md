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

**My limits:** 10 per minute, 200 per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->
I chose 10 submissions per minute because it allows a real writer to submit and retry several pieces of writing without immediately being blocked, while making it harder for an automated script to rapidly probe the detector with many variations. I chose 200 per day because it is much higher than I would expect a normal individual writer to need, while still placing a practical cap on sustained automated testing.


**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

The limiter primarily treats each creator_id as a caller. Requests sharing the same creator_id count against the same limit. If a request does not provide a usable creator_id, the limiter falls back to the request's network address.


**The run of status codes when I pushed past it:**

Produced by: run_attacks.py::run_flood

15 submissions as flood_tester on 2026-11-04. Five requests were rate limited.

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `3352a82f-5085-461d-a753-0dca44f2c53d` | human | 0.305 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `1eaff903-5911-464d-b1c1-1dc7c57b89d8` | unsure | 0.454 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `e7a2d17f-27c4-4ff5-9e14-23bff4c0e032` | unsure | 0.565 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `ce7c24a7-4891-4efb-b81f-e0c05c53cf76` | unsure | 0.588 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `3c7cb757-65ea-4fea-adcf-e274d7d81923` | human | 0.281 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `78da8dbc-c684-4dac-bb71-7638d28ab3a6` | unsure | 0.453 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `590a4bb8-5c14-4c27-b529-1365f5e5a738` | unsure | 0.580 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `f84c46eb-cd56-4003-89e7-847ab06bb5b7` | human | 0.338 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `141d018e-9124-4de6-b962-9a143ab77eed` | unsure | 0.585 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `44f00683-57a8-4928-81fd-a08131351327` | ai | 0.861 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `eb994e78-4363-4807-950e-1044049c8e55` | unsure | 0.561 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `aaa6da88-39bf-410f-af93-b547f70d4fba` | ai | 0.693 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `2101a34c-7877-4405-aeef-c08eaef2b0e2` | ai | 0.721 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `d4825bc0-3561-4084-a5bd-d6d6472a1ec9` | ai | 0.714 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `5440f9e3-6337-42be-9a58-c15ff6677abe` | ai | 0.731 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `7302fff5-0e89-49dc-8219-043691972926` | ai | 0.717 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `4e29ad03-e6d4-4935-b36a-248796728ece` | ai | 0.689 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `51a675f4-30cc-451e-9245-5a1e14485575` | unsure | 0.353 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `f4608ad0-4ff9-40dd-98ec-6330ea07b597` | unsure | 0.398 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `230b9759-9ad3-43d5-9a5f-1fe1056e815a` | human | 0.210 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `d0fdfbda-b4cd-4df8-a991-5a11ee5aed23` | unsure | 0.552 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `8166d69a-e5a0-4770-b9ba-b890fd7b23ca` | unsure | 0.473 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `a3249171-fe3e-406e-8469-31887c37ad2f` | unsure | 0.485 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `41dca23d-df88-48bb-98f9-090eb0ca384f` | unsure | 0.526 | HELD |
| MF01 | malformed | text is only whitespace | 200 | `4cada33a-d3b6-4141-9792-1af3edee6a34` | unsure | 0.483 | BROKE |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `f5b4b8c5-bfb9-4f1c-9df1-6e746d4fdd95` | human | 0.245 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c4fed13d-b663-439e-a159-3c5a9534e9a9` | unsure | 0.357 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `d8418d70-1cb5-4ff3-b33b-a715886efb07` | ai | 0.893 | BROKE |
| MF06 | malformed | text is emoji only | 200 | `fb7dda17-b0b5-4bc4-be24-1aaec8e95d29` | ai | 0.998 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | `6868c507-209d-4fd9-9c37-05065394186a` | ai | 0.939 | BROKE |
| MF08 | malformed | text is 60,000 characters | 200 | `a8af8ec9-587e-461c-b604-8d03374538ad` | ai | 0.882 | BROKE |
| RQ01 | malformed | no text field at all | 500 | `—` | — | — | BROKE |
| RQ02 | malformed | no creator_id | 200 | `aca51415-8f0c-4bee-a8f7-d133aac207a5` | unsure | 0.401 | BROKE |
| RQ03 | malformed | text is a number | 500 | `—` | — | — | BROKE |
| RQ04 | malformed | text is a list | 500 | `—` | — | — | BROKE |
| RQ05 | malformed | text is null | 500 | `—` | — | — | BROKE |
| RQ06 | malformed | creator_id is an object | 200 | `c713f911-3bbd-4064-9fd4-b7808a7c9ace` | human | 0.277 | BROKE |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 500 | `—` | — | — | BROKE |
| RQ09 | malformed | body is empty | 500 | `—` | — | — | BROKE |
| RQ10 | malformed | body is form-encoded, not JSON | 500 | `—` | — | — | BROKE |
| RQ11 | malformed | body is JSON claiming to be plain text | 500 | `—` | — | — | BROKE |
| RQ12 | malformed | deeply nested JSON | 500 | `—` | — | — | BROKE |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `18247df1-73d1-43c0-9fc8-2685d7466279` | human | 0.264 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b2b74a5c-f043-4dd7-ae88-4523d964a83d` | human | 0.264 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4ba0ce7e-aab5-437d-972e-3047566f2655` | human | 0.264 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f9b41eac-6abe-432e-b900-9dcf84966f71` | human | 0.264 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e2e5f085-7190-4a96-859b-803f13c78bbb` | human | 0.264 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `828db235-5776-4616-9c8c-bc9736f35e33` | human | 0.264 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b2be7fcc-ac75-4f94-8f3d-5d339c7485dd` | human | 0.264 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `879093d9-7034-4cde-9f70-ecf267f86438` | human | 0.264 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `072309d1-3626-4eef-b102-7edb89fc766d` | human | 0.264 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e171e1b8-f734-4517-a9a7-870e854f828c` | human | 0.264 | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
[
  {
    "combined_score": 0.3054,
    "content_id": "3352a82f-5085-461d-a753-0dca44f2c53d",
    "creator_id": "attacker_EV01",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.1635,
    "status": "decided",
    "style_score": 0.5689,
    "timestamp": "2026-11-05T00:21:08+00:00"
  },
  {
    "combined_score": 0.2807,
    "content_id": "3c7cb757-65ea-4fea-adcf-e274d7d81923",
    "creator_id": "attacker_EV05",
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.3212,
    "status": "decided",
    "style_score": 0.2054,
    "timestamp": "2026-11-05T00:21:08+00:00"
  },
  {
    "combined_score": 0.8609,
    "content_id": "44f00683-57a8-4928-81fd-a08131351327",
    "creator_id": "attacker_EV10",
    "guess": "ai",
    "label": "We think this was probably generated by AI.",
    "model_score": 0.9792,
    "status": "decided",
    "style_score": 0.6413,
    "timestamp": "2026-11-05T00:21:09+00:00"
  },
  {
    "combined_score": 0.6933,
    "content_id": "aaa6da88-39bf-410f-af93-b547f70d4fba",
    "creator_id": "attacker_FP02",
    "guess": "ai",
    "label": "We think this was probably generated by AI.",
    "model_score": 0.7387,
    "status": "decided",
    "style_score": 0.609,
    "timestamp": "2026-11-05T00:21:09+00:00"
  },
  {
    "combined_score": 0.7208,
    "content_id": "2101a34c-7877-4405-aeef-c08eaef2b0e2",
    "creator_id": "attacker_FP03",
    "guess": "ai",
    "label": "We think this was probably generated by AI.",
    "model_score": 0.8051,
    "status": "decided",
    "style_score": 0.5643,
    "timestamp": "2026-11-05T00:21:09+00:00"
  },
  {
    "combined_score": 0.7309,
    "content_id": "5440f9e3-6337-42be-9a58-c15ff6677abe",
    "creator_id": "attacker_FP05",
    "guess": "ai",
    "label": "We think this was probably generated by AI.",
    "model_score": 0.8005,
    "status": "decided",
    "style_score": 0.6016,
    "timestamp": "2026-11-05T00:21:09+00:00"
  },
  {
    "combined_score": 0.6886,
    "content_id": "4e29ad03-e6d4-4935-b36a-248796728ece",
    "creator_id": "attacker_FP07",
    "guess": "ai",
    "label": "We think this was probably generated by AI.",
    "model_score": 0.8816,
    "status": "decided",
    "style_score": 0.3303,
    "timestamp": "2026-11-05T00:21:09+00:00"
  },
  {
    "combined_score": 0.4846,
    "content_id": "a3249171-fe3e-406e-8469-31887c37ad2f",
    "creator_id": "attacker_PI05",
    "guess": "unsure",
    "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
    "model_score": 0.6401,
    "status": "decided",
    "style_score": 0.1957,
    "timestamp": "2026-11-05T00:21:10+00:00"
  },
  {
    "combined_score": 0.998,
    "content_id": "fb7dda17-b0b5-4bc4-be24-1aaec8e95d29",
    "creator_id": "attacker_MF06",
    "guess": "ai",
    "label": "We think this was probably generated by AI.",
    "model_score": 0.9969,
    "status": "decided",
    "style_score": 1.0,
    "timestamp": "2026-11-05T00:21:10+00:00"
  },
  {
    "creator_id": "attacker_flood",
    "event": "rejected",
    "limit": "10 per 1 minute",
    "reason": "rate_limited",
    "status": "rejected",
    "timestamp": "2026-11-05T00:21:12+00:00"
  }
]
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

FP03 was genuine writing from a non-native English speaker writing carefully, but the system labeled it AI with a combined score of 0.7208. The model signal was 0.8051 and the style signal was 0.5643. This is the outcome I would least want to explain to a real writer because the system confidently accused genuine human writing of being AI-generated.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives | No more than 1 of 10 human-written samples labeled high-confidence AI | 4/10 flagged AI | 4/10 flagged AI | 4/10 flagged AI | MISSED |
| 2. Score spread | AI average combined score at least 0.30 higher than human average | -0.1695 gap | -0.1695 gap | -0.1695 gap | MISSED |
| 3. Label coverage | All 3 labels must be produced at least once | 2/3 labels | 2/3 labels | 2/3 labels | MISSED |
| 4. Appeal path | 5 of 5 valid appeals change to `under_review` and are logged | 5/5 | 5/5 | 5/5 | MET |
| 5. Bad input | 3 of 3 invalid requests cleanly rejected with a 4xx response | 0/3 | 0/3 | 0/3 | MISSED |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

File: `results/run_2026-11-08_1535_before.md`  
Produced by: `run_eval.py::main`

```json
{
  "criterion_1_false_positives": {
    "trial": 1,
    "results": [
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.6087,
        "model_score": 0.6349,
        "style_score": 0.5601
      },
      {
        "status": 200,
        "guess": "ai",
        "confidence": 0.6843,
        "model_score": 0.6634,
        "style_score": 0.7232
      },
      {
        "status": 200,
        "guess": "ai",
        "confidence": 0.6729,
        "model_score": 0.725,
        "style_score": 0.5761
      },
      {
        "status": 200,
        "guess": "ai",
        "confidence": 0.7103,
        "model_score": 0.7069,
        "style_score": 0.7167
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.3987,
        "model_score": 0.3345,
        "style_score": 0.5178
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.5424,
        "model_score": 0.4715,
        "style_score": 0.6742
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.6378,
        "model_score": 0.6352,
        "style_score": 0.6425
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.6033,
        "model_score": 0.6684,
        "style_score": 0.4825
      },
      {
        "status": 200,
        "guess": "ai",
        "confidence": 0.7825,
        "model_score": 0.8498,
        "style_score": 0.6575
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.3613,
        "model_score": 0.2914,
        "style_score": 0.4911
      }
    ]
  },

  "criterion_2_score_spread": {
    "trial": 1,
    "human_average": 0.61498,
    "ai_average": 0.44544,
    "ai_minus_human_gap": -0.16954,
    "target_gap": 0.30,
    "result": "MISSED"
  },

  "criterion_3_label_coverage": {
    "trial": 1,
    "results": [
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.6153,
        "model_score": 0.6657,
        "style_score": 0.5216
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.491,
        "model_score": 0.6794,
        "style_score": 0.1411
      },
      {
        "status": 200,
        "guess": "ai",
        "confidence": 0.8052,
        "model_score": 0.8446,
        "style_score": 0.7321
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.6378,
        "model_score": 0.7652,
        "style_score": 0.4012
      },
      {
        "status": 200,
        "guess": "unsure",
        "confidence": 0.4894,
        "model_score": 0.4622,
        "style_score": 0.54
      }
    ],
    "labels_reached": [
      "unsure",
      "ai"
    ],
    "labels_reached_count": "2/3"
  },

  "criterion_4_appeal_path": {
    "trial": 1,
    "results": [
      {
        "case": 1,
        "submit_status": 200,
        "appeal_status": 200,
        "status": "under_review",
        "log_recorded": true
      },
      {
        "case": 2,
        "submit_status": 200,
        "appeal_status": 200,
        "status": "under_review",
        "log_recorded": true
      },
      {
        "case": 3,
        "submit_status": 200,
        "appeal_status": 200,
        "status": "under_review",
        "log_recorded": true
      },
      {
        "case": 4,
        "submit_status": 200,
        "appeal_status": 200,
        "status": "under_review",
        "log_recorded": true
      },
      {
        "case": 5,
        "submit_status": 200,
        "appeal_status": 200,
        "status": "under_review",
        "log_recorded": true
      }
    ]
  },

  "criterion_5_bad_input": {
    "trial": 1,
    "results": [
      {
        "status": 500,
        "error": "JSONDecodeError: Expecting value: line 1 column 1 (char 0)",
        "sent": "{\"creator_id\": \"eval_bad_missing\"}"
      },
      {
        "status": 500,
        "error": "JSONDecodeError: Expecting value: line 1 column 1 (char 0)",
        "sent": "(empty text)"
      },
      {
        "status": 200,
        "guess": "ai",
        "confidence": 0.9984,
        "model_score": 0.9975,
        "style_score": 1.0,
        "sent": "word word word word word word word word word word word word word word ..."
      }
    ]
  }
}
```

**Diagnoses**

### Criterion 1 — False positives: MISSED

My target allowed no more than 1 of 10 human-written samples to be labeled high-confidence AI. All three trials labeled 4 of 10 as AI, so the target was missed in every trial.

**Stage: signal one, signal two, and the combining rule. Mechanism:** The falsely flagged human writing received high scores before the label was assigned. The four false positives had combined scores of `0.6843`, `0.6729`, `0.7103`, and `0.7825`. Their model scores were especially high, and several also had high style scores. Polished, structured, and predictable human writing looks AI-like to the properties my signals measure. Because signal one receives 65% of the combined score, those high model scores often push genuine human writing above the `0.65` AI threshold.

### Criterion 2 — Score spread: MISSED

My target required the AI-written group to average at least `0.30` higher than the human-written group. Instead, the human group averaged `0.61498` and the AI group averaged `0.44544`, giving a gap of `-0.16954` in every trial. The groups were separated in the opposite direction from the target.

**Stage: signal one, signal two, and the combining rule. Mechanism:** Both signals measure indirect characteristics such as predictability, sentence structure, vocabulary variety, and punctuation rather than actual authorship. In this test, the human examples happened to look more predictable and regular than the AI examples. The combining rule then preserved those incorrect signal relationships instead of producing the expected separation.

### Criterion 3 — Label coverage: MISSED

My target required all three labels to appear at least once. Every trial produced only `unsure` and `ai`, so only 2 of the 3 labels were reached.

**Stage: combining rule and label mapping. Mechanism:** The human label requires a combined score of `0.35` or lower, but the lowest score in the label-coverage test was `0.4894`. None of the tested inputs therefore crossed the human threshold, so the label mapping could only return `unsure` or `ai`.

### Criterion 4 — Appeal path: MET

The target required all 5 valid appeals to change the submission status to `under_review` and be recorded in the audit log. All three trials were `5/5`, and every appeal showed `under_review` with a corresponding logged appeal, so this criterion was met.

### Criterion 5 — Bad input: MISSED

After revising the criterion so it could be measured objectively, all three invalid requests returned `500` in every trial, giving `0/3`, `0/3`, and `0/3`. None were cleanly rejected with a `4xx` response.

**Stage: route. Mechanism:** `POST /submit` does not validate `text` before passing it into the detector. Missing, empty, and `null` text therefore reach downstream code that assumes usable text is present. Those failures are not converted into controlled client-error responses, so Flask returns `500` instead.

### Broken attack diagnoses

#### Evasion attacks — EV01 through EV09

Nine of the ten evasion attacks broke the detector. `EV10` held, so it does not need a failure diagnosis.

**EV01, EV04, and EV08 — Stage: signal one and combining rule. Mechanism:** These attacks changed characteristics that the model signal relies on. Typos, unusual vocabulary, or too little text lowered the model score even though the text was AI-generated. Because the model receives 65% of the final weight, the low model score pulled the combined result toward `human` or `unsure`.

**EV02, EV03, and EV06 — Stage: signal two and combining rule. Mechanism:** These attacks changed sentence shape or inserted material that altered the stylometric measurements. Broken-up sentences, quotations, and extreme sentence-length variation lowered the style score and pulled otherwise suspicious text into the `unsure` range.

**EV07 — Stage: signal one and signal two. Mechanism:** Padding the text with punctuation changed the surface form enough that neither signal produced a strong AI score. The combined result was therefore only `0.5798`, which mapped to `unsure`.

**EV05 — Stage: signal one and signal two. Mechanism:** Heavy human editing changed both predictability and surface-level writing style. The model score fell to `0.3212` and the style score to `0.2054`, producing a combined score of `0.2807` and a human label.

**EV09 — Stage: signal two and combining rule. Mechanism:** Adding a human-written opening paragraph lowered the style score to `0.3622`. Although signal one still scored the text `0.7042`, the disagreement lowered the combined result to `0.5845`, which mapped to `unsure`.

**Pattern:** The evasion failures show that authorship is not what either signal directly measures. Editing sentence structure, vocabulary, punctuation, or adding human-written text can change the measured properties enough to move AI text out of the AI range.

#### False-positive attacks — FP02 through FP07

Six of the eight false-positive attacks broke the system. `FP01` and `FP08` held.

**Stage: signal one, with signal two and the combining rule contributing in some cases. Mechanism:** Formal, technical, careful, rubric-driven, or deliberately repetitive human writing is predictable enough that signal one often treats it as AI-like. `FP02` through `FP07` all crossed the high-confidence AI threshold even though they were genuine human writing.

The strongest pattern is visible in the model signal. For example, `FP03` had a model score of `0.8051`, `FP04` scored `0.8329`, `FP05` scored `0.8005`, `FP06` scored `0.8814`, and `FP07` scored `0.8816`. Because the model receives 65% of the combined score, even a more human-looking style score is sometimes unable to pull the final result below the AI threshold.

**Pattern:** Signal one treats predictable human prose as evidence of AI authorship even though predictability is not the same thing as authorship. The combining rule gives that signal enough weight to produce confident false accusations.

#### Malformed attacks — MF01 through MF08 and RQ01 through RQ12

All 20 malformed attacks broke the system.

**Stage: route. Mechanism:** `/submit` does not have sufficient input validation before the request reaches the detector and scoring pipeline.

The following malformed inputs were accepted as normal `200` submissions instead of being rejected:

`MF01`, `MF03`, `MF04`, `MF05`, `MF06`, `MF07`, `MF08`, `RQ02`, and `RQ06`.

These include whitespace-only text, control characters, punctuation-only text, an extremely long word, emoji-only text, right-to-left text, a 60,000-character input, a missing `creator_id`, and an object used as `creator_id`. The route does not enforce usable text, valid field types, or reasonable input limits before scoring.

The following malformed inputs crashed with `500` instead of receiving a controlled client-error response:

`MF02`, `RQ01`, `RQ03`, `RQ04`, `RQ05`, `RQ07`, `RQ08`, `RQ09`, `RQ10`, `RQ11`, and `RQ12`.

These include text that is too short, missing, numeric, a list, `null`, a JSON array instead of an object, malformed JSON, an empty body, form data, incorrect content types, and deeply nested input. The route lets invalid data reach code that assumes the expected schema or usable text. When that downstream code raises an exception, the error becomes a `500` rather than a controlled `4xx`.

**Pattern:** These are not 20 unrelated bugs. They are one major route-validation problem: invalid requests are not rejected before reaching the detection pipeline.

### Overall pattern

The failures mostly reduce to two root problems.

First, the detector's signals measure indirect properties of text instead of authorship. Predictable and structured human writing can look AI-like, while edited or stylistically unusual AI writing can look human-like. The 65% weight on signal one amplifies several of those errors.

Second, `/submit` lacks strong request validation. That explains all 20 malformed attacks and Criterion 5: some invalid inputs are scored as if they were valid, while others crash the service.

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
