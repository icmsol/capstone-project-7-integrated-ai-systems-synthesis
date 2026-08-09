import csv, json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

class P604ReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "outputs/evaluation/p6_04/reproducibility_manifest.json").read_text())
        cls.env = json.loads((ROOT / "outputs/evaluation/p6_04/environment_and_version_spec.json").read_text())
        cls.sources = read_csv(ROOT / "docs/P6_04_Source_Snapshot_and_Checksum_Inventory.csv")
        cls.replay = read_csv(ROOT / "docs/P6_04_Replay_Matrix.csv")

    def test_candidate_identity_is_preserved(self):
        self.assertEqual(self.manifest["candidate_id"], "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0")

    def test_frozen_seed_and_results(self):
        self.assertEqual(self.manifest["frozen_evaluation"]["deterministic_seed"], 42)
        self.assertEqual(self.manifest["frozen_evaluation"]["cases_passed"], 19)
        self.assertEqual(self.manifest["frozen_evaluation"]["assertions_passed"], 262)
        self.assertEqual(self.manifest["frozen_evaluation"]["regressions"], 0)

    def test_runtime_api_boundary(self):
        self.assertFalse(self.env["api_and_format_versions"]["openai_api_runtime_dependency"])
        self.assertEqual(self.env["api_and_format_versions"]["model_provider_api"], "None in the final Project 7 runtime")

    def test_model_identity(self):
        self.assertEqual(
            self.manifest["project4_model"]["checkpoint_sha256"],
            "50a280950d31466d7002578295c64e957d144611f5b9731bb059be50e68c6c92",
        )

    def test_replay_inventory_is_complete(self):
        self.assertGreaterEqual(len(self.sources), 10)
        self.assertEqual(len(self.replay), 10)

    def test_production_and_external_action_boundaries(self):
        self.assertFalse(self.manifest["governance"]["production_ready"])
        self.assertEqual(self.manifest["external_actions_performed"], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
