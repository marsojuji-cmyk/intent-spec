#!/usr/bin/env python3
"""IntentSpec v0.1 validator — structural checks + the intent-diff gate.

Two layers:
  1. STRUCTURAL — required fields, vocabulary (epistemics, ambiguity classes,
     authority tiers), disclosure of inferences.
  2. DRIFT (heuristic) — the intent-diff gate: raw <-> IntentSpec <-> lane brief.
     Keyword heuristics catch the *shape* of drift; they do not understand
     meaning. Every drift finding is labeled HEURISTIC. A human still reads
     the diff. A heuristic that never fires on real drift is decorative and
     should be deleted (the spec's own falsifier applies to this script).

Usage: validator.py <spec.json>  -> prints a JSON report; exit 0 PASS, 1 FAIL.
"""

import json
import re
import sys

EPISTEMICS = {"EXPLICIT", "INFERRED", "ASSUMED", "UNKNOWN"}
AMBIGUITY = {"A0", "A1", "A2", "A3", "A4"}
TIERS = {"log", "build-report", "ask"}

IRREVERSIBLE_VERBS = {
    "publish", "published", "publishing", "delete", "deleted", "deleting",
    "send", "sent", "sending", "deploy", "deployed", "merge", "merged",
    "spend", "spent", "buy", "bought", "post", "posted", "ship", "shipped",
    "launch", "launched",
}
CONSTRAINT_HINTS = {
    "don't", "do not", "never", "only", "must not", "cannot", "can't",
    "read-only", "readonly", "without", "no ", "not ",
}
ROLLBACK_HINTS = {"rollback", "revert", "undo", "kill", "reverse", "restore"}

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
    "it", "is", "are", "be", "as", "at", "by", "my", "me", "you", "your",
    "we", "our", "that", "this", "these", "those", "from", "into", "all",
    "then", "than", "so", "but", "if", "when", "while", "do", "does",
}


def words(text):
    out = []
    for w in re.findall(r"[a-z0-9']+", (text or "").lower()):
        if w.endswith("'s"):
            w = w[:-2]
        if w not in STOPWORDS and len(w) > 2:
            out.append(w)
    return out


def grounded(word, raw_words):
    """Stem-tolerant grounding: exact match, or shared stem (min 4 chars).

    HEURISTIC. Paraphrase ('sorted' for 'sort') is not invention; a word with
    no stem-overlap to the raw utterance is ungrounded. False positives and
    false negatives both possible — the human reads the diff."""
    if word in raw_words:
        return True
    return any(
        len(word) >= 4 and len(r) >= 4 and (word.startswith(r) or r.startswith(word))
        for r in raw_words
    )


def new_finding(layer, code, message, severity="drift"):
    return {"layer": layer, "code": code, "severity": severity, "message": message}


def check_structural(spec):
    findings = []
    for field in ("intent_id", "objective"):
        if not spec.get(field):
            findings.append(new_finding("structural", "MISSING_FIELD",
                                        f"required field '{field}' is missing or empty", "error"))
    raw = spec.get("raw") or {}
    if not raw.get("utterance"):
        findings.append(new_finding("structural", "MISSING_FIELD",
                                    "required field 'raw.utterance' is missing or empty", "error"))
    for name, status in (spec.get("epistemics") or {}).items():
        if status not in EPISTEMICS:
            findings.append(new_finding("structural", "BAD_EPISTEMIC",
                                        f"epistemics['{name}'] = '{status}' not in {sorted(EPISTEMICS)}", "error"))
    for key in ("unknowns", "ambiguities"):
        for item in spec.get(key) or []:
            cls = item.get("ambiguity_class")
            if cls not in AMBIGUITY:
                findings.append(new_finding("structural", "BAD_AMBIGUITY_CLASS",
                                            f"{key} item '{item.get('id')}' class '{cls}' not in {sorted(AMBIGUITY)}", "error"))
    tier = (spec.get("authority") or {}).get("tier")
    if tier is not None and tier not in TIERS:
        findings.append(new_finding("structural", "BAD_TIER",
                                    f"authority.tier '{tier}' not in {sorted(TIERS)}", "error"))
    # Disclosure: inferred constraints must be labeled in epistemics, never silent.
    if (spec.get("constraints") or {}).get("inferred"):
        label = (spec.get("epistemics") or {}).get("constraints")
        if label not in ("INFERRED", "ASSUMED"):
            findings.append(new_finding("structural", "UNDISCLOSED_INFERENCE",
                                        "constraints.inferred is non-empty but epistemics['constraints'] "
                                        f"is '{label}' — inferences must be disclosed, never collapsed", "error"))
    return findings


