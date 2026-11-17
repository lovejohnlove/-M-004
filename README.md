# Experiment 004c — Execution and Audit Pipeline

## Environment Status
ENVIRONMENT_STATUS: BLOCKED, no §12 VM. Pipeline closed on code audit. No code change unless a run surfaces something. When a compliant VM exists, resume with Precondition Run A plus B, Sweep Run A plus B, aggregate, diff, file as v1.6.2 EXECUTION REPORT.

---

## Historical File Manifest — Claimed Hashes Pending Recovery (Not Verified)
The four entries below are preserved as historical claims; the referenced artifacts were unavailable for recovery and verification. These hashes must not be treated as hashes of the REBUILD-1 files listed later.
- **`server_004c_FINAL_v1_6_2.py`**
  - **SHA-256**: `afe84dc1ad9630fafad2e2923ddb8f5ceb5e1eac9371605e28993bf785703ee6`
  - **Size**: 14,415 bytes (242 lines) — **Claimed frozen; not verified**
- **`generator_004c_FINAL_v1_6_2.py`**
  - **SHA-256**: `c24f15e655bfb7b16dc84c72198489c81fdb02005d0e5a39e7bdd61660602ec5`
  - **Size**: 20,419 bytes (317 lines) — **Claimed frozen; not verified**
- **`aggregate.py`**
  - **SHA-256**: `145f82da8fbb9fc54dd41b0ff03d0f56bf67b7e34373d6fe4381864f433c4294`
  - **Size**: 10,097 bytes (247 lines) — **Claimed signed off (v1.0.8); not verified**
- **`diff.py`**
  - **SHA-256**: `e39c30f18c25542318b23c05fb686098f55d6a6eeb5e8eb1c4eb257011887ea1`
  - **Size**: 6,990 bytes (187 lines) — **Claimed signed off (v1.0.9); not verified**
*(Note: Supersedes draft hash `68a06947...`)*

---

## Specifications & Amendments
- **v1.0.8 Design-Spec**: Implements ensemble-weighted aggregation formulas, max-based `p99_N` selection, and one-sided physics sigma threshold checks.
- **v1.0.9 Amendment**: Enforces zero duplicate lambdas (paste-integrity check) and zero dropped trials (hard stop; manifest-based salvage deferred to v1.6.3).

---

## v1.6.3 Deferred Items & Known Issues (Non-Blocking)
- **Item #8**: Remove stale draft-status header comment from hashed `aggregate.py`.
- **Item #9**: Add explicit CSV schema validation / missing-column guardrails in `diff.py`.

## 004c Rebuild Intake Status — 2026-11-14

**Status:** §12 environment/run remains blocked. No experiment was executed. This intake makes no claim of novelty or experimental success.

**SEAL STATUS: BYTE-STATE SEALED.** The four listed REBUILD-1 files are identified by their recorded SHA-256 hashes, and each `code/` file is byte-identical to its corresponding `unsealed/REBUILD-1/` file. This seal applies only to the four hash-identified local byte-states; provenance, preregistration compliance, runtime correctness, performance, concurrency, and any §12 result remain unverified.
- `experiments/004c/code/diff_004c_REBUILD-1.py` — SHA-256 `05c787f759259e2bf96822575940a2f090e775d8eeb6e4666c66648192e6fc11` (7,220 bytes; 188 lines)
- `experiments/004c/code/aggregate_004c_REBUILD-1.py` — SHA-256 `81170771423418c471c2c33990000f18490bbfd004d2557600401fa9a0b4c45c` (10,404 bytes; 250 lines)
- `experiments/004c/code/server_004c_FINAL_REBUILD-1.py` — SHA-256 `57113d646488c1cefc36f4a45d9ba3fec208659253af5229f489b99a13478eda` (14,546 bytes; 243 lines)
- `experiments/004c/code/generator_004c_FINAL_REBUILD-1.py` — SHA-256 `f722de8b46cb90b448de8f4ee4ad131e7f6930ac2c6fab5f9f768a4c6f95fc9c` (20,536 bytes; 319 lines)

**Documentation-only artifacts — hash-verified, not sealed:**
- `experiments/004c/docs/EXECUTION_REPORT_template.md` — SHA-256 `1f0852dfec57f700ea62a804de9138dbe9f219206bae429b768dc60e4729c015` (3,128 bytes; 95 lines)
- `experiments/004c/docs/README-RELAY-DRIFT.md` — SHA-256 `7c6a51bed65535e8762942521c0f6024a2f02e9917fe77364fd61b457dc9dc00` (1,901 bytes; 42 lines)
- `experiments/004c/docs/V1_6_3_KNOWN_ISSUES.md` — SHA-256 `b027ace8114b1a26e5d0b7313495078e35bc581e9389cc0a096fe078143a05d6` (2,445 bytes; 30 lines)

**Locked preregistration values only:** Run A server seed 1001 / generator seed 1003; Run B server seed 2002 / generator seed 2004. No run was performed with these values.

The hashes in the pre-existing “File Manifest & Canonical SHA-256 Hashes” section above are preserved as historical claims pending recovery and verification of their referenced files; they are not verified by this intake and should not be treated as hashes for the rebuild artifacts listed here.
