# Event / Evidence Schema — v0.1 (frozen at Phase 0)

Per Section 10 of the design doc: **freeze this before building anything downstream.**
Changing field names or states later means reworking every phase that already
consumed them. This is the single highest-leverage artifact in Phase 0.

Any change after freezing bumps the version number below and is logged in
`CHANGELOG_SCHEMA.md` (create when the first change happens).

---

## 1. Per-stream output (produced by A1/A3/A6 + their reliability checks)

Every stream (vision / machine / cyber) reports the same four fields —
one common framework, stream-specific values:

```json
{
  "stream": "vision | machine | cyber",
  "label": "GOOD|BAD|UNCERTAIN  (vision)  /  NORMAL|ANOMALOUS  (machine, cyber)",
  "confidence": 0.0,
  "reliability_status": "TRUSTWORTHY | SUSPICIOUS | UNRELIABLE",
  "reason_codes": ["blur", "flatline", "missing_flow", "..."],
  "optional_class": "defect/fault/attack subtype, when the dataset supports it"
}
```

## 2. Event record (built by the event builder, M6)

One event = one logical decision unit (Section 5). For the public datasets used
here, `scenario_id` replaces a real product/event ID — **never inferred from row
order**, always an explicit constructed mapping.

```json
{
  "event_id": "E103 (real-line style) | scenario_id (Part B)",
  "timestamp": "ISO-8601 or simulated tick",
  "source": "real | constructed",
  "vision": { "...per-stream output above, or null" },
  "machine": { "...per-stream output above, or 'UNKNOWN' if unreliable/missing" },
  "cyber": { "...per-stream output above, or 'UNKNOWN' if unreliable/missing" },
  "compatibility": "COMPATIBLE | NOT-COMPATIBLE | NO-DEFECT-TO-SCORE",
  "decision": "ACCEPT | REJECT | REINSPECT | HOLD | INVESTIGATE",
  "decision_priority": "normal | highest  (set when compatible-HOLD + cyber both present)",
  "source_refs": ["original sample IDs / file paths, for traceability"]
}
```

Rules baked into this schema (do not relax these later):

- A stream that is `UNRELIABLE` never appears as its raw label downstream —
  it is recorded as `UNKNOWN` context, per the missing-evidence rule (Section 14).
- `UNKNOWN` context can never satisfy the HOLD-compatibility condition or the
  INVESTIGATE cyber-presence condition, and never triggers REINSPECT
  (REINSPECT is vision-only).
- `source_refs` is mandatory for every Part B scenario record — this is what
  the B2 test criteria (traceable source reference) actually checks.

## 3. Group window record (M8, group monitor)

```json
{
  "window_id": "W10",
  "window_size": 50,
  "products_inspected": 50,
  "bad_count": 8,
  "uncertain_count": 2,
  "defect_rate": 0.16,
  "baseline_defect_rate": 0.06,
  "machine_anomaly_count": 12,
  "cyber_anomaly_count": 3,
  "reliability_issue_count": 2,
  "group_status": "NORMAL | WARNING | INVESTIGATION | HIGH ALERT",
  "throughput_assumption": "stated units/min assumption used to size this window (Section 10)"
}
```

**Group records are append-only and never mutate an individual event record.**
This is exactly what A10's no-mutation CI check (added when A10 is built) verifies.

## 4. Part B scenario record (extends the event record)

```json
{
  "scenario_family": "immediate_onset | delayed_onset | recovery | negative_control | stealth_simulation | ...",
  "expected_action": "the predefined label, assigned independently of the Section 7.4 heuristic (B3)",
  "holdout_split": "train | holdout"
}
```

---

## Verified reference figures (Phase 0 test criteria)

| Dataset | Verified figure |
|---|---|
| MVTec LOCO AD | 3,644 images across 5 categories |
| MVTec AD | 5,354 images across 15 categories |
| Tennessee Eastman Process (Rieth et al. 2017) | 52 process variables, 20 fault scenarios, 55 total columns (`faultNumber`, `simulationRun`, `sample` + 52 vars) |
| Paderborn Bearing DataCenter | 32 bearing codes = 6 healthy (K001-K006) + 26 damaged (12 artificial + 14 real-damage) |
| SWaT | 11 days (7 normal + 4 attack), 51 sensors/actuators, 41 labeled attack scenarios |

Schema reviewed and frozen on: **____________** (fill in when you sign off — this date is the Phase 0 gate per the test criteria).
