# Royalty Cell Manifest Specification

Version: 0.1.0

## 1. Purpose

The Royalty Cell Manifest defines the minimum identity and governance
information required for an autonomous Royalty Cell.

A Royalty Cell is a bounded community, project, organization, research group,
or agent collective that records origins, usages, derivatives, contributions,
allocation policies, and royalty receipts under locally defined rules.

Version 0.1 defines the Cell itself.

It does not define:

- ownership adjudication;
- contribution-weight calculation;
- monetary valuation;
- payment execution;
- cross-cell settlement;
- legally enforceable rights.

## 2. Normative language

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are to be
interpreted as normative requirements.

## 3. Core principles

### 3.1 Local autonomy

Each Royalty Cell MAY define its own admission, evidence, recognition,
allocation, and governance policies.

The protocol MUST NOT impose one universal royalty percentage or one universal
contribution-weight formula.

### 3.2 Claims are not ownership judgments

Registering an Origin in a Royalty Cell records that an origin claim was made
at a particular time.

Registration MUST NOT, by itself, be interpreted as a final determination of:

- copyright ownership;
- patent ownership;
- exclusive authorship;
- legal priority;
- entitlement to payment.

### 3.3 Evidence before allocation

A Cell SHOULD define how origin, usage, derivative, and contribution claims
are supported by evidence before distributable value is allocated.

### 3.4 Bottom-up interoperability

A Cell MUST be able to operate independently.

Interoperability MAY later connect multiple Cells without requiring them to use
identical internal governance or allocation rules.

## 4. Record identity

Every manifest MUST contain:

- `schema_version`
- `record_type`
- `cell_id`
- `cell_name`
- `description`
- `status`
- `created_at`
- `updated_at`

`schema_version` MUST be `0.1.0`.

`record_type` MUST be `royalty_cell_manifest`.

`cell_id` MUST remain stable for the lifetime of the Cell.

Changing the Cell name MUST NOT require changing the Cell ID.

## 5. Cell scope

`cell_scope` defines the boundary within which the Cell operates.

The scope MUST declare:

- a scope type;
- one or more domains;
- a human-readable purpose.

A Cell SHOULD keep its scope narrow enough that participants can understand:

- which origins may be registered;
- which usages should be declared;
- which contribution rules apply;
- which authority is responsible for disputes.

## 6. Governance

`governance` identifies how Cell-level decisions are approved.

At least one `authority_ref` MUST be declared.

The selected governance mode MUST NOT automatically imply that the named
authority owns all registered Origins.

If `governance.mode` is `external_policy`, a decision-policy reference MUST
be supplied.

If `decision_policy.approval_rule` is `external`, a decision-policy reference
MUST be supplied.

## 7. Membership and roles

Every Cell MUST define at least one role.

Every `role_id` MUST be unique inside the manifest.

At least one role MUST include the `administer_cell` permission.

Administration permission allows maintenance of the Cell manifest. It does not
automatically grant ownership of registered Origins or entitlement to Royalty.

When `admission_mode` is `request` or `invite_only`, an
`admission_policy_ref` MUST be supplied.

## 8. Recording policy

The recording policy determines:

- who may register an Origin;
- who may declare Usage;
- whether evidence is required;
- who may view records;
- how long records are retained.

When `evidence_requirement` is `required`, at least one accepted evidence type
MUST be declared.

When `evidence_requirement` is `policy_defined`, an `evidence_policy_ref`
MUST be supplied.

If retention mode is `fixed_period`, `duration_days` MUST be supplied.

If retention mode is `external_policy`, a retention `policy_ref` MUST be
supplied.

## 9. Allocation-policy declaration

Version 0.1 does not define allocation formulas.

It only declares whether an allocation policy exists and which settlement
types the Cell intends to support.

When allocation-policy status is `internal` or `external`, `policy_ref` MUST
be supplied.

When allocation-policy status is `not_configured`, `policy_ref` MUST be
omitted.

Supported settlement types may include:

- money;
- credit;
- points;
- attribution;
- access rights;
- governance rights;
- future claims;
- community-fund contributions.

Declaring a supported settlement type does not prove that a settlement was
executed.

## 10. Interoperability

Every Cell MUST declare a canonical identifier namespace.

The namespace SHOULD be used as the prefix for records created by the Cell.

A Cell MAY export records as YAML, JSON, or NDJSON.

An interoperability-profile reference MAY be supplied when the Cell conforms
to an external profile.

Version 0.1 does not define cross-cell identifier mapping. That capability is
reserved for a later version.

## 11. Timestamp rules

`created_at` and `updated_at` MUST be valid date-time values.

`updated_at` MUST be equal to or later than `created_at`.

## 12. Security and abuse considerations

Implementations SHOULD account for:

- false origin claims;
- duplicate origin registration;
- impersonated contributors;
- fabricated evidence;
- unauthorized manifest changes;
- coercive allocation policies;
- privacy leakage through public records;
- malicious export of restricted records.

A Cell SHOULD retain sufficient evidence to audit important decisions without
publishing confidential material unnecessarily.

## 13. Version 0.1 conformance

A manifest conforms to version 0.1 when:

1. it validates against the JSON Schema;
2. it satisfies all semantic rules in this specification;
3. its Cell ID remains stable;
4. it declares at least one administrator role;
5. it does not represent Origin registration as final ownership adjudication.
