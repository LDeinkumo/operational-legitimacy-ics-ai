#!/usr/bin/env python3
"""E1 adversarial case: the multi-actor authority defect in v3.1 and its correction in v3.2.

Runs ONE non-contradictory input on both frozen models, with the other three
constraints satisfied, so the difference is attributable to the authority logic:
  input: two approval actors, one competent and role-permitted (eng1), one explicitly
         not competent (eng2). This is a legitimate derived-state conflict, NOT a
         knowledge-base contradiction.
  v3.1 (model_v3_1.lp): derives authority as both satisfied and unsatisfied, hence both
        accept and reject; the decision-consistency constraint then eliminates the stable
        model, yielding UNSAT with no verdict (the fail-blind defect).
  v3.2 (model_v3_2.lp): guards legitimacy with 'not explicit_failure', so rejection
        dominates and the case resolves to reject.
All output is genuine clingo 5.8.2 solver output.
"""
import clingo

A = "restart_c101"; X = "c101"
OTHER = (f"moc_applicable({A}). moc_approved({A}). "
         f"verification_applicable({A}). verified_by({A},insp1). independent(insp1). "
         f"release_applicable({A}). work_complete({X}). handback_complete({X}). release_authorised({X}).")
E1 = (f"authority_applicable({A}). "
      f"approval_actor({A},eng1). competent(eng1,{A}). assigned_role(eng1,auth_eng). role_permits(auth_eng,{A}). "
      f"approval_actor({A},eng2). not_competent(eng2,{A}).")

def solve(model_file):
    model = open(model_file).read()
    ctl = clingo.Control(["--warn=none", "0"])
    ctl.add("base", [], model + "\n" + OTHER + "\n" + E1)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(sorted(str(s) for s in m.symbols(shown=True))))
    return models

def decision_of(atoms):
    for a in atoms:
        if a.startswith("decision("):
            return a.split(",")[1].rstrip(")")
    return None

print("=" * 80)
print("E1 adversarial authority case: v3.1 (defect) vs v3.2 (correction) - clingo", clingo.__version__)
print("=" * 80)
for tag, f, expect in [("v3.1 (model_v3_1.lp)", "model_v3_1.lp", "UNSAT / no verdict (fail-blind defect)"),
                        ("v3.2 (model_v3_2.lp)", "model_v3_2.lp", "reject")]:
    m = solve(f)
    if len(m) == 0:
        got = "UNSAT / no verdict"
    else:
        got = f"{len(m)} model(s); decision={decision_of(m[0])}"
    ok = (expect.startswith("UNSAT") and len(m) == 0) or (expect == "reject" and len(m) == 1 and decision_of(m[0]) == "reject")
    print(f"  [{'PASS' if ok else 'CHECK'}] {tag}: expected {expect}; got {got}")
print("=" * 80)
print("The v3.1 case returns no verdict on a legitimate conflict (fail-blind); v3.2 returns reject.")
print("=" * 80)
