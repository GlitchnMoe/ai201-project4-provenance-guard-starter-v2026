
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import app as service
import operational_logging


class CapstoneLoggingTests(unittest.TestCase):

    def setUp(self):
        # Use a temporary log file so tests do not modify real evidence.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.log_path = Path(self.temp_dir.name) / "operations.jsonl"
        log_patch = patch.object(
            operational_logging, "LOG_PATH", self.log_path
        )
        log_patch.start()
        self.addCleanup(log_patch.stop)

        self.client = service.app.test_client()

    def check_log(self, response, expected_status, expected_path):
        """Verify the response and exactly one structured log entry."""
        self.assertEqual(response.status_code, expected_status)
        self.assertTrue(self.log_path.exists())

        lines = self.log_path.read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(len(lines), 1)

        entry = json.loads(lines[0])
        request_id = response.headers.get("X-Request-ID")

        self.assertIsNotNone(request_id)
        self.assertRegex(request_id, r"^[0-9a-f]{32}$")
        self.assertEqual(entry.get("request_id"), request_id)

        required = {
            "timestamp", "method", "path", "input",
            "output", "status_code", "duration_ms", "error"
        }

        self.assertTrue(required.issubset(entry.keys()))
        self.assertEqual(entry["status_code"], expected_status)
        self.assertEqual(entry["path"], expected_path)
        self.assertGreaterEqual(entry["duration_ms"], 0)

        if expected_status >= 400:
            self.assertIsNotNone(entry["error"])
        else:
            self.assertIsNone(entry["error"])

        return entry
    def test_request_ids_are_unique(self):
        """Verify separate requests receive different correlation IDs."""

        first = self.client.post(
            "/ping",
            json={"message": "first"}
        )

        second = self.client.post(
            "/ping",
            json={"message": "second"}
        )

        first_id = first.headers.get("X-Request-ID")
        second_id = second.headers.get("X-Request-ID")

        self.assertIsNotNone(first_id)
        self.assertIsNotNone(second_id)
        self.assertNotEqual(first_id, second_id)

        lines = self.log_path.read_text(
            encoding="utf-8"
        ).splitlines()

        self.assertEqual(len(lines), 2)

        entries = [json.loads(line) for line in lines]

        self.assertEqual(entries[0]["request_id"], first_id)
        self.assertEqual(entries[1]["request_id"], second_id)


    def test_ping_still_works(self):
        response = self.client.post(
            "/ping", json={"message": "capstone test"}
        )
        self.assertEqual(
            response.get_json()["you_sent"], "capstone test"
        )
        self.check_log(response, 200, "/ping")

    def test_health_still_works(self):
        response = self.client.get("/health")
        self.assertTrue(response.get_json()["ok"])
        self.check_log(response, 200, "/health")

    def test_valid_submission(self):
        # Mock only the model signals, preserving Flask and scoring.
        with patch(
            "app.detector.model_signal", return_value=0.2
        ), patch(
            "app.stylometry.style_signal", return_value=0.3
        ), patch("app.audit.log_decision"):

            response = self.client.post(
                "/submit",
                json={
                    "creator_id": str(uuid.uuid4()),
                    "text": (
                        "This is a sample paragraph written to verify "
                        "that the existing submission pipeline works."
                    ),
                },
            )

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("content_id", data)
        self.assertIn("guess", data)
        self.assertIn("confidence", data)

        entry = self.check_log(response, 200, "/submit")
        self.assertIn("text_length", entry["input"])
        self.assertIn("guess", entry["output"])
        self.assertNotIn(
            "This is a sample paragraph",
            self.log_path.read_text(encoding="utf-8")
        )

    def test_invalid_submission(self):
        with patch("app.detector.model_signal") as model:
            response = self.client.post(
                "/submit",
                json={
                    "creator_id": str(uuid.uuid4()),
                    "text": "",
                },
            )
            model.assert_not_called()

        self.assertEqual(
            response.get_json()["error"], "empty_text"
        )
        self.check_log(response, 400, "/submit")

    def test_invalid_appeal(self):
        response = self.client.post("/appeal", json={})
        self.assertEqual(
            response.get_json()["error"], "missing_fields"
        )
        self.check_log(response, 400, "/appeal")

    def test_missing_content(self):
        response = self.client.get(
            "/content/capstone-nonexistent-id"
        )
        self.assertEqual(
            response.get_json()["error"], "not_found"
        )
        self.check_log(
            response, 404, "/content/capstone-nonexistent-id"
        )

    def test_unhandled_exception_is_logged(self):
        # Intentionally inject a failure; the model is not loaded.
        with patch.dict(
            service.app.config,
            {"PROPAGATE_EXCEPTIONS": False}
        ):
            with patch(
                "app.detector.model_signal",
                side_effect=RuntimeError("Injected test failure")
            ):
                # Capture the expected Flask error output.
                with self.assertLogs(
                    service.app.logger, level="ERROR"
                ):
                    response = self.client.post(
                        "/submit",
                        json={
                            "creator_id": str(uuid.uuid4()),
                            "text": (
                                "A normal paragraph used to test "
                                "unexpected detector failures."
                            ),
                        },
                    )

        self.check_log(response, 500, "/submit")


if __name__ == "__main__":
    unittest.main(verbosity=2)
