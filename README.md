# Royalty Cell Protocol

A bottom-up protocol for autonomous communities to record Origins, declare
Usages, trace Derivatives, recognize Contributions, allocate value, issue
Royalty Receipts, connect with other Cells, and preserve value during disputes.

## Status

Current protocol version: `v0.5.0`

The initial `v0.1`–`v0.5` lifecycle is complete.

```text
Manifest
  ↓
Origin
  ↓
Usage
  ↓
Derivative
  ↓
Contribution
  ↓
Weight Resolution
  ↓
Allocation Plan
  ↓
Royalty Receipt
  ↓
Interoperability
  ↓
Dispute
  ↓
Holdback or Release
```

Royalty Cell Protocol does not define one centralized Royalty OS.

It defines the minimum records required for many independently governed
Royalty Cells to operate locally and connect later through shared protocol
structures.

---

## Core idea

A civilization-scale Royalty OS should not begin as one global platform,
institution, or legal mandate.

It should emerge from small, locally governed value-return cycles.

```text
Individual declaration
    ↓
Local Trace
    ↓
Community recognition
    ↓
Local Allocation
    ↓
Voluntary or contractual return
    ↓
Cell-to-Cell interoperability
    ↓
Institutional adoption
    ↓
Legal recognition
```

A Royalty Cell may begin as:

* an open-source project;
* a creator community;
* a research group;
* an enterprise project team;
* an AI-agent collective;
* a protocol-design community;
* a local knowledge network;
* another bounded contribution community.

Each Cell may define its own internal governance, evidence standards,
recognition methods, and Allocation policies.

The protocol standardizes the records and their relationships. It does not
force every Cell to use the same Royalty percentage or economic model.

---

## What is a Royalty Cell?

A Royalty Cell is the smallest autonomous unit capable of recording and
governing a local value-return cycle.

A Cell can answer the following questions:

```text
Who governs this Cell?

What was declared as an Origin?

What was used?

What was created from that use?

Who contributed?

Which Contributions were recognized?

How were recognized Contributions weighted?

What allocable value was generated?

Who was assigned which units?

What was actually returned?

How does this Cell connect to another Cell?

What happens when records or policies conflict?
```

A Royalty Cell is not merely a database table.

It is a bounded governance and evidence structure in which value attribution
can be recorded before large institutions or legal systems formally recognize
it.

---

## Design principles

### 1. Origin registration is not ownership adjudication

An Origin Record means:

> A participant made this Origin claim, with this Evidence, at this time,
> inside this Royalty Cell.

It does not automatically establish:

* copyright ownership;
* patent ownership;
* exclusive authorship;
* contractual entitlement;
* legal priority;
* entitlement to payment.

Every Origin Record therefore declares:

```yaml
claim_effect: claim_record_only
```

### 2. Usage remains separate from Authorization

A Usage Record states that a use was declared or observed.

It does not automatically prove that the use was authorized.

Likewise, an Authorization record does not prove that the authorized action
actually occurred.

```text
Authorization
≠ Usage

Usage
≠ Execution

Execution
≠ Value realization

Value realization
≠ Settlement
```

### 3. Derivative relationships are not legal judgments

A Derivative Record identifies a declared transformation from one or more
Origins or Derivatives.

It does not determine:

* copyright infringement;
* legal originality;
* ownership independence;
* a fixed Contribution percentage;
* a payment obligation.

Every Derivative Record declares:

```yaml
allocation_effect: not_yet_determined
```

### 4. Contribution Claims remain separate from recognition

A contributor may submit a Contribution Claim.

The Cell may then:

* acknowledge it;
* recognize it;
* partially recognize it;
* reject it;
* dispute it;
* allow it to be withdrawn or superseded.

A submitted claim is not automatically a recognized Contribution.

Every Contribution Claim declares:

```yaml
allocation_effect: contribution_evidence_only
```

### 5. Recognition remains separate from numeric weighting

Qualitative significance may be recorded as:

* `foundational`
* `major`
* `supporting`
* `minor`
* `unspecified`

These labels are not percentages.

Numeric weights are established only through a separate Contribution Weight
Resolution.

### 6. Weighting remains separate from Allocation

A Weight Resolution determines normalized Contribution weights.

It does not move value.

Every Weight Resolution declares:

```yaml
allocation_effect: weight_resolution_only
```

### 7. Allocation remains separate from settlement

