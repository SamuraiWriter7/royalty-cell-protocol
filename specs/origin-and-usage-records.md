# Origin and Usage Records Specification

Version: 0.2.0

## 1. Purpose

Version 0.2 defines two records:

1. Royalty Cell Origin Record
2. Royalty Cell Usage Record

Together, these records establish the first operational Trace inside a
Royalty Cell.

```text
Origin claim
    ↓
Declared use
    ↓
Derivative and contribution records
    ↓
Allocation and Royalty

Version 0.2 does not calculate contribution weights, determine Royalty
amounts, or execute settlement.

2. Core separation

Implementations MUST preserve the following distinctions:

Origin registration
is not legal ownership adjudication.

Usage declaration
is not proof of authorization.

Authorization
is not proof that Usage occurred.

Completed Usage
is not proof that value was generated.

Value generation
is not proof that Royalty was settled.

These stages may later be connected, but they MUST remain separately
identifiable.

3. Origin Record
3.1 Definition

An Origin Record states that one or more claimants declared a concept,
question, framework, method, specification, code artifact, dataset, model,
prompt, design, creative work, or other resource as an Origin inside a
Royalty Cell.

3.2 Claim effect

Every Origin Record MUST contain:

claim_effect: claim_record_only

This field confirms that the record is a timestamped claim.

The record MUST NOT, by itself, be interpreted as a final determination of:

copyright ownership;
patent ownership;
exclusive authorship;
legal priority;
contractual entitlement;
entitlement to Royalty.
3.3 Evidence

Every Origin Record MUST contain at least one Evidence item.

A self-declared Origin MAY use a signed statement or timestamped record as
its initial evidence.

Evidence strength may vary. Recording evidence does not automatically make
the claim true.

3.4 Claim status

Supported Origin claim states are:

declared
acknowledged
contested
withdrawn
superseded

A contested claim MUST identify at least one contest reference.

A withdrawn claim MUST provide a status reason.

A superseded claim MUST identify the succeeding Origin Record.

3.5 Imported Origin Records

When claim_basis is imported_record, the record MUST identify the source
through imported_from_ref.

Importing a record MUST NOT silently convert an external claim into a
locally verified claim.

3.6 Precedence references

An Origin MAY cite earlier records through precedence_refs.

A precedence reference indicates structural or historical dependency.

It does not automatically assign ownership or contribution weight.

4. Usage Record
4.1 Definition

A Usage Record states that a participant, system, authority, or imported
record declared the use of one or more Origins.

Usage may include:

reference;
adaptation;
transformation;
execution;
training;
retrieval;
distillation;
embedding;
publication;
commercial service;
internal use.
4.2 Declarant

The declarant is the party responsible for submitting the Usage Record.

The declarant MAY be:

the person who used the Origin;
an AI agent;
a project authority;
an observing system;
an importer of an external Usage Record.

The declarant is not necessarily the beneficiary, rights holder, or final
operator.

4.3 Origin links

Every Usage Record MUST identify at least one Origin.

Each Origin link records:

the Origin identifier;
its source Cell;
the relationship to the Usage;
its dependency level;
its resolution status.

Dependency level MUST NOT be interpreted as an allocation percentage.

For example:

primary
does not mean 100 percent of Royalty.

supporting
does not mean a fixed lower percentage.

incidental
does not mean zero contribution.

Allocation is defined in a later protocol version.

4.4 Resolution status

Supported Origin resolution states are:

resolved
externally_resolved
unresolved

A locally resolved Origin SHOULD be resolvable inside the same Royalty Cell.

An externally resolved Origin MUST identify an external record reference.

An unresolved Origin MAY be recorded to preserve incomplete Trace, but its
uncertainty SHOULD remain visible to downstream Audit and Allocation stages.

4.5 Usage status

Supported Usage states are:

declared
completed
blocked
disputed
withdrawn

A completed Usage MUST identify when the Usage occurred.

A completed Usage MUST NOT have a denied authorization state.

A disputed Usage MUST identify at least one dispute reference.

A withdrawn Usage MUST provide a status reason.

4.6 Authorization

The Authorization object records the declared authorization state.

Supported states are:

not_required
granted
pending
denied
unknown

When Authorization is granted, an authorization reference MUST be
provided.

When Authorization is not_required, a policy reference MUST be provided.

A Usage Record MUST NOT silently treat an unknown or missing authorization
state as granted.

4.7 Attribution

A Usage Record MAY record attribution independently of monetary settlement.

Supported attribution states are:

not_required
planned
provided
omitted
disputed

When attribution is provided, the record MUST identify display text or a
target reference.

Attribution is one possible form of value return, but it does not replace
Royalty when a separate Royalty obligation exists.

5. Evidence identifiers

Evidence identifiers MUST be unique inside each record.

Evidence MAY include:

signed declarations;
repository commits;
publication records;
timestamps;
usage logs;
execution receipts;
Audit records;
external references.
6. Local reference validation

A repository conformance suite MAY verify that a locally resolved Usage
Origin exists among the local Origin examples.

This validation is intended to detect broken examples and incomplete
protocol packages.

Production systems MAY use external resolvers instead of storing every
Origin Record in one repository.

7. Privacy

Origin and Usage records may contain sensitive information.

Implementations SHOULD minimize unnecessary disclosure of:

private prompts;
confidential source materials;
personal data;
unpublished concepts;
internal execution logs;
contractual terms.

A public record MAY expose a digest or reference instead of the underlying
content.

8. Security considerations

Implementations SHOULD account for:

false Origin claims;
fabricated timestamps;
evidence substitution;
fake Usage declarations;
undeclared commercial Usage;
impersonated declarants;
unauthorized record modification;
hidden external Origins;
deliberate use of unresolved references;
false authorization declarations.
9. Version 0.2 conformance

An Origin Record conforms to version 0.2 when:

it validates against the Origin Record JSON Schema;
it preserves claim_effect: claim_record_only;
it includes at least one Evidence item;
it satisfies claim-status semantic rules;
its Evidence identifiers are unique.

A Usage Record conforms to version 0.2 when:

it validates against the Usage Record JSON Schema;
it identifies at least one Origin;
it declares Authorization separately from Usage status;
it satisfies Usage-status semantic rules;
locally resolved Origins can be resolved by the conformance suite;
its Evidence identifiers are unique.
