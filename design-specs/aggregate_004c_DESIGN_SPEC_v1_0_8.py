#!/usr/bin/env python3
# aggregate_004c_DESIGN_SPEC_v1_0_8.py
# DESIGN-SPEC DRAFT — NOT HASHED, NOT FOR EXECUTION UNTIL REVIEWED AND SAVED
# Implements aggregation pipeline from EXPERIMENT 004c aggregate.py + diff.py DESIGN-SPEC v1.0.8
# Every decision-relevant line carries # v1.0.8 §N

import argparse
import csv
import sys
from collections import defaultdict

# ---- §8 gate thresholds from v1.6.2, embedded as literals ----
GATE_THRU_TOL       = 3.0     # v1.0.8 §Decision 3 Table B
GATE_REJ_TOL_MAX    = 3.0     # v1.0.8 §Decision 3 Table B
GATE_REJ_TOL_MIN    = 0.5     # v1.0.8 §Decision 3 Table B
GATE_REJ_TOL_FRAC   = 0.25    # v1.0.8 §Decision 3 Table B
GATE_PK_TOL_MAX     = 0.03    # v1.0.8 §Decision 3 Table B
GATE_PK_TOL_MIN     = 0.005   # v1.0.8 §Decision 3 Table B
GATE_PK_TOL_FRAC    = 0.20    # v1.0.8 §Decision 3 Table B
PHYSICS_CEILING     = 102.0   # v1.0.8 §Physics
PHYSICS_SIGMA_FAIL  = 3.0     # v1.0.8 §Physics

# ---- §6 report column order (from generator.py LOG_HEADER — 20 columns) ----
REPORT_COLUMNS = [
    "lambda", "rho", "Off.Load", "Th.Thru", "Obs.Thru",
    "Th.Rej", "Obs.Rej", "Obs.MeanN", "P_K_Obs", "P_K_Th",
    "TimeAtFull_s", "p99_N", "MeanResp_ms_Server", "MeanResp_ms_Client",
    "Served", "Rejected_503", "Timeout", "Refused", "Reset", "Status",
]

# ---- Audit columns appended at end of aggregated.csv — v1.0.8 §Decision 3 ----
AUDIT_COLUMNS = [
    "n_trials", "total_time_agg", "dropped_trials",
    "measurement_status", "physics_violation", "physics_sigma",
]

# Row field indices after split on ' | ' — mirrors generator.py row format
(I_LAMBDA, I_RHO, I_OFFLOAD, I_TH_THRU, I_OBS_THRU,
 I_TH_REJ, I_OBS_REJ, I_MEANN, I_PK_OBS, I_PK_TH,
 I_TAF, I_P99, I_RSRV, I_RCLI,
 I_SERVED, I_REJ, I_TIMEOUT, I_REFUSED, I_RESET, I_STATUS) = range(20)


def parse_trial_row(line):
    """Return dict if line matches per-trial row, else None."""
    if "|" not in line:
        return None
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != len(REPORT_COLUMNS):
        return None
    try:
        return {
            "lambda": float(parts[I_LAMBDA]),
            "rho": float(parts[I_RHO]),
            "off_load": float(parts[I_OFFLOAD]),
            "th_thru": float(parts[I_TH_THRU]),
            "obs_thru": float(parts[I_OBS_THRU]),
            "obs_rej_raw": float(parts[I_OBS_REJ]),
            "obs_meanN": float(parts[I_MEANN]),
            "p_k_obs": float(parts[I_PK_OBS]),
            "p_k_th": float(parts[I_PK_TH]),
            "time_at_full": float(parts[I_TAF]),
            "p99": int(parts[I_P99]),
            "mean_resp_srv": float(parts[I_RSRV]),
            "mean_resp_cli": float(parts[I_RCLI]),
            "served": int(parts[I_SERVED]),
            "rejected": int(parts[I_REJ]),
            "timeout": int(parts[I_TIMEOUT]),
            "refused": int(parts[I_REFUSED]),
            "reset": int(parts[I_RESET]),
            "status": parts[I_STATUS],
        }
    except (ValueError, IndexError):
        return None