An Allocation Plan determines how distributable units should be assigned.

It does not prove that those units were delivered.

Every Allocation Plan declares:

```yaml
allocation_effect: allocation_plan_only
```

### 8. A Royalty Receipt is a settlement record

A Royalty Receipt records the Cell's evidence that an Allocation line is:

* pending;
* partially settled;
* settled;
* failed;
* held;
* waived;
* reversed.

Every Royalty Receipt declares:

```yaml
receipt_effect: settlement_record_only
```

A Royalty Receipt does not replace external banking, accounting, tax, or legal
evidence.

### 9. Interoperability does not create universal trust

A Cell-to-Cell Link records a controlled relationship between independently
governed Cells.

It does not mean that every remote record is automatically trusted.

Every Interoperability Link declares:

```yaml
link_effect: interoperability_record_only
```

### 10. A dispute is not proof of wrongdoing

A Dispute Record states that a record, relationship, policy, decision, or
settlement has been challenged.

Filing a dispute does not establish that the respondent violated a rule.

Every Dispute Record declares:

```yaml
dispute_effect: dispute_record_only
```

### 11. Holdback is not confiscation

A Holdback temporarily preserves allocable or settleable units while a dispute
or review remains unresolved.

It does not permanently revoke the underlying Contribution or Allocation.

Every Holdback Record declares:

```yaml
holdback_effect: settlement_hold_only
```

---

## Protocol records

Royalty Cell Protocol v0.5 defines eleven record types.

| Version | Record type                    | Purpose                                                                                          |
| ------- | ------------------------------ | ------------------------------------------------------------------------------------------------ |
| v0.1    | Royalty Cell Manifest          | Defines Cell identity, scope, governance, roles, recording policy, and interoperability settings |
| v0.2    | Origin Record                  | Records a timestamped Origin claim and supporting Evidence                                       |
| v0.2    | Usage Record                   | Records declared use, scope, Authorization state, Evidence, and attribution                      |
| v0.3    | Derivative Record              | Records transformations from Origins or earlier Derivatives                                      |
| v0.3    | Contribution Claim             | Records a participant's claimed Contribution and recognition decision                            |
| v0.4    | Contribution Weight Resolution | Converts recognized Claims into normalized weights                                               |
| v0.4    | Allocation Plan                | Applies weights to a value event and assigns distributable units                                 |
| v0.4    | Royalty Receipt                | Records pending or completed value return                                                        |
| v0.5    | Interoperability Link          | Connects independently governed Cells and maps identifiers                                       |
| v0.5    | Dispute Record                 | Records challenges, decisions, remedies, withdrawal, or escalation                               |
| v0.5    | Holdback Record                | Temporarily preserves units and records partial or full release                                  |

---

## Protocol lifecycle

### v0.1 — Royalty Cell Manifest

The Manifest defines the identity and operating boundary of a Cell.

It records:

* stable Cell identifier;
* Cell name and description;
* lifecycle status;
* scope type and domains;
* governance mode;
* governing authorities;
* membership roles;
* role permissions;
* admission policy;
* Origin and Usage recording policy;
* Evidence requirements;
* visibility and retention rules;
* Allocation-policy status;
* supported settlement types;
* canonical identifier namespace;
* supported export formats.

A Cell must contain at least one role with the `administer_cell` permission.

Cell administration does not automatically establish ownership of registered
Origins.

### v0.2 — Origin and Usage Records

Origin Records establish the first local Trace.

They record:

* Origin identifier;
* Cell identifier;
* title and description;
* Origin type;
* claimant references;
* claim basis;
* claim status;
* timestamps;
* content fingerprint;
* Evidence;
* precedence references;
* Usage-policy references;
* visibility.

Usage Records then connect an Origin to a declared use.

They record:

* Usage identifier;
* declarant;
* declaration basis;
* Usage type;
* Usage status;
* purpose;
* linked Origins;
* relationship to each Origin;
* dependency level;
* Usage scope;
* Authorization state;
* Evidence;
* attribution;
* output references.

A locally resolved Usage-to-Origin link must resolve to a passing local Origin
Record.

### v0.3 — Derivative and Contribution Records

Derivative Records describe what was produced from one or more parent records.

They record:

* Derivative identifier;
* creator references;
* parent Origins or Derivatives;
* transformation relationships;
* dependency levels;
* transformation operations;
* qualitative Derivative distance;
* Evidence;
* lifecycle status;
* output references.

