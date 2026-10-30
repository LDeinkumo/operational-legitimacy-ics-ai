% ===================================================================
% OPERATIONAL LEGITIMACY REASONER
% ASP MODEL v3.1
%
% Purpose:
%   Evaluate whether an AI-supported industrial action is
%   operationally legitimate on the basis of explicit evidence.
%
% Decision semantics:
%   ACCEPT   = all representative legitimacy constraints satisfied
%   REJECT   = at least one applicable constraint explicitly unsatisfied
%   WITHHOLD = no explicit failure, but required evidence/applicability
%              remains unknown
%
% Inconsistent evidence makes the ASP program UNSATISFIABLE.
%
% Representative constraint subset:
%   1. Management of Change (MoC)
%   2. Role, competence and authority
%   3. Independent verification
%   4. Return-to-service release
%
% Primary demonstration action:
%   restart_c101
% ===================================================================


% ===================================================================
% 1. ACTION / ASSET
% ===================================================================

action(restart_c101).
acts_on(restart_c101, c101).


% ===================================================================
% 2. MANAGEMENT OF CHANGE
% ===================================================================

% ----- SATISFIED -----

moc_satisfied(A) :-
    action(A),
    moc_applicable(A),
    moc_approved(A).

moc_satisfied(A) :-
    action(A),
    moc_not_applicable(A).


% ----- UNSATISFIED -----

moc_unsatisfied(A) :-
    action(A),
    moc_applicable(A),
    moc_not_approved(A).


% ----- UNKNOWN APPLICABILITY -----

moc_applicability_unknown(A) :-
    action(A),
    not moc_applicable(A),
    not moc_not_applicable(A).


% ----- UNKNOWN EVIDENCE -----

moc_evidence_unknown(A) :-
    action(A),
    moc_applicable(A),
    not moc_approved(A),
    not moc_not_approved(A).


% ===================================================================
% 3. ROLE, COMPETENCE AND AUTHORITY
% ===================================================================

% ----- SATISFIED -----

authority_satisfied(A) :-
    action(A),
    authority_applicable(A),
    approval_actor(A,P),
    competent(P,A),
    assigned_role(P,R),
    role_permits(R,A).

authority_satisfied(A) :-
    action(A),
    authority_not_applicable(A).


% ----- UNSATISFIED -----

authority_unsatisfied(A) :-
    action(A),
    authority_applicable(A),
    approval_actor(A,P),
    not_competent(P,A).

authority_unsatisfied(A) :-
    action(A),
    authority_applicable(A),
    approval_actor(A,P),
    assigned_role(P,R),
    role_does_not_permit(R,A).


% ----- UNKNOWN APPLICABILITY -----

authority_applicability_unknown(A) :-
    action(A),
    not authority_applicable(A),
    not authority_not_applicable(A).


% ----- UNKNOWN EVIDENCE -----

authority_evidence_unknown(A) :-
    action(A),
    authority_applicable(A),
    not authority_satisfied(A),
    not authority_unsatisfied(A).


% ===================================================================
% 4. INDEPENDENT VERIFICATION
% ===================================================================

% ----- SATISFIED -----

verification_satisfied(A) :-
    action(A),
    verification_applicable(A),
    verified_by(A,V),
    independent(V).

verification_satisfied(A) :-
    action(A),
    verification_not_applicable(A).


% ----- UNSATISFIED -----

verification_unsatisfied(A) :-
    action(A),
    verification_applicable(A),
    verification_not_completed(A).

verification_unsatisfied(A) :-
    action(A),
    verification_applicable(A),
    verified_by(A,V),
    not_independent(V).


% ----- UNKNOWN APPLICABILITY -----

verification_applicability_unknown(A) :-
    action(A),
    not verification_applicable(A),
    not verification_not_applicable(A).


% ----- UNKNOWN EVIDENCE -----

verification_evidence_unknown(A) :-
    action(A),
    verification_applicable(A),
    not verification_satisfied(A),
    not verification_unsatisfied(A).


% ===================================================================
% 5. RETURN-TO-SERVICE RELEASE
% ===================================================================

% ----- SATISFIED -----

release_satisfied(A) :-
    action(A),
    release_applicable(A),
    acts_on(A,X),
    work_complete(X),
    handback_complete(X),
    release_authorised(X).

release_satisfied(A) :-
    action(A),
    release_not_applicable(A).


% ----- UNSATISFIED -----

release_unsatisfied(A) :-
    action(A),
    release_applicable(A),
    acts_on(A,X),
    release_not_authorised(X).

release_unsatisfied(A) :-
    action(A),
    release_applicable(A),
    acts_on(A,X),
    handback_incomplete(X).

release_unsatisfied(A) :-
    action(A),
    release_applicable(A),
    acts_on(A,X),
    work_incomplete(X).


% ----- UNKNOWN APPLICABILITY -----

release_applicability_unknown(A) :-
    action(A),
    not release_applicable(A),
    not release_not_applicable(A).


% ----- UNKNOWN EVIDENCE -----

release_evidence_unknown(A) :-
    action(A),
    release_applicable(A),
    not release_satisfied(A),
    not release_unsatisfied(A).


% ===================================================================
% 6. OPERATIONAL LEGITIMACY
% ===================================================================

