% ===================================================================
% OPERATIONAL LEGITIMACY REASONER — ASP MODEL v3.2 (HARDENED)
% *** CLAUDE'S RECONSTRUCTION from Liberty's stated v3.2 semantics +
%     the predicate contract in run_v32_hardening.py. NOT the frozen
%     hardened source. Diff against Liberty's file before adopting. ***
%
% Changes vs frozen v3.1:
%   (1) Option B: operationally_legitimate guarded with not explicit_failure.
%   (2) Authority hardened: required_approver/2 + approval_given_by/2.
%       Authority is decided ONLY by designated required approvers; a
%       contextual_actor/2 who lacks competence does NOT contaminate.
%       BOTH satisfied and unsatisfied rules are scoped to required_approver.
%   (3) Added integrity constraint for approval_given_by vs approval_not_given_by.
% MoC / verification / release are unchanged from v3.1.
% ===================================================================

action(restart_c101).
acts_on(restart_c101, c101).

% ===================================================================
% 2. MANAGEMENT OF CHANGE  (unchanged from v3.1)
% ===================================================================
moc_satisfied(A)   :- action(A), moc_applicable(A), moc_approved(A).
moc_satisfied(A)   :- action(A), moc_not_applicable(A).
moc_unsatisfied(A) :- action(A), moc_applicable(A), moc_not_approved(A).
moc_applicability_unknown(A) :- action(A), not moc_applicable(A), not moc_not_applicable(A).
moc_evidence_unknown(A) :- action(A), moc_applicable(A), not moc_approved(A), not moc_not_approved(A).

% ===================================================================
% 3. ROLE, COMPETENCE AND AUTHORITY  (HARDENED — required-approver scoped)
% ===================================================================
% A required approver is fully cleared iff approval given AND competent AND
% holds a role that permits the action.
approver_cleared(A,P) :-
    required_approver(A,P),
    approval_given_by(A,P),
    competent(P,A),
    assigned_role(P,R),
    role_permits(R,A).

% A required approver is explicitly bad iff positive negative evidence exists.
approver_bad(A,P) :- required_approver(A,P), not_competent(P,A).
approver_bad(A,P) :- required_approver(A,P), assigned_role(P,R), role_does_not_permit(R,A).

has_required_approver(A) :- required_approver(A,_).
required_approver_not_cleared(A) :- required_approver(A,P), not approver_cleared(A,P).

% ----- SATISFIED -----
% Applicable, at least one required approver, and none left un-cleared.
authority_satisfied(A) :-
    action(A),
    authority_applicable(A),
    has_required_approver(A),
    not required_approver_not_cleared(A).
authority_satisfied(A) :-
    action(A),
    authority_not_applicable(A).

% ----- UNSATISFIED ----- (scoped to required approvers only)
authority_unsatisfied(A) :-
    action(A),
    authority_applicable(A),
    approver_bad(A,P).

% ----- UNKNOWN -----
authority_applicability_unknown(A) :-
    action(A),
    not authority_applicable(A),
    not authority_not_applicable(A).
authority_evidence_unknown(A) :-
    action(A),
    authority_applicable(A),
    not authority_satisfied(A),
    not authority_unsatisfied(A).

% ===================================================================
% 4. INDEPENDENT VERIFICATION  (unchanged from v3.1)
% ===================================================================
verification_satisfied(A) :- action(A), verification_applicable(A), verified_by(A,V), independent(V).
verification_satisfied(A) :- action(A), verification_not_applicable(A).
verification_unsatisfied(A) :- action(A), verification_applicable(A), verification_not_completed(A).
verification_unsatisfied(A) :- action(A), verification_applicable(A), verified_by(A,V), not_independent(V).
verification_applicability_unknown(A) :- action(A), not verification_applicable(A), not verification_not_applicable(A).
verification_evidence_unknown(A) :- action(A), verification_applicable(A), not verification_satisfied(A), not verification_unsatisfied(A).

