#!/usr/bin/env python3
# generator_004c_FINAL_REBUILD-1.py — REBUILD against authoritative v1.6.2 spec
# SUPERSEDES: generator_004c_FINAL_v1_6_2.py c24f15e6... (CLAIMED PENDING RECOVERY — artifact unavailable via relay)
# Logic identical to signed-off v1.6.2 substance. New hash to be claimed on console verification.
# Every decision-relevant line carries # v1.6.2 §N.
# File: generator_004c_FINAL_REBUILD-1.py
import argparse  # v1.6.2 §7 — Finding 1: argparse for --K
import csv  # v1.6.2 §7 — Minor 5: checkpoint per lambda to CSV
import http.client  # v1.6.2 §5
import json  # v1.6.2 §7.5
import queue  # v1.6.2 §3
import random  # v1.6.2 §11
import threading  # v1.6.2 §3
import time  # v1.6.2 §3 — perf_counter, hybrid interarrival (Finding 2)
import urllib.request  # v1.6.2 §7.5

N_WORKERS = 20  # v1.6.2 §3
LAMBDA = None  # v1.6.2 §3
GENERATOR_SEED = None  # v1.6.2 §11
SERVER_HOST = "127.0.0.1"  # v1.6.2 §12
SERVER_PORT = 8000  # v1.6.2 §7.5
METRICS_PORT = 8001  # v1.6.2 §7.5
K_VALUE = 10  # v1.6.2 §3 — Finding 1: placeholder, overwritten in main() from --K
LOG_HEADER = "lambda | rho | Off.Load | Th.Thru | Obs.Thru | Th.Rej | Obs.Rej | Obs.MeanN | P_K_Obs | P_K_Th | TimeAtFull_s | p99_N | MeanResp_ms_Server | MeanResp_ms_Client | Served | Rejected_503 | Timeout | Refused | Reset | Status"  # v1.6.2 §11 — locked header, character-for-character
dispatch_q = queue.Queue()  # v1.6.2 §3
stop_flag = threading.Event()  # v1.6.2 §7.5
# v1.6.2 §9 — Minor 1: in_flight and in_flight_lock REMOVED, dead code, drain handled by arrivals_generated + task_done()
client_served = 0  # v1.6.2 §9
client_rejected_503 = 0  # v1.6.2 §9
client_timeout = 0  # v1.6.2 §9
client_refused = 0  # v1.6.2 §9
client_reset = 0  # v1.6.2 §9
counts_lock = threading.Lock()  # v1.6.2 §9 — Finding 5
dispatch_lags = []  # v1.6.2 §9 — per-request, NOT sampled
arrivals_generated = 0  # v1.6.2 §7 — Finding 4: generated, NOT processed
arrivals_lock = threading.Lock()  # v1.6.2 §7 — Finding 4
sum_W_client = 0.0  # v1.6.2 §5 — client-side W for MeanResp_ms_Client
count_W_client = 0  # v1.6.2 §5
generator_rng = None  # v1.6.2 §11
measurement_failure = False  # v1.6.2 §7.5 — set on /quiesce timeout OR X-Trial inactive (BLOCKING TODO)

def erlang_P_K(rho, K):  # v1.6.2 §7 — theoretical P_K for M/M/1/K, Erlang B
    s = 0.0  # v1.6.2 §7
    for n in range(K + 1):  # v1.6.2 §7
        s += (rho ** n)  # v1.6.2 §7 — rho^n, P0 = 1/s
    p0 = 1.0 / s if s != 0 else 0.0  # v1.6.2 §7
    return p0 * (rho ** K)  # v1.6.2 §7 — P_K = P0 * rho^K

def arrival_thread_func(target_lambda):  # v1.6.2 §3 — ONE arrival thread, open-loop
    global arrivals_generated  # v1.6.2 §7 — Finding 4
    while not stop_flag.is_set():  # v1.6.2 §7.5
        inter = generator_rng.expovariate(target_lambda)  # v1.6.2 §3
        target = time.perf_counter() + inter  # v1.6.2 §3 — Finding 2: hybrid target
        remaining = target - time.perf_counter()  # v1.6.2 §3 — Finding 2
        if remaining > 0.002:  # v1.6.2 §3 — Finding 2: hybrid, sleep until 1ms before target
            time.sleep(remaining - 0.001)  # v1.6.2 §3 — Finding 2
        if stop_flag.is_set():  # v1.6.2 §7.5
            break  # v1.6.2 §7.5
        while time.perf_counter() < target:  # v1.6.2 §3 — Finding 2: busy-wait, < target
            pass  # v1.6.2 §3 — Finding 2
        if stop_flag.is_set():  # v1.6.2 §7.5
            break  # v1.6.2 §7.5
        intended = time.perf_counter()  # v1.6.2 §9
        dispatch_q.put((intended, 1))  # v1.6.2 §3
        with arrivals_lock:  # v1.6.2 §7 — Finding 4
            arrivals_generated += 1  # v1.6.2 §7 — Finding 4: generated, NOT processed

