# Worked examples

Three `IntentSpec` v0.1 instances. Run the validator against them:

```bash
python3 validator/validator.py examples/01-organize-estate.json  # expect PASS (exit 0)
python3 validator/validator.py examples/02-chat-with-hermes.json  # expect PASS (exit 0)
python3 validator/validator.py examples/03-drift-caught.json      # expect FAIL (exit 1)
```

- **01-organize-estate** — adapted from a real request ("sort and organize a
  workspace, triage the best work, refine to DARPA standard before any
  portfolio addition"). Identifying details generalized; the intent structure
  is verbatim. PASSes: constraints explicit, ambiguity disclosed (A1/A2),
  authority at build-report tier, no irreversible moves.
- **02-chat-with-hermes** — an ambiguous request ("can I chat with my agent
  directly?") with the inferences disclosed rather than collapsed: which
  persona, which model (A2), what "directly" means (A3). Ask-tier, because the
  operator's data leaves the machine. PASSes.
- **03-drift-caught** — deliberately bad: "organize my files" compiled into
  publishing to a public repo at log-tier. The validator FAILs it with four
  named drift signatures (invented-requirements, authority-escalation,
  unmarked-irreversible, scope-expansion). The gate is demonstrated, not
  asserted.

`intent_id` is sha256 of the raw utterance, truncated to 16 hex chars.
