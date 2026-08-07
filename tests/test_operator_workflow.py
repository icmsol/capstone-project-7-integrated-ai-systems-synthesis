from __future__ import annotations

from pathlib import Path
import json
import tempfile
import unittest

from project7.operator_workflow import (
    OperatorWorkflow,
    OperatorWorkflowError,
    build_evidence_request_set,
    safe_filename,
)


class OperatorWorkflowTests(unittest.TestCase):
    def test_safe_filename_removes_path_and_unsafe_characters(self):
        self.assertEqual(
            safe_filename("../../My RFO #7.pdf"),
            "My_RFO_7.pdf",
        )

    def test_evidence_requests_are_derived_from_prediction_and_passage(self):
        result = build_evidence_request_set(
            case_id="CASE-001",
            predictions=[
                {
                    "passage_id": "P-1",
                    "predicted_category": "Insurance",
                }
            ],
            passages=[
                {
                    "passage_id": "P-1",
                    "text": "Contractor shall maintain required insurance.",
                }
            ],
            source_domain="public_sector",
            consequential_use=True,
        )
        self.assertEqual(len(result["requests"]), 1)
        request = result["requests"][0]
        self.assertIn("Insurance", request["request_text"])
        self.assertIsNone(request["exact_clause_number"])
        self.assertIsNone(request["claimed_title"])
        self.assertTrue(request["consequential_use"])

    def test_evidence_request_fails_when_prediction_has_no_source_passage(self):
        with self.assertRaises(OperatorWorkflowError):
            build_evidence_request_set(
                case_id="CASE-001",
                predictions=[
                    {
                        "passage_id": "MISSING",
                        "predicted_category": "Insurance",
                    }
                ],
                passages=[],
                source_domain="public_sector",
                consequential_use=True,
            )

    def test_case_bundle_round_trip_preserves_checksums_and_stage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            workspace = root / "case"
            workflow = OperatorWorkflow(
                repo_root=repo,
                workspace_root=workspace,
            )
            (workflow.input_dir / "example.json").write_text(
                json.dumps({"a": 1}) + "\n",
                encoding="utf-8",
            )
            workflow._set_stage(
                "intake_validated",
                case_id="CASE-TEST",
                source_file="source/example.pdf",
                source_sha256="abc",
            )

            bundle = root / "case_bundle.zip"
            workflow.export_case_bundle(bundle)

            restored_dir = root / "restored"
            restored = OperatorWorkflow.restore_case_bundle(
                repo_root=repo,
                bundle_path=bundle,
                destination_root=restored_dir,
            )
            self.assertEqual(restored.stage, "intake_validated")
            self.assertEqual(restored.case_id, "CASE-TEST")
            self.assertEqual(
                json.loads(
                    (restored.input_dir / "example.json").read_text(
                        encoding="utf-8"
                    )
                ),
                {"a": 1},
            )

    def test_restore_rejects_nonempty_destination(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            workspace = root / "case"
            workflow = OperatorWorkflow(
                repo_root=repo,
                workspace_root=workspace,
            )
            bundle = root / "case_bundle.zip"
            workflow.export_case_bundle(bundle)

            destination = root / "restored"
            destination.mkdir()
            (destination / "occupied.txt").write_text("x", encoding="utf-8")

            with self.assertRaises(OperatorWorkflowError):
                OperatorWorkflow.restore_case_bundle(
                    repo_root=repo,
                    bundle_path=bundle,
                    destination_root=destination,
                )


if __name__ == "__main__":
    unittest.main()
