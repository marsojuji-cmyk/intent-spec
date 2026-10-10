"""Core path: the validator rejects a missing field and rejects drift."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validator", ROOT / "validator" / "validator.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def _clean():
    return {
        "intent_id": "abc",
        "objective": "organize files",
        "raw": {"utterance": "organize my files"},
        "epistemics": {"objective": "EXPLICIT"},
        "deliverable": "organized files",
        "authority": {"tier": "log"},
        "constraints": {"explicit": [], "inferred": []},
    }


class Structural(unittest.TestCase):
    def test_missing_intent_id_is_an_error(self):
        spec_doc = _clean()
        spec_doc["intent_id"] = ""
        findings = validator.check_structural(spec_doc)
        codes = [f["code"] for f in findings]
        self.assertIn("MISSING_FIELD", codes)
        self.assertTrue(any(f["severity"] == "error" for f in findings))

    def test_clean_spec_has_no_structural_errors(self):
        self.assertEqual(validator.check_structural(_clean()), [])


class Drift(unittest.TestCase):
    def test_clean_spec_has_no_drift(self):
        self.assertEqual(validator.check_drift(_clean()), [])

    def test_worked_example_of_drift_fails(self):
        path = ROOT / "examples" / "03-drift-caught.json"
        spec_doc = json.loads(path.read_text(encoding="utf-8"))
        drift = validator.check_drift(spec_doc)
        codes = " ".join(f["code"] for f in drift)
        self.assertIn("AUTHORITY_ESCALATION", codes)
        structural = validator.check_structural(spec_doc)
        errors = [f for f in structural if f["severity"] == "error"]
        verdict = "FAIL" if (errors or drift) else "PASS"
        self.assertEqual(verdict, "FAIL")


if __name__ == "__main__":
    unittest.main()