def derive_total_time(t):
    """v1.0.8 §Decision 2 (v1.0.3 fix): served/obs_thru primary, time_at_full/p_k_obs fallback."""
    if t["served"] > 0 and t["obs_thru"] > 0:
        return t["served"] / t["obs_thru"], False
    if t["p_k_obs"] > 0 and t["time_at_full"] > 0:
        return t["time_at_full"] / t["p_k_obs"], True
    return 0.0, True  # INVALID_DATA


def aggregate_lambda(lam, trials):
    """v1.0.8 §Decision 2 — aggregate one lambda's 10 trials."""
    n = len(trials)
    tts = []
    invalid_count = 0
    for t in trials:
        tt, inv = derive_total_time(t)
        tts.append(tt)
        if inv:
            invalid_count += 1
    total_time_agg = sum(tts)
    if total_time_agg <= 0:
        return {"error": f"INVALID: all total_time_i zero at lambda {lam}"}

    served_agg   = sum(t["served"]   for t in trials)
    rejected_agg = sum(t["rejected"] for t in trials)
    timeout_agg  = sum(t["timeout"]  for t in trials)
    refused_agg  = sum(t["refused"]  for t in trials)
    reset_agg    = sum(t["reset"]    for t in trials)
    taf_agg      = sum(t["time_at_full"] for t in trials)

    # v1.0.8 §Decision 2 formulas
    obs_thru = served_agg / total_time_agg
    obs_rej  = rejected_agg / total_time_agg  # v1.0.2/v1.0.3: rate, req/s
    p_k_obs  = taf_agg / total_time_agg
    obs_meanN = sum(t["obs_meanN"] * tt for t, tt in zip(trials, tts)) / total_time_agg

    w_srv = served_agg
    mean_resp_srv = (sum(t["mean_resp_srv"] * t["served"] for t in trials) / w_srv
                     if w_srv > 0 else 0.0)
    w_cli = sum(t["served"] + t["rejected"] for t in trials)
    mean_resp_cli = (sum(t["mean_resp_cli"] * (t["served"] + t["rejected"]) for t in trials) / w_cli
                     if w_cli > 0 else 0.0)

    p99_agg = max(t["p99"] for t in trials)  # v1.0.8 §Decision 2: max, filed as bound

    # Theoretical columns — v1.0.8 §Decision 2 Fix 2
    rho       = trials[0]["rho"]
    off_load  = trials[0]["off_load"]
    th_thru   = trials[0]["th_thru"]
    p_k_th    = trials[0]["p_k_th"]
    th_rej    = lam * p_k_th  # v1.0.3 correction: computed, not from generator

    # Consistency check across trials
    for col, val in [("rho", rho), ("off_load", off_load),
                     ("th_thru", th_thru), ("p_k_th", p_k_th)]:
        for i, t in enumerate(trials[1:], 1):
            if abs(t[col] - val) > 1e-9:
                return {"error": f"Inconsistent {col} at trial {i}: {t[col]} vs {val}"}

    # measurement_status — v1.0.8 §Decision 3 Fix 1
    mf = any(t["status"] == "MEASUREMENT_FAILURE" for t in trials) or invalid_count > 0
    measurement_status = "MEASUREMENT_FAILURE" if mf else "COMPLETE"

    # Gate evaluation — v1.0.8 §Decision 3 Table B
    thru_ok = abs(obs_thru - th_thru) <= GATE_THRU_TOL
    rej_tol = max(GATE_REJ_TOL_MIN, min(GATE_REJ_TOL_MAX, GATE_REJ_TOL_FRAC * th_rej))
    rej_ok  = abs(obs_rej - th_rej) <= rej_tol
    pk_tol  = max(GATE_PK_TOL_MIN, min(GATE_PK_TOL_MAX, GATE_PK_TOL_FRAC * p_k_th))
    pk_ok   = abs(p_k_obs - p_k_th) <= pk_tol

    # Physics — v1.0.8 §Physics
    phys_viol = obs_thru > PHYSICS_CEILING
    if n > 1:
        sample_thrus = [t["served"] / tt if tt > 0 else 0.0 for t, tt in zip(trials, tts)]
        mu = sum(sample_thrus) / n
        var = sum((x - mu) ** 2 for x in sample_thrus) / (n - 1)
        std = var ** 0.5
        se = std / (n ** 0.5) if std > 0 else 0.0
        if phys_viol:
            phys_sigma = (obs_thru - PHYSICS_CEILING) / se if se > 0 else float("inf")
        else:
            phys_sigma = (obs_thru - PHYSICS_CEILING) / se if se > 0 else 0.0
    else:
        phys_sigma = float("inf") if phys_viol else 0.0

    # Combined status — v1.0.8 §Decision 3 Fix 1
    if measurement_status == "MEASUREMENT_FAILURE":
        status = "MEASUREMENT_FAILURE"
    elif phys_viol and phys_sigma > PHYSICS_SIGMA_FAIL:  # v1.0.8 §Fix 4: one-sided
        status = "MEASUREMENT_FAILURE"
    elif thru_ok and rej_ok and pk_ok:
        status = "PASS"
    else:
        status = "FAIL"

    return {
        "lambda": lam, "rho": rho, "Off.Load": off_load,
        "Th.Thru": th_thru, "Obs.Thru": obs_thru,
        "Th.Rej": th_rej, "Obs.Rej": obs_rej,
        "Obs.MeanN": obs_meanN,
        "P_K_Obs": p_k_obs, "P_K_Th": p_k_th,
        "TimeAtFull_s": taf_agg, "p99_N": p99_agg,
        "MeanResp_ms_Server": mean_resp_srv, "MeanResp_ms_Client": mean_resp_cli,
        "Served": served_agg, "Rejected_503": rejected_agg,
        "Timeout": timeout_agg, "Refused": refused_agg, "Reset": reset_agg,
        "Status": status,
        "n_trials": n, "total_time_agg": total_time_agg,
        "dropped_trials": 0,  # set by main if n < expected
        "measurement_status": measurement_status,
        "physics_violation": int(phys_viol), "physics_sigma": phys_sigma,
    }


