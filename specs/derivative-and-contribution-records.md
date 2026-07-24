# Derivative and Contribution Records Specification

Version: 0.3.0

## 1. Purpose

Version 0.3 defines:

1. Royalty Cell Derivative Record
2. Royalty Cell Contribution Claim

These records connect declared Usage to later contribution evaluation and
Royalty allocation.

```text
Origin
    ↓
Usage
    ↓
Derivative
    ↓
Contribution Claim
    ↓
Recognition
    ↓
Allocation

Version 0.3 does not calculate final contribution weights, determine Royalty
amounts, or execute settlement.

2. Required separation

Implementations MUST preserve the following distinctions:

A Derivative Record
is not a legal infringement judgment.

A Contribution Claim
is not a recognized contribution.

A recognized contribution
is not a final allocation weight.

A final allocation weight
is not proof of settlement.
3. Derivative Record
3.1 Definition

A Derivative Record identifies a structure, artifact, implementation, or
output that was created from one or more Origin or Derivative records.

A Derivative may include:

adaptation;
transformation;
combination;
translation;
summary;
extraction;
extension;
implementation;
distillation;
remix;
another declared transformation.
3.2 Parent records

Every Derivative Record MUST identify at least one parent.

A parent may be:

an Origin Record;
another Derivative Record.

Every parent link MUST declare:

the source identifier;
the source record type;
the source Cell;
the relationship;
the dependency level;
the resolution status.
3.3 Dependency level

Supported dependency levels are:

primary
supporting
incidental

Dependency level is qualitative.

It MUST NOT be interpreted as a fixed allocation percentage.

For example:

primary
does not automatically mean the largest Royalty share.

supporting
does not automatically mean a minority share.

incidental
does not automatically mean zero contribution.
3.4 Derivative distance

A transformation profile declares one of the following qualitative distances:

direct
near
moderate
substantial

Derivative distance describes the declared degree of transformation.

It MUST NOT, by itself, determine:

originality;
legal independence;
copyright status;
contribution weight;
Royalty obligation.
3.5 Transformation operations

A Derivative Record MAY describe operations such as:

translation;
summarization;
reorganization;
implementation;
parameterization;
combination;
reduction;
expansion;
stylistic change;
format change;
extraction;
distillation.

At least one operation MUST be declared.

3.6 Combination records

When derivative_type is combination, the record MUST identify at least two
distinct parent records.

3.7 Local resolution

A locally resolved parent MUST be resolvable among the local passing Origin
or Derivative records.

An externally resolved parent MUST provide a record_ref.

An unresolved parent MAY remain visible so that incomplete Trace is not
silently discarded.

3.8 Self-reference

A Derivative Record MUST NOT identify itself as its own parent.

Circular Derivative chains SHOULD be rejected by broader conformance suites.

3.9 Derivative status

Supported states are:

declared
acknowledged
contested
withdrawn
superseded

A contested Derivative MUST identify at least one contest reference.

A withdrawn Derivative MUST provide a status reason.

A superseded Derivative MUST identify its successor.

3.10 Allocation effect

Every Derivative Record MUST contain:

allocation_effect: not_yet_determined

This confirms that the Derivative Record does not itself establish a Royalty
share.

4. Contribution Claim
4.1 Definition

A Contribution Claim records that a participant claims to have contributed to
an Origin, Usage, Derivative, project, or output.

A Contribution Claim may describe:

conceptualization;
research;
architecture;
protocol design;
implementation;
writing;
editing;
review;
data provision;
model provision;
prompt design;
orchestration;
validation;
governance;
funding;
infrastructure.
4.2 Claim and recognition

A claim is submitted by a contributor.

Recognition is a separate Cell-governance decision.

The contributor and the recognizing authority MAY be different parties.

A submitted claim MUST NOT be treated as recognized unless a corresponding
recognition decision exists.

4.3 Claimed significance

The contributor may declare the claimed significance as:

foundational
major
supporting
minor
unspecified

This classification is qualitative.

It MUST NOT be interpreted as a numeric contribution weight.

4.4 Claim status

Supported states are:

submitted
acknowledged
recognized
partially_recognized
rejected
disputed
withdrawn
superseded

A recognized claim MUST contain a matching recognition decision.

A partially recognized claim MUST contain a matching partial-recognition
decision.

A rejected claim MUST contain a rejection decision and rationale.

A disputed claim MUST identify at least one dispute reference.

A withdrawn claim MUST provide a status reason.

A superseded claim MUST identify its successor.

4.5 Recognition decision

A completed recognition decision MUST identify:

the recognition status;
one or more recognizing authorities;
the decision time;
a rationale;
the applicable recognition policy.

Recognized and partially recognized claims MUST also identify the recognized
significance.

4.6 Allocation effect

Every Contribution Claim MUST contain:

allocation_effect: contribution_evidence_only

A Contribution Claim and its recognition provide evidence for a later
Allocation stage.

They do not directly establish:

a payment amount;
a percentage share;
a settlement obligation;
legal ownership.
5. Evidence

Every Derivative Record and Contribution Claim MUST contain at least one
Evidence item.

Evidence identifiers MUST be unique within each record.

Evidence may include:

repository commits;
publication records;
signed statements;
execution receipts;
content hashes;
audit records;
external references.

Evidence records support verification but do not automatically prove that a
claim is true.

6. Privacy

Derivative and Contribution records may expose sensitive information.

Implementations SHOULD minimize disclosure of:

unpublished concepts;
private prompts;
internal source code;
employee performance details;
confidential review comments;
contractual contribution terms;
personal data.

A record MAY publish a digest or protected reference instead of the underlying
content.

7. Security considerations

Implementations SHOULD account for:

fabricated Derivative relationships;
hidden parent Origins;
circular Derivative chains;
false contributor identities;
inflated significance claims;
collusive recognition;
unauthorized recognition decisions;
duplicate claims;
Evidence substitution;
retaliation through Contribution rejection;
privacy leakage.
8. Version 0.3 conformance

A Derivative Record conforms when:

it validates against the Derivative Record JSON Schema;
it identifies at least one parent;
it does not reference itself;
local parent references resolve;
external references include a record reference;
Evidence identifiers are unique;
status-dependent requirements are satisfied;
allocation_effect remains not_yet_determined.

A Contribution Claim conforms when:

it validates against the Contribution Claim JSON Schema;
its target is properly identified;
local record targets resolve when applicable;
claim and recognition states are consistent;
completed decisions identify authority, time, rationale, and policy;
Evidence identifiers are unique;
status-dependent requirements are satisfied;
allocation_effect remains contribution_evidence_only.
