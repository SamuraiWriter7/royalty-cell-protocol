# Changelog

All notable changes to the Royalty Cell Protocol are documented in this file.

The project follows semantic versioning while the protocol remains in active
development.

---

## [Unreleased]

### Planned

* Broader cross-file graph validation.
* Circular Derivative-chain detection across multiple records.
* Explicit imported-record provenance profiles.
* Cross-Cell Allocation and shared-settlement examples.
* Adapter conformance examples.
* Machine-readable conformance profiles.
* Dedicated value-realization and settlement protocols where responsibilities
  exceed the intended scope of a single Royalty Cell.
* Preparation for the first stable compatibility profile.

---

## [0.5.0] - 2026-07-25

### Added

* Royalty Cell Interoperability Link JSON Schema.
* Royalty Cell Dispute Record JSON Schema.
* Royalty Cell Holdback Record JSON Schema.
* Cell Interoperability, Disputes and Holdbacks normative specification.
* Remote Royalty Cell identity references.
* Remote Manifest references.
* Remote canonical namespace declarations.
* Remote Cell operator references.
* Cell-to-Cell trust modes:

  * `unverified`;
  * `declarative`;
  * `verified`;
  * `federated`.
* Interoperability-profile references.
* Local-to-remote identifier mappings.
* Mapping relationships:

  * `equivalent_to`;
  * `alias_of`;
  * `mirrors`;
  * `derived_from`;
  * `supersedes`;
  * `conflicts_with`.
* Mapping lifecycle states.
* Mapping-confidence states.
* Local and remote record-resolution states.
* Import, export, and bidirectional record exchange.
* YAML, JSON, and NDJSON exchange declarations.
* Permitted cross-Cell record-type declarations.
* Exchange visibility ceilings.
* Import-policy references.
* Export-policy references.
* Resolver references.
* Policy-compatibility states:

  * `compatible`;
  * `adapter_required`;
  * `conflict`;
  * `unassessed`.
* Adapter references.
* Policy-conflict references.
* Compatibility-assessment references.
* Explicit activation overrides for active Links with known policy conflicts.
* Interoperability Link lifecycle timestamps.
* Dispute types covering:

  * Origin priority;
  * Authorization;
  * Usage;
  * Derivative relationships;
  * Contribution recognition;
  * Weight Resolution;
  * Allocation;
  * settlement;
  * interoperability mappings;
  * policy conflicts.
* Dispute filer and respondent references.
* Contested record references.
* Contested field paths.
* Requested remedies.
* Dispute review and mediation states.
* Formal Dispute decisions.
* Decision outcomes.
* Remedy Action records.
* Remedy execution references.
* Dispute withdrawal.
* Dispute escalation.
* Escalation references.
* Holdback-to-Dispute references.
* Holdback-to-Allocation Plan references.
* Holdback-to-Allocation-line references.
* Held, released, and remaining unit fields.
* Active, partial-release, released, and cancelled Holdback states.
* Release Event records.
* Holdback authority references.
* Related Royalty Receipt references.
* Holdback Evidence records.
* Local Interoperability Link resolution.
* Local Dispute resolution.
* Local Holdback reference resolution.
* Full `v0.1`–`v0.5` multi-record validator.
* Expected-failure example for a Cell linked to itself.
* Expected-failure example for an active policy conflict without an override.
* Expected-failure example for a decided Dispute without a decision.
* Expected-failure example for overlapping filer and respondent identities.
* Expected-failure example for invalid Holdback arithmetic.
* Expected-failure example for a Holdback beneficiary mismatch.

### Validation

* Added rejection of Interoperability Links whose local and remote Cell IDs are
  identical.
* Added active-Link activation-time requirements.
* Added suspended-Link timestamp and reason requirements.
* Added retired-Link timestamp and reason requirements.
* Added local mapping resolution.
* Added external mapping-reference requirements.
* Added duplicate mapping-ID detection.
* Added duplicate local/remote mapping-pair detection.
* Added adapter-reference requirements.
* Added policy-conflict reference requirements.
* Added activation-override requirements.
* Added filer/respondent overlap detection.
* Added duplicate contested-record detection.
* Added Dispute self-reference rejection.
* Added local contested-record resolution.
* Added formal-decision requirements for decided and dismissed disputes.
* Added Remedy Action ID uniqueness validation.
* Added execution-reference requirements for completed Remedy Actions.
* Added withdrawal-state requirements.
* Added escalation-state requirements.
* Added Holdback arithmetic validation:

```text
held_units
- released_units
= remaining_held_units
```

* Added Release Event total validation.
* Added duplicate Release Event ID detection.
* Added Holdback-to-Allocation-line resolution.
* Added Holdback beneficiary matching.
* Added Holdback unit matching.
* Added maximum Holdback amount validation.
* Added active Holdback state validation.
* Added partial-release state validation.
* Added full-release state validation.
* Added cancelled Holdback state validation.
* Added released-Holdback Dispute-state validation.

### Protocol decisions

* Interoperability does not create universal trust.
* Royalty Cells retain independent local governance.
* An identifier mapping does not establish final legal identity.
* An `equivalent_to` mapping does not automatically establish equal legal
  ownership, rights, or obligations.
* Remote records may remain unresolved.
* Unresolved records must not be silently treated as trusted records.
* Policy incompatibilities must remain visible.
* Adapter requirements must be explicit.
* Active Links with known policy conflicts require explicit overrides.
* Filing a Dispute does not establish wrongdoing.
* The same identity cannot be both filer and respondent in one Dispute Record.
* Decided and dismissed disputes require explicit decisions.
* Completed Remedy Actions require execution references.
* A Holdback is a temporary settlement control.
* A Holdback does not confiscate or permanently transfer the underlying value.
* Held units cannot exceed the referenced Allocation line.
* Released units must be supported by Release Events.
* A released Holdback requires a resolved Dispute state.
* Cross-Cell governance remains federated rather than centralized.
* Every Interoperability Link declares:

```yaml
link_effect: interoperability_record_only
```

* Every Dispute Record declares:

```yaml
dispute_effect: dispute_record_only
```

* Every Holdback Record declares:

```yaml
holdback_effect: settlement_hold_only
```

### Completed lifecycle

Version 0.5 completes the first Royalty Cell lifecycle:

```text
Manifest
→ Origin
→ Usage
→ Derivative
→ Contribution
→ Weight Resolution
→ Allocation Plan
→ Royalty Receipt
→ Interoperability Link
→ Dispute
→ Holdback or Release
```

---

## [0.4.0] - 2026-07-25

### Added

* Royalty Cell Contribution Weight Resolution JSON Schema.
* Royalty Cell Allocation Plan JSON Schema.
* Royalty Cell Royalty Receipt JSON Schema.
* Allocation and Royalty Receipts normative specification.
* Weight Resolution identifiers.
* Weight Resolution target references.
* Weighting methods:

  * `equal_weight`;
  * `fixed_policy`;
  * `score_normalization`;
  * `consensus`;
  * `external`.
* Weight Resolution lifecycle states.
* Weight assignments.
* Assignment identifiers.
* Contribution Claim references.
* Contributor references.
* Raw Contribution scores.
* Normalized weights.
* Sum-to-one normalization policy.
* Weight precision declarations.
* Weight tolerance declarations.
* Weight decision authorities.
* Weight decision timestamps.
* Weight-policy references.
* Weight decision rationales.
* External weighting-result references.
* Weight Resolution revocation.
* Value Event records inside Allocation Plans.
* Value Event types:

  * sale;
  * license;
  * subscription;
  * service fee;
  * grant;
  * donation;
  * cost saving;
  * point issuance;
  * credit issuance;
  * rights grant;
  * other.
* Monetary and non-monetary unit definitions.
* Gross unit declarations.
* Allocation deductions.
* Platform-cost deductions.
* Tax deductions.
* Community-fund deductions.
* Reserve deductions.
* Refund deductions.
* Distributable unit declarations.
* Beneficiary Allocation lines.
* Applied weights.
* Allocated units.
* Settlement types.
* Allocation rounding rules.
* Allocation approval records.
* Allocation Plan cancellation.
* Royalty Receipt identifiers.
* Allocation Plan references from Receipts.
* Allocation-line references.
* Allocated, settled, and remaining unit fields.
* Settlement states:

  * `pending`;
  * `partially_settled`;
  * `settled`;
  * `failed`;
  * `held`;
  * `waived`;
  * `reversed`.
* Settlement timestamps.
* Settlement Evidence.
* Attribution inside Royalty Receipts.
* Hold, waiver, and reversal references.
* Passing Contribution Weight Resolution example.
* Passing Allocation Plan example.
* Passing Royalty Receipt examples.
* Additional recognized Contribution Claim for validation work.
* Expected-failure example for normalized weights not summing to one.
* Expected-failure example for Allocation totals not reconciling.
* Expected-failure example for a settled Receipt without Settlement Evidence.
* Expected-failure example for a Royalty Receipt beneficiary mismatch.

