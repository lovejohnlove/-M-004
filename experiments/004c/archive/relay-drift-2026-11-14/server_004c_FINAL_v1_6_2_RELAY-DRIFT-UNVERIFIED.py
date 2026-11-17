# server_004c_FINAL_v1_6_2.py — FINAL, AGAINST v1.6.2, FOR REVIEW BEFORE HASH
# Implements v1.6.2 design-spec + X-Trial TODO + minor fixes 1-6. Do NOT run until hash after final review.
# Every decision-relevant line carries # v1.6.2 §N.
# File: server_004c_FINAL_v1_6_2.py
import argparse  # v1.6.2 §7
import http.server  # v1.6.2 §5
import json  # v1.6.2 §7.5
import os  # v1.6.2 §12
import random  # v1.6.2 §11
import resource  # v1.6.2 §15.8
import threading  # v1.6.2 §3
import time  # v1.6.2 §5 — perf_counter only, never time.time()

if os.name != "posix":  # v1.6.2 §12
    raise SystemExit("004c requires Linux per v1.6.2 §12")  # v1.6.2 §12

K = 10  # v1.6.2 §3 — placeholder, overwritten in main() from --K
MU = 100.0  # v1.6.2 §5 — placeholder, overwritten in main() from --mu
admission_sem = None  # v1.6.2 §4 — created in main() AFTER parsing --K
service_sem = None  # v1.6.2 §4 — created in main(), Semaphore(1)
server_rng = None  # v1.6.2 §11 — set in main() from --server-seed
integrator_lock = threading.Lock()  # v1.6.2 §4
time_at_full = 0.0  # v1.6.2 §4
time_at_N = [0.0] * 11  # v1.6.2 §4
last_transition = None  # v1.6.2 §4
diag_counter = 0  # v1.6.2 §4
sum_W_server = 0.0  # v1.6.2 §5
count_W_server = 0  # v1.6.2 §5
served_count = 0  # v1.6.2 §9
rejected_count = 0  # v1.6.2 §9
server_exception_count = 0  # v1.6.2 §9 — Minor 3: exceptions in service path are counted, NOT silent 1-request loss
trial_active = False  # v1.6.2 §7.5
trial_lock = threading.Lock()  # v1.6.2 §7.5 — held across check + diag increment (Finding 3)
last_snapshot = {}  # v1.6.2 §7.5
last_activity = time.perf_counter()  # v1.6.2 §7.5 — last served/rejected/admitted attempt, see /quiesce docstring Minor 2

def update_integrator_locked(new_occupancy):  # v1.6.2 §4
    global time_at_full, last_transition, diag_counter  # v1.6.2 §4
    now = time.perf_counter()  # v1.6.2 §5 — perf_counter, never time.time()
    if last_transition is None:  # v1.6.2 §4
        last_transition = now  # v1.6.2 §4
        diag_counter = new_occupancy  # v1.6.2 §4
        return  # v1.6.2 §4
    dt = now - last_transition  # v1.6.2 §4
    if dt < 0:  # v1.6.2 §4
        dt = 0.0  # v1.6.2 §4
    old = diag_counter  # v1.6.2 §4
    if 0 <= old <= K:  # v1.6.2 §4 — K from main(), K=11 uses index 11
        time_at_N[old] += dt  # v1.6.2 §4
        if old == K:  # v1.6.2 §4
            time_at_full += dt  # v1.6.2 §4
    last_transition = now  # v1.6.2 §4
    diag_counter = new_occupancy  # v1.6.2 §4

