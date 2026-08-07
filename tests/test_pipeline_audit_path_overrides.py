"""Acceptance regression tests for operator-supplied audit handoff paths."""

from __future__ import annotations

import inspect
import unittest

from project7.p4_02_pipeline import run_alignment_and_history
from project7.p4_03_pipeline import run_clause_triage
from project7.p4_04_pipeline import run_evidence_workflow
from project7.p4_05_pipeline import run_packet_assembly


class PipelineAuditPathOverrideTests(unittest.TestCase):
    def test_integrated_wrappers_accept_prior_audit_path_override(self):
        for function in [
            run_alignment_and_history,
            run_clause_triage,
            run_evidence_workflow,
            run_packet_assembly,
        ]:
            parameter = inspect.signature(function).parameters.get(
                "prior_audit_path"
            )
            self.assertIsNotNone(parameter, function.__name__)
            self.assertIsNone(parameter.default, function.__name__)


if __name__ == "__main__":
    unittest.main(verbosity=2)
