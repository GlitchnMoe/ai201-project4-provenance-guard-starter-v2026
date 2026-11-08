#!/usr/bin/env python3
"""
Run your five criteria three times each.  <- UNIT 8, MILESTONE 3

    python app.py                              # in one terminal
    python run_eval.py --label before          # in another
    python run_eval.py --label after

The attack set tests what staff thought to test. This tests what *you* thought
to test, and the two rarely overlap much. Both count.

Fill in `scenarios.py` first — that's where you say what each criterion needs
run against it. A criterion about false positives needs your own writing. One
about label coverage needs inputs across the score range.

!! Three trials, and **your first signal runs a model, so identical input can
score differently twice.** That's exactly why repeats matter here.

This does the sending and the recording. It does not decide whether a trial
passed — that depends on the criterion you wrote, so the Verdict column comes
back blank.
"""

import argparse
import datetime as dt
import json
import sys

import config


# Windows consoles often run a codepage that can't print every character in
# this file's help text. Without this, `--help` ends in a UnicodeEncodeError
# traceback instead of the help.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"


def bodies_for(scenario):
    """
    Return the request bodies for a normal /submit scenario.

    A "texts" scenario gets a creator_id made up for it.

    A "bodies" scenario is sent exactly as written. This lets a bad-input
    criterion test things such as:
      - no text field
      - empty text
      - null text
      - very large text
    """

    if scenario.get("bodies"):
        return list(scenario["bodies"])

    return [
        {
            "text": text,
            "creator_id": f"eval_{scenario['name'][:12]}_{i}",
        }
        for i, text in enumerate(scenario["texts"], 1)
    ]


def describe(body):
    """Return a short readable description of what was sent."""

    if set(body) == {"text", "creator_id"} and isinstance(
        body.get("text"), str
    ):
        text = body["text"]

        if not text:
            return "(empty text)"

        if len(text) > 70:
            return text[:70] + "..."

        return text

    return json.dumps(body)[:120]


def run_submit_trial(requests, base_url, timeout, scenario):
    """
    Run one normal criterion trial through POST /submit.
    """

    results = []

    for body in bodies_for(scenario):
        preview = describe(body)

        try:
            response = requests.post(
                f"{base_url}/submit",
                json=body,
                timeout=timeout,
            )

            try:
                payload = response.json() if response.content else {}
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "status": response.status_code,
                        "error": (
                            f"{type(exc).__name__}: {exc}"
                        ),
                        "sent": preview,
                    }
                )
                continue

            results.append(
                {
                    "status": response.status_code,
                    "guess": payload.get("guess"),
                    "confidence": payload.get("confidence"),
                    "model_score": payload.get("model_score"),
                    "style_score": payload.get("style_score"),
                    "label": payload.get("label"),
                    "sent": preview,
                }
            )

        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "status": None,
                    "error": f"{type(exc).__name__}: {exc}",
                    "sent": preview,
                }
            )

    return results