def check_drift(spec):
    """HEURISTIC intent-diff gate. Keyword overlap is a shape check, not meaning."""
    findings = []
    raw_text = ((spec.get("raw") or {}).get("utterance") or "")
    raw_words = set(words(raw_text))
    spec_text_fields = {
        "objective": spec.get("objective") or "",
        "deliverable": spec.get("deliverable") or "",
        "desired_state": spec.get("desired_state") or "",
        "success_conditions": " ".join(spec.get("success_conditions") or []),
        "failure_conditions": " ".join(spec.get("failure_conditions") or []),
        "scope.in": " ".join((spec.get("scope") or {}).get("in") or []),
    }
    blob = " ".join(spec_text_fields.values())
    blob_words = set(words(blob))

    # INVENTED_REQUIREMENTS — deliverable content with no grounding in the raw utterance.
    deliverable_words = set(words(spec_text_fields["deliverable"]))
    if deliverable_words:
        ungrounded = sorted(w for w in deliverable_words if not grounded(w, raw_words))
        if len(ungrounded) / len(deliverable_words) > 0.5:
            findings.append(new_finding(
                "drift", "INVENTED_REQUIREMENTS (HEURISTIC)",
                f"{len(ungrounded)}/{len(deliverable_words)} deliverable content-words ungrounded "
                f"in the raw utterance: {ungrounded[:8]} — possible invented requirements"))

    # AUTHORITY_ESCALATION / UNMARKED_IRREVERSIBLE — irreversible verbs without ask-tier.
    irreversible = sorted({w for w in words(blob) if w in IRREVERSIBLE_VERBS})
    tier = (spec.get("authority") or {}).get("tier")
    if irreversible and tier != "ask":
        findings.append(new_finding(
            "drift", "AUTHORITY_ESCALATION (HEURISTIC)",
            f"irreversible verbs {irreversible} with authority.tier='{tier}' — "
            "irreversible moves require the 'ask' tier"))
        rollback_words = set(words(spec_text_fields["failure_conditions"]))
        if not (rollback_words & ROLLBACK_HINTS):
            findings.append(new_finding(
                "drift", "UNMARKED_IRREVERSIBLE (HEURISTIC)",
                "irreversible move with no rollback/kill language in failure_conditions"))

    # CONSTRAINT_LOSS — the raw utterance carried constraints the spec dropped.
    raw_lower = raw_text.lower()
    if any(h in raw_lower for h in CONSTRAINT_HINTS):
        explicit = (spec.get("constraints") or {}).get("explicit") or []
        if not explicit:
            findings.append(new_finding(
                "drift", "CONSTRAINT_LOSS (HEURISTIC)",
                "raw utterance contains constraint language but constraints.explicit is empty"))

    # SCOPE_EXPANSION — scope.in items ungrounded in the raw utterance.
    for item in (spec.get("scope") or {}).get("in") or []:
        item_words = set(words(item))
        if item_words and not any(grounded(w, raw_words) for w in item_words):
            findings.append(new_finding(
                "drift", "SCOPE_EXPANSION (HEURISTIC)",
                f"scope.in item '{item}' shares no stem-grounded words with the raw utterance"))

    # ASSUMPTION_PROMOTION — unknowns exist but nothing is labeled ASSUMED/UNKNOWN.
    if spec.get("unknowns") or spec.get("ambiguities"):
        labels = set((spec.get("epistemics") or {}).values())
        if not (labels & {"ASSUMED", "UNKNOWN"}):
            findings.append(new_finding(
                "drift", "ASSUMPTION_PROMOTION (HEURISTIC)",
                "unknowns/ambiguities listed but no field is labeled ASSUMED or UNKNOWN — "
                "uncertainty may be promoted to fact elsewhere in the spec"))
    return findings


def main():
    if len(sys.argv) != 2:
        print("usage: validator.py <spec.json>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1]) as f:
        spec = json.load(f)
    structural = check_structural(spec)
    drift = check_drift(spec)
    errors = [f for f in structural + drift if f["severity"] == "error"]
    verdict = "FAIL" if (errors or drift) else "PASS"
    report = {
        "spec": sys.argv[1],
        "intent_id": spec.get("intent_id"),
        "verdict": verdict,
        "structural": structural,
        "drift": drift,
        "note": "Drift findings are HEURISTIC keyword checks — the shape of drift, not its meaning. "
                "A human reads the raw <-> IntentSpec <-> lane-brief diff before any consequential execution.",
    }
    print(json.dumps(report, indent=2))
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
