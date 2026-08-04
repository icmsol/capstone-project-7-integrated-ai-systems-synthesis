# P1-03 — Project 4 Model and Inference Asset Review

## Decision

Project 4 remains a conditional runtime contributor.

The repository contains the processed dataset, locked experiment configuration, tokenizer, training-only vocabulary construction, dataset encoding, model class, evaluation logic, and the code that freezes the best validation checkpoints in CPU memory. It does **not** contain a serialized checkpoint, vocabulary, label map, or standalone inference package.

A one-time Google Colab T4 rerun is required to recreate and export the validation-selected baseline.

## Why the Baseline Checkpoint Will Be Exported

The original protocol selected checkpoints using validation macro F1, with validation loss as the tie-breaker. Validation selected dropout 0.10. Although the untouched test set modestly favored dropout 0.30, selecting the experimental model because of test performance would weaken the original validation-only selection discipline.

## Assets Already Available

- `config/experiment_configuration.json`
- `data/processed/cuad_clause_classification.csv`
- fixed tokenizer regular expression
- `<PAD>` and `<UNK>` token definitions
- training-only vocabulary construction
- ten-category label IDs
- `TransformerModelConfig`
- `TransformerClauseClassifier`
- mask-aware mean-pooling inference
- checkpoint-selection logic
- evaluation and error-analysis evidence

## Missing Runtime Assets

- serialized validation-selected state dictionary
- serialized `index_to_token`
- serialized `token_to_index`
- serialized `label_id_to_category`
- inference-only model configuration
- tokenizer configuration
- package manifest and checksums
- fresh CPU load-and-predict validation

## Planned Export Package

```text
models/project4/
├── selected_clause_classifier.pt
├── index_to_token.json
├── token_to_index.json
├── label_id_to_category.json
├── model_config.json
├── tokenizer_config.json
└── README.md

audit/
└── project4_inference_manifest.json

src/
└── clause_triage.py

tests/
└── test_project4_inference.py
```

## Required Export Validation

1. Run the authoritative Project 4 notebook on a Colab T4.
2. Recreate the deterministic training-only vocabulary.
3. Train both original configurations so the original selection logic remains intact.
4. Export the validation-selected baseline and companion assets.
5. Start a fresh CPU runtime.
6. Load the package without rerunning training.
7. Classify known passages and confirm finite probabilities, valid labels, and stable package metadata.
8. Preserve the domain-shift and human-review warnings.

## Runtime Boundary

The classifier may recommend a clause-review category, priority, or reviewer type. It may not determine legal meaning, enforceability, compliance, acceptance, or contractual action.

## Key Limitations

- CUAD is commercial-contract data, not a public-sector solicitation benchmark.
- Only ten of the original CUAD categories are modeled.
- Long inputs are truncated to 256 tokens.
- High confidence is not legal certainty.
- Low-confidence or out-of-domain passages must abstain or escalate.

## Sources

- https://github.com/icmsol/capstone-project-4-deep-learning-systems
- https://raw.githubusercontent.com/icmsol/capstone-project-4-deep-learning-systems/main/config/experiment_configuration.json
- https://raw.githubusercontent.com/icmsol/capstone-project-4-deep-learning-systems/main/data/processed/cuad_clause_classification.csv
