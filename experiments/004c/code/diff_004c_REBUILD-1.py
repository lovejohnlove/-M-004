#!/usr/bin/env python3
# diff_004c_REBUILD-1.py — REBUILD against authoritative v1.0.9 spec
# SUPERSEDES: diff.py e39c30f1... (CLAIMED PENDING RECOVERY — artifact unavailable via relay)
# Logic identical to signed-off v1.0.9 substance. New hash to be claimed on console verification.
# Implements Table A (paste-integrity) + Table B (§8 gates) from v1.0.8 / v1.0.9
# Enforces zero-duplicate paste-integrity and zero-dropped-trial rules.
# Every decision-relevant line carries # v1.0.9 §N

import argparse
import csv
import sys

# ---- Table A from design-spec v1.0.8: paste-integrity, exact at printed precision ----
TABLE_A = {
    "lambda":             ("float", 4),
    "rho":                ("float", 4),
    "Off.Load":           ("float", 4),
    "Th.Thru":            ("float", 2),
    "Obs.Thru":           ("float", 2),
    "Th.Rej":             ("float", 2),
    "Obs.Rej":            ("float", 2),
    "Obs.MeanN":          ("float", 4),
    "P_K_Obs":            ("float", 4),
    "P_K_Th":             ("float", 4),
    "TimeAtFull_s":       ("float", 6),
    "p99_N":              ("int",   0),
    "MeanResp_ms_Server": ("float", 2),
    "MeanResp_ms_Client": ("float", 2),
    "Served":             ("int",   0),
    "Rejected_503":       ("int",   0),
    "Timeout":            ("int",   0),
    "Refused":            ("int",   0),
    "Reset":              ("int",   0),
    "Status":             ("str",   0),
}

# ---- §8 gate thresholds from v1.6.2 — for Table B independent recompute ----
GATE_THRU_TOL       = 3.0     # v1.0.9 §Decision 3 Table B
GATE_REJ_TOL_MAX    = 3.0
GATE_REJ_TOL_MIN    = 0.5
GATE_REJ_TOL_FRAC   = 0.25
GATE_PK_TOL_MAX     = 0.03
GATE_PK_TOL_MIN     = 0.005
GATE_PK_TOL_FRAC    = 0.20
PHYSICS_CEILING     = 102.0   # v1.0.9 §Physics
PHYSICS_SIGMA_FAIL  = 3.0


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def coerce(val, kind, dp):
    if kind == "int":
        return int(val)
    if kind == "float":
        return round(float(val), dp)
    return val.strip()


def compare_table_a(report_row, agg_row, col):
    kind, dp = TABLE_A[col]
    r = coerce(report_row[col], kind, dp)
    a = coerce(agg_row[col], kind, dp)
    passed = (r == a)
    return {"col": col, "expected": r, "actual": a,
            "delta": (r - a) if kind in ("float", "int") else None,
            "tolerance": "exact@{}dp".format(dp) if kind != "str" else "exact",
            "pass": passed}


def eval_gates(agg_row):
    """Table B — independent recompute of §8 gates. Returns dict of gate results."""
    obs_thru = float(agg_row["Obs.Thru"])
    obs_rej  = float(agg_row["Obs.Rej"])
    th_thru  = float(agg_row["Th.Thru"])
    th_rej   = float(agg_row["Th.Rej"])
    p_k_obs  = float(agg_row["P_K_Obs"])
    p_k_th   = float(agg_row["P_K_Th"])

    thru_ok = abs(obs_thru - th_thru) <= GATE_THRU_TOL
    rej_tol = max(GATE_REJ_TOL_MIN, min(GATE_REJ_TOL_MAX, GATE_REJ_TOL_FRAC * th_rej))
    rej_ok  = abs(obs_rej - th_rej) <= rej_tol
    pk_tol  = max(GATE_PK_TOL_MIN, min(GATE_PK_TOL_MAX, GATE_PK_TOL_FRAC * p_k_th))
    pk_ok   = abs(p_k_obs - p_k_th) <= pk_tol

    # Physics — v1.0.9 §Physics / §Fix 4 (one-sided)
    phys_viol = obs_thru > PHYSICS_CEILING
    phys_sigma = float(agg_row.get("physics_sigma", 0.0))
    phys_fail = phys_viol and phys_sigma > PHYSICS_SIGMA_FAIL

    return {
        "thru": thru_ok, "rej": rej_ok, "pk": pk_ok,
        "physics_violation": phys_viol,
        "physics_sigma": phys_sigma,
        "physics_fail": phys_fail,
    }