% ===================================================================
% 5. RETURN-TO-SERVICE RELEASE  (unchanged from v3.1)
% ===================================================================
release_satisfied(A) :- action(A), release_applicable(A), acts_on(A,X), work_complete(X), handback_complete(X), release_authorised(X).
release_satisfied(A) :- action(A), release_not_applicable(A).
release_unsatisfied(A) :- action(A), release_applicable(A), acts_on(A,X), release_not_authorised(X).
release_unsatisfied(A) :- action(A), release_applicable(A), acts_on(A,X), handback_incomplete(X).
release_unsatisfied(A) :- action(A), release_applicable(A), acts_on(A,X), work_incomplete(X).
release_applicability_unknown(A) :- action(A), not release_applicable(A), not release_not_applicable(A).
release_evidence_unknown(A) :- action(A), release_applicable(A), not release_satisfied(A), not release_unsatisfied(A).

% ===================================================================
% 6. OPERATIONAL LEGITIMACY  (Option B guard added)
% ===================================================================
operationally_legitimate(A) :-
    action(A),
    moc_satisfied(A),
    authority_satisfied(A),
    verification_satisfied(A),
    release_satisfied(A),
    not explicit_failure(A).

% ===================================================================
% 7. AGGREGATED FAILURE STATE
% ===================================================================
explicit_failure(A) :- moc_unsatisfied(A).
explicit_failure(A) :- authority_unsatisfied(A).
explicit_failure(A) :- verification_unsatisfied(A).
explicit_failure(A) :- release_unsatisfied(A).

% ===================================================================
% 8. AGGREGATED UNKNOWN STATE
% ===================================================================
unknown_evidence(A) :- moc_applicability_unknown(A).
unknown_evidence(A) :- moc_evidence_unknown(A).
unknown_evidence(A) :- authority_applicability_unknown(A).
unknown_evidence(A) :- authority_evidence_unknown(A).
unknown_evidence(A) :- verification_applicability_unknown(A).
unknown_evidence(A) :- verification_evidence_unknown(A).
unknown_evidence(A) :- release_applicability_unknown(A).
unknown_evidence(A) :- release_evidence_unknown(A).

% ===================================================================
% 9. DECISION LAYER
% ===================================================================
decision(A,accept)   :- operationally_legitimate(A).
decision(A,reject)   :- action(A), explicit_failure(A).
decision(A,withhold) :- action(A), not explicit_failure(A), unknown_evidence(A).
decision(A,withhold) :- action(A), not operationally_legitimate(A), not explicit_failure(A), not unknown_evidence(A).

% ===================================================================
% 10-11. EXPLANATION LAYER
% ===================================================================
failed_moc(A)          :- moc_unsatisfied(A).
failed_authority(A)    :- authority_unsatisfied(A).
failed_verification(A) :- verification_unsatisfied(A).
failed_release(A)      :- release_unsatisfied(A).

unknown_moc_applicability(A)          :- moc_applicability_unknown(A).
unknown_moc_evidence(A)               :- moc_evidence_unknown(A).
unknown_authority_applicability(A)    :- authority_applicability_unknown(A).
unknown_authority_evidence(A)         :- authority_evidence_unknown(A).
unknown_verification_applicability(A) :- verification_applicability_unknown(A).
unknown_verification_evidence(A)      :- verification_evidence_unknown(A).
unknown_release_applicability(A)      :- release_applicability_unknown(A).
unknown_release_evidence(A)           :- release_evidence_unknown(A).

% ===================================================================
% 12. KNOWLEDGE-BASE INTEGRITY CONSTRAINTS
% ===================================================================
:- moc_applicable(A), moc_not_applicable(A).
:- authority_applicable(A), authority_not_applicable(A).
:- verification_applicable(A), verification_not_applicable(A).
:- release_applicable(A), release_not_applicable(A).
:- moc_approved(A), moc_not_approved(A).
:- competent(P,A), not_competent(P,A).
:- role_permits(R,A), role_does_not_permit(R,A).
:- independent(V), not_independent(V).
:- verified_by(A,V), verification_not_completed(A).
:- release_authorised(X), release_not_authorised(X).
:- work_complete(X), work_incomplete(X).
:- handback_complete(X), handback_incomplete(X).
% v3.2: same required actor cannot both have and not have given approval
:- approval_given_by(A,P), approval_not_given_by(A,P).

% ===================================================================
% 13. DECISION CONSISTENCY
% ===================================================================
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
