#!/usr/bin/env python3
"""Transparent discrete-time STL monitor with 3-valued online semantics.

Robustness (quantitative) semantics follow the standard recursive definition
(Fainekos & Pappas 2009; Donzé & Maler 2010):
    rob(x>=c, t)      = x[t] - c
    rob(x<=c, t)      = c - x[t]
    rob(not p, t)     = -rob(p, t)
    rob(p and q, t)   = min(rob(p,t), rob(q,t))
    rob(p or q, t)    = max(rob(p,t), rob(q,t))
    rob(G[a,b]p, t)   = min_{t' in [t+a,t+b]} rob(p, t')
    rob(F[a,b]p, t)   = max_{t' in [t+a,t+b]} rob(p, t')

Three-valued ONLINE extension for a finite trace prefix (last index = `last`):
a verdict is decisive iff it cannot change with future samples.
    - G is FAIL as soon as one instant in the (available) window violates.
    - G is PASS only if the whole window is available and all instants hold.
    - F is PASS as soon as one instant in the (available) window satisfies.
    - F is FAIL only if the whole window is available and none satisfy.
    - otherwise (needed samples lie beyond `last`): UNKNOWN.
This is exactly the "PA is three-valued (pass/fail/unknown)" behaviour the
cross-layer gate consumes.

Formula AST (plain tuples):
    ("geq", var, c) ("leq", var, c)
    ("not", f) ("and", f, g, ...) ("or", f, g, ...) ("implies", f, g)
    ("G", a, b, f) ("F", a, b, f)
"""
PASS, FAIL, UNK = "pass", "fail", "unknown"

def _num(robs):
    vals = [r for r in robs if r is not None]
    return vals

def ev(f, t, sig, last):
    """Return (verdict, robustness_or_None) for formula f at time t."""
    op = f[0]

    if op in ("geq", "leq"):
        _, var, c = f
        if t > last or t < 0:
            return (UNK, None)
        x = sig[var][t]
        r = (x - c) if op == "geq" else (c - x)
        return (PASS if r >= 0 else FAIL, r)

    if op == "not":
        v, r = ev(f[1], t, sig, last)
        flip = {PASS: FAIL, FAIL: PASS, UNK: UNK}[v]
        return (flip, (-r if r is not None else None))

    if op == "and":
        res = [ev(g, t, sig, last) for g in f[1:]]
        vs = [v for v, _ in res]
        robs = _num([r for _, r in res])
        rob = min(robs) if robs else None
        if FAIL in vs: return (FAIL, rob)
        if UNK in vs:  return (UNK, rob)
        return (PASS, rob)

    if op == "or":
        res = [ev(g, t, sig, last) for g in f[1:]]
        vs = [v for v, _ in res]
        robs = _num([r for _, r in res])
        rob = max(robs) if robs else None
        if PASS in vs: return (PASS, rob)
        if UNK in vs:  return (UNK, rob)
        return (FAIL, rob)

    if op == "implies":
        return ev(("or", ("not", f[1]), f[2]), t, sig, last)

    if op in ("G", "F"):
        _, a, b, sub = f
        lo, hi = t + a, t + b
        truncated = hi > last
        verdicts, robs = [], []
        for i in range(lo, hi + 1):
            if i > last:
                continue
            v, r = ev(sub, i, sig, last)
            verdicts.append(v); robs.append(r)
        nums = _num(robs)
        if op == "G":
            rob = min(nums) if nums else None
            if FAIL in verdicts:            return (FAIL, rob)
            if UNK in verdicts or truncated: return (UNK, rob)
            return (PASS, rob)
        else:  # F
            rob = max(nums) if nums else None
            if PASS in verdicts:            return (PASS, rob)
            if UNK in verdicts or truncated: return (UNK, rob)
            return (FAIL, rob)

    raise ValueError(f"unknown op {op}")

def monitor(formula, sig):
    """Evaluate a formula at t=0 over signal dict sig -> (verdict, robustness)."""
    last = min(len(v) for v in sig.values()) - 1
    return ev(formula, 0, sig, last)
