# Operational-legitimacy decision shield: reproducibility package

Computational artefacts for the manuscript *"Physically Safe, Procedurally
Unauthorised: Formalising Operational Legitimacy Constraints for Trustworthy AI
Decision Support in Industrial Control Systems"* (Deinkumo Liberty, Independent
Researcher, United Kingdom).

This repository reproduces every computational result reported in the paper. The
framework composes an operational-legitimacy layer (rule-based reasoning in Answer
Set Programming) with a physical-admissibility layer (Signal Temporal Logic
monitoring) in a decision shield where physical admissibility is necessary but not
sufficient for acceptance.

## Quick start

```
python3 -m pip install -r requirements.txt   # installs the clingo Python module
python3 verify_all.py                         # runs every experiment and checks all results
```

`verify_all.py` exits 0 only if all checks pass. On the reference environment it
prints `ALL CHECKS PASS`.

## Reference environment

- Python 3.11.15
- clingo 5.8.2 (Answer Set Programming grounder/solver, via the `clingo` Python module)
- Signal Temporal Logic monitoring: `stl_monitor.py`, a transparent discrete-time
  monitor implementing the standard quantitative (robustness) semantics (Fainekos and
  Pappas 2009; Donzé and Maler 2010) with three-valued online semantics. No external
  STL tool is required to reproduce the results.

### Optional: RTAMT cross-validation

The STL results are independently cross-validated under RTAMT 0.4.10, an established
STL tool. RTAMT is pure Python but pins `antlr4-python3-runtime==4.7`, whose packaging
breaks against current setuptools; it builds in an isolated environment with a pinned
build backend:

```
python3 -m venv venv && . venv/bin/activate
pip install 'setuptools==57.5.0' 'wheel==0.37.1'
pip install rtamt==0.4.10
python3 rtamt_tseries.py        # 7/7 decisive robustness values match the transparent monitor
```

Availability note: the cross-validation used RTAMT 0.4.10, and its output is recorded in
`logs/rtamt_tseries.log`. If that exact version is no longer served by PyPI, install it from
the RTAMT project's release archive, or treat the recorded log as the reference for the
comparison. This step is optional and does not affect the core results, which `verify_all.py`
reproduces using clingo alone.

See `docs/rtamt_crossvalidation.docx` for the full comparison. `verify_all.py` does
not require RTAMT.

## Model versions (important)

Three versions of the operational-legitimacy reasoner are included and must not be
confused. See `PROVENANCE.md` for the full mapping of results to sources.

- `model_v3_1.lp` — the initial frozen reasoner. It contains the E1 multi-actor
  authority defect (a legitimate derived-state conflict is treated as unsatisfiable,
  yielding no verdict: fail-blind). It is retained only to document that defect and
  is NOT used to generate any reported acceptance result.
- `model_v3_2.lp` — the corrected frozen reasoner (Option B: operational legitimacy
  is guarded by `not explicit_failure`). **This is the model used for every reported
  result** (Tables 1 through 5 and the composition and transfer results).
- `model_v3_2_hardened.lp` — a prototyped required-approver hardening that
  distinguishes a designated required approver from a contextual actor. It is NOT
  used for any reported result and is included only as the design alternative named
  as future work in the paper.

The frozen `.lp` and harness files are run unmodified; defects are addressed by
versioning, never by silent edits.

## Files

Models and monitor:
- `model_v3_1.lp`, `model_v3_2.lp`, `model_v3_2_hardened.lp`, `compose.lp`, `stl_monitor.py`

Experiments (each prints genuine solver/monitor output):
- `run_p_series_v31.py` — P1-P12 + integrity on the v3.1 model (baseline)
- `run_p_series_v32.py` — P1-P12 + integrity on the v3.2 model (manuscript Tables 1, 2)
- `run_e1_comparison.py` — E1 adversarial case on v3.1 (defect) vs v3.2 (fix) (Section 6.2)
- `run_t_series.py` — T1-T9 STL property suite + robustness ground-truth checks (Table 3)
- `run_c_series.py` — C1-C7 cross-layer composition (Table 4 and text)
- `run_transfer_sis.py` — S1-S4 SIS-bypass transfer scenario (Table 5)
- `run_authority_adversarial.py` — authority-boundary probe on v3.2 (Section 7 limitation)
- `rtamt_tseries.py` — optional RTAMT cross-validation of T1-T9
- `verify_all.py` — one-command verification of all of the above

Outputs and documentation:
- `logs/` — captured output of a fresh run of each experiment
- `docs/evidence_ledger.docx` — maps each computational claim to its source and output
- `docs/rtamt_crossvalidation.docx` — the RTAMT cross-validation report
- `checksums.txt` — MD5 checksums of all source files

## Data

No proprietary or plant data are used. All signal thresholds are symbolic and
normalised; all governance facts are constructed. The scenarios are synthetic.

## Scope of what this establishes

These artefacts establish the coherence and computational realisability of the
framework and that it decides the constructed cases as the theory predicts. They do
not constitute validation against operational plant data, and the transfer scenario
(S1-S4) is a synthetic cross-scenario reuse demonstration, not field validation.

## Licence

Released under the MIT Licence (see `LICENSE`). The documentation files under `docs/`
may be reused under CC-BY 4.0. Copyright (c) 2026 Deinkumo Liberty.

## Citation

See `CITATION.cff`. Please cite the manuscript once it is published.