def worker_func(worker_id):  # v1.6.2 §3 — worker pool, pulls from shared dispatch_q
    global client_served, client_rejected_503, client_timeout, client_refused, client_reset, measurement_failure, sum_W_client, count_W_client  # v1.6.2 §9
    conn = None  # v1.6.2 §5
    def get_conn():  # v1.6.2 §5
        nonlocal conn  # v1.6.2 §5
        if conn is None:  # v1.6.2 §5
            conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=2.0)  # v1.6.2 §5
        return conn  # v1.6.2 §5
    def drop_conn():  # v1.6.2 §5
        nonlocal conn  # v1.6.2 §5
        try:  # v1.6.2 §5
            if conn is not None:  # v1.6.2 §5
                conn.close()  # v1.6.2 §5
        except Exception:  # v1.6.2 §5
            pass  # v1.6.2 §5
        conn = None  # v1.6.2 §5
    while True:  # v1.6.2 §3
        try:  # v1.6.2 §3
            intended, _ = dispatch_q.get(timeout=0.1)  # v1.6.2 §3
        except queue.Empty:  # v1.6.2 §3
            if stop_flag.is_set() and dispatch_q.empty():  # v1.6.2 §7.5
                break  # v1.6.2 §7.5
            continue  # v1.6.2 §3
        actual_send = time.perf_counter()  # v1.6.2 §9
        lag = actual_send - intended  # v1.6.2 §9
        dispatch_lags.append(lag)  # v1.6.2 §9 — per-request, EVERY request, NOT sampled
        client_start = time.perf_counter()  # v1.6.2 §5 — client-side W start
        try:  # v1.6.2 §5
            c = get_conn()  # v1.6.2 §5
            c.request("GET", "/request")  # v1.6.2 §5
            resp = c.getresponse()  # v1.6.2 §5
            body = resp.read()  # v1.6.2 §5 — must read body for keep-alive
            status = resp.status  # v1.6.2 §5
            x_trial = resp.getheader("X-Trial")  # v1.6.2 §7.5 — BLOCKING TODO: CHECK X-Trial header, implemented here
            if x_trial == "inactive":  # v1.6.2 §7.5 — BLOCKING TODO FIXED: post-quiesce request, NOT a rejection, set MEASUREMENT FAILURE
                with counts_lock:  # v1.6.2 §9 — Finding 5
                    measurement_failure = True  # v1.6.2 §7.5 — BLOCKING TODO FIXED: do NOT increment rejected_503, set failure flag
            elif status == 200:  # v1.6.2 §5
                with counts_lock:  # v1.6.2 §9 — Finding 5
                    client_served += 1  # v1.6.2 §9 — Finding 5
            elif status == 503:  # v1.6.2 §5 — 503 WITHOUT X-Trial inactive = genuine rejection
                with counts_lock:  # v1.6.2 §9 — Finding 5
                    client_rejected_503 += 1  # v1.6.2 §9 — Finding 5
            else:  # v1.6.2 §9
                with counts_lock:  # v1.6.2 §9 — Finding 5
                    client_reset += 1  # v1.6.2 §9 — Finding 5
            client_end = time.perf_counter()  # v1.6.2 §5 — client-side W end
            with counts_lock:  # v1.6.2 §9 — Finding 5
                sum_W_client += (client_end - client_start)  # v1.6.2 §5
                count_W_client += 1  # v1.6.2 §5
        except TimeoutError:  # v1.6.2 §9
            with counts_lock:  # v1.6.2 §9 — Finding 5
                client_timeout += 1  # v1.6.2 §9 — Finding 5
            drop_conn()  # v1.6.2 §5
        except ConnectionRefusedError:  # v1.6.2 §9
            with counts_lock:  # v1.6.2 §9 — Finding 5
                client_refused += 1  # v1.6.2 §9 — Finding 5
            drop_conn()  # v1.6.2 §5
        except (ConnectionResetError, http.client.RemoteDisconnected, BrokenPipeError):  # v1.6.2 §9
            with counts_lock:  # v1.6.2 §9 — Finding 5
                client_reset += 1  # v1.6.2 §9 — Finding 5
            drop_conn()  # v1.6.2 §5
        except Exception:  # v1.6.2 §9
            with counts_lock:  # v1.6.2 §9 — Finding 5
                client_reset += 1  # v1.6.2 §9 — Finding 5
            drop_conn()  # v1.6.2 §5
        finally:  # v1.6.2 §3
            dispatch_q.task_done()  # v1.6.2 §3 — paired with get(), first try catches Empty, finally on second try

