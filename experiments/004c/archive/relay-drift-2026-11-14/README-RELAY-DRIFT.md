# Relay Drift — 004c Preservation Archive

**PRESERVATION ONLY. These are unverified relayed byte states, not sealed pipeline files. Do not run them as 004c.**

## What is preserved

This folder contains exact byte copies of the selected server and generator relay sources. Their measured hashes, sizes, line counts, claim comparisons, and source-variant distinctions are recorded in [the detailed audit](AUDIT-RELAY-DRIFT.md).

- `server_004c_FINAL_v1_6_2_RELAY-DRIFT-UNVERIFIED.py` — 14,135 bytes, 240 LF-terminated lines; SHA-256 `a0886b4c70f0648da67beccf373e9bb9bc8e5a8ed5fd9183a11f4ac078066803`.
- `generator_004c_FINAL_v1_6_2_RELAY-DRIFT-UNVERIFIED.py` — 20,235 bytes, 318 LF-terminated lines; SHA-256 `7f3f99d6fa7678bbce694e02465fef078b2bfbaea52c92bc136bf952d5274ded`.

The names deliberately say `RELAY-DRIFT-UNVERIFIED`. The files were supplied through chat relay; the copies are not console-direct reads and do not establish the identity or integrity of a sealed original.

## Generator finding: structural drift

The selected relay generator has `measurement_failure = False` at module scope on line 40, but no per-trial reset inside `run_trial` (which begins on line 156). This is not cosmetic drift: without the reset, a failure in one trial can persist into later trials and falsely mark them `MEASUREMENT_FAILURE`. Q’s measurement diagnosed this state-leakage problem; the earlier wording that the cause was not fully diagnosed is withdrawn.

A separate chat-copy state, SHA-256 `a89f3f48aa6ffaa51d493a7b6483c02348d5c1eb34fdd4c2bcb95d6d2efc5e6b`, has the module-level assignment on line 38 and the per-trial reset on line 156. It is documented as a distinct variant only; it was not substituted for the selected relay source and is not, by itself, evidence of console-direct verification or a seal.

## Related 004c status

- The four REBUILD-1 files are preserved separately under `unsealed/REBUILD-1/`. Their byte counts and hashes match the existing report template, but this does not make them sealed or console-direct verified. See that folder’s `README-PRESERVATION-ONLY.md`.
- The stated rebuild basis is **v1.0.8**, not superseded v1.0.7; v1.0.8 includes the `n_trials` Table A fix. The known-issue record has **9 items**: 7 code issues and 2 non-code items ([existing list](../../docs/V1_6_3_KNOWN_ISSUES.md)).
- **§1 remains unresolved.** The authoritative full v1.6.1/v1.6.2 preregistration base is missing; no source text is inferred. See `prereg/README-PREREG-STATUS.md`.
- **VM BLOCKED — VM REPORTED, NOT VERIFIED.**

No project code was run or tested during this preparation. No commit or push was made.

