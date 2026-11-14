# v1.6.3 Known-Issue List

Deferred from v1.6.2. Fixing any of these voids the current generator or server hash and requires a v1.6.3 amendment plus re-review. None blocks the v1.6.2 run; all are masked by `aggregate.py` recomputing around them.

| # | File | Issue | Impact | Workaround in v1.6.2 |
|---|---|---|---|---|
| 1 | `generator.py` | `Off.Load` column emits `rho`, not `offered/total_time` | Cosmetic; column label misleading | `aggregate.py` takes from first trial; value equals rho, verified consistent across trials |
| 2 | `generator.py` | `Th.Rej` column emits `p_k_th`, not `target_lambda * p_k_th` | Column shows probability, not rate | `aggregate.py` computes `th_rej = lam * p_k_th`; ignores generator column |
| 3 | `generator.py` | `Obs.Rej` column emits `rejected/offered` (probability), not `rejected/total_time` (rate) | Column shows probability, not rate | `aggregate.py` recomputes `obs_rej = rejected_agg / total_time_agg` |
| 4 | `generator.py` | `count_W_client` includes unexpected-status responses in client weight | Aggregated client mean is approximate | Assumed 0 unexpected-status in valid runs; filed as known |
| 5 | `generator.py` | Per-trial histograms not emitted | Blocks merged-p99 computation | `p99_N` aggregated as max across trials, filed as bound not point estimate |
| 6 | `generator.py` | `total_time_i` not emitted as a column | Requires reconstruction | Derived as `served/obs_thru` primary, `time_at_full/p_k_obs` fallback |
| 7 | `generator.py` + `diff.py` | No trial-exclusion mechanism | Any dropped trial → MEASUREMENT_FAILURE, no salvage | v1.0.9 rule: zero dropped trials acceptable, re-run required |

## Additional (non-code)

| # | Item | Status |
|---|---|---|
| 8 | Stale "DESIGN-SPEC DRAFT — NOT HASHED" headers on hashed files | Cosmetic, deferred to avoid voiding hashes |
| 9 | CSV load in `diff.py` crashes on missing `lambda` column | Hardening only; files from `aggregate.py` always have column |

## Resolution order for v1.6.3

1. Items 1–3 (column bugs) — same class, one pass, all void `generator.py` hash
2. Item 6 (`total_time_i` emission) — removes reconstruction workaround
3. Item 5 (per-trial histograms) — enables exact merged p99, replaces max-bound
4. Item 7 (trial exclusion) — needs manifest format design
5. Items 4, 8, 9 — opportunistic

All deferred until the v1.6.2 run completes, so the current hashes stay intact through the experiment.
