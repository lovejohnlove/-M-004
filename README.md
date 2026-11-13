# Experiment 004c — Execution and Audit Pipeline

## Environment Status
ENVIRONMENT_STATUS: BLOCKED, no §12 VM. Pipeline closed on code audit. No code change unless a run surfaces something. When a compliant VM exists, resume with Precondition Run A plus B, Sweep Run A plus B, aggregate, diff, file as v1.6.2 EXECUTION REPORT.

---

## File Manifest & Canonical SHA-256 Hashes
- **`server_004c_FINAL_v1_6_2.py`**
  - **SHA-256**: `afe84dc1ad9630fafad2e2923ddb8f5ceb5e1eac9371605e28993bf785703ee6`
  - **Size**: 14,415 bytes (242 lines) — **Frozen**
- **`generator_004c_FINAL_v1_6_2.py`**
  - **SHA-256**: `c24f15e655bfb7b16dc84c72198489c81fdb02005d0e5a39e7bdd61660602ec5`
  - **Size**: 20,419 bytes (317 lines) — **Frozen**
- **`aggregate.py`**
  - **SHA-256**: `145f82da8fbb9fc54dd41b0ff03d0f56bf67b7e34373d6fe4381864f433c4294`
  - **Size**: 10,097 bytes (247 lines) — **Signed Off (v1.0.8)**
- **`diff.py`**
  - **SHA-256**: `e39c30f18c25542318b23c05fb686098f55d6a6eeb5e8eb1c4eb257011887ea1`
  - **Size**: 6,990 bytes (187 lines) — **Signed Off (v1.0.9)**
  *(Note: Supersedes draft hash `68a06947...`)*

---

## Specifications & Amendments
- **v1.0.8 Design-Spec**: Implements ensemble-weighted aggregation formulas, max-based `p99_N` selection, and one-sided physics sigma threshold checks.
- **v1.0.9 Amendment**: Enforces zero duplicate lambdas (paste-integrity check) and zero dropped trials (hard stop; manifest-based salvage deferred to v1.6.3).

---

## v1.6.3 Deferred Items & Known Issues (Non-Blocking)
- **Item #8**: Remove stale draft-status header comment from hashed `aggregate.py`.
- **Item #9**: Add explicit CSV schema validation / missing-column guardrails in `diff.py`.