def recompute_status(agg_row, gates):
    """v1.0.9 §Decision 3 Fix 1 — recompute gate_status independently."""
    if agg_row.get("measurement_status") == "MEASUREMENT_FAILURE":
        return "MEASUREMENT_FAILURE"
    if gates["physics_fail"]:
        return "MEASUREMENT_FAILURE"
    if gates["thru"] and gates["rej"] and gates["pk"]:
        return "PASS"
    return "FAIL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--aggregate", required=True)
    args = ap.parse_args()

    report = load_csv(args.report)
    aggregate = load_csv(args.aggregate)

    # v1.0.9 — Enforce zero duplicates (paste-integrity check)
    if len(report) != len({r["lambda"] for r in report}):
        print(f"ERROR: duplicate lambdas in report — paste-integrity failure", file=sys.stderr)
        return 2
    if len(aggregate) != len({r["lambda"] for r in aggregate}):
        print(f"ERROR: duplicate lambdas in aggregate — cannot have two rows per λ", file=sys.stderr)
        return 2

    by_lam_rep = {r["lambda"]: r for r in report}
    by_lam_agg = {r["lambda"]: r for r in aggregate}

    # v1.0.9 — Enforce zero dropped trials (no manifest salvage in v1.6.2)
    for lam, row in by_lam_agg.items():
        if int(row.get("dropped_trials", 0)) > 0:
            print(f"ERROR: lambda {lam} has {row['dropped_trials']} dropped trials. "
                  f"Re-run required; v1.0.9 dropped-row rule does not permit manifest-based "
                  f"salvage in v1.6.2.", file=sys.stderr)
            return 2

    # v1.0.9 §Dropped-row rule — lambdas must match
    if set(by_lam_rep) != set(by_lam_agg):
        print(f"ERROR: lambda sets differ. report={sorted(by_lam_rep)} agg={sorted(by_lam_agg)}",
              file=sys.stderr)
        return 2

    any_fail = False
    for lam in sorted(by_lam_rep):
        rep, agg = by_lam_rep[lam], by_lam_agg[lam]
        print(f"\n=== lambda {lam} ===")

        # Table A — paste-integrity
        table_a_pass = True
        for col in TABLE_A:
            if col not in rep or col not in agg:
                print(f"ERROR: missing column {col}", file=sys.stderr)
                return 2
            res = compare_table_a(rep, agg, col)
            tag = "PASS" if res["pass"] else "FAIL"
            print(f"  A.{col:20s} {tag}  expected={res['expected']} actual={res['actual']} tol={res['tolerance']}")
            if not res["pass"]:
                table_a_pass = False
                any_fail = True

        # Table B — §8 gates, independent recompute
        gates = eval_gates(agg)
        diff_gate_status = recompute_status(agg, gates)
        print(f"  B.gates  thru={gates['thru']} rej={gates['rej']} pk={gates['pk']} "
              f"phys_viol={gates['physics_violation']} phys_sigma={gates['physics_sigma']:.3f} "
              f"phys_fail={gates['physics_fail']}")

        # Cross-check biconditional — v1.0.9 §Decision 3 Fix 1
        rep_is_mf = rep["Status"] == "MEASUREMENT_FAILURE"
        agg_is_mf = agg.get("measurement_status") == "MEASUREMENT_FAILURE"
        bicond_ok = (rep_is_mf == agg_is_mf)
        print(f"  X.status  {rep['Status']} vs recomputed {diff_gate_status}  "
              f"bicond_ok={bicond_ok}")
        if not bicond_ok:
            any_fail = True

        # Also: report Status must match recomputed status
        if rep["Status"] != diff_gate_status:
            print(f"  X.verdict FAIL: report.Status={rep['Status']} != recomputed={diff_gate_status}")
            any_fail = True

    return 0 if not any_fail else 1


if __name__ == "__main__":
    sys.exit(main())
