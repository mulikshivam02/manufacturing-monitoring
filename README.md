# Manufacturing Monitoring — Trust-Aware Multimodal Fusion

Dissertation project: *Trust-Aware Multimodal Fusion for Correlating Manufacturing
Defects with Process and Cyber-Physical Anomalies.*

Student: Mulik Shivam Santosh (MIS 712522024) · Guide: Dr. Sunil B. Mane

## Structure

- `part_a/` — operational system (rule-based decisions). **Never imports from `part_b/`.**
- `part_b/` — controlled multimodal fusion experiment. **Never imports from `part_a/`**
  except via trained-model *output artifacts*, never code.
- `data/` — `raw/` (untouched downloads), `processed/`, `derived_evidence/`, `scenarios/`, `schema/`
- `tests/` — `unit/`, `integration/`, `scenarios/`
- `scripts/` — dataset download/verification utilities
- `configs/`, `notebooks/`, `reports/`

See `data/schema/evidence_schema.md` for the frozen Event/Evidence record format —
read this before writing any module that produces or consumes an event.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest tests/test_import_boundary.py -v   # should pass on an empty skeleton too
```

## Dataset status

Run `python scripts/verify_datasets.py --dataset all` any time to check what's
downloaded against the verified figures in `data/schema/evidence_schema.md`.

| Dataset | Status |
|---|---|
| MVTec AD | not yet downloaded |
| MVTec LOCO AD | not yet downloaded |
| Tennessee Eastman Process | not yet downloaded |
| Paderborn Bearing DataCenter | not yet downloaded |
| SWaT | access requested: ______ (fill in date) |
