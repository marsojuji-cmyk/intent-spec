# IntentSpec v0.1 — a canonical intermediate representation for agent intent

**Status:** DRAFT · **Version:** 0.1 · **Date:** 2026-09-27 (refined from 2026-09-21 draft)
**Author:** Marcus Richards · **Provenance:** refined from an estate-internal draft (`INTENT-SPEC.md`, 2026-09-21); the draft's adversarial review and canonization are pending — see Honesty below.
**License:** MIT (on publication)

## The catechism

**1. What we are trying to do.** Give raw human intent a canonical, typed form — an `IntentSpec` — that compiles *into* an existing agent estate's routing, authority, handoff, and receipt machinery, instead of letting every agent re-interpret raw chat text and drift on scope, authority, and verification.

**2. How it is done today, and why it fails.** Today intent travels as raw utterance. Each agent recovers objective, constraints, and authority by re-reading the text, per session, by hand. The failure mode is specification drift: scope creeps, constraints are lost, authority escalates silently, assumptions get promoted to facts. This is not a model-capability problem — it is a missing contract at the boundary.

**3. What is new.** The IR sits strictly *between* raw intent and existing machinery. It does not re-decide anything the estate already decides — one law: **compile to the router, never become a router.** It adds what the machinery lacks: an explicit, typed, diffable statement of objective, constraints (explicit vs inferred — the split is mandatory), scope in/out, compiled authority, unknowns with ambiguity classes, pre-designed success/failure conditions, verification contracts, and epistemic labels (explicit / inferred / assumed / unknown, never collapsed).

**4. Why it might work — the causal mechanism.** Drift happens at the boundary between human language and machine execution, and it is invisible because there is nothing to diff. The `IntentSpec` makes drift *checkable*: the intent-diff gate (§4) diffs `raw ↔ IntentSpec ↔ lane brief` before execution, and material drift fails the compile. A compile that cannot show its diff is unverified. The mechanism is detection, not intelligence.

**5. Risks, first.** (a) It is a spec, not a system — the mechanical compiler is not built, so everything below is designed, not exercised. (b) `route.reason` could grow into a hidden second decision point — a second router wearing the IR as a mask; council question §8.1 exists to kill this. (c) The superset-of-handoff claim may not hold field-by-field; two truths (`intent_id` vs `id`) would diverge silently. (d) Over-specification risk: the IR could cost more attention than the drift it prevents — the objective function (§1) is the governor, and the falsifier (§7) deletes the compiler if it never catches anything.

**6. Cost and clock.** Schema + validator + worked examples: ~1 week of build time, negligible cash. The schema's marginal cost once landed is ≈ 0; the mechanical compiler is one small script plus a ledger row per compile.

