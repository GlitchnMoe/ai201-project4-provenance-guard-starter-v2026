# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-08 16:03
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `019c43b2-5b55-4f91-b618-3df4c04d3ab6` | human | 0.305 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `ef2eddd2-1978-4041-b744-42caa559bb17` | unsure | 0.454 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `e4dfa226-a562-4c82-9c40-fe1272f3cac7` | unsure | 0.565 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `fde04ce6-c84a-48a2-a057-063d65cd9c5a` | unsure | 0.588 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `592ed58a-3e70-4d20-9edf-29751dd81fa1` | human | 0.281 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `4cf41f3e-9bb8-4183-b7d2-dc0af8685fb6` | unsure | 0.453 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `70baa765-f7a0-496f-84a2-3ac2dc1a0a22` | unsure | 0.580 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `67aaa168-5802-483b-be6b-9da51f73fd22` | human | 0.338 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `bd67d57c-58f7-48a5-9278-9f579abb97ff` | unsure | 0.585 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `bc4f4018-bc9e-4a35-a262-a0a3ec77b781` | ai | 0.861 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `ac2c3b6b-9b67-490c-876e-b224aafca935` | unsure | 0.561 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `13017817-fae4-4a58-8fb1-67040399f9b5` | ai | 0.693 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `1d5dc14a-1aab-4be1-ae0a-0831d5c20510` | ai | 0.721 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `5d0ed623-f36f-45b4-a985-00b1a849eb59` | ai | 0.714 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `35ecc780-d10c-4a12-ad92-5e3b8d21791b` | ai | 0.731 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `35eec6e9-6c64-4a70-ae8d-da5e1fd5b771` | ai | 0.717 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `293dad88-ef59-40a3-bf86-54b37cdb53f8` | ai | 0.689 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `3987b2cd-4015-4739-8159-c7680140fbf2` | unsure | 0.353 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `68781ae0-f216-4dc5-8b74-394273986a61` | unsure | 0.398 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `ba4a3690-0272-46b8-881d-0e429d3abffc` | human | 0.210 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `d0396723-8d63-4012-b5cd-78feb2c60664` | unsure | 0.552 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `cb53b0e1-32b8-4589-85e1-d5b1cf487011` | unsure | 0.473 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `fc1652ce-14ec-458f-affe-3bd4f2224e5c` | unsure | 0.485 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `706b929e-cd9e-4670-aa9c-dc49c3f04ffd` | unsure | 0.526 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 400 | `—` | — | — |  |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — |  |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 400 | `—` | — | — |  |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d73778fa-f16d-4ebe-83ed-60225b48fa2a` | human | 0.264 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `bb2a99d8-8358-4d1f-a9a6-6a50e85799e4` | human | 0.264 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a67fb14b-138d-4cc6-92dd-4ac5db74ae7d` | human | 0.264 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `3edbf705-af8b-4444-9a12-ed4a81245e29` | human | 0.264 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `659f3b7c-18c8-4656-8b44-7ebfe2c25536` | human | 0.264 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `95b8c2b1-f42c-43bc-a001-d2e47befc17d` | human | 0.264 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `1bd6e22c-e531-4f50-a99e-beee8d1616d6` | human | 0.264 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4d10b0fc-063b-4828-ad56-241d80532823` | human | 0.264 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b0b482a4-edbe-461d-8e32-613e3c361b35` | human | 0.264 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `fad2b476-5831-4ac0-afda-94bf532f44b3` | human | 0.264 |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "019c43b2-5b55-4f91-b618-3df4c04d3ab6",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.3054,
  "model_score": 0.1635,
  "style_score": 0.5689,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "ef2eddd2-1978-4041-b744-42caa559bb17",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.4542,
  "model_score": 0.5943,
  "style_score": 0.1941,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "e4dfa226-a562-4c82-9c40-fe1272f3cac7",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.565,
  "model_score": 0.6662,
  "style_score": 0.3771,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "fde04ce6-c84a-48a2-a057-063d65cd9c5a",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5881,
  "model_score": 0.6114,
  "style_score": 0.5449,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "592ed58a-3e70-4d20-9edf-29751dd81fa1",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.2807,
  "model_score": 0.3212,
  "style_score": 0.2054,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "4cf41f3e-9bb8-4183-b7d2-dc0af8685fb6",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.4533,
  "model_score": 0.5727,
  "style_score": 0.2315,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "70baa765-f7a0-496f-84a2-3ac2dc1a0a22",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5798,
  "model_score": 0.5862,
  "style_score": 0.568,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "67aaa168-5802-483b-be6b-9da51f73fd22",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.3384,
  "model_score": 0.2452,
  "style_score": 0.5115,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "bd67d57c-58f7-48a5-9278-9f579abb97ff",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5845,
  "model_score": 0.7042,
  "style_score": 0.3622,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "bc4f4018-bc9e-4a35-a262-a0a3ec77b781",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8609,
  "model_score": 0.9792,
  "style_score": 0.6413,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "ac2c3b6b-9b67-490c-876e-b224aafca935",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5612,
  "model_score": 0.6175,
  "style_score": 0.4565,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "13017817-fae4-4a58-8fb1-67040399f9b5",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.6933,
  "model_score": 0.7387,
  "style_score": 0.609,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "1d5dc14a-1aab-4be1-ae0a-0831d5c20510",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.7208,
  "model_score": 0.8051,
  "style_score": 0.5643,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "5d0ed623-f36f-45b4-a985-00b1a849eb59",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.714,
  "model_score": 0.8329,
  "style_score": 0.4933,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "35ecc780-d10c-4a12-ad92-5e3b8d21791b",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7309,
  "model_score": 0.8005,
  "style_score": 0.6016,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "35eec6e9-6c64-4a70-ae8d-da5e1fd5b771",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.7174,
  "model_score": 0.8814,
  "style_score": 0.4127,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "293dad88-ef59-40a3-bf86-54b37cdb53f8",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.6886,
  "model_score": 0.8816,
  "style_score": 0.3303,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "3987b2cd-4015-4739-8159-c7680140fbf2",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.3534,
  "model_score": 0.3223,
  "style_score": 0.4113,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "68781ae0-f216-4dc5-8b74-394273986a61",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.398,
  "model_score": 0.4625,
  "style_score": 0.2782,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "ba4a3690-0272-46b8-881d-0e429d3abffc",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2097,
  "model_score": 0.2044,
  "style_score": 0.2196,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "d0396723-8d63-4012-b5cd-78feb2c60664",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5523,
  "model_score": 0.5943,
  "style_score": 0.4743,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "cb53b0e1-32b8-4589-85e1-d5b1cf487011",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4734,
  "model_score": 0.4998,
  "style_score": 0.4245,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "fc1652ce-14ec-458f-affe-3bd4f2224e5c",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4846,
  "model_score": 0.6401,
  "style_score": 0.1957,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "706b929e-cd9e-4670-aa9c-dc49c3f04ffd",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5264,
  "model_score": 0.5583,
  "style_score": 0.4671,
  "label": "We cannot confidently tell whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF07",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "d73778fa-f16d-4ebe-83ed-60225b48fa2a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "bb2a99d8-8358-4d1f-a9a6-6a50e85799e4",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "a67fb14b-138d-4cc6-92dd-4ac5db74ae7d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "3edbf705-af8b-4444-9a12-ed4a81245e29",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "659f3b7c-18c8-4656-8b44-7ebfe2c25536",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "95b8c2b1-f42c-43bc-a001-d2e47befc17d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "1bd6e22c-e531-4f50-a99e-beee8d1616d6",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "4d10b0fc-063b-4828-ad56-241d80532823",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "b0b482a4-edbe-461d-8e32-613e3c361b35",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "fad2b476-5831-4ac0-afda-94bf532f44b3",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2637,
  "model_score": 0.0287,
  "style_score": 0.7,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
