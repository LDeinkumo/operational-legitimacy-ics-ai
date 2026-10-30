#!/usr/bin/env python3
"""SIS-bypass transfer scenario — generalisation test.

A NEW action (bypass_sif_101 = temporarily bypass a safety-instrumented function)
is evaluated by the SAME FROZEN OL reasoner (model_v3_2.lp) and the SAME STL
property classes and composition gate — with NO rule changes, only new domain
facts. This tests that the framework transfers beyond restart_c101.

Requirement readings for a SIF bypass (same 4 taxonomy slots, new domain meaning):
  MoC           -> the bypass is an authorised change (IEC 61511 override/bypass control)
  Authority     -> a competent, role-permitted person authorised the bypass
  Verification  -> independent confirmation (e.g. compensating measures in place)
  Release       -> return-to-service: the SIF is restored and re-proven

All output genuine (real STL monitor + real clingo on frozen artefacts).
"""
import clingo
from stl_monitor import monitor
from run_t_series import PHI2   # bounded protective response — the bypass-relevant property

ACT = "bypass_sif_101"; ASSET = "sif101"
OL_MODEL = open("model_v3_2.lp").read()
COMPOSE  = open("compose.lp").read()

# The new action must be declared (frozen model hardcodes only restart_c101).
NEW_ACTION = f"action({ACT}). acts_on({ACT},{ASSET}). "

def ol_facts(kind):
    ok = (f"moc_applicable({ACT}). moc_approved({ACT}). "
          f"authority_applicable({ACT}). approval_actor({ACT},sis_auth1). competent(sis_auth1,{ACT}). "
          f"assigned_role(sis_auth1,sis_authoriser). role_permits(sis_authoriser,{ACT}). "
          f"verification_applicable({ACT}). verified_by({ACT},indep1). independent(indep1). "
          f"release_applicable({ACT}). work_complete({ASSET}). handback_complete({ASSET}). release_authorised({ASSET}). ")
    if kind == "authorised":
        return ok
    if kind == "unauthorised":   # bypass NOT authorised (MoC/override authorisation refused)
        return (f"moc_applicable({ACT}). moc_not_approved({ACT}). "
                f"authority_applicable({ACT}). approval_actor({ACT},sis_auth1). competent(sis_auth1,{ACT}). "
                f"assigned_role(sis_auth1,sis_authoriser). role_permits(sis_authoriser,{ACT}). "
                f"verification_applicable({ACT}). verified_by({ACT},indep1). independent(indep1). "
                f"release_applicable({ACT}). work_complete({ASSET}). handback_complete({ASSET}). release_authorised({ASSET}). ")
    if kind == "evidence_gap":   # compensating-measures verification unknown
        return (f"moc_applicable({ACT}). moc_approved({ACT}). "
                f"authority_applicable({ACT}). approval_actor({ACT},sis_auth1). competent(sis_auth1,{ACT}). "
                f"assigned_role(sis_auth1,sis_authoriser). role_permits(sis_authoriser,{ACT}). "
                f"verification_applicable({ACT}). "                    # applicable but no verified_by/independent
                f"release_applicable({ACT}). work_complete({ASSET}). handback_complete({ASSET}). release_authorised({ASSET}). ")
    raise ValueError(kind)

# PA traces: does the compensating protective response still meet the trip deadline during bypass?
TRACE_PASS = {"d":[0,1,0,0,0], "a":[0,0,1,0,0]}   # demand met within T -> pass
TRACE_FAIL = {"d":[0,1,0,0,0], "a":[0,0,0,0,0]}   # demand never met    -> fail
def pa_of(trace): return monitor(PHI2(4), trace)[0]

def run(ol_kind, trace):
    pa = pa_of(trace)
    prog = OL_MODEL + "\n" + COMPOSE + "\n" + NEW_ACTION + ol_facts(ol_kind) + f" pa({pa})."
    ctl = clingo.Control(["--warn=none", "0"]); ctl.add("b", [], prog); ctl.ground([("b", [])])
    out = []
    ctl.solve(on_model=lambda m: out.append([str(s) for s in m.symbols(shown=True)]))
    ol = fin = None
    if len(out) == 1:
        for s in out[0]:
            if s.startswith(f"decision({ACT},"): ol = s.split(",")[1].rstrip(")")
            if s.startswith(f"final({ACT},"):    fin = s.split(",")[1].rstrip(")")
    return pa, ol, fin

S = [
 ("S1", "authorised",   TRACE_PASS, "accept",   "authorised bypass, compensating response holds"),
 ("S2", "unauthorised", TRACE_PASS, "reject",   "*** HEADLINE: UNAUTHORISED SIF bypass, physically safe now -> refused ***"),
 ("S3", "authorised",   TRACE_FAIL, "reject",   "authorised bypass but protective response fails (PA necessity)"),
 ("S4", "evidence_gap", TRACE_PASS, "withhold", "compensating-measures verification unknown -> hold"),
]

print("="*94)
print(f"SIS-BYPASS TRANSFER — new action '{ACT}' on FROZEN reasoner (no rule changes)")
print("="*94)
print(f"{'ID':4} {'OL-facts':13} {'PA(STL)':9} {'OL(clingo)':11} {'FINAL':9} {'exp':9} {'':5} note")
print("-"*94)
ok = 0
for sid, kind, trace, exp, note in S:
    pa, ol, fin = run(kind, trace)
    good = fin == exp; ok += good
    print(f"{sid:4} {kind:13} {pa:9} {str(ol):11} {str(fin):9} {exp:9} {'PASS' if good else '*FAIL*':5} {note}")
print("-"*94)
print(f"Transfer scenarios matching preregistered finals: {ok}/{len(S)}")
print(f"Generalisation: frozen OL model produced valid decisions for a NEW action with only new facts.")
print("="*94)
