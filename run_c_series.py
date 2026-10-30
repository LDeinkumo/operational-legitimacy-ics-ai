#!/usr/bin/env python3
"""C-series: end-to-end cross-layer composition.

Pipeline per case:
  STL trace --stl_monitor--> PA verdict (pass/fail/unknown)
  OL facts  --clingo(model_v3_2.lp)--> OL decision (accept/reject/withhold)
  (OL decision + pa fact) --clingo(compose.lp)--> final decision

Both layers are the FROZEN artefacts; compose.lp is a separate module.
All output is genuine (real STL monitor + real clingo). Expected finals preregistered.
"""
import clingo
from stl_monitor import monitor, PASS, FAIL, UNK
from run_t_series import PHI1, PHI2, PHI3   # reuse the frozen property classes

A = "restart_c101"; X = "c101"
OL_MODEL  = open("model_v3_2.lp").read()
COMPOSE   = open("compose.lp").read()

# --- OL fact-sets (drive the frozen OL reasoner) ------------------------------
def ol_facts(kind):
    base_ok = (f"moc_applicable({A}). moc_approved({A}). "
               f"verification_applicable({A}). verified_by({A},insp1). independent(insp1). "
               f"release_applicable({A}). work_complete({X}). handback_complete({X}). release_authorised({X}). "
               f"authority_applicable({A}). ")
    if kind == "accept":
        return base_ok + f"approval_actor({A},eng1). competent(eng1,{A}). assigned_role(eng1,auth_eng). role_permits(auth_eng,{A})."
    if kind == "reject":   # authority explicitly unsatisfied
        return base_ok + f"approval_actor({A},eng1). not_competent(eng1,{A})."
    if kind == "withhold": # verification evidence unknown
        return (f"moc_applicable({A}). moc_approved({A}). "
                f"verification_applicable({A}). "                      # applicable but no verified_by/independent
                f"release_applicable({A}). work_complete({X}). handback_complete({X}). release_authorised({X}). "
                f"authority_applicable({A}). approval_actor({A},eng1). competent(eng1,{A}). assigned_role(eng1,auth_eng). role_permits(auth_eng,{A}).")
    raise ValueError(kind)

# --- STL traces -> real PA verdicts -------------------------------------------
TRACES = {
    "pass":    (PHI1(4), {"p":[0.0,0.2,-0.3,0.1,0.0]}),      # T1  -> pass
    "fail":    (PHI1(3), {"p":[0.0,0.5,1.3,0.2]}),           # T2  -> fail
    "unknown": (PHI2(4), {"d":[0,0,0,0,1],"a":[0,0,0,0,0]}), # T6  -> unknown
}
def pa_verdict(kind):
    phi, sig = TRACES[kind]
    v, _ = monitor(phi, sig)
    return v   # 'pass' | 'fail' | 'unknown'

def ol_decision(kind):
    ctl = clingo.Control(["--warn=none", "0"])
    ctl.add("b", [], OL_MODEL + "\n" + ol_facts(kind))
    ctl.ground([("b", [])])
    out = []
    ctl.solve(on_model=lambda m: out.append([str(s) for s in m.symbols(shown=True)]))
    if len(out) != 1: return None
    for a in out[0]:
        if a.startswith("decision("): return a.split(",")[1].rstrip(")")
    return None

def final_decision(ol_kind, pa_kind):
    pa = pa_verdict(pa_kind)
    ctl = clingo.Control(["--warn=none", "0"])
    ctl.add("b", [], OL_MODEL + "\n" + COMPOSE + "\n" + ol_facts(ol_kind) + f" pa({pa}).")
    ctl.ground([("b", [])])
    out = []
    ctl.solve(on_model=lambda m: out.append([str(s) for s in m.symbols(shown=True)]))
    if len(out) != 1: return pa, None
    fin = None
    for a in out[0]:
        if a.startswith("final("): fin = a.split(",")[1].rstrip(")")
    return pa, fin

# --- C-series: (id, PA source, OL source, expected final, note) ---------------
C = [
 ("C1", "pass",    "accept",   "accept",   "physically safe + procedurally authorised"),
 ("C2", "pass",    "reject",   "reject",   "*** HEADLINE: physically safe + procedurally UNAUTHORISED ***"),
 ("C3", "fail",    "accept",   "reject",   "physically UNSAFE + procedurally authorised (PA necessity)"),
 ("C4", "fail",    "reject",   "reject",   "both fail"),
 ("C5", "unknown", "accept",   "withhold", "PA unknown + OL accept -> insufficient basis"),
 ("C6", "pass",    "withhold", "withhold", "PA pass + OL withhold (evidence gap)"),
 ("C7", "unknown", "reject",   "reject",   "OL reject decisive despite PA unknown"),
]

print("="*90)
print("C-SERIES — cross-layer composition (real STL PA  x  frozen OL decision  ->  final)")
print("="*90)
print(f"{'ID':4} {'PA(STL)':9} {'OL(clingo)':11} {'FINAL':9} {'exp':9} {'':4} note")
print("-"*90)
ok = 0
for cid, pa_src, ol_src, exp, note in C:
    olv = ol_decision(ol_src)
    pav, fin = final_decision(ol_src, pa_src)
    good = fin == exp
    ok += good
    print(f"{cid:4} {pav:9} {olv:11} {str(fin):9} {exp:9} {'PASS' if good else '*FAIL*':4} {note}")
print("-"*90)
print(f"C-series matching preregistered finals: {ok}/{len(C)}")
print("="*90)
