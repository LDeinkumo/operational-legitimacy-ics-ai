# Provenance: which source produces which reported result

Every reported result is produced by the frozen **v3.2** operational-legitimacy
model (`model_v3_2.lp`) or the transparent STL monitor (`stl_monitor.py`), composed
through `compose.lp`. The v3.1 model appears only to document the corrected defect;
the hardened model appears only as a named future-work alternative and produces no
reported result.

| Manuscript item | Source model / monitor | Script | Log |
|---|---|---|---|
| Table 1 (P1-P12 decisions) | model_v3_2.lp | run_p_series_v32.py | logs/p_series_v32.log |
| Table 2 (integrity I1-I3 UNSAT) | model_v3_2.lp | run_p_series_v32.py | logs/p_series_v32.log |
| Section 6.2 (E1 defect -> fix) | model_v3_1.lp vs model_v3_2.lp | run_e1_comparison.py | logs/e1_comparison.log |
| Table 3 (T1-T9 STL verdicts + robustness) | stl_monitor.py | run_t_series.py | logs/t_series.log |
| Table 4 + text (C1-C7 composition) | stl_monitor.py x model_v3_2.lp via compose.lp | run_c_series.py | logs/c_series.log |
| Table 5 (S1-S4 transfer) | model_v3_2.lp (new facts only) + stl_monitor.py | run_transfer_sis.py | logs/transfer.log |
| Section 7 authority limitation | model_v3_2.lp | run_authority_adversarial.py | logs/authority_adversarial.log |
| STL cross-validation | RTAMT 0.4.10 vs stl_monitor.py | rtamt_tseries.py | logs/rtamt_tseries.log |
| v3.1 baseline (context only) | model_v3_1.lp | run_p_series_v31.py | logs/p_series_v31.log |

Notes.

- The v3.1 model passes the P1-P12 battery too (each P-case isolates one condition
  with a single actor, so none triggers the multi-actor defect). The defect appears
  only on the E1 multi-actor case; that is why `run_e1_comparison.py` exists and why
  the v3.1 baseline log is provided for context, not as a result source.
- The transfer scenario (S1-S4) reuses the frozen v3.2 model and the frozen property
  classes with only new domain facts and no rule changes. Its release fact represents
  the return-to-service authorisation (restoration and re-proving complete), not
  authorisation to enter the bypass; see the manuscript Section 5.7 and Section 7.
- Integrity constraints make contradictory evidence yield no stable model. The
  uniqueness-of-model property therefore holds for consistent, well-formed inputs;
  contradictory inputs are the deliberate exception and produce no verdict.

## Checksums

`checksums.txt` lists MD5 checksums of all source files in this repository. The
frozen model and monitor files match the checksums recorded in the manuscript's
evidence pack.