def handle_request_logic():  # v1.6.2 §4
    global served_count, rejected_count, sum_W_server, count_W_server, last_activity, server_exception_count  # v1.6.2 §4, §5, §9
    with trial_lock:  # v1.6.2 §7.5 — Finding 3: hold trial_lock across check + increment
        if not trial_active:  # v1.6.2 §7.5
            return 599  # v1.6.2 §7.5 — inactive sentinel, MainHandler maps to 503 + X-Trial inactive
        with integrator_lock:  # v1.6.2 §4 — lock ordering trial_lock -> integrator_lock
            update_integrator_locked(diag_counter + 1)  # v1.6.2 §4
    admitted = False  # v1.6.2 §4
    try:  # v1.6.2 §4
        admitted = admission_sem.acquire(blocking=False)  # v1.6.2 §4
    except Exception:  # v1.6.2 §4
        with integrator_lock:  # v1.6.2 §4
            update_integrator_locked(diag_counter - 1)  # v1.6.2 §4
        raise  # v1.6.2 §4
    if not admitted:  # v1.6.2 §4 — Finding 6: single lock block
        with integrator_lock:  # v1.6.2 §4 — Finding 6: SINGLE with block
            update_integrator_locked(diag_counter - 1)  # v1.6.2 §4
            rejected_count += 1  # v1.6.2 §9 — SAME lock block, Finding 6 fixed
        last_activity = time.perf_counter()  # v1.6.2 §7.5 — Minor 2: last served/rejected/admitted attempt
        return 503  # v1.6.2 §5
    acquired_service = False  # v1.6.2 §4
    try:  # v1.6.2 §4
        service_sem.acquire()  # v1.6.2 §4
        acquired_service = True  # v1.6.2 §4
        try:  # v1.6.2 §5 — Minor 3: inner try/except counts service exceptions, NOT silent loss
            enter = time.perf_counter()  # v1.6.2 §5
            service_time = server_rng.expovariate(MU)  # v1.6.2 §11 — §5 Exp(100)
            target = enter + service_time  # v1.6.2 §5
            remaining = target - time.perf_counter()  # v1.6.2 §5
            if remaining > 0.002:  # v1.6.2 §5
                time.sleep(remaining - 0.001)  # v1.6.2 §5
            while time.perf_counter() < target:  # v1.6.2 §5 — < target, NOT <=
                pass  # v1.6.2 §5
            exit_ = time.perf_counter()  # v1.6.2 §5
            with integrator_lock:  # v1.6.2 §5
                sum_W_server += (exit_ - enter)  # v1.6.2 §5
                count_W_server += 1  # v1.6.2 §5
        except Exception:  # v1.6.2 §9 — Minor 3: count exception, then re-raise so finally releases semaphores
            with integrator_lock:  # v1.6.2 §9 — Minor 3
                server_exception_count += 1  # v1.6.2 §9 — Minor 3: exception counted in snapshot, NOT silent
            raise  # v1.6.2 §9 — Minor 3
        with integrator_lock:  # v1.6.2 §9
            served_count += 1  # v1.6.2 §9
        last_activity = time.perf_counter()  # v1.6.2 §7.5 — Minor 2
        return 200  # v1.6.2 §5
    finally:  # v1.6.2 §4 — counter-before-release, then service, then admission
        with integrator_lock:  # v1.6.2 §4
            update_integrator_locked(diag_counter - 1)  # v1.6.2 §4
        if acquired_service:  # v1.6.2 §4
            service_sem.release()  # v1.6.2 §4 — service FIRST
        admission_sem.release()  # v1.6.2 §4 — admission SECOND

class MainHandler(http.server.BaseHTTPRequestHandler):  # v1.6.2 §5
    protocol_version = "HTTP/1.1"  # v1.6.2 §5
    def do_GET(self):  # v1.6.2 §5
        if self.path != "/request":  # v1.6.2 §5
            body = b"NOT FOUND"  # v1.6.2 §5
            self.send_response(404)  # v1.6.2 §5
            self.send_header("Content-Length", str(len(body)))  # v1.6.2 §5
            self.end_headers()  # v1.6.2 §5
            self.wfile.write(body)  # v1.6.2 §5
            return  # v1.6.2 §5
        try:  # v1.6.2 §9 — Minor 3: catch service exception, return 500, exception already counted
            status = handle_request_logic()  # v1.6.2 §4 — atomic check+increment inside, NO separate check-then-act (Finding 3)
        except Exception:  # v1.6.2 §9 — Minor 3
            body = b"SERVER EXCEPTION"  # v1.6.2 §9 — Minor 3
            self.send_response(500)  # v1.6.2 §9 — Minor 3
            self.send_header("Content-Length", str(len(body)))  # v1.6.2 §5
            self.end_headers()  # v1.6.2 §5
            self.wfile.write(body)  # v1.6.2 §5
            return  # v1.6.2 §9 — Minor 3
        if status == 599:  # v1.6.2 §7.5
            body = b"TRIAL INACTIVE"  # v1.6.2 §7.5
            self.send_response(503)  # v1.6.2 §7.5
            self.send_header("Content-Length", str(len(body)))  # v1.6.2 §5
            self.send_header("X-Trial", "inactive")  # v1.6.2 §7.5 — BLOCKING TODO: client MUST check this header, see generator.py
            self.end_headers()  # v1.6.2 §5
            self.wfile.write(body)  # v1.6.2 §5
            return  # v1.6.2 §7.5
        if status == 200:  # v1.6.2 §5
            body = b"OK"  # v1.6.2 §5
            self.send_response(200)  # v1.6.2 §5
        else:  # v1.6.2 §5
            body = b"REJECTED"  # v1.6.2 §5
            self.send_response(503)  # v1.6.2 §5
        self.send_header("Content-Length", str(len(body)))  # v1.6.2 §5
        self.end_headers()  # v1.6.2 §5
        self.wfile.write(body)  # v1.6.2 §5
    def log_message(self, *args):  # v1.6.2 §5
        pass  # v1.6.2 §5

