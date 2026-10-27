import json
import tempfile
import unittest
from pathlib import Path
from osint99.core import new_case, add_lead, add_finding, username_candidates, url_details, save_json


class CoreTests(unittest.TestCase):
    def test_case_and_lead(self):
        case = new_case("test")
        add_lead(case, "name", "Example Person")
        self.assertEqual(case["leads"][0]["value"], "Example Person")

    def test_username_candidates_are_unverified(self):
        results = username_candidates("@example_user")
        self.assertGreaterEqual(len(results), 3)
        self.assertTrue(all(x["verified"] is False for x in results))

    def test_reject_invalid_username(self):
        with self.assertRaises(ValueError):
            username_candidates("bad username!")

    def test_url_details(self):
        info = url_details("example.com/path")
        self.assertEqual(info["domain"], "example.com")
        self.assertEqual(info["scheme"], "https")

    def test_finding_and_export(self):
        case = new_case("test")
        add_finding(case, "Public page", "https://example.com", "Example note")
        with tempfile.TemporaryDirectory() as tmp:
            path = save_json(case, str(Path(tmp) / "case.json"))
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(len(data["findings"]), 1)


if __name__ == "__main__":
    unittest.main()
