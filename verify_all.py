#!/usr/bin/env python3
"""One-command verification of every reported result, from the repository root.

Runs each experiment in this directory and checks its outcome against the value
reported in the manuscript. Exit code 0 iff all checks pass. Run:  python3 verify_all.py

Requires: Python 3.11+, and the clingo Python module (see requirements.txt) for the
Answer Set Programming experiments. The RTAMT cross-validation is optional and checked
separately (see README); this script does not require RTAMT.
"""
import subprocess, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

# --- dependency check: fail early with a helpful message, not a traceback -------
try:
    import clingo  # noqa: F401
except ImportError:
    sys.stderr.write(
        "ERROR: the 'clingo' Python module is not installed.\n"
        "The Answer Set Programming experiments (P-series, integrity, E1, C-series,\n"
        "SIS-transfer and the authority probe) require clingo 5.8.2.\n\n"
        "Install it with:\n"
        "    python3 -m pip install -r requirements.txt\n"
        "or:\n"
        "    python3 -m pip install clingo==5.8.2\n\n"
        "Then re-run:  python3 verify_all.py\n"
        "(The STL-only suite, run_t_series.py, does not need clingo and can be run on its own.)\n"
    )
    sys.exit(2)

def run(script):
    """Run a repo script; return its stdout. Fail clearly if it errors."""
    path = os.path.join(HERE, script)
    if not os.path.exists(path):
        sys.stderr.write(f"ERROR: expected script not found: {script}\n")
        sys.exit(3)
    p = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd=HERE)
    if p.returncode != 0:
        sys.stderr.write(f"ERROR: {script} exited with code {p.returncode}.\n")
        tail = (p.stderr or p.stdout or "").strip().splitlines()[-8:]
        sys.stderr.write("  " + "\n  ".join(tail) + "\n")
        sys.exit(4)
    return p.stdout

checks = []
def check(label, got, want):
    checks.append((label, str(got), str(want), str(got) == str(want)))

def grab(output, pattern, script):
    """Regex-extract with a clear error instead of an AttributeError on no match."""
    m = re.search(pattern, output)
    if m is None:
        sys.stderr.write(
            f"ERROR: could not find the expected result pattern in the output of {script}.\n"
            f"  pattern: {pattern}\n"
            f"  last lines of output:\n    " + "\n    ".join(output.strip().splitlines()[-6:]) + "\n"
        )
        sys.exit(5)
    return m

# P-series on the frozen v3.2 model (manuscript Tables 1 and 2)
p = run("run_p_series_v32.py")
m = grab(p, r"matching expectation:\s*(\d+)/(\d+)", "run_p_series_v32.py")
check("P-series decisions (v3.2)", f"{m.group(1)}/{m.group(2)}", "12/12")
check("Integrity cases UNSAT (v3.2)", p.count("UNSAT (correct)"), 3)

# E1 adversarial defect vs fix (manuscript Section 6.2 / ledger Table L3)
e = run("run_e1_comparison.py")
check("E1 v3.1 fail-blind + v3.2 reject", e.count("[PASS]"), 2)

# T-series STL (manuscript Table 3)
t = run("run_t_series.py")
m = grab(t, r"verdicts:\s*(\d+)/(\d+)", "run_t_series.py")
check("T-series verdicts", f"{m.group(1)}/{m.group(2)}", "9/9")
check("T-series ground-truth checks (all ok)", t.count("[ok]"), 4)
check("T-series no failed check", "[X]" in t, False)

# Cross-layer composition (manuscript Table 4 and text)
c = run("run_c_series.py")
m = grab(c, r"matching preregistered finals:\s*(\d+)/(\d+)", "run_c_series.py")
check("C-series finals", f"{m.group(1)}/{m.group(2)}", "7/7")

# SIS-bypass transfer (manuscript Table 5)
s = run("run_transfer_sis.py")
m = grab(s, r"matching preregistered finals:\s*(\d+)/(\d+)", "run_transfer_sis.py")
check("S-series finals", f"{m.group(1)}/{m.group(2)}", "4/4")

# Authority boundary probe (manuscript Section 7 limitation / ledger L3 note)
a = run("run_authority_adversarial.py")
check("Authority probe: 3 single-model, no fail-blind", a.count("1 model(s)"), 3)

print("=" * 78)
print("VERIFY ALL: reported results vs this run")
print("=" * 78)
allok = True
for label, got, want, ok in checks:
    allok &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {label:44s} got={got:10s} want={want}")
print("=" * 78)
print("ALL CHECKS PASS" if allok else "*** SOME CHECKS FAILED ***")
sys.exit(0 if allok else 1)
