%% ===========================================================================
%% CROSS-LAYER COMPOSITION GATE  (separate module — loaded WITH the frozen
%% model_v3_2.lp; the frozen OL reasoner is NOT modified).
%%
%% Inputs:
%%   decision(A, accept|reject|withhold)   -- from the frozen OL reasoner
%%   pa(pass|fail|unknown)                 -- from the STL layer (stl_monitor)
%% Output:
%%   final(A, accept|reject|withhold)
%%
%% Principle: Physical Admissibility is NECESSARY BUT NOT SUFFICIENT.
%%   REJECT   if PA fail  OR OL reject          (physically inadmissible OR
%%                                               procedurally illegitimate)
%%   ACCEPT   if PA pass AND OL accept
%%   WITHHOLD otherwise (PA unknown, or OL withhold), absent any reject
%% ===========================================================================

final(A, reject)   :- action(A), pa(fail).
final(A, reject)   :- decision(A, reject).
final(A, accept)   :- decision(A, accept), pa(pass).
final(A, withhold) :- decision(A, withhold), not pa(fail).
final(A, withhold) :- action(A), pa(unknown), not decision(A, reject).

%% integrity: exactly one final decision
:- final(A, D1), final(A, D2), D1 != D2.
:- action(A), not final(A, _).

#show final/2.
