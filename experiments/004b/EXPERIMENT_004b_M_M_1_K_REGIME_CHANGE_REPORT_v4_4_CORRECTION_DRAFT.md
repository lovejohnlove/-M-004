# Experiment 004b — v4.4 Correction Draft

**Document:** Proposed correction overlay for `EXPERIMENT_004b_M_M_1_K_REGIME_CHANGE_REPORT_v4_3.md`  
**Status:** DRAFT — NOT APPROVED, NOT SEALED, and not a replacement for v4.3  
**Prepared:** 2026-11-25  
**Purpose:** Record corrections and unresolved audit findings without changing the preserved v4.3 report or claiming a new experiment run.

> This is a correction draft, not a new execution report. It contains no new runtime output. Keep v4.3 unchanged. If approved, issue a dated v4.4 copy with its own explicit provenance; do not silently alter or reseal v4.3.

## Evidence basis and limits

The available local v4.3 report is `experiments/004b/EXPERIMENT_004b_M_M_1_K_REGIME_CHANGE_REPORT_v4_3.md`. The same bytes were found in three local copies, with SHA-256 `e0be7a76e1841d690962bfa71dac6e89c638dc93dc94b237dd7e27cd524cc873`. This digest identifies the local bytes inspected for this draft; it does not explain or authenticate the older digest stamped inside the report.

The additional findings below were relayed as results of a Dropbox-only review. The reviewer reportedly could not access newer GitHub files, and the review notes version drift and unread files. Those findings are therefore **reported claims**, not an independently verified current-source audit. Dropbox and newer GitHub copies, the simulation source, raw logs, and original preregistration artifacts were not available for this draft. No conclusion here should be read as resolving differences between those sources.

## Proposed correction record

### 1. λ = 1.50 status label — source/version discrepancy; unresolved

**Local evidence:** In the locally available v4.3 §6 execution table, the λ = 1.50 row is marked `PASS`, and the footer says all 14 rows passed. Its displayed observed values are throughput 0.9942 versus theoretical 0.9942 and rejection 0.5044 versus theoretical 0.5058. The local copy does not show `Loss` for this row.

**Reported finding:** The Dropbox-only review says the λ = 1.50 row is labeled “Loss” while the footer says all rows passed.

**Draft disposition:** Do not silently change the local v4.3 record. Reconcile the exact Dropbox and GitHub versions first. If the authoritative copy for the same run does show `Loss`, inspect the status-generation rule and raw row before correcting it. The local values appear within the report’s stated ±0.02 throughput/rejection tolerance, but that does not establish which remote copy or label is authoritative.

### 2. λ = 2.00 theoretical row — corrected analytical reference

For an M/M/1/K queue with ρ = λ/μ = 2 and K = 10,

`P_n = ρ^n / Σ(j=0…K)ρ^j`, `P_K = 2^10 / 2047`;

throughput is `λ(1 − P_K)` and rejection rate is `λP_K`. Direct calculation gives:

| λ | ρ | Throughput | Rejection rate | P_K |
|---:|---:|---:|---:|---:|
| 2.00 | 2.00 | 0.9995114802… → **0.9995** | 1.0004885198… → **1.0005** | 0.5002442599… → **0.5002** |

The v4.3 §5 table instead prints 0.9990, 1.0010, and 0.5005. Its §6 execution table already prints the corrected throughput and rejection values (0.9995 and 1.0005), but does not show `P_K` there. The theoretical row should be amended in a future v4.4 copy to the exact values above, while retaining the old table values in the correction history as the values originally printed—not rewriting them as if they had never appeared. In particular, 0.5005 is not correct rounding from 0.5002442599…; rounded to four decimal places, the latter is 0.5002. Treat the printed `P_K` as a numerical discrepancy, not a formatting variant.

Using the v4.3 §6 observed values (throughput 1.0025; rejection 1.0013), the absolute differences from the corrected values are about 0.00299 and 0.00081, respectively. Both remain within the stated ±0.02 tolerance **if** those observed values and that gate are the applicable record. This calculation does not independently verify the run.

### 3. MaxQ at low load — explanation not established

The v4.3 §6 table records `MaxQ = 3` at λ = 0.30. Its §7 diagnostic says this is consistent with finite-trial variance and further asserts that MaxQ reflects trial-aggregated peaks. The available report does not define MaxQ’s aggregation or provide enough source/run detail to establish that explanation. The reported review also flags the value as unexpectedly low relative to a claimed run length.

As a limited analytical check, for the stationary M/M/1/10 model at ρ = 0.30, the probability mass in states `N ≥ 4` is approximately 0.008098. Under a simplified assumption of 450,000 independent stationary observations, that would correspond to about 3,644 observations at `N ≥ 4`. Queue observations are dependent, and the report’s phrase “450,000 pooled units” is not defined; this calculation is therefore a warning signal, **not** a probability estimate for the actual run and not proof that the observed maximum is impossible.

**Draft disposition:** Replace the claim that the explanation is established with “unresolved pending source and run-definition inspection.” Before asserting what MaxQ means, inspect the actual computation, whether it is per run or pooled, the observation window and warm-up, number of replications, units counted, and raw run output. Do not infer a corrected MaxQ value from the theoretical distribution.

### 4. Embedded SHA-256 — scope and provenance unspecified

The v4.3 metadata stamps `d4d9c79f3238122c1b82f099c2bfb1b7a2d42b03948e718b95861b58a55c2f81` inside the file and dates it 2026-11-12. The report does not state which exact bytes were hashed, whether the digest excluded the seal line or used a normalized form, or who or what calculated it. It therefore cannot be treated here as a verified digest of the final file bytes or as an independently attributable seal. The local-copy digest listed above is a separate checksum calculated during preparation of this draft; it does not establish the older stamp’s method or author.

**Draft disposition:** Do not carry the old embedded digest forward as a verified full-file seal. Keep this v4.4 document unsealed while it is a draft. If a final integrity digest is desired, calculate it only after the final bytes are fixed and place it in a detached checksum file or external manifest that names the exact file, byte scope, algorithm, date, and responsible person/tool.

## Related items not resolved by this correction

- The reported handoff dwell-fit mismatch is separate from 004b. If the intended equation is `1/(1−ε) = 10`, then `ε = 0.9`; the reported value `0.900601` does not satisfy that equation. Audit the handoff source and intended fit separately; do not import that correction into the 004b report without evidence it belongs there.
- Dropbox/GitHub version drift and unread files remain open provenance gaps. Until the relevant copies and files are compared, describe this as a local-copy review informed by reported Dropbox findings—not as a complete or current-source audit.
- v4.3 states the experiment was a single run and not reproduced. This draft does not change that status or claim a rerun.

## Proposed v4.4 status language

> **Status:** CORRECTION DRAFT — analytical table correction prepared; row-label discrepancy and MaxQ interpretation unresolved; embedded v4.3 digest provenance unspecified. No new run performed. v4.3 preserved unchanged. Not sealed and not approved as a replacement.

## Revision relationship

- **Base preserved:** `EXPERIMENT_004b_M_M_1_K_REGIME_CHANGE_REPORT_v4_3.md` remains untouched.
- **Proposed relationship:** This draft records an errata overlay for review. It does not yet supersede v4.3. Only an owner-approved final v4.4 should establish the superseding relationship and its seal/provenance.
