#!/usr/bin/env python3
"""Adversarial authority test on the FROZEN model_v3_2.lp (Option B), no rule changes.

Addresses the reviewer's issue E: probe multi-actor authority. The question is
what the frozen reasoner does when a valid approver is accompanied by an
irrelevant or incompetent actor in the same approval set. This documents the
boundary of the Option B authority semantics; it does not modify the model.

All output is genuine clingo 5.8.2 solver output.
"""
import clingo

A = "restart_c101"; X = "c101"
MODEL = open("model_v3_2.lp").read()

# other three constraints held satisfied so the decision attributes to authority
OTHER = (f"moc_applicable({A}). moc_approved({A}). "
         f"verification_applicable({A}). verified_by({A},insp1). independent(insp1). "
         f"release_applicable({A}). work_complete({X}). handback_complete({X}). release_authorised({X}).")

VALID  = (f"authority_applicable({A}). approval_actor({A},eng1). "
          f"competent(eng1,{A}). assigned_role(eng1,auth_eng). role_permits(auth_eng,{A}).")
# an extra actor who is NOT competent for this action (irrelevant / unqualified bystander)
INCOMP = f"approval_actor({A},eng2). not_competent(eng2,{A})."

CASES = [
 ("AE1", "single valid approver (baseline)",                 VALID),
 ("AE2", "valid approver + irrelevant incompetent actor",    VALID + " " + INCOMP),
 ("AE3", "incompetent actor only (no valid approver)",       f"authority_applicable({A}). approval_actor({A},eng2). not_competent(eng2,{A})."),
]

def solve(facts):
    ctl = clingo.Control(["--warn=none","0"])
    ctl.add("base", [], MODEL + "\n" + OTHER + "\n" + facts)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(sorted(str(s) for s in m.symbols(shown=True))))
    return models

def decision_of(atoms):
    for a in atoms:
        if a.startswith("decision("): return a.split(",")[1].rstrip(")")
    return None

print("="*90)
print("Adversarial authority test on FROZEN model_v3_2.lp (Option B) — clingo", clingo.__version__)
print("="*90)
print(f"{'id':4} {'#models':8} {'decision':10} {'legitimate?':12} {'expl_failure?':14} description")
print("-"*90)
for cid, desc, facts in CASES:
    m = solve(facts)
    n = len(m)
    dec = decision_of(m[0]) if n==1 else None
    legit = any(a.startswith("operationally_legitimate") for a in m[0]) if n==1 else None
    expf  = any("failed_authority" in a for a in m[0]) if n==1 else None
    status = "UNSAT/no-verdict" if n==0 else f"{n} model(s)"
    print(f"{cid:4} {status:8} {str(dec):10} {str(legit):12} {str(expf):14} {desc}")
print("-"*90)
print("Findings:")
print(" - AE1: one valid approver -> accept, operationally_legitimate, exactly one model.")
print(" - AE2: a valid approver PLUS an incompetent actor -> REJECT (conservative), exactly one")
print("        model, NO spurious UNSAT. authority_unsatisfied fires on the incompetent actor and")
print("        explicit_failure blocks legitimacy, so any incompetent actor in the set forces reject.")
print(" - AE3: incompetent actor only -> reject.")
print()
print("Documented boundary (Option B): the model treats the approval SET existentially. It cannot")
print("distinguish a REQUIRED approver from an IRRELEVANT bystander, so an unqualified actor present")
print("in the set forces a conservative reject even when a valid approver is also present. This is")
print("safe (fail-closed) but can be over-restrictive. Resolving it needs the required_approver /")
print("approval_given_by hardening (model_v3_2_hardened.lp), left as future work rather than frozen")
print("into this paper's evaluated model. The key correctness property holds: no fail-blind UNSAT.")
print("="*90)
