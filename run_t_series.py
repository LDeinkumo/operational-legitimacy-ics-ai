#!/usr/bin/env python3
"""T1-T9: three STL property classes over symbolic/normalised traces.

Produces the three-valued Physical-Admissibility (PA) verdict (pass/fail/unknown)
that replaces the pa/1 input fact in the cross-layer C-series.
All verdicts are computed by stl_monitor.py (transparent standard STL semantics);
expected verdicts are preregistered here BEFORE running.
"""
from stl_monitor import monitor, ev, PASS, FAIL, UNK

EPS = 0.2   # normalised stability band
T   = 2     # bounded-response deadline (steps)

# --- three property classes (normalised thresholds; setpoint = 0) -------------
# Phi1  operating-envelope invariant: G[0,H] (-1 <= p <= 1)
def PHI1(H): return ("G", 0, H, ("and", ("geq","p",-1.0), ("leq","p",1.0)))
# Phi2  bounded protective response: G[0,H]( d>=0.5 -> F[0,T] a>=0.5 )
def PHI2(H): return ("G", 0, H, ("implies", ("geq","d",0.5), ("F",0,T,("geq","a",0.5))))
# Phi3  bounded post-action stability: G[ts,te] |p| <= eps
def PHI3(ts,te): return ("G", ts, te, ("and", ("leq","p",EPS), ("geq","p",-EPS)))

# --- T-series: (id, class, formula, signals, expected_verdict, note) ----------
CASES = [
 ("T1","Phi1", PHI1(4), {"p":[0.0,0.2,-0.3,0.1,0.0]},                 PASS, "nominal, within envelope"),
 ("T2","Phi1", PHI1(3), {"p":[0.0,0.5,1.3,0.2]},                      FAIL, "excursion above +1 at t2"),
 ("T3","Phi1", PHI1(3), {"p":[0.0,0.9,0.95,0.8]},                     PASS, "near-boundary, small margin"),

 ("T4","Phi2", PHI2(4), {"d":[0,1,0,0,0],"a":[0,0,1,0,0]},            PASS, "demand@t1, response within T"),
 ("T5","Phi2", PHI2(4), {"d":[0,1,0,0,0],"a":[0,0,0,0,0]},            FAIL, "demand@t1, response never"),
 ("T6","Phi2", PHI2(4), {"d":[0,0,0,0,1],"a":[0,0,0,0,0]},            UNK,  "demand@t4(last): response window truncated"),

 ("T7","Phi3", PHI3(2,5), {"p":[0.8,0.4,0.15,0.1,-0.05,0.1]},         PASS, "settles inside band over window"),
 ("T8","Phi3", PHI3(2,5), {"p":[0.8,0.4,0.15,0.5,0.1,0.1]},           FAIL, "excursion (0.5) inside stability window"),
 ("T9","Phi3", PHI3(2,5), {"p":[0.8,0.4,0.15,0.1]},                   UNK,  "stability window extends beyond trace"),
]

def rr(r): return "None" if r is None else f"{r:+.3f}"

print("="*84)
print("STL T-series — three-valued PA verdicts (transparent monitor, standard STL robustness)")
print("="*84)
ok = 0
pa_verdicts = {}
for cid, cls, phi, sig, exp, note in CASES:
    v, r = monitor(phi, sig)
    good = v == exp
    ok += good
    pa_verdicts[cid] = v
    print(f"[{cid}] {cls:5s} expected={exp:7s} actual={v:7s} rob={rr(r):8s} {'PASS' if good else '*** MISMATCH ***'}  ({note})")

print("-"*84)
print(f"T-series matching preregistered verdicts: {ok}/{len(CASES)}")

# --- validation: hand-computed robustness ground truth (monitor self-check) ---
# Each check compares a MONITOR-COMPUTED robustness (left) against an independently
# hand-derived expected value (right). The T5 inner-response robustness is computed
# through the monitor at the demand instant (t=1), not asserted, so the check is
# genuinely independent of the value it is compared against.
_t5_sig   = {"d":[0,1,0,0,0], "a":[0,0,0,0,0]}
_t5_last  = min(len(v) for v in _t5_sig.values()) - 1
_t5_inF   = ev(("F",0,T,("geq","a",0.5)), 1, _t5_sig, _t5_last)[1]   # monitor-computed F[0,2](a>=0.5) at t=1
checks = [
 ("T1 rob == +0.700 (min of p+1 and 1-p over trace)", monitor(PHI1(4), {"p":[0.0,0.2,-0.3,0.1,0.0]})[1], 0.700),
 ("T3 rob == +0.050 (1 - 0.95)",                       monitor(PHI1(3), {"p":[0.0,0.9,0.95,0.8]})[1],     0.050),
 ("T5 inner-F rob @t1 == -0.500 (monitor-computed, a never reaches 0.5)", _t5_inF, -0.500),
 ("T5 top-level rob == -0.500 (monitor-computed over full formula)",      monitor(PHI2(4), _t5_sig)[1],   -0.500),
]
print("\nrobustness ground-truth checks:")
allok = True
for label, got, want in checks:
    passed = abs(got - want) < 1e-9
    allok &= passed
    print(f"  [{'ok' if passed else 'X'}] {label}: got {got:+.3f}")
print(f"\nPA verdicts for cross-layer C-series: {pa_verdicts}")
print("="*84)