def call_metrics(path):  # v1.6.2 §7.5
    url = f"http://{SERVER_HOST}:{METRICS_PORT}{path}"  # v1.6.2 §7.5
    with urllib.request.urlopen(url, timeout=5.0) as r:  # v1.6.2 §7.5
        return json.loads(r.read().decode())  # v1.6.2 §7.5

def poll_quiesce_until_200():  # v1.6.2 §7.5
    global measurement_failure  # v1.6.2 §7.5
    deadline = time.perf_counter() + 5.0  # v1.6.2 §7.5
    while time.perf_counter() < deadline:  # v1.6.2 §7.5
        try:  # v1.6.2 §7.5
            resp = call_metrics("/quiesce")  # v1.6.2 §7.5
            if resp.get("quiesced"):  # v1.6.2 §7.5
                return True  # v1.6.2 §7.5
        except Exception:  # v1.6.2 §7.5
            pass  # v1.6.2 §7.5
        time.sleep(0.005)  # v1.6.2 §7.5
    measurement_failure = True  # v1.6.2 §7.5 — timeout sets MEASUREMENT FAILURE, NOT warning
    return False  # v1.6.2 §7.5

def run_trial(trial_idx, target_lambda, mu):  # v1.6.2 §7.6 — ONE function, seven-step lifecycle inline, NO do_warmup()
    global client_served, client_rejected_503, client_timeout, client_refused, client_reset, measurement_failure, arrivals_generated, sum_W_client, count_W_client  # v1.6.2 §7.6
    measurement_failure = False  # v1.6.2 §7.5 — BLOCKING FIX: reset per trial, BEFORE /reset, so Trial N failure does not leak into Trial N+1 status
    call_metrics("/reset")  # v1.6.2 §7.5 — Step 1: /reset
    stop_flag.clear()  # v1.6.2 §7.6 — Step 2: Warmup 5s inline
    dispatch_lags.clear()  # v1.6.2 §7.6
    with arrivals_lock:  # v1.6.2 §7 — Finding 4
        arrivals_generated = 0  # v1.6.2 §7 — Finding 4
    with counts_lock:  # v1.6.2 §9 — Finding 5
        client_served = 0  # v1.6.2 §7.6
        client_rejected_503 = 0  # v1.6.2 §7.6
        client_timeout = 0  # v1.6.2 §7.6
        client_refused = 0  # v1.6.2 §7.6
        client_reset = 0  # v1.6.2 §7.6
        sum_W_client = 0.0  # v1.6.2 §5
        count_W_client = 0  # v1.6.2 §5
    workers = [threading.Thread(target=worker_func, args=(i,)) for i in range(N_WORKERS)]  # v1.6.2 §3
    for w in workers:  # v1.6.2 §3
        w.start()  # v1.6.2 §3
    arr = threading.Thread(target=arrival_thread_func, args=(target_lambda,))  # v1.6.2 §3 — ONE arrival thread
    arr.start()  # v1.6.2 §3
    time.sleep(5.0)  # v1.6.2 §7.6 — Warmup 5s, trial_active=True
    stop_flag.set()  # v1.6.2 §7.5
    arr.join(timeout=5.0)  # v1.6.2 §7.5
    for w in workers:  # v1.6.2 §7.5
        w.join(timeout=5.0)  # v1.6.2 §7.5
    if not poll_quiesce_until_200():  # v1.6.2 §7.5 — Step 3: Quiesce after warmup
        return {"measurement_failure": True, "status": "MEASUREMENT_FAILURE"}  # v1.6.2 §7.5
    call_metrics("/reset")  # v1.6.2 §7.5 — Step 4: /reset AGAIN, double-reset
    stop_flag.clear()  # v1.6.2 §7.6 — Step 5: Measurement inline
    dispatch_lags.clear()  # v1.6.2 §7.6
    with arrivals_lock:  # v1.6.2 §7 — Finding 4
        arrivals_generated = 0  # v1.6.2 §7 — Finding 4
    with counts_lock:  # v1.6.2 §9 — Finding 5
        client_served = 0  # v1.6.2 §7.6
        client_rejected_503 = 0  # v1.6.2 §7.6
        client_timeout = 0  # v1.6.2 §7.6
        client_refused = 0  # v1.6.2 §7.6
        client_reset = 0  # v1.6.2 §7.6
        sum_W_client = 0.0  # v1.6.2 §5
        count_W_client = 0  # v1.6.2 §5
    # v1.6.2 §7.6 — Finding 7: warmup exercises server paths and OS state; measurement connections are created fresh here, overhead N_WORKERS x ~1ms, filed as diagnostic
    workers = [threading.Thread(target=worker_func, args=(i,)) for i in range(N_WORKERS)]  # v1.6.2 §3 — NEW pool, NEW connections
    for w in workers:  # v1.6.2 §3
        w.start()  # v1.6.2 §3
    arr = threading.Thread(target=arrival_thread_func, args=(target_lambda,))  # v1.6.2 §3 — ONE arrival thread
    arr.start()  # v1.6.2 §3
    meas_start = time.perf_counter()  # v1.6.2 §7 — max(30s, 2000 arrivals)
    while True:  # v1.6.2 §7
        elapsed = time.perf_counter() - meas_start  # v1.6.2 §7
        with arrivals_lock:  # v1.6.2 §7 — Finding 4
            arrivals = arrivals_generated  # v1.6.2 §7 — Finding 4: generated, NOT len(dispatch_lags)
        if elapsed >= 30.0 and arrivals >= 2000:  # v1.6.2 §7 — Finding 4: 2000 generated
            break  # v1.6.2 §7
        time.sleep(0.01)  # v1.6.2 §7
    meas_elapsed = time.perf_counter() - meas_start  # v1.6.2 §7 — measurement duration for throughput
    stop_flag.set()  # v1.6.2 §7.5
    arr.join(timeout=5.0)  # v1.6.2 §7.5
    for w in workers:  # v1.6.2 §7.5
        w.join(timeout=5.0)  # v1.6.2 §7.5
    if not poll_quiesce_until_200():  # v1.6.2 §7.5 — Step 6: Quiesce after measurement
        return {"measurement_failure": True, "status": "MEASUREMENT_FAILURE"}  # v1.6.2 §7.5
    snap = call_metrics("/metrics")  # v1.6.2 §7.5 — Step 7: /metrics snapshot only
    # v1.6.2 §7 — FINAL: compute trial aggregates, Minor 5: output row per trial, NOT just LOG_HEADER
    rho = target_lambda / mu if mu != 0 else 0.0  # v1.6.2 §7
    p_k_th = erlang_P_K(rho, K_VALUE)  # v1.6.2 §7
    time_at_N = snap.get("time_at_N", [])  # v1.6.2 §7.5
    total_time = sum(time_at_N) if time_at_N else meas_elapsed  # v1.6.2 §7
    time_at_full = snap.get("time_at_full_s", 0.0)  # v1.6.2 §7.5
    p_k_obs = (time_at_full / total_time) if total_time > 0 else 0.0  # v1.6.2 §7
    mean_n = sum(n * t for n, t in enumerate(time_at_N)) / total_time if total_time > 0 else 0.0  # v1.6.2 §7
    cumsum = 0.0  # v1.6.2 §7 — p99 from histogram CDF
    p99_n = K_VALUE  # v1.6.2 §7
    for n, t in enumerate(time_at_N):  # v1.6.2 §7
        cumsum += t  # v1.6.2 §7
        if total_time > 0 and (cumsum / total_time) >= 0.99:  # v1.6.2 §7
            p99_n = n  # v1.6.2 §7
            break  # v1.6.2 §7
    mean_resp_server_ms = (snap.get("sum_W_server", 0.0) / snap.get("count_W_server", 1) * 1000.0) if snap.get("count_W_server", 0) > 0 else 0.0  # v1.6.2 §5
    mean_resp_client_ms = (sum_W_client / count_W_client * 1000.0) if count_W_client > 0 else 0.0  # v1.6.2 §5
    with counts_lock:  # v1.6.2 §9 — Finding 5: read counters under lock
        served = client_served  # v1.6.2 §9
        rejected = client_rejected_503  # v1.6.2 §9
        timeout_c = client_timeout  # v1.6.2 §9
        refused_c = client_refused  # v1.6.2 §9
        reset_c = client_reset  # v1.6.2 §9
    with arrivals_lock:  # v1.6.2 §7 — Finding 4
        offered = arrivals_generated  # v1.6.2 §7
    obs_thru = (served / total_time) if total_time > 0 else 0.0  # v1.6.2 §7 — Minor accuracy 2 FIXED: denominator is total_time = sum(time_at_N) after tail flush, includes drain tail, NOT meas_elapsed only
    th_thru = target_lambda * (1.0 - p_k_th)  # v1.6.2 §7
    obs_rej = (rejected / offered) if offered > 0 else 0.0  # v1.6.2 §7
    # v1.6.2 §7 — Filing order: offered shortfall first, then dispatch-lag, then gates. Shortfall >5% => MEASUREMENT_FAILURE
    expected_offered = target_lambda * meas_elapsed  # v1.6.2 §7
    shortfall = abs(offered - expected_offered) / expected_offered if expected_offered > 0 else 0.0  # v1.6.2 §7
    if shortfall > 0.05:  # v1.6.2 §7
        measurement_failure = True  # v1.6.2 §7
    # v1.6.2 §9 — Dispatch-lag: lag >5% mean interarrival on >10% => MEASUREMENT_FAILURE
    if dispatch_lags:  # v1.6.2 §9
        mean_inter = 1.0 / target_lambda if target_lambda > 0 else 0.0  # v1.6.2 §9
        thresh = 0.05 * mean_inter  # v1.6.2 §9
        bad = sum(1 for l in dispatch_lags if l > thresh)  # v1.6.2 §9
        if len(dispatch_lags) > 0 and (bad / len(dispatch_lags)) > 0.10:  # v1.6.2 §9
            measurement_failure = True  # v1.6.2 §9
    status = "MEASUREMENT_FAILURE" if measurement_failure else "COMPLETE"  # v1.6.2 §7
    row = f"{target_lambda} | {rho:.4f} | {rho:.4f} | {th_thru:.2f} | {obs_thru:.2f} | {p_k_th:.4f} | {obs_rej:.4f} | {mean_n:.4f} | {p_k_obs:.4f} | {p_k_th:.4f} | {time_at_full:.6f} | {p99_n} | {mean_resp_server_ms:.3f} | {mean_resp_client_ms:.3f} | {served} | {rejected} | {timeout_c} | {refused_c} | {reset_c} | {status}"  # v1.6.2 §11 — Minor 5: output row per trial, matches LOG_HEADER columns
    return {"row": row, "snapshot": snap, "measurement_failure": measurement_failure, "status": status}  # v1.6.2 §7