**7. Milestones and kill lines.** M1 — JSON schema + validator + 3 worked examples, all passing. M2 — adversarial review complete (the draft's own council questions answered in writing). M3 — one real intent compiled end-to-end through a live estate, with the intent-diff catching at least one material drift. **Kill:** 14 days live with zero compiled instances while requests ran, or instances whose intent-diff never catches a drift a human later catches — either means decorative; delete rather than keep ceremony.

**8. Falsifier.** A blind test: two operators compile the same raw intent independently. If their `IntentSpec`s diverge on authority or scope fields, the spec does not pin down what it claims to — the IR is vocabulary, not a contract.

## Honesty — designed vs exercised

- **Designed:** the IR schema, the six passes, the intent-diff gate, the R0–R6/A0–A4 depth and ambiguity economics, the non-goals.
- **Exercised:** one worked compile run exists in the author's estate (`COMPILE-RUN-2026-09-21.md`, not included here).
- **Not done:** adversarial review, canonization, the mechanical compiler (code), the deferred stages (DAG, prompt optimization, strategy learning). Nothing here has run in production.
- **Historical baseline:** the original draft recorded machine-state measurements from the author's estate on 2026-09-21 (memory pressure, load, model defaults) as its greenfield baseline. Those numbers are estate-specific and dated; re-measure on your own estate.

---

## §0 The one law

**The Intent Compiler does not re-decide anything the estate already decides.**

It has exactly one output of consequence: a typed `IntentSpec` that **compiles TO** the machinery the estate already runs — its router, its authority tiers, its review lanes, its handoff record, its receipt. A second router, a second authority model, or a second ledger would be a second writer on a decision that already has one writer. **Compile to the router. Never become a router.**

## §1 Position

```text
OPERATOR ──raw utterance──► INTENT COMPILER ──IntentSpec──► EXISTING MACHINERY
                                              │              ├─ Router        (route classes)
                                              │              ├─ Authority tiers (log / build-report / ask)
                                              │              ├─ Review lanes  (conductor · adversary · builder · operator)
                                              │              ├─ Handoff record (id, goal, constraints, owner, status, evidence, next, blocker)
                                              │              └─ Receipt        (trace / receipt / next)
                                              └── never invents a parallel one of the above
```

Objective function:

```text
ROI = Expected Verified Value / (Human Attention + Compute + Latency + Risk + Rework)
```

The best specification is the **cheapest sufficient specification that reliably produces the required outcome** — not the longest, the strongest-model, or the most-agent.

## §2 The IR — what an `IntentSpec` is

The IR is a **strict superset of the existing handoff record**, so a compiled intent is *also* a valid handoff and needs no translation layer.

| IntentSpec field | Maps to (handoff) | Notes |
|---|---|---|
| `intent_id` | `id` | stable, content-addressed |
| `raw` | — | immutable: utterance, timestamp, attachments, referenced objects. **Never discard.** |
| `objective`, `desired_state`, `deliverable` | `goal` | recovered meaning, not restated words |
| `constraints.explicit` / `.inferred` | `constraints` | the split is mandatory |
| `scope.in` / `.out` | — | anti-scope-creep |
| `authority` | authority tiers | compiled FROM the tiers, never re-derived |
| `unknowns[]`, `ambiguities[]` | `blocker` | each carries an ambiguity class (§5) |
| `success_conditions[]`, `failure_conditions[]` | — | designed before execution |
| `route.class`, `route.owner`, `route.reason` | `owner_lane` | one of the router's classes |
| `verification` | — | probes / regression checks / independent read-back |
| `receipt` | `evidence_path` | trace · receipt · next |
| `epistemics` | — | EXPLICIT / INFERRED / ASSUMED / UNKNOWN, never collapsed |

Machine form: `intent_spec.schema.json` (to be published with the validator).

## §3 Stage map — twenty stages, six executable passes, each owned by an existing mechanism

| Pass | Owned by |
|---|---|
| 1 Capture | append `raw` verbatim (provenance) |
| 2 Recover | objective / constraints / epistemics extraction |
| 3 Hydrate | memory + vault + live probe — **utility-weighted, never a memory dump** |
| 4 Classify & plan | task class → expected value → **the router** (owns the lane) |
| 5 Emit | one IntentSpec → per-lane briefs + authority + verification contract |
| 6 Verify & receipt | intent-diff check, then trace/receipt/next + outcome row |

Deferred, not dropped — each is a real build with its own blueprint: execution DAG, prompt optimization, receipt/outcome/strategy learning. (Prompt refinement as a standing duty already exists in most estates; don't rebuild it.)

## §4 The intent-diff gate — the one hard check

Before execution, diff three layers: `raw ↔ IntentSpec ↔ lane brief`. **Material drift fails the compile.** Failure signatures: objective drift · scope expansion · constraint loss · authority escalation · invented requirements · assumption promoted to fact · irreversible move not marked.

This is the compiler's analogue of a claim gate: a compile that cannot show its diff is unverified.

## §5 Depth (R0–R6) and ambiguity economics (A0–A4) — adopted, but bound

- **R0 NONE … R6 FULL REVIEW** (refinement depth) and **A0 irrelevant … A4 consequential** (ambiguity) are adopted. The governor: **apply exactly enough.** The deepest review is never automatic.
- **A0–A2:** do not interrupt the operator — infer, and *disclose* the inference in the spec.
- **A3:** may clarify. **A4:** blocks the affected consequential action only.
- **Bound to live gates, not parallel ones:** the deepest review *is* the estate's existing adversarial lane, not a new council; intelligence budgeting resolves through existing model routing, never a new dispatcher.

## §6 Non-goals (the anti-overengineering governor, turned inward)

The compiler MUST NOT build: a second router · a second authority model · a second ledger · an auto-review-board · a prompt-rewriting engine that runs without an outcome receipt · any component whose measured entropy is zero. Each proposed addition must answer: *will this materially raise expected verified value?* If not — remove it, recursively, including from the compiler itself.

## §7 Falsifier and rollback (from the catechism)

**Kill it:** 14 days live with (a) zero `IntentSpec` instances produced while requests ran, **or** (b) instances whose intent-diff never catches a drift a human later catches. Either ⇒ decorative; delete rather than keep ceremony. Any instrument derived from the IR must also pass a measured-entropy test before it ships.

**Rollback:** one directory. No config, no scheduler, no state touched. Reversible by deletion.

## §8 Open questions (for adversarial review before canonization)

1. Is "compile to the existing router" sufficient, or does the IR smuggle in a hidden second decision point (e.g. `route.reason` growing into a scorer)?
2. Does the superset-of-handoff claim hold field-by-field, or are there two truths (`intent_id` vs `id`) that will diverge?
3. Is the deferred set correctly deferred, or is one of them load-bearing for the IR to be worth anything?
4. What is the smallest **mechanical** step that turns the IR from a document into a running artifact — is a JSON-schema validator enough, or must the router be bound at write time?
