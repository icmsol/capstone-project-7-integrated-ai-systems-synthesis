# Project 4 Clause-Theme Classifier Inference Package

## Selected Model

- Configuration: Baseline dropout 0.10
- Vocabulary size: 4,417
- Output classes: 10
- Maximum sequence length: 256
- PAD index: 0
- UNK index: 1
- Best validation epoch: 14
- Best validation macro F1: 0.887792

## Selection Discipline

The checkpoint was selected using validation performance before test-set
evaluation. The state dictionary was exported from a controlled reproduction
of Capstone Project 4.

## Intended Project 7 Use

The model may support bounded clause-theme triage, review prioritization,
and reviewer routing.

It may not determine:

- legal meaning;
- enforceability;
- compliance;
- contract acceptability;
- required contractual action;
- a final human decision.

## Domain Limitation

The model was trained on ten CUAD commercial-contract categories. Public-sector
solicitations and contracts can differ materially. Low-confidence,
out-of-domain, or consequential cases must abstain or escalate for qualified
human review.

## Package Files

- selected_clause_classifier.pt
- index_to_token.json
- token_to_index.json
- label_id_to_category.json
- model_config.json
- tokenizer_config.json
- validation_selection_metrics.json