### Validation

* Added local Contribution Claim resolution.
* Added contributor matching between Claims and assignments.
* Added recognized-Claim eligibility requirements.
* Added duplicate assignment-ID detection.
* Added duplicate Contribution Claim detection.
* Added Decimal-based normalized-weight validation.
* Added finalized Weight Resolution decision requirements.
* Added external-method result-reference requirements.
* Added Weight Resolution revocation requirements.
* Added local finalized Weight Resolution resolution from Allocation Plans.
* Added deduction arithmetic validation:

```text
gross_units
- sum(deductions)
= distributable_units
```

* Added Allocation arithmetic validation:

```text
sum(allocated_units)
= distributable_units
```

* Added applied-weight normalization validation.
* Added Contribution Claim coverage validation.
* Added rejection of Claims allocated more than once.
* Added Allocation-line weight matching against referenced Claims.
* Added approval requirements.
* Added cancellation requirements.
* Added local Allocation Plan resolution from Royalty Receipts.
* Added Allocation-line existence validation.
* Added Receipt beneficiary matching.
* Added Receipt settlement-type matching.
* Added Receipt unit matching.
* Added Receipt amount matching.
* Added Receipt arithmetic validation:

```text
allocated_units
- settled_units
= balance_remaining_units
```

* Added settlement-state Evidence requirements.
* Added partial-settlement constraints.
* Added pending-settlement constraints.
* Added failed-settlement reason requirements.
* Added held-settlement reference requirements.
* Added waiver-reference requirements.
* Added reversal-reference requirements.

### Protocol decisions

* Contribution recognition is not a numeric Contribution weight.
* A numeric Contribution weight is not an approved Allocation.
* An approved Allocation is not completed settlement.
* Finalized Contribution weights must sum to one.
* Only recognized or partially recognized Claims may enter a finalized Weight
  Resolution.
* Every Claim in a Weight Resolution must be allocated exactly once.
* Deductions must be explicit and policy-bound.
* Allocation arithmetic must be reproducible.
* A Royalty Receipt represents one Allocation Plan line.
* Settlement Evidence is required before a Receipt may be marked settled.
* Monetary and non-monetary value returns use the same record lifecycle.
* Every Weight Resolution declares:

```yaml
allocation_effect: weight_resolution_only
```

* Every Allocation Plan declares:

```yaml
allocation_effect: allocation_plan_only
```

* Every Royalty Receipt declares:

```yaml
receipt_effect: settlement_record_only
```

---

## [0.3.0] - 2026-07-25

### Added

* Royalty Cell Derivative Record JSON Schema.
* Royalty Cell Contribution Claim JSON Schema.
* Derivative and Contribution Records normative specification.
* Derivative identifiers.
* Derivative types:

  * adaptation;
  * transformation;
  * combination;
  * translation;
  * summary;
  * extraction;
  * extension;
  * implementation;
  * distillation;
  * remix;
  * other.
* Derivative lifecycle states.
* Creator references.
* Origin-to-Derivative links.
* Derivative-to-Derivative links.
* Parent source record types.
* Parent dependency levels.
* Parent resolution states.
* Derivative transformation profiles.
* Transformation operations.
* Qualitative Derivative distances.
* Transformation method references.
* Novelty notes.
* Usage references from Derivative Records.
* Derivative output references.
* Derivative Evidence.
* Contribution Claim identifiers.
* Contribution targets.
* Contribution types:

  * conceptualization;
  * research;
  * architecture;
  * protocol design;
  * implementation;
  * writing;
  * editing;
  * review;
  * data provision;
  * model provision;
  * prompt design;
  * orchestration;
  * validation;
  * governance;
  * funding;
  * infrastructure;
  * other.
* Claimed Contribution significance.
* Contribution descriptions.
* Contribution lifecycle states.
* Contribution periods.
* Contribution scope references.
* Contribution Evidence.
* Recognition decisions.
* Recognition authorities.
* Recognition timestamps.
* Recognition rationales.
* Recognized significance.
* Recognition-policy references.
* Contribution dispute references.
* Contribution withdrawal.
* Contribution supersession.
* Passing Derivative Record example.
* Passing Contribution Claim example.
* Expected-failure example for a self-referencing Derivative.
* Expected-failure example for a missing local Derivative parent.
* Expected-failure example for a recognized Contribution without a decision.
* Expected-failure example for a rejected Contribution without rationale.