A Derivative cannot reference itself as its own parent.

At least one parent must have `dependency_level: primary`.

A `combination` Derivative must identify at least two distinct parents.

Contribution Claims record who contributed and how.

They record:

* contributor;
* target record or output;
* Contribution type;
* claimed significance;
* description;
* Evidence;
* Contribution period;
* claim status;
* optional recognition decision;
* recognized significance;
* recognition rationale;
* governing policy.

Recognized, partially recognized, and rejected Claims require explicit
recognition decisions.

### v0.4 — Weight Resolution, Allocation, and Royalty Receipts

Contribution Weight Resolution converts recognized Claims into normalized
weights.

A finalized resolution must satisfy:

```text
sum(normalized_weight) = 1
```

Each local assignment must resolve to a recognized or partially recognized
Contribution Claim.

An Allocation Plan applies those weights to a value event.

Supported value events include:

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
* other locally defined events.

The Allocation arithmetic must satisfy:

```text
gross_units
- sum(deductions)
= distributable_units
```

and:

```text
sum(allocated_units)
= distributable_units
```

Applied weights must sum to one.

Each Contribution Claim in the Weight Resolution must be allocated exactly
once.

A Royalty Receipt records settlement of one Allocation line.

Its arithmetic must satisfy:

```text
allocated_units
- settled_units
= balance_remaining_units
```

A settled Receipt requires:

* `settled_at`;
* at least one Settlement Evidence item;
* zero remaining balance.

### v0.5 — Interoperability, Disputes, and Holdbacks

An Interoperability Link connects one local Cell to one remote Cell.

It records:

* remote Cell identity;
* remote manifest reference;
* trust mode;
* interoperability profiles;
* local-to-remote identifier mappings;
* mapping relationships;
* mapping confidence;
* permitted record types;
* exchange direction;
* exchange formats;
* visibility ceiling;
* import and export policies;
* resolver reference;
* policy compatibility;
* adapter requirements;
* policy conflicts;
* activation override.

Supported trust modes are:

* `unverified`
* `declarative`
* `verified`
* `federated`

Supported mapping relationships include:

* `equivalent_to`
* `alias_of`
* `mirrors`
* `derived_from`
* `supersedes`
* `conflicts_with`

An active Link with a known policy conflict requires an explicit activation
override.

A Dispute Record may challenge:

* Origin priority;
* Authorization;
* Usage;
* Derivative relationships;
* Contribution recognition;
* Weight Resolution;
* Allocation;
* settlement;
* interoperability mappings;
* policy compatibility.

The same identity cannot appear as both filer and respondent in one Dispute
Record.

Decided and dismissed disputes require a formal decision containing:

* outcome;
* decision authorities;
* decision time;
* governing policies;
* rationale;
* remedy actions.

A completed remedy action requires an execution reference.

A Holdback Record connects a Dispute to an Allocation line.

Its arithmetic must satisfy:

```text
held_units
- released_units
= remaining_held_units
```

Released units must also equal the total units recorded in Release Events.

Held units cannot exceed the referenced Allocation line.

A released Holdback requires:

* full release of held units;
* zero remaining held units;
* at least one Release Event;
* `released_at`;
* a resolved Dispute state.

---

## Supported contribution types

Version 0.5 supports Contributions such as:

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
* other locally defined Contributions.

The protocol does not assign universal values to these categories.

Each Cell defines its own recognition and weighting policy.

---

## Supported return types

Royalty Cells may return value using monetary or non-monetary units.

Supported settlement types include:

* money;
* credit;
* points;
* attribution;
* access rights;
* governance rights;
* future claims;
* community-fund contributions.

One Allocation Plan uses one consistent unit definition.

Examples:

```yaml
unit:
  kind: currency
  code: JPY
  decimals: 0
```

```yaml
unit:
  kind: point
  code: COMMUNITY_POINT
  decimals: 2
```

```yaml
unit:
  kind: attribution
  code: ATTRIBUTION
  decimals: 0
```

---

## Local and external reference resolution

Protocol records distinguish among:

* `resolved`
* `externally_resolved`
* `unresolved`

### Resolved

A locally resolved record is expected to exist in the local record set.

The conformance validator verifies local passing examples for supported record
types.

### Externally resolved

An externally resolved record must include a record reference.

