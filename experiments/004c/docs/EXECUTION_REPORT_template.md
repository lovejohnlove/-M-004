# EXPERIMENT 004c — EXECUTION REPORT (template)

**Status:** [DRAFT | EXECUTED | INSPECTED | REPRODUCED]
**Date:** [YYYY-MM-DD]
**Code commit:** all four REBUILD-1 hashes recorded below
**Prepared by:** [operator]
**Reproducibility:** [SINGLE RUN | REPRODUCED]

---

## 1. Environment (§12)
```

prereg §11 seeds confirmed: 1001 / 2002 / 1003 / 2004

CPU model:        [from lscpu]
vCPU count:       [from nproc]
Governor:         [from cpupower frequency-info — must be "performance"]
OS:               [from lsb_release -a]
Kernel:           [from uname -r]
Python:           [from python3 --version]
Instance type:    [cloud provider + instance name]
Idle during run:  [Y/N, evidence]
Server/generator co-hosted: [Y/N]

```

## 2. Code hashes (sealed)

| File | sha256 | Bytes | Lines |
|---|---|---|---|
| `server_004c_FINAL_REBUILD-1.py` | `57113d646488c1cefc36f4a45d9ba3fec208659253af5229f489b99a13478eda` | 14,546 | 243 |
| `generator_004c_FINAL_REBUILD-1.py` | `f722de8b46cb90b448de8f4ee4ad131e7f6930ac2c6fab5f9f768a4c6f95fc9c` | 20,536 | 319 |
| `aggregate_004c_REBUILD-1.py` | `81170771423418c471c2c33990000f18490bbfd004d2557600401fa9a0b4c45c` | 10,404 | 250 |
| `diff_004c_REBUILD-1.py` | `05c787f759259e2bf96822575940a2f090e775d8eeb6e4666c66648192e6fc11` | 7,220 | 188 |

Supersedes: `afe84dc1...`, `c24f15e6...`, `145f82da...`, `e39c30f1...` (CLAIMED PENDING RECOVERY, artifacts unavailable)

## 3. Precondition

Run A (server 1001 / generator 1003): [raw stdout]
Run B (server 2002 / generator 2004): [raw stdout]

Pass criteria per §6: mean occupancy within 0.15 of 1.00, 0 rejections, 0 timeouts.
Both must pass before sweep.

## 4. Sweep — Run A

Seeds: server 1001, generator 1003
Raw stdout: [paste, no truncation]
sha256 of raw stdout: [hash]
λ values covered: 30, 50, 70, 85, 95, 99, 100, 101, 105, 115, 130, 150, 200, 300
Trials per λ: 10

## 5. Sweep — Run B

Seeds: server 2002, generator 2004
Raw stdout: [paste, no truncation]
sha256 of raw stdout: [hash]

## 6. Aggregation and diff
```

$ python3 aggregate_004c_REBUILD-1.py --input raw_A.txt --output agg_A.csv
[exit code, any warnings]

$ python3 diff_004c_REBUILD-1.py --report report_table.csv --aggregate agg_A.csv
[full output, exit code]

```

[Same for Run B]

## 7. Gate evaluation (§8)

| Gate | Tolerance | Run A | Run B |
|---|---|---|---|
| Throughput | \|Δ\| ≤ 3.0 | [result] | [result] |
| Rejection | \|Δ\| ≤ max(0.5, min(3.0, 0.25·Th.Rej)) | [result] | [result] |
| P_K | \|Δ\| ≤ max(0.005, min(0.03, 0.20·Th.P_K)) | [result] | [result] |
| Physics | Obs.Thru ≤ 102.0, >3σ fails | [result] | [result] |

Per-row MEASUREMENT_FAILURE count: [n] — each examined for cause before exclusion.

## 8. Result

[PASS | FAIL | MEASUREMENT_FAILURE | NOT REPRODUCED]

If PASS: model predicts observed throughput and rejection within tolerance for both independent runs.
If FAIL: [which rows, which direction, diagnostic from §9 pre-registered patterns]
If MEASUREMENT_FAILURE: [which trials, cause, re-run required]

## 9. Challenge line

[All known limitations, unresolved gaps, and caveats. Nothing suppressed.]
