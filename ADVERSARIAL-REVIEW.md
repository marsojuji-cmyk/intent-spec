# Adversarial review — the four council questions (§8), answered in writing

Status: M2 of the catechism milestones. The job here is to try to kill the
idea. Where it survives, the survival is conditional and the conditions are
written down.

---

## Q1. Does the IR smuggle in a hidden second decision point?

**The charge.** "Compile to the existing router, never become a router" — but
someone picks `route.class`, and picking is deciding. `route.reason` is a
justification-shaped field one edit away from becoming a scorer. The one law
is a slogan until a mechanism enforces it.

**Verdict: the risk is real; the containment is procedural, not mechanical.**

Three containments, in increasing strength:

1. `route.class` draws from a **closed vocabulary owned by the estate**, not
   the compiler. The compiler selects; it cannot invent classes.
2. The selection is **advisory until the estate's machinery confirms it.** If
   the estate's router would have chosen differently, the compiler's choice
   loses. This must be a written rule, not a vibe: *the compiler never
   overrides the router, and any override by the router is recorded on the
   receipt.*
3. `route.reason` stays a **string justification, never a number.** The day it
   becomes a score, a weight, or a ranking, that is the second router wearing
   the IR as a mask — delete the field, keep the class.

The honest concession: whoever writes the reason exercises judgment, and
judgment is a decision point. The defense is not that no decision happens —
it is that the decision is **recorded, challengeable, and inside the
estate's existing review lane** rather than hidden. Hidden is the enemy, not
judgment. An unrecorded router choice is worse than a recorded compiler
choice; the IR moves the decision into the light.

**Survival condition:** the advisory-only rule and the no-scores rule are
written into the schema's field descriptions. Done in this revision.

---

## Q2. Does the superset-of-handoff claim hold field-by-field?

**The charge.** Two identifiers — `intent_id` (content-addressed on the raw
utterance) and the handoff record's `id` (ledger sequence) — are two truths
that will diverge silently the first time someone joins on the wrong one.

**Verdict: the claim does not fully hold. One fix required.**

Field-by-field:

| Handoff field | IntentSpec counterpart | Holds? |
|---|---|---|
| id | intent_id | **No** — different stability properties (see below) |
| goal | objective | Yes |
| constraints | constraints.explicit + constraints.inferred | Yes — the split is an addition, not a conflict |
| owner | route.owner | Yes |
| status | — | Correctly absent: status belongs to the work, not the compile. The spec is immutable once compiled; a changed intent recompiles under a new intent_id. |
| evidence | verification | Yes |
| next | receipt.next | Yes |
| blocker | unknowns + failure_conditions | Partially — acceptable; blockers discovered mid-work belong to the handoff, not the compile |

The id problem is genuine: `intent_id` is stable across recompiles of the
same utterance; the handoff `id` is stable across the work lifecycle. Neither
subsumes the other. **Fix applied in this revision:** `receipt` gains an
optional `handoff_id` field, and the rule is stated explicitly — *the compile
is identified by `intent_id`; the work it authorizes is identified by the
handoff id; the receipt records the mapping.* One join, in one place, written
down. The superset claim now holds under that rule.

---

## Q3. Is the deferred set correctly deferred?

**The charge.** The deferred stages are DAG planning, prompt optimization,
and strategy learning. If any of them is load-bearing for the IR to be worth
anything, deferring it is not discipline — it is shipping a broken thing
slowly.

**Verdict: correctly deferred, with one tripwire.**

- **DAG:** multi-compile planning for multi-step work. The IR's core claim is
  per-request drift-catching; a DAG is a composition layer above it. Not
  load-bearing for the falsifier (which is per-compile). Correctly deferred.
- **Strategy learning:** learning across compiles. Pure optimization; the IR
  works or fails on single instances first. Correctly deferred.
- **Prompt optimization:** correctly deferred *only while the compiler is
  mechanical.* **Tripwire:** if the compiler is ever LLM-driven, prompt
  versioning becomes load-bearing immediately — an unversioned prompt
  compiler drifts in its own compiling, and the intent-diff gate cannot see
  its own author's drift. If that day comes, prompt optimization returns with
  its own falsifier (the blind two-operator test, §7, applied to prompts).

---

## Q4. What is the smallest mechanical step that makes the IR real?

**The charge.** A JSON-schema validator checks structure. Structure is not
execution. Without a binding, the IR is documentation with a test suite.

**Verdict: the validator is necessary but not sufficient. The binding is the
artifact.**

The smallest mechanical step is one rule at the estate's intake: **no
`IntentSpec` artifact, no route.** The router — the existing one, not a new
one — requires the compiled spec before it accepts the request, and writes
the `intent_id` into the handoff's receipt. That is:

1. `validator.py` — the check (built, this revision).
2. One intake rule in the existing router — the binding (not built; it
   belongs to the estate, not the repo).
3. One ledger row per compile — the trace (the estate's existing ledger).

Without (2), M1 is a well-tested document. With (2), the intent-diff gate
runs before consequential execution, which is the entire point. **M3 — one
real intent compiled end-to-end through a live estate with the gate catching
a material drift — is the milestone that promotes this from document to
artifact.** Nothing in this repo may claim otherwise before M3.

---

## Net assessment

The idea survives with two modifications made (advisory-only routing rule +
no-scores rule written into the schema; `receipt.handoff_id` added with an
explicit id-mapping rule) and one tripwire set (LLM-driven compiler revives
prompt optimization). The load-bearing unknown remains M3: a gate nobody has
run is a gate nobody trusts. The falsifier stands as written — including the
blind two-operator test, which this review itself partially performs: if two
readers of this review compile the same intent and diverge on authority or
scope, the IR is vocabulary, not a contract, and §7 says what to do with it.