def run_appeal_trial(
    requests,
    base_url,
    timeout,
    trial_number,
    count,
):
    """
    Run criterion 4.

    For each appeal test:

      1. Create a real submission.
      2. Get its real content_id.
      3. POST an appeal using that content_id.
      4. Check that the appeal response says under_review.
      5. Check /log to make sure the appeal and reasoning were recorded.

    The criterion requires 5 valid appeals to work correctly.
    """

    results = []

    for i in range(1, count + 1):
        creator_id = f"eval_appeal_t{trial_number}_{i}"

        submission_text = (
            "This is a normal piece of writing used to test the appeal path. "
            "The exact classification of this text does not matter for this "
            "criterion. The purpose of the test is to create a valid submission "
            "with a real content ID and then verify that the writer can appeal "
            "the decision successfully."
        )

        reasoning = (
            f"Evaluation appeal trial {trial_number}, case {i}. "
            "I believe this decision should be reviewed."
        )

        result = {
            "case": i,
            "creator_id": creator_id,
            "submit_status": None,
            "content_id": None,
            "appeal_status": None,
            "status": None,
            "reasoning": reasoning,
            "log_recorded": False,
        }

        try:
            # ------------------------------------------------------------
            # Step 1: create a real submission
            # ------------------------------------------------------------
            submit_response = requests.post(
                f"{base_url}/submit",
                json={
                    "text": submission_text,
                    "creator_id": creator_id,
                },
                timeout=timeout,
            )

            result["submit_status"] = submit_response.status_code

            try:
                submit_payload = (
                    submit_response.json()
                    if submit_response.content
                    else {}
                )
            except Exception as exc:  # noqa: BLE001
                result["error"] = (
                    "submit response was not JSON: "
                    f"{type(exc).__name__}: {exc}"
                )
                results.append(result)
                continue

            content_id = submit_payload.get("content_id")
            result["content_id"] = content_id

            if not content_id:
                result["error"] = (
                    "submission did not return a content_id"
                )
                results.append(result)
                continue

            # ------------------------------------------------------------
            # Step 2: appeal that real content_id
            # ------------------------------------------------------------
            appeal_response = requests.post(
                f"{base_url}/appeal",
                json={
                    "content_id": content_id,
                    "reasoning": reasoning,
                },
                timeout=timeout,
            )

            result["appeal_status"] = appeal_response.status_code

            try:
                appeal_payload = (
                    appeal_response.json()
                    if appeal_response.content
                    else {}
                )
            except Exception as exc:  # noqa: BLE001
                result["error"] = (
                    "appeal response was not JSON: "
                    f"{type(exc).__name__}: {exc}"
                )
                results.append(result)
                continue

            result["status"] = appeal_payload.get("status")

            # ------------------------------------------------------------
            # Step 3: confirm it actually appeared in the audit log
            # ------------------------------------------------------------
            log_response = requests.get(
                f"{base_url}/log?limit=500",
                timeout=timeout,
            )

            try:
                log_payload = (
                    log_response.json()
                    if log_response.content
                    else {}
                )
            except Exception as exc:  # noqa: BLE001
                result["error"] = (
                    "log response was not JSON: "
                    f"{type(exc).__name__}: {exc}"
                )
                results.append(result)
                continue

            entries = log_payload.get("entries", [])

            matching_appeal = None

            for entry in entries:
                if (
                    entry.get("content_id") == content_id
                    and entry.get("event") == "appeal"
                    and entry.get("status") == "under_review"
                    and entry.get("reasoning") == reasoning
                ):
                    matching_appeal = entry
                    break

            result["log_recorded"] = matching_appeal is not None

            if matching_appeal is not None:
                result["logged_entry"] = matching_appeal

        except Exception as exc:  # noqa: BLE001
            result["error"] = f"{type(exc).__name__}: {exc}"

        results.append(result)

    return results


def print_submit_trial(trial_number, results):
    """
    Print the short terminal summary for a normal /submit trial.
    """

    guesses = []

    for result in results:
        if result.get("guess"):
            guesses.append(result["guess"])
        elif result.get("status") is not None:
            guesses.append(f"HTTP {result['status']}")
        else:
            guesses.append("ERROR")

    print(
        f"  trial {trial_number}: "
        f"{', '.join(guesses)}"
    )


