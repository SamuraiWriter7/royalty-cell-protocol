# Allocation and Royalty Receipts Specification

Version: 0.4.0

## 1. Purpose

Version 0.4 defines:

1. Contribution Weight Resolution
2. Allocation Plan
3. Royalty Receipt

These records convert recognized Contribution evidence into an auditable
value-return process.

```text
Recognized Contribution Claims
    ↓
Contribution Weight Resolution
    ↓
Allocation Plan
    ↓
Royalty Receipt
2. Required separation

Implementations MUST preserve these distinctions:

Contribution recognition
is not a numeric weight.

A numeric weight
is not an approved Allocation.

An approved Allocation
is not completed settlement.

A Royalty Receipt
is not final legal adjudication.
3. Contribution Weight Resolution
3.1 Definition

A Contribution Weight Resolution converts one or more recognized or partially
recognized Contribution Claims into normalized weights.

3.2 Eligible claims

A finalized Weight Resolution MUST reference only Contribution Claims whose
Cell recognition status is:

recognized; or
partially_recognized.

Submitted, rejected, withdrawn, disputed, or superseded claims MUST NOT be
included in a finalized Weight Resolution.

3.3 Normalization

A finalized Weight Resolution MUST satisfy:

sum(normalized_weight) = 1

The declared normalization tolerance MAY account for decimal representation.

3.4 Duplicate claims

The same Contribution Claim MUST NOT appear more than once in one Weight
Resolution.

Assignment identifiers MUST be unique.

3.5 Decision

A finalized Weight Resolution MUST identify:

the deciding authorities;
the decision time;
the applicable policy;
the rationale.

An external method MUST also identify the external result.

3.6 Allocation effect

Every Weight Resolution MUST declare:

allocation_effect: weight_resolution_only

A Weight Resolution does not move value.

4. Allocation Plan
4.1 Definition

An Allocation Plan applies one finalized Weight Resolution to one declared
value event.

4.2 Value event

A value event identifies the economic or non-monetary event that created
allocable units.

Examples include:

sale;
license;
subscription;
service fee;
grant;
donation;
cost saving;
point issuance;
credit issuance;
rights grant.
4.3 Allocation arithmetic

The following relation MUST hold:

gross_units
- sum(deductions)
= distributable_units

The following relation MUST also hold:

sum(allocated_units)
= distributable_units

Applied allocation weights MUST sum to one.

4.4 Weight coverage

Each Contribution Claim in the referenced Weight Resolution MUST be assigned
to exactly one Allocation line.

An Allocation line's applied_weight MUST equal the sum of the normalized
weights of its referenced Contribution Claims.

4.5 Deductions

Deductions may include:

platform cost;
tax;
community fund;
reserve;
refund;
another locally defined deduction.

A deduction MUST identify its governing policy.

4.6 Approval

An approved, partially executed, or executed plan MUST contain an explicit
approval record.

A cancelled plan MUST identify the cancellation time and reason.

4.7 Allocation effect

Every Allocation Plan MUST declare:

allocation_effect: allocation_plan_only

The plan records an obligation or intention. It does not prove execution.

5. Royalty Receipt
5.1 Definition

A Royalty Receipt records the settlement state of one Allocation Plan line.

5.2 Settlement states

Supported states are:

pending
partially_settled
settled
failed
held
waived
reversed
5.3 Arithmetic

The following relation MUST hold:

allocated_units
- settled_units
= balance_remaining_units

Settled units MUST NOT exceed allocated units.

5.4 Completed settlement

A settled Royalty Receipt MUST contain:

settled_at;
at least one Settlement Evidence item;
zero remaining balance.
5.5 Partial settlement

A partially settled receipt MUST have:

0 < settled_units < allocated_units

It MUST contain Settlement Evidence.

5.6 Pending settlement

A pending receipt MUST have zero settled units.

5.7 Failed settlement

A failed receipt MUST provide a status reason.

5.8 Held settlement

A held receipt MUST identify the relevant hold record.

5.9 Waiver and reversal

A waived receipt MUST identify a waiver record.

A reversed receipt MUST identify a reversal record.

5.10 Receipt effect

Every Royalty Receipt MUST declare:

receipt_effect: settlement_record_only

The receipt records what the Cell claims occurred.

It does not replace external payment, tax, accounting, or legal evidence.

6. Units

Version 0.4 supports:

currency;
points;
credits;
attribution units;
access rights;
governance rights;
future claims;
other Cell-defined units.

One Allocation Plan MUST use one consistent unit definition.

7. Security considerations

Implementations SHOULD account for:

inflated Contribution weights;
omitted recognized contributors;
duplicated Contribution Claims;
hidden deductions;
manipulated rounding;
false value events;
beneficiary substitution;
fabricated payment evidence;
receipts exceeding approved Allocation;
unauthorized waivers;
concealed reversals;
self-approved distributions;
collusive governance.
8. Privacy

Allocation Plans and Royalty Receipts may expose:

contributor identities;
payment amounts;
bank or ledger references;
internal business revenue;
employee compensation data;
contractual terms.

Implementations SHOULD permit restricted records and protected Evidence
references.

9. Version 0.4 conformance

A Weight Resolution conforms when:

it validates against its JSON Schema;
local Contribution Claims resolve;
finalized claims are recognized or partially recognized;
normalized weights sum to one;
assignment and claim identifiers are unique;
the decision is complete.

An Allocation Plan conforms when:

it validates against its JSON Schema;
the referenced Weight Resolution resolves and is finalized;
gross value, deductions, and distributable value reconcile;
allocation lines sum to distributable value;
applied weights sum to one;
all Weight assignments are covered exactly once;
approval-state requirements are satisfied.

A Royalty Receipt conforms when:

it validates against its JSON Schema;
the referenced Allocation Plan and line resolve;
the beneficiary, unit, amount, and Settlement type match the Plan;
allocated, settled, and remaining amounts reconcile;
status-dependent Evidence requirements are satisfied.
