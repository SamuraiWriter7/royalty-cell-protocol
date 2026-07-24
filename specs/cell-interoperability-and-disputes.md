# Cell Interoperability, Disputes and Holdbacks

Version: 0.5.0

## 1. Purpose

Version 0.5 defines:

1. Royalty Cell Interoperability Link
2. Royalty Cell Dispute Record
3. Royalty Cell Holdback Record

These records allow independently governed Royalty Cells to exchange
references without surrendering local autonomy.

```text
Royalty Cell A
    ↓
Interoperability Link
    ↓
Royalty Cell B
    ↓
Cross-Cell records
    ↓
Dispute
    ↓
Holdback or Remedy
2. Required separation

Implementations MUST preserve the following distinctions:

Interoperability
is not universal trust.

Identifier mapping
is not legal identity adjudication.

A dispute filing
is not proof of violation.

A Holdback
is not confiscation.

A Cell decision
is not necessarily an external legal judgment.
3. Interoperability Link
3.1 Definition

An Interoperability Link records a controlled relationship between a local
Royalty Cell and one remote Royalty Cell.

Each Link MUST identify:

the local Cell;
the remote Cell;
the trust mode;
the interoperability profiles;
identifier mappings;
permitted record exchange;
policy compatibility.
3.2 Independent governance

A Link MUST NOT imply that either Cell has authority over the internal
governance of the other Cell.

Each Cell retains authority over:

membership;
Origin registration;
Contribution recognition;
Allocation policies;
dispute procedures;
settlement rules.
3.3 Trust modes

Supported trust modes are:

unverified
declarative
verified
federated

Trust mode describes the declared verification relationship.

It does not eliminate the need to verify individual records.

3.4 Identifier mappings

An identifier mapping connects one local identifier to one remote identifier.

Supported relationships include:

equivalent to;
alias of;
mirrors;
derived from;
supersedes;
conflicts with.

An equivalent_to mapping MUST NOT automatically be interpreted as proof
that two records have identical legal owners, rights, or obligations.

3.5 Local resolution

A locally resolved identifier MUST exist among known local passing records
when its record type is supported by the conformance suite.

A remote externally resolved identifier MUST identify a remote record
reference.

3.6 Policy compatibility

Policy compatibility may be:

compatible
adapter_required
conflict
unassessed

An adapter-required relationship MUST identify at least one adapter.

A conflict relationship MUST identify at least one conflict reference.

An active Link with a known policy conflict MUST identify an explicit
activation override.

3.7 Link lifecycle

An active Link MUST identify activated_at.

A suspended Link MUST identify:

suspended_at;
status_reason.

A retired Link MUST identify:

retired_at;
status_reason.
4. Dispute Record
4.1 Definition

A Dispute Record states that one or more parties challenge a record,
relationship, policy, decision, or settlement state.

A dispute may concern:

Origin priority;
Authorization;
Usage;
Derivative relationships;
Contribution recognition;
Contribution weights;
Allocation;
settlement;
interoperability mappings;
policy conflicts.
4.2 Filing effect

Every Dispute Record MUST declare:

dispute_effect: dispute_record_only

A filed dispute does not establish that the respondent acted improperly.

4.3 Parties

The same identity MUST NOT appear as both filer and respondent in the same
Dispute Record.

A Cell MAY support internal disputes, cross-Cell disputes, or both.

4.4 Contested records

Every dispute MUST identify at least one contested record or policy.

A locally resolved contested record MUST resolve among the local records
known to the conformance suite.

An externally resolved contested record MUST provide a record reference.

A Dispute Record MUST NOT identify itself as a contested record.

4.5 Decision

A decided or dismissed dispute MUST contain a decision.

The decision MUST identify:

outcome;
decision authorities;
decision time;
governing policies;
rationale;
remedy actions.
4.6 Withdrawal and escalation

A withdrawn dispute MUST identify:

withdrawn_at;
status_reason.

An escalated dispute MUST identify:

escalated_at;
escalation_ref;
status_reason.
5. Holdback Record
5.1 Definition

A Holdback Record temporarily prevents some or all units assigned to one
Allocation Plan line from being settled or treated as freely available.

A Holdback MUST reference:

a dispute;
an Allocation Plan;
one Allocation line;
one beneficiary;
one unit definition.
5.2 Holdback effect

Every Holdback MUST declare:

holdback_effect: settlement_hold_only

A Holdback does not revoke the underlying Contribution Claim or permanently
transfer the held value.

5.3 Arithmetic

The following relation MUST hold:

held_units
- released_units
= remaining_held_units

Released units MUST equal the sum of all Release Event units.

Held units MUST NOT exceed the units assigned to the referenced Allocation
Plan line.

5.4 Statuses

Supported statuses are:

pending
active
partially_released
released
cancelled

An active Holdback MUST identify:

imposed_at;
one or more imposing authorities.

A partially released Holdback MUST satisfy:

0 < released_units < held_units

A released Holdback MUST have:

released_units = held_units
remaining_held_units = 0

A released Holdback MUST contain at least one Release Event and
released_at.

A cancelled Holdback MUST identify:

cancelled_at;
cancellation_reason.
6. Cross-Cell governance

Version 0.5 does not create one global authority above all Cells.

Cross-Cell relationships remain federated.

Local Cell governance
    ↓
Shared protocol format
    ↓
Interoperability Link
    ↓
Negotiated compatibility
    ↓
Dispute or adapter when needed
7. Security considerations

Implementations SHOULD account for:

forged remote Cell manifests;
malicious identifier mappings;
false equivalent-record claims;
incompatible Allocation policies;
fabricated remote evidence;
dispute spam;
collusive dispute decisions;
indefinite Holdbacks;
beneficiary substitution;
concealed releases;
replayed settlement evidence;
unauthorized activation overrides.
8. Version 0.5 conformance

An Interoperability Link conforms when:

it validates against its JSON Schema;
local and remote Cell identifiers differ;
active Links identify activation time;
local identifier mappings resolve;
remote resolved mappings include references;
mapping identifiers and pairs are unique;
policy compatibility requirements are satisfied.

A Dispute Record conforms when:

it validates against its JSON Schema;
filer and respondent identities do not overlap;
contested references are unique;
local contested records resolve;
completed statuses contain decisions;
status-dependent requirements are satisfied.

A Holdback Record conforms when:

it validates against its JSON Schema;
its Dispute and Allocation Plan references resolve;
the Allocation line exists;
beneficiary and unit match the Allocation line;
held units do not exceed allocated units;
held, released, and remaining amounts reconcile;
status-dependent requirements are satisfied.