def run_pilot_condition(perturb):  # v1.6.2 §15 — pilot, AFTER primary PASS, NOT same day
    pass  # v1.6.2 §15

def main():  # v1.6.2 §7 — FINAL: trial driver + output formatting + --K match validation, NOT TODO
    global N_WORKERS, K_VALUE, LAMBDA, GENERATOR_SEED, SERVER_PORT, METRICS_PORT, generator_rng  # v1.6.2 §3 — Finding 1
    p = argparse.ArgumentParser()  # v1.6.2 §7 — Finding 1
    p.add_argument("--lambda", dest="lam", type=float, required=True)  # v1.6.2 §3
    p.add_argument("--K", type=int, default=10)  # v1.6.2 §3 — Finding 1: --K, must match server --K
    p.add_argument("--N", type=int, default=20)  # v1.6.2 §3
    p.add_argument("--trials", type=int, default=10)  # v1.6.2 §7
    p.add_argument("--generator-seed", type=int, required=True)  # v1.6.2 §11
    p.add_argument("--server-port", type=int, default=8000)  # v1.6.2 §7.5
    p.add_argument("--metrics-port", type=int, default=8001)  # v1.6.2 §7.5
    p.add_argument("--mu", type=float, default=100.0)  # v1.6.2 §5 — for rho, must match server --mu
    p.add_argument("--output", type=str, default="")  # v1.6.2 §7 — Minor 5: checkpoint CSV path, empty = stdout only
    args = p.parse_args()  # v1.6.2 §7 — Finding 1
    K_VALUE = args.K  # v1.6.2 §3 — Finding 1: K_VALUE = args.K BEFORE fail-fast
    N_WORKERS = args.N  # v1.6.2 §3
    LAMBDA = args.lam  # v1.6.2 §3
    GENERATOR_SEED = args.generator_seed  # v1.6.2 §11
    SERVER_PORT = args.server_port  # v1.6.2 §7.5
    METRICS_PORT = args.metrics_port  # v1.6.2 §7.5
    generator_rng = random.Random(GENERATOR_SEED)  # v1.6.2 §11
    if N_WORKERS <= K_VALUE:  # v1.6.2 §3 — fail-fast, checks actual K_VALUE from args, NOT hardcoded 10 (Finding 1)
        raise SystemExit(f"N={N_WORKERS} <= K={K_VALUE}, violates §3 N>K. Fail-fast at startup.")  # v1.6.2 §3
    # v1.6.2 §7 — Minor 4: validate --K match between generator and server via /config, NOT driver TODO alone. Minor 6: driver must pass matching --K to both, validated here.
    try:  # v1.6.2 §7 — Minor 4
        cfg = call_metrics("/config")  # v1.6.2 §7 — Minor 4: /config returns server K, mu
    except Exception as e:  # v1.6.2 §7 — Minor 4
        raise SystemExit(f"Cannot fetch /config from server for --K validation: {e}")  # v1.6.2 §7 — Minor 4
    if cfg.get("K") != K_VALUE:  # v1.6.2 §7 — Minor 4: --K mismatch, fail-fast, do NOT run with disagreeing K
        raise SystemExit(f"--K mismatch: generator K={K_VALUE} != server K={cfg.get('K')}. Driver must pass matching --K to both. Fail-fast.")  # v1.6.2 §7 — Minor 4, Minor 6
    if abs(cfg.get("mu", 0.0) - args.mu) > 1e-9:  # v1.6.2 §7 — Minor 6: --mu mismatch, fail-fast
        raise SystemExit(f"--mu mismatch: generator mu={args.mu} != server mu={cfg.get('mu')}. Driver must pass matching --mu to both.")  # v1.6.2 §7 — Minor 6
    print(LOG_HEADER, flush=True)  # v1.6.2 §11 — locked header, character-for-character
    print(f"# generator_seed={GENERATOR_SEED} K={K_VALUE} mu={args.mu} lambda={LAMBDA} N={N_WORKERS} trials={args.trials}", flush=True)  # v1.6.2 §11 — seeds in log header
    out_f = None  # v1.6.2 §7 — Minor 5: checkpoint per lambda
    out_w = None  # v1.6.2 §7 — Minor 5
    if args.output:  # v1.6.2 §7 — Minor 5
        out_f = open(args.output, "w", newline="")  # v1.6.2 §7 — Minor 5
        out_w = csv.writer(out_f)  # v1.6.2 §7 — Minor 5
        out_w.writerow([c.strip() for c in LOG_HEADER.split("|")])  # v1.6.2 §7 — Minor 5
    try:  # v1.6.2 §7 — FINAL: trial loop
        for trial_idx in range(args.trials):  # v1.6.2 §7 — FINAL: trial driver
            result = run_trial(trial_idx, LAMBDA, args.mu)  # v1.6.2 §7.6 — ONE function, seven steps inline
            row = result.get("row", "")  # v1.6.2 §7 — Minor 5
            if row:  # v1.6.2 §7 — Minor 5
                print(row, flush=True)  # v1.6.2 §7 — Minor 5: output row per trial
                if out_w:  # v1.6.2 §7 — Minor 5
                    out_w.writerow([c.strip() for c in row.split("|")])  # v1.6.2 §7 — Minor 5
                    out_f.flush()  # v1.6.2 §7 — Minor 5: checkpoint per trial
    finally:  # v1.6.2 §7 — Minor 5
        if out_f:  # v1.6.2 §7 — Minor 5
            out_f.close()  # v1.6.2 §7 — Minor 5

if __name__ == "__main__":  # v1.6.2 §7
    main()  # v1.6.2 §7