The local Cell acknowledges the external record without silently converting it
into a locally verified record.

### Unresolved

An unresolved reference may remain in the Trace.

This allows incomplete information to remain visible instead of being silently
deleted or treated as verified.

Downstream Audit, Allocation, or settlement systems may restrict actions based
on unresolved records.

---

## Repository structure

```text
royalty-cell-protocol/
├── .github/
│   └── workflows/
│       └── validate.yml
├── schemas/
│   ├── royalty-cell-manifest.schema.json
│   ├── royalty-cell-origin-record.schema.json
│   ├── royalty-cell-usage-record.schema.json
│   ├── royalty-cell-derivative-record.schema.json
│   ├── royalty-cell-contribution-claim.schema.json
│   ├── royalty-cell-contribution-weight-resolution.schema.json
│   ├── royalty-cell-allocation-plan.schema.json
│   ├── royalty-cell-royalty-receipt.schema.json
│   ├── royalty-cell-interoperability-link.schema.json
│   ├── royalty-cell-dispute-record.schema.json
│   └── royalty-cell-holdback-record.schema.json
├── specs/
│   ├── royalty-cell-manifest.md
│   ├── origin-and-usage-records.md
│   ├── derivative-and-contribution-records.md
│   ├── allocation-and-royalty-receipts.md
│   └── cell-interoperability-and-disputes.md
├── examples/
│   ├── pass/
│   └── fail/
├── scripts/
│   └── validate_examples.py
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

---

## Validation

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Run the conformance validator

```bash
python scripts/validate_examples.py
```

The validator performs:

1. YAML loading;
2. record-type-specific JSON Schema validation;
3. protocol-specific semantic validation;
4. local cross-record reference resolution;
5. lifecycle consistency checks;
6. Decimal-based arithmetic checks;
7. pass-example verification;
8. expected-failure verification.

Files under `examples/pass` must pass both schema and semantic validation.

Files under `examples/fail` must fail at least one validation stage.

### Supported validator records

```text
royalty_cell_manifest
royalty_cell_origin_record
royalty_cell_usage_record
royalty_cell_derivative_record
royalty_cell_contribution_claim
royalty_cell_contribution_weight_resolution
royalty_cell_allocation_plan
royalty_cell_royalty_receipt
royalty_cell_interoperability_link
royalty_cell_dispute_record
royalty_cell_holdback_record
```

### Successful output

A successful run ends with:

```text
All Royalty Cell Protocol examples behaved as expected.
```

If a passing example fails, the process exits with status code `1`.

If an invalid example unexpectedly passes, the process also exits with status
code `1`.

---

## Expected-failure coverage

The fail examples are intended to verify rejection of invalid protocol states,
including:

* a Manifest without an administrator role;
* an Allocation policy without its policy reference;
* a superseded Origin without a successor;
* a missing locally resolved Origin;
* completed Usage with denied Authorization;
* a self-referencing Derivative;
* a missing local Derivative parent;
* recognized Contribution without a recognition decision;
* rejected Contribution without rationale;
* finalized Contribution weights that do not sum to one;
* Allocation totals that do not reconcile;
* settled Receipts without Settlement Evidence;
* Receipt beneficiaries that do not match Allocation lines;
* a Cell linked to itself;
* an active policy conflict without an override;
* a decided Dispute without a decision;
* overlapping filer and respondent identities;
* invalid Holdback arithmetic;
* Holdback beneficiaries that do not match Allocation lines.

These files are not broken examples.

They are conformance tests that demonstrate the validator rejects invalid
states intentionally.

---

## Security considerations

Implementations should account for:

* false Origin claims;
* fabricated timestamps;
* impersonated claimants or contributors;
* forged Evidence;
* hidden parent Origins;
* undeclared commercial Usage;
* false Authorization declarations;
* circular Derivative chains;
* inflated Contribution significance;
* collusive recognition;
* manipulated Contribution weights;
* omitted recognized contributors;
* hidden deductions;
* manipulated rounding;
* fabricated value events;
* beneficiary substitution;
* false settlement evidence;
* malicious identifier mappings;
* forged remote Cell manifests;
* incompatible policies;
* dispute spam;
* collusive dispute decisions;
* indefinite Holdbacks;
* concealed release events;
* unauthorized overrides;
* replayed records.

Protocol conformance does not guarantee that the underlying statements are
true.

Conformance means that the records are structurally and semantically
consistent with the protocol.

External Audit and Evidence verification remain necessary.

---

## Privacy considerations

Royalty Cell records may expose:

* unpublished concepts;
* private prompts;
* confidential source materials;
* employee Contribution data;
* internal project activity;
* payment amounts;
* revenue or cost-saving events;
* contractual terms;
* dispute communications;
* personal information.

Implementations should apply data minimization.

A public record may expose:

* a digest;
* a timestamp;
* a protected reference;
* a redacted Evidence description;

instead of publishing the underlying confidential content.

Record visibility may be:

* `public`
* `members`
* `restricted`
* `inherit`, where supported by the record type.

Interoperability Links should define an exchange visibility ceiling so that a
remote Cell cannot receive records beyond the locally authorized visibility
level.

---

## Non-goals

Royalty Cell Protocol v0.5 does not:

* establish final legal ownership;
* replace copyright, patent, trademark, or contract law;
* determine whether a legal infringement occurred;
* create one global Royalty authority;
* force all Cells to use the same Contribution formula;
* force all Cells to use the same Royalty percentage;
* execute bank transfers;
* determine tax treatment;
* replace payment processors;
* replace accounting systems;
* make every remote record trustworthy;
* replace courts, mediation, or arbitration;
* require blockchain infrastructure;
* require cryptocurrency;
* require one centralized identity provider;
* guarantee that Evidence is authentic;
* guarantee that a claim is factually true.

---

## Adoption model

Royalty Cell Protocol is designed for bottom-up adoption.

```text
One participant records an Origin
    ↓
