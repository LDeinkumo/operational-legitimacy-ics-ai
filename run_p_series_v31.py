#!/usr/bin/env python3
"""Execute model_v3_1.lp (FROZEN, unmodified) against a controlled P-series.

Design: each P-case isolates ONE condition on ONE constraint while holding the
other three SATISFIED, so the decision and the explanation atoms attribute
cleanly. Integrity (INC) cases inject contradictory evidence and must be UNSAT.

All output is genuine clingo 5.8.2 solver output.
"""
import clingo

A = "restart_c101"
X = "c101"
MODEL = open("model_v3_1.lp").read()

# --- per-constraint fact builders (states: sat / unsat / unk_ev / unk_app / na)
def moc(s):
    return {
        "sat":    [f"moc_applicable({A}).", f"moc_approved({A})."],
        "unsat":  [f"moc_applicable({A}).", f"moc_not_approved({A})."],
        "unk_ev": [f"moc_applicable({A})."],
        "unk_app":[],
        "na":     [f"moc_not_applicable({A})."],
    }[s]

def auth(s):
    return {
        "sat":    [f"authority_applicable({A}).", f"approval_actor({A},eng1).",
                   f"competent(eng1,{A}).", f"assigned_role(eng1,auth_eng).",
                   f"role_permits(auth_eng,{A})."],
        "unsat":  [f"authority_applicable({A}).", f"approval_actor({A},eng1).",
                   f"not_competent(eng1,{A})."],
        "unk_ev": [f"authority_applicable({A})."],
        "unk_app":[],
        "na":     [f"authority_not_applicable({A})."],
    }[s]

def ver(s):
    return {
        "sat":    [f"verification_applicable({A}).", f"verified_by({A},insp1).",
                   f"independent(insp1)."],
        "unsat":  [f"verification_applicable({A}).", f"verification_not_completed({A})."],
        "unk_ev": [f"verification_applicable({A})."],
        "unk_app":[],
        "na":     [f"verification_not_applicable({A})."],
    }[s]

def rel(s):
    return {
        "sat":    [f"release_applicable({A}).", f"work_complete({X}).",
                   f"handback_complete({X}).", f"release_authorised({X})."],
        "unsat":  [f"release_applicable({A}).", f"release_not_authorised({X})."],
        "unk_ev": [f"release_applicable({A})."],
        "unk_app":[],
        "na":     [f"release_not_applicable({A})."],
    }[s]

def case(m, a, v, r, extra=None):
    f = moc(m) + auth(a) + ver(v) + rel(r) + (extra or [])
    return " ".join(f)

# --- P-series: (id, label, facts, expected_decision) --------------------------
P = [
    ("P1",  "All satisfied (accept control)",              case("sat","sat","sat","sat"),   "accept"),
    ("P2",  "MoC unsatisfied",                             case("unsat","sat","sat","sat"), "reject"),
    ("P3",  "MoC evidence unknown",                        case("unk_ev","sat","sat","sat"),"withhold"),
    ("P4",  "MoC applicability unknown",                   case("unk_app","sat","sat","sat"),"withhold"),
    ("P5",  "Authority unsatisfied",                       case("sat","unsat","sat","sat"), "reject"),
    ("P6",  "Authority evidence unknown",                  case("sat","unk_ev","sat","sat"),"withhold"),
    ("P7",  "Verification unsatisfied",                    case("sat","sat","unsat","sat"), "reject"),
    ("P8",  "Verification evidence unknown",               case("sat","sat","unk_ev","sat"),"withhold"),
    ("P9",  "Release unsatisfied",                         case("sat","sat","sat","unsat"), "reject"),
    ("P10", "Release evidence unknown",                    case("sat","sat","sat","unk_ev"),"withhold"),
    ("P11", "Multiple failures (MoC+Auth+Release)",        case("unsat","unsat","sat","unsat"),"reject"),
    ("P12", "All not-applicable (accept)",                 case("na","na","na","na"),       "accept"),
]

# --- Integrity cases: contradictory evidence must be UNSAT --------------------
INC = [
    ("INC1", "MoC approved AND not approved",
     f"moc_applicable({A}). moc_approved({A}). moc_not_approved({A})."),
    ("INC2", "Release authorised AND not authorised",
     f"release_applicable({A}). release_authorised({X}). release_not_authorised({X})."),
    ("INC3", "Verifier independent AND not independent",
     f"verification_applicable({A}). verified_by({A},insp1). independent(insp1). not_independent(insp1)."),
]


def solve(facts):
    ctl = clingo.Control(["--warn=none", "0"])  # 0 = enumerate all models
    ctl.add("base", [], MODEL + "\n" + facts)
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(sorted(str(s) for s in m.symbols(shown=True))))
    return models


def decision_of(atoms):
    for a in atoms:
        if a.startswith("decision("):
            return a.split(",")[1].rstrip(")")
    return None


def explain(atoms):
    return [a for a in atoms if a.startswith(("failed_", "unknown_", "operationally_legitimate"))]


print("=" * 82)
print("model_v3_1.lp (frozen) — P-series + integrity cases — clingo", clingo.__version__)
print("=" * 82)
ok = 0
for cid, label, facts, exp in P:
    models = solve(facts)
    n = len(models)
    dec = decision_of(models[0]) if n == 1 else None
    verdict = "PASS" if (n == 1 and dec == exp) else "*** CHECK ***"
    if n == 1 and dec == exp:
        ok += 1
    print(f"\n[{cid}] {label}")
    print(f"   #models={n}  expected={exp:9s} actual={str(dec):9s} {verdict}")
    if n == 1:
        ex = explain(models[0])
        print("   explanation atoms: " + (", ".join(a.replace(f"({A})","") for a in ex) or "(none)"))

print("\n" + "-" * 82)
print("Integrity cases (contradictory evidence MUST be UNSAT):")
for cid, label, facts in INC:
    models = solve(facts)
    status = "UNSAT (correct)" if len(models) == 0 else f"*** SAT with {len(models)} model(s) — integrity NOT enforced ***"
    print(f"   [{cid}] {label:42s} -> {status}")

print("\n" + "=" * 82)
print(f"P-series decisions matching expectation: {ok}/{len(P)}")
print("=" * 82)