### Validation

* Added Derivative timestamp-order validation.
* Added Derivative lifecycle validation.
* Added Derivative self-reference rejection.
* Added parent identifier-prefix validation.
* Added local parent resolution.
* Added external parent-reference requirements.
* Added duplicate parent detection.
* Added primary-parent requirements.
* Added two-parent minimum for combination Derivatives.
* Added Contribution target identifier-prefix validation.
* Added local Contribution target resolution.
* Added external target-reference requirements.
* Added Contribution-period ordering.
* Added consistency checks between Claim status and recognition status.
* Added completed recognition-decision requirements.
* Added recognized-significance requirements.
* Added Contribution dispute requirements.
* Added withdrawal requirements.
* Added supersession requirements.
* Added multi-record local identifier registry to the validator.

### Protocol decisions

* A Derivative Record does not determine copyright infringement.
* Derivative distance is qualitative.
* Derivative distance does not determine legal independence.
* Parent dependency levels do not define fixed Royalty percentages.
* Every Derivative must identify at least one primary parent.
* Combination Derivatives require at least two distinct parents.
* A Derivative cannot identify itself as its own parent.
* A Contribution Claim remains separate from Cell recognition.
* Recognition remains separate from Allocation.
* Claimed significance and recognized significance are qualitative.
* Recognized and rejected Claims require explicit decisions.
* Every Derivative Record declares:

```yaml
allocation_effect: not_yet_determined
```

* Every Contribution Claim declares:

```yaml
allocation_effect: contribution_evidence_only
```

---

## [0.2.0] - 2026-07-25

### Added

* Royalty Cell Origin Record JSON Schema.
* Royalty Cell Usage Record JSON Schema.
* Origin and Usage Records normative specification.
* Origin identifiers.
* Origin titles and descriptions.
* Origin types:

  * concept;
  * question;
  * framework;
  * method;
  * specification;
  * protocol;
  * code;
  * dataset;
  * model;
  * prompt;
  * design;
  * text;
  * image;
  * audio;
  * video;
  * other.
* Origin claimant references.
* Origin claim-basis classification.
* Origin claim-effect declaration.
* Origin lifecycle states.
* Origin creation timestamps.
* Origin declaration timestamps.
* Content fingerprints.
* Origin Evidence records.
* Precedence references.
* Usage-policy references.
* Imported-Origin references.
* Contest references.
* Superseding-Origin references.
* Origin visibility states.
* Usage identifiers.
* Usage declarants.
* Usage declaration bases.
* Usage lifecycle states.
* Usage types:

  * reference;
  * adaptation;
  * transformation;
  * execution;
  * training;
  * retrieval;
  * distillation;
  * embedding;
  * publication;
  * commercial service;
  * internal use;
  * other.
* Usage purposes.
* Usage occurrence timestamps.
* Origin links from Usage Records.
* Usage-to-Origin relationships.
* Origin dependency levels.
* Local, external, and unresolved Origin-reference states.
* Usage-scope declarations.
* Audience classifications.
* Commerciality classifications.
* Territory declarations.
* Channel declarations.
* Authorization-state declarations.
* Authorization references.
* Authorization-policy references.
* Authorization terms references.
* Usage Evidence.
* Attribution records.
* Usage output references.
* Usage dispute references.
* Passing Origin Record example.
* Passing Usage Record example.
* Expected-failure example for a superseded Origin without a successor.
* Expected-failure example for a missing locally resolved Origin.
* Expected-failure example for completed Usage with denied Authorization.

### Changed

* Corrected the passing Usage example from:

```yaml
usage_type: specification
```

to:

```yaml
usage_type: transformation
```

* Preserved `specification` as an output classification rather than a Usage
  action classification.

### Validation

* Added Origin timestamp-order validation.
* Added imported-Origin reference requirements.
* Added contested-Origin reference requirements.
* Added withdrawn-Origin reason requirements.
* Added superseded-Origin successor requirements.
* Added Evidence identifier uniqueness checks.
* Added completed-Usage timestamp requirements.
* Added disputed-Usage reference requirements.
* Added withdrawn-Usage reason requirements.
* Added granted-Authorization reference requirements.
* Added `not_required` Authorization policy requirements.
* Added rejection of completed Usage with denied Authorization.
* Added local Origin-reference resolution.
* Added external Origin-reference requirements.
* Added duplicate Origin-link detection.
* Added attribution-content requirements.
* Added Usage-scope time-range validation.

