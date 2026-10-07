# IntentSpec v0.1

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) [![Validator](https://img.shields.io/badge/validator-3%20examples-brightgreen)](validator/)

A canonical intermediate representation that compiles raw operator intent into
existing agent machinery — without becoming a second router.

**The one law:** the Intent Compiler does not re-decide anything the estate
already decides. It has exactly one output of consequence: a typed
`IntentSpec` that compiles *to* the machinery already running — router,
authority tiers, review lanes, handoff record, receipt. Compile to the
router. Never become a router.

## Status — read this first

- **Designed:** the IR schema, the six compilation passes, the intent-diff
  gate, the validator, the adversarial review.
- **Exercised:** three worked examples in `examples/` — two pass, one
  deliberately fails with four named drift signatures.
- **Not done:** no live-estate binding yet. The milestone that promotes this
  from document to artifact is an estate intake rule — *no spec, no route* —
  which is not built here. Nothing in this repo has run in production.

## Quickstart

```bash
python3 validator/validator.py examples/01-organize-estate.json  # PASS (exit 0)
python3 validator/validator.py examples/02-chat-with-hermes.json  # PASS (exit 0)
python3 validator/validator.py examples/03-drift-caught.json      # FAIL (exit 1)
```

The validator runs two layers: structural checks (required fields, the
epistemics/ambiguity/authority vocabularies, disclosure of inferences) and a
heuristic intent-diff gate — invented-requirements, authority-escalation,
unmarked-irreversible, constraint-loss, scope-expansion, assumption-promotion.
Drift findings are keyword heuristics, labeled as such; a human reads the
diff before any consequential execution. Dependency-free Python 3.

## Contents

- `SPEC.md` — the full specification, headed by the Heilmeier catechism
  (8 questions: what, why now, risks first, cost/clock, milestones with kill
  lines, falsifier)
- `intent_spec.schema.json` — the IR schema (JSON Schema draft-07)
- `validator/validator.py` — structural checks + the intent-diff gate
- `examples/` — three worked `IntentSpec` instances with a provenance note
- `ADVERSARIAL-REVIEW.md` — the spec's own four council questions, answered
  as kill-attempts, with the two fixes they forced

## Revision history

- **Corrected during build:** the drift gate's first run false-flagged
  paraphrase ("sorted" vs "sort") as invented requirements. Fixed with
  stem-tolerant grounding rather than weakening the check.
- **Corrected after adversarial review:** the "superset of handoff" claim
  failed field-by-field on the id — `intent_id` (content-addressed on the
  utterance) and the handoff id (ledger sequence) are different truths.
  Fixed with an optional `receipt.handoff_id` and an explicit one-join
  mapping rule. The advisory-only routing rule and the no-scores rule
  (`route.reason` is a string justification, never a number) were written
  into the schema.

Corrections are the credential: what changed is recorded here, not hidden.

## License

MIT — see `LICENSE`.

---

## Verify it yourself

```bash
python3 scripts/check_claims.py
```

The same command this repository's CI runs on every push. If it does not pass on a clean clone,
the CI badge is wrong and so is this README — please open an issue.

Every claim in this README is meant to be checkable by someone who does not trust it yet.