def format_row(agg):
    return [
        f"{agg['lambda']:.4f}", f"{agg['rho']:.4f}", f"{agg['Off.Load']:.4f}",
        f"{agg['Th.Thru']:.2f}", f"{agg['Obs.Thru']:.2f}",
        f"{agg['Th.Rej']:.2f}", f"{agg['Obs.Rej']:.2f}",
        f"{agg['Obs.MeanN']:.4f}",
        f"{agg['P_K_Obs']:.4f}", f"{agg['P_K_Th']:.4f}",
        f"{agg['TimeAtFull_s']:.6f}", f"{agg['p99_N']}",
        f"{agg['MeanResp_ms_Server']:.2f}", f"{agg['MeanResp_ms_Client']:.2f}",
        f"{agg['Served']}", f"{agg['Rejected_503']}",
        f"{agg['Timeout']}", f"{agg['Refused']}", f"{agg['Reset']}",
        agg["Status"],
        f"{agg['n_trials']}", f"{agg['total_time_agg']:.6f}", f"{agg['dropped_trials']}",
        agg["measurement_status"],
        f"{agg['physics_violation']}", f"{agg['physics_sigma']:.4f}",
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--expected-trials", type=int, default=10)
    args = ap.parse_args()

    by_lambda = defaultdict(list)
    with open(args.input) as f:
        for line in f:
            row = parse_trial_row(line)
            if row:
                by_lambda[row["lambda"]].append(row)

    rows_out = []
    for lam in sorted(by_lambda):
        trials = by_lambda[lam]
        if len(trials) > args.expected_trials:
            print(f"ERROR: lambda {lam} has {len(trials)} rows, expected ≤ {args.expected_trials}",
                  file=sys.stderr)
            return 2
        agg = aggregate_lambda(lam, trials)
        if "error" in agg:
            print(f"ERROR: {agg['error']}", file=sys.stderr)
            return 2
        agg["dropped_trials"] = args.expected_trials - len(trials)
        if agg["dropped_trials"] > 0:
            print(f"WARNING: lambda {lam} has {len(trials)}/{args.expected_trials} rows — "
                  f"DROPPED_ROW rule requires manifest and report note", file=sys.stderr)
        rows_out.append(format_row(agg))

    with open(args.output, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(REPORT_COLUMNS + AUDIT_COLUMNS)
        w.writerows(rows_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