def print_appeal_trial(trial_number, results):
    """
    Print a short terminal summary for an appeal trial.
    """

    statuses = []

    for result in results:
        passed = (
            result.get("submit_status") == 200
            and result.get("appeal_status") == 200
            and result.get("status") == "under_review"
            and result.get("log_recorded") is True
        )

        statuses.append("PASS" if passed else "FAIL")

    print(
        f"  trial {trial_number}: "
        f"{', '.join(statuses)}"
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--trials",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--label",
        default="",
    )

    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=90.0,
    )

    args = parser.parse_args()

    # ------------------------------------------------------------------
    # requests
    # ------------------------------------------------------------------
    try:
        import requests
    except ImportError:
        print(
            "The `requests` package isn't installed.\n"
            "Run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # scenarios.py
    # ------------------------------------------------------------------
    try:
        import scenarios
    except ImportError:
        print(
            "No scenarios.py found. "
            "Milestone 3 starts by filling it in.",
            file=sys.stderr,
        )
        sys.exit(1)

    problems = scenarios.validate()

    if problems:
        print(
            "scenarios.py has problems:\n",
            file=sys.stderr,
        )

        for problem in problems:
            print(
                f"  - {problem}",
                file=sys.stderr,
            )

        sys.exit(1)

    # ------------------------------------------------------------------
    # Confirm service is running
    # ------------------------------------------------------------------
    try:
        health_response = requests.get(
            f"{args.url}/health",
            timeout=5,
        )

        if health_response.status_code >= 500:
            raise RuntimeError(
                f"/health returned HTTP "
                f"{health_response.status_code}"
            )

    except Exception:  # noqa: BLE001
        print(
            f"Nothing answering at {args.url}. "
            "Start it:  python app.py",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.trials < 3:
        print(
            f"!! {args.trials} trial(s). "
            "The submission asks for three.\n"
        )

    # ------------------------------------------------------------------
    # Run all five criteria
    # ------------------------------------------------------------------
    rows = []

    for scenario in scenarios.SCENARIOS:
        criterion = scenario.get("criterion") or "—"

        print(
            f"\n{scenario['name']}  "
            f"(criterion {criterion})"
        )

        trials = []

        for trial in range(1, args.trials + 1):

            # ----------------------------------------------------------
            # Criterion that tests POST /appeal
            # ----------------------------------------------------------
            if scenario.get("appeals") is not None:
                results = run_appeal_trial(
                    requests=requests,
                    base_url=args.url,
                    timeout=args.timeout,
                    trial_number=trial,
                    count=scenario["appeals"],
                )

                print_appeal_trial(
                    trial,
                    results,
                )

            # ----------------------------------------------------------
            # Normal POST /submit criteria
            # ----------------------------------------------------------
            else:
                results = run_submit_trial(
                    requests=requests,
                    base_url=args.url,
                    timeout=args.timeout,
                    scenario=scenario,
                )

                print_submit_trial(
                    trial,
                    results,
                )

            trials.append(results)

        rows.append(
            {
                "scenario": scenario,
                "trials": trials,
            }
        )

    write_report(
        rows,
        args,
    )


def write_report(rows, args):
    """
    Write the full Milestone 3 evidence into results/.

    The report intentionally leaves Target and Verdict blank.
    We fill those from criteria.md after seeing the actual results.
    """

    config.RESULTS_DIR.mkdir(exist_ok=True)

    stamp = dt.datetime.now().strftime(
        "%Y-%m-%d_%H%M"
    )

    label = (
        f"_{args.label}"
        if args.label
        else ""
    )

    path = (
        config.RESULTS_DIR
        / f"run_{stamp}{label}.md"
    )

    n = args.trials

    headers = " | ".join(
        f"Run {i}"
        for i in range(1, n + 1)
    )

    divider = "|".join(
        ["---"] * n
    )

    lines = [
        (
            f"# Run log"
            f"{f' — {args.label}' if args.label else ''}"
        ),
        "",
        "- Produced by: `run_eval.py::main`",
        (
            "- Service: `app.py::submit` and "
            "`app.py::appeal` · "
            "scoring: `scoring.py::combine_signals`"
        ),
        (
            f"- {n} trials per criterion · "
            f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ),
        "",
        (
            "Fill in Target from `criteria.md`, "
            "and Run and Verdict from the output"
        ),
        (
            "underneath. Whether a trial passed "
            "depends on the criterion you wrote."
        ),
        "",
        (
            f"| Criterion | Target | "
            f"{headers} | Verdict |"
        ),
        f"|---|---|{divider}|---|",
    ]

    # ------------------------------------------------------------------
    # Five-row run log
    # ------------------------------------------------------------------
    for row in rows:
        scenario = row["scenario"]

        number = scenario.get("criterion")

        if number:
            name = (
                f"{number}. "
                f"{scenario['name']}"
            )
        else:
            name = scenario["name"]

        blank_runs = " | ".join(
            [" "] * n
        )

        lines.append(
            f"| {name} |  | "
            f"{blank_runs} |  |"
        )

    # ------------------------------------------------------------------
    # Raw evidence
    # ------------------------------------------------------------------
    lines += [
        "",
        "---",
        "",
        "## What actually came back",
        "",
        (
            "Real output. Paste the relevant parts "
            "into your README — the rubric"
        ),
        (
            "asks for the actual JSON, "
            "not a description of it."
        ),
        "",
    ]

    for row in rows:
        scenario = row["scenario"]

        number = scenario.get("criterion")

        if number:
            heading = (
                f"### Criterion {number} — "
                f"{scenario['name']}"
            )
        else:
            heading = (
                f"### {scenario['name']}"
            )

        lines += [
            heading,
            "",
        ]

        for trial_number, results in enumerate(
            row["trials"],
            1,
        ):
            lines += [
                f"**Trial {trial_number}**",
                "",
                "```json",
                json.dumps(
                    results,
                    indent=2,
                ),
                "```",
                "",
            ]

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        f"\nWrote "
        f"{path.relative_to(config.ROOT)}"
    )

    print(
        "Commit it. It's the evidence "
        "the test actually happened."
    )


if __name__ == "__main__":
    main()