% Operational legitimacy requires affirmative satisfaction of
% every representative constraint.

operationally_legitimate(A) :-
    action(A),
    moc_satisfied(A),
    authority_satisfied(A),
    verification_satisfied(A),
    release_satisfied(A).


% ===================================================================
% 7. AGGREGATED FAILURE STATE
% ===================================================================

explicit_failure(A) :-
    moc_unsatisfied(A).

explicit_failure(A) :-
    authority_unsatisfied(A).

explicit_failure(A) :-
    verification_unsatisfied(A).

explicit_failure(A) :-
    release_unsatisfied(A).


% ===================================================================
% 8. AGGREGATED UNKNOWN STATE
% ===================================================================

unknown_evidence(A) :-
    moc_applicability_unknown(A).

unknown_evidence(A) :-
    moc_evidence_unknown(A).

unknown_evidence(A) :-
    authority_applicability_unknown(A).

unknown_evidence(A) :-
    authority_evidence_unknown(A).

unknown_evidence(A) :-
    verification_applicability_unknown(A).

unknown_evidence(A) :-
    verification_evidence_unknown(A).

unknown_evidence(A) :-
    release_applicability_unknown(A).

unknown_evidence(A) :-
    release_evidence_unknown(A).


% ===================================================================
% 9. DECISION LAYER
% ===================================================================

% ACCEPT:
% All representative operational-legitimacy constraints are
% affirmatively established.

decision(A,accept) :-
    operationally_legitimate(A).


% REJECT:
% At least one applicable constraint has explicit evidence
% establishing non-satisfaction.

decision(A,reject) :-
    action(A),
    explicit_failure(A).


% WITHHOLD:
% There is no explicit failure, but one or more required
% applicability/evidence states remain unknown.

decision(A,withhold) :-
    action(A),
    not explicit_failure(A),
    unknown_evidence(A).


% Defensive completeness rule:
% If an action is neither legitimate, explicitly failed nor
% associated with a classified unknown state, do not permit it.

decision(A,withhold) :-
    action(A),
    not operationally_legitimate(A),
    not explicit_failure(A),
    not unknown_evidence(A).


% ===================================================================
% 10. EXPLANATION LAYER — EXPLICIT FAILURES
% ===================================================================

failed_moc(A) :-
    moc_unsatisfied(A).

failed_authority(A) :-
    authority_unsatisfied(A).

failed_verification(A) :-
    verification_unsatisfied(A).

failed_release(A) :-
    release_unsatisfied(A).


% ===================================================================
% 11. EXPLANATION LAYER — UNKNOWN STATES
% ===================================================================

unknown_moc_applicability(A) :-
    moc_applicability_unknown(A).

unknown_moc_evidence(A) :-
    moc_evidence_unknown(A).

unknown_authority_applicability(A) :-
    authority_applicability_unknown(A).

unknown_authority_evidence(A) :-
    authority_evidence_unknown(A).

unknown_verification_applicability(A) :-
    verification_applicability_unknown(A).

unknown_verification_evidence(A) :-
    verification_evidence_unknown(A).

unknown_release_applicability(A) :-
    release_applicability_unknown(A).

unknown_release_evidence(A) :-
    release_evidence_unknown(A).


% ===================================================================
% 12. KNOWLEDGE-BASE INTEGRITY CONSTRAINTS
% ===================================================================

% Applicability cannot simultaneously be true and false.

:- moc_applicable(A), moc_not_applicable(A).

:- authority_applicable(A), authority_not_applicable(A).

:- verification_applicable(A), verification_not_applicable(A).

:- release_applicable(A), release_not_applicable(A).


% MoC approval cannot simultaneously be approved and explicitly
% not approved.

:- moc_approved(A), moc_not_approved(A).


% Competence evidence cannot contradict itself.

:- competent(P,A), not_competent(P,A).


% Role permission cannot simultaneously permit and prohibit
% the same action.

:- role_permits(R,A), role_does_not_permit(R,A).


% Verification independence cannot simultaneously hold and fail.

:- independent(V), not_independent(V).


% A completed verification and explicit declaration that
% verification was not completed cannot coexist for the action.

:- verified_by(A,V), verification_not_completed(A).


% Release evidence cannot contradict itself.

:- release_authorised(X), release_not_authorised(X).

:- work_complete(X), work_incomplete(X).

:- handback_complete(X), handback_incomplete(X).


% ===================================================================
% 13. DECISION CONSISTENCY
% ===================================================================

% No action may receive more than one decision state.

:- decision(A,accept), decision(A,reject).
:- decision(A,accept), decision(A,withhold).
:- decision(A,reject), decision(A,withhold).


% ===================================================================
% 14. OUTPUT
% ===================================================================

#show decision/2.
#show operationally_legitimate/1.

#show failed_moc/1.
#show failed_authority/1.
#show failed_verification/1.
#show failed_release/1.

#show unknown_moc_applicability/1.
#show unknown_moc_evidence/1.

#show unknown_authority_applicability/1.
#show unknown_authority_evidence/1.

#show unknown_verification_applicability/1.
#show unknown_verification_evidence/1.

#show unknown_release_applicability/1.
#show unknown_release_evidence/1.