A project declares Usage
    ↓
A community recognizes Contributions
    ↓
A local Allocation policy is tested
    ↓
Royalty Receipts establish return history
    ↓
Multiple Cells exchange records
    ↓
Institutions adopt compatible profiles
    ↓
Legal and accounting systems may later recognize the records
```

The protocol therefore does not depend on immediate adoption by governments,
large platforms, publishers, or financial institutions.

A Cell can begin with:

* YAML files;
* Git repository history;
* signed statements;
* publication timestamps;
* local governance policies;
* manual or external settlement Evidence.

More advanced infrastructure may be added later.

---

## Relationship to a civilization-scale Royalty OS

Royalty Cell Protocol treats a civilization-scale Royalty OS as an emergent
network rather than one centralized machine.

```text
Royalty Cell
= minimum autonomous value-return unit

Interoperability Link
= Cell-to-Cell connection rule

Dispute Record
= conflict visibility and decision record

Holdback Record
= temporary value-preservation mechanism

Royalty Cell federation
= many independently governed Cells connected through shared records
```

The global structure is not created first.

It emerges after many local structures become useful enough to require shared
identifiers, compatibility rules, adapters, and dispute procedures.

---

## Contributing

Contributions should preserve the protocol's core separations:

```text
Claim
≠ Recognition

Recognition
≠ Weighting

Weighting
≠ Allocation

Allocation
≠ Settlement

Mapping
≠ Legal identity

Dispute
≠ Violation judgment

Holdback
≠ Confiscation
```

New fields or record types should include:

* a clearly bounded purpose;
* explicit non-goals;
* lifecycle states;
* Evidence requirements;
* local and external resolution behavior;
* semantic validation rules;
* passing examples;
* expected-failure examples;
* backward-compatibility considerations.

Changes that silently merge distinct stages of the lifecycle should be avoided.

---

## Versioning

The protocol currently uses semantic versioning during active development.

```text
v0.1 — Cell identity and governance
v0.2 — Origin and Usage
v0.3 — Derivative and Contribution
v0.4 — Weighting, Allocation, and Royalty Receipt
v0.5 — Interoperability, Dispute, and Holdback
```

The `v0.1`–`v0.5` cycle defines the first complete Royalty Cell lifecycle.

Future development may extract mature components into dedicated protocols or
profiles without turning the repository into one indivisible specification.

---

## Summary

Royalty Cell Protocol allows a small community to record:

```text
where value began,
how it was used,
what was derived,
who contributed,
how Contribution was recognized,
how value was allocated,
what was returned,
how another Cell was connected,
and how conflict was handled.
```

The protocol does not attempt to impose one universal economic answer.

It provides the shared evidence structure through which many local answers can
be tested, compared, connected, and improved.

A civilization-scale Royalty OS is therefore not installed from above.

It grows from many Royalty Cells below.