def reset_trial_state_locked():  # v1.6.2 §7.5
    global time_at_full, time_at_N, last_transition, diag_counter, sum_W_server, count_W_server, served_count, rejected_count, last_snapshot, trial_active, server_exception_count  # v1.6.2 §7.5
    time_at_full = 0.0  # v1.6.2 §7.5
    time_at_N = [0.0] * (K + 1)  # v1.6.2 §7.5
    last_transition = time.perf_counter()  # v1.6.2 §7.5
    diag_counter = 0  # v1.6.2 §7.5
    sum_W_server = 0.0  # v1.6.2 §5
    count_W_server = 0  # v1.6.2 §5
    served_count = 0  # v1.6.2 §9
    rejected_count = 0  # v1.6.2 §9
    server_exception_count = 0  # v1.6.2 §9 — Minor 3: cleared on reset
    last_snapshot = {}  # v1.6.2 §7.5
    trial_active = True  # v1.6.2 §7.5

class MetricsHandler(http.server.BaseHTTPRequestHandler):  # v1.6.2 §7.5 — NO admission_sem, NO service_sem
    protocol_version = "HTTP/1.1"  # v1.6.2 §7.5
    def do_GET(self):  # v1.6.2 §7.5
        global trial_active, last_snapshot, last_activity  # v1.6.2 §7.5
        if self.path == "/reset":  # v1.6.2 §7.5
            with trial_lock:  # v1.6.2 §7.5 — trial_lock -> integrator_lock
                with integrator_lock:  # v1.6.2 §7.5
                    reset_trial_state_locked()  # v1.6.2 §7.5 — ONE function, called ONLY here
            self._json(200, {"reset": True})  # v1.6.2 §7.5
            return  # v1.6.2 §7.5
        if self.path == "/config":  # v1.6.2 §7 — Minor 4: /config returns K, mu so generator driver can validate --K match, NOT rely on driver TODO alone
            self._json(200, {"K": K, "mu": MU})  # v1.6.2 §7 — Minor 4
            return  # v1.6.2 §7 — Minor 4
        if self.path == "/quiesce":  # v1.6.2 §7.5 — 200 only when no served/rejected/admitted attempt in last 50ms AND diag_counter==0 (Minor 2: docstring fixed to attempted)
            idle_ms = (time.perf_counter() - last_activity) * 1000.0  # v1.6.2 §7.5 — Minor 2: last served/rejected/admitted attempt
            with trial_lock:  # v1.6.2 §7.5 — Finding 3: hold trial_lock across check + set
                with integrator_lock:  # v1.6.2 §7.5 — hold BOTH locks together
                    cur = diag_counter  # v1.6.2 §7.5
                    if cur == 0 and idle_ms >= 50.0:  # v1.6.2 §7.5
                        trial_active = False  # v1.6.2 §7.5
                        last_snapshot = {"time_at_full_s": time_at_full, "time_at_N": list(time_at_N), "sum_W_server": sum_W_server, "count_W_server": count_W_server, "served": served_count, "rejected_503": rejected_count, "server_exception": server_exception_count}  # v1.6.2 §7.5 — Minor 3: snapshot includes exception count
                        quiesced = True  # v1.6.2 §7.5
                    else:  # v1.6.2 §7.5
                        quiesced = False  # v1.6.2 §7.5
            if quiesced:  # v1.6.2 §7.5
                self._json(200, {"quiesced": True})  # v1.6.2 §7.5
            else:  # v1.6.2 §7.5
                self._json(503, {"quiesced": False, "diag_counter": cur, "last_activity_ms_ago": idle_ms})  # v1.6.2 §7.5
            return  # v1.6.2 §7.5
        if self.path == "/metrics":  # v1.6.2 §7.5
            self._json(200, last_snapshot)  # v1.6.2 §7.5
            return  # v1.6.2 §7.5
        self._json(404, {"error": "not found"})  # v1.6.2 §7.5
    def _json(self, code, obj):  # v1.6.2 §7.5
        body = json.dumps(obj).encode()  # v1.6.2 §7.5
        self.send_response(code)  # v1.6.2 §7.5
        self.send_header("Content-Type", "application/json")  # v1.6.2 §7.5
        self.send_header("Content-Length", str(len(body)))  # v1.6.2 §7.5
        self.end_headers()  # v1.6.2 §7.5
        self.wfile.write(body)  # v1.6.2 §7.5
    def log_message(self, *args):  # v1.6.2 §7.5
        pass  # v1.6.2 §7.5