### Protocol decisions

* Origin registration is a timestamped claim record.
* Origin registration does not establish final legal ownership.
* Usage declarations remain separate from Authorization.
* Authorization remains separate from execution.
* Usage completion does not prove value realization.
* Dependency levels are qualitative and do not define Contribution
  percentages.
* Unresolved Origins may remain visible in the Trace.
* Attribution remains separate from monetary Royalty.
* Every Origin Record declares:

```yaml
claim_effect: claim_record_only
```

---

## [0.1.0] - 2026-07-25

### Added

* Initial Royalty Cell Protocol repository.
* Royalty Cell Manifest JSON Schema.
* Royalty Cell Manifest normative specification.
* Stable Cell identifiers.
* Cell names and descriptions.
* Cell lifecycle states:

  * draft;
  * active;
  * suspended;
  * retired.
* Cell creation and update timestamps.
* Cell scope types:

  * community;
  * project;
  * organization;
  * agent collective;
  * research group;
  * other.
* Cell domain declarations.
* Cell purpose declarations.
* Jurisdiction references.
* Cell resource references.
* Governance modes:

  * steward led;
  * council;
  * member vote;
  * consensus;
  * external policy.
* Governance authority references.
* Governance approval rules.
* Governance quorum declarations.
* Governance policy references.
* Dispute-policy references.
* Membership admission modes.
* Membership policy references.
* Cell role definitions.
* Role identifiers.
* Role permissions.
* Origin-registration policy declarations.
* Usage-declaration policy declarations.
* Evidence requirements.
* Accepted Evidence types.
* Evidence-policy references.
* Record visibility settings.
* Record-retention policies.
* Allocation-policy status declarations.
* Supported settlement types.
* Canonical identifier namespaces.
* Record export settings.
* YAML, JSON, and NDJSON export declarations.
* Extension fields.
* Passing Royalty Cell Manifest example.
* Expected-failure example for a Cell without an administrator role.
* Expected-failure example for a missing Allocation-policy reference.
* Initial JSON Schema validator.
* Initial semantic validator.
* GitHub Actions validation workflow.
* Initial README.
* Initial CHANGELOG.

### Validation

* Added Manifest creation/update timestamp-order validation.
* Added external governance-policy requirements.
* Added admission-policy requirements.
* Added duplicate role-ID detection.
* Added mandatory `administer_cell` permission.
* Added Evidence-policy requirements.
* Added retention-duration validation.
* Added external retention-policy requirements.
* Added Allocation-policy reference requirements.
* Added rejection of policy references when Allocation is not configured.
* Added pass-example validation.
* Added expected-failure validation.
* Added non-zero exit status for validation failures.

### Protocol decisions

* A Royalty Cell is the minimum autonomous value-return unit.
* A Cell must be able to operate independently.
* Cells retain autonomy over Contribution and Allocation policies.
* The protocol does not impose one universal Royalty percentage.
* Every Cell requires at least one administrator role.
* Cell administrators do not automatically own registered Origins.
* Origin registration is not ownership adjudication.
* Version 0.1 records Cell governance but does not execute value settlement.
* A Royalty Cell may operate without blockchain infrastructure.
* A Royalty Cell may support monetary or non-monetary returns.
* Interoperability is designed to be added after local autonomy is established.

---

## Initial `v0.1`–`v0.5` milestone

The first development cycle establishes the following structure:

```text
Royalty Cell Manifest
    ↓
Origin Record
    ↓
Usage Record
    ↓
Derivative Record
    ↓
Contribution Claim
    ↓
Recognition Decision
    ↓
Contribution Weight Resolution
    ↓
Allocation Plan
    ↓
Royalty Receipt
    ↓
Interoperability Link
    ↓
Dispute Record
    ↓
Holdback or Release
```

This milestone turns Royalty Cell Protocol from a local Origin registry into a
complete, federated, auditable value-return lifecycle.

The protocol now supports a Cell that can:

* define itself;
* record Origins;
* record Usage;
* trace Derivatives;
* recognize Contributions;
* normalize Contribution weights;
* allocate value;
* record settlement;
* connect to another Cell;
* expose policy incompatibilities;
* record disputes;
* preserve value during review;
* release held value after resolution.

The result is not one centralized Royalty OS.

It is the minimum protocol structure from which many local Royalty systems can
grow and later connect.