def check_transport_limit(requested_K):  # v1.6.2 §15.8 — OS TRANSPORT, NOT semaphore
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)  # v1.6.2 §15.8
    needed = requested_K + 25  # v1.6.2 §15.8
    if soft < needed:  # v1.6.2 §15.8
        raise SystemExit(f"Transport limit: RLIMIT_NOFILE soft={soft} < needed={needed} for K={requested_K}. K=11 infeasible for OS transport, not semaphore. Drop K=11 with filed note per §15.8.")  # v1.6.2 §15.8
    return True  # v1.6.2 §15.8

def main():  # v1.6.2 §7 — FINAL: HTTP server startup implemented, NOT TODO
    global K, MU, admission_sem, service_sem, server_rng, time_at_N  # v1.6.2 §3
    p = argparse.ArgumentParser()  # v1.6.2 §7
    p.add_argument("--port", type=int, required=True)  # v1.6.2 §7.5
    p.add_argument("--metrics-port", type=int, required=True)  # v1.6.2 §7.5
    p.add_argument("--K", type=int, default=10)  # v1.6.2 §3
    p.add_argument("--mu", type=float, default=100.0)  # v1.6.2 §5
    p.add_argument("--server-seed", type=int, required=True)  # v1.6.2 §11
    args = p.parse_args()  # v1.6.2 §7
    K = args.K  # v1.6.2 §3
    MU = args.mu  # v1.6.2 §5
    check_transport_limit(K)  # v1.6.2 §15.8
    admission_sem = threading.Semaphore(K)  # v1.6.2 §4 — Semaphore(K) from --K
    service_sem = threading.Semaphore(1)  # v1.6.2 §4
    server_rng = random.Random(args.server_seed)  # v1.6.2 §11
    time_at_N = [0.0] * (K + 1)  # v1.6.2 §4
    print(f"server_seed={args.server_seed} K={K} mu={MU} port={args.port} metrics_port={args.metrics_port}", flush=True)  # v1.6.2 §11 — Minor 5: startup header, flush
    metrics_server = http.server.ThreadingHTTPServer(("127.0.0.1", args.metrics_port), MetricsHandler)  # v1.6.2 §7 — FINAL: metrics server startup
    metrics_thread = threading.Thread(target=metrics_server.serve_forever, daemon=True)  # v1.6.2 §7 — FINAL
    metrics_thread.start()  # v1.6.2 §7 — FINAL
    main_server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), MainHandler)  # v1.6.2 §7 — FINAL: main server startup
    try:  # v1.6.2 §7 — FINAL
        main_server.serve_forever()  # v1.6.2 §7 — FINAL
    except KeyboardInterrupt:  # v1.6.2 §7 — FINAL
        pass  # v1.6.2 §7 — FINAL
    finally:  # v1.6.2 §7 — FINAL
        main_server.shutdown()  # v1.6.2 §7 — FINAL
        metrics_server.shutdown()  # v1.6.2 §7 — FINAL

if __name__ == "__main__":  # v1.6.2 §7
    main()  # v1.6.2 §7
