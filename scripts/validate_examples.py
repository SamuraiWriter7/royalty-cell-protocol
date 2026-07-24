#!/usr/bin/env python3
"""Validate Royalty Cell Protocol examples from v0.1 through v0.5.

Pass examples must satisfy JSON Schema and semantic validation.
Fail examples must be rejected by at least one validation stage.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

SCHEMAS: dict[str, Path] = {
    "royalty_cell_manifest": ROOT / "schemas" / "royalty-cell-manifest.schema.json",
    "royalty_cell_origin_record": ROOT / "schemas" / "royalty-cell-origin-record.schema.json",
    "royalty_cell_usage_record": ROOT / "schemas" / "royalty-cell-usage-record.schema.json",
    "royalty_cell_derivative_record": ROOT / "schemas" / "royalty-cell-derivative-record.schema.json",
    "royalty_cell_contribution_claim": ROOT / "schemas" / "royalty-cell-contribution-claim.schema.json",
    "royalty_cell_contribution_weight_resolution": (
        ROOT / "schemas" / "royalty-cell-contribution-weight-resolution.schema.json"
    ),
    "royalty_cell_allocation_plan": ROOT / "schemas" / "royalty-cell-allocation-plan.schema.json",
    "royalty_cell_royalty_receipt": ROOT / "schemas" / "royalty-cell-royalty-receipt.schema.json",
    "royalty_cell_interoperability_link": (
        ROOT / "schemas" / "royalty-cell-interoperability-link.schema.json"
    ),
    "royalty_cell_dispute_record": ROOT / "schemas" / "royalty-cell-dispute-record.schema.json",
    "royalty_cell_holdback_record": ROOT / "schemas" / "royalty-cell-holdback-record.schema.json",
}

ID_FIELDS = {
    "royalty_cell_manifest": "cell_id",
    "royalty_cell_origin_record": "origin_id",
    "royalty_cell_usage_record": "usage_id",
    "royalty_cell_derivative_record": "derivative_id",
    "royalty_cell_contribution_claim": "claim_id",
    "royalty_cell_contribution_weight_resolution": "resolution_id",
    "royalty_cell_allocation_plan": "allocation_plan_id",
    "royalty_cell_royalty_receipt": "receipt_id",
    "royalty_cell_interoperability_link": "link_id",
    "royalty_cell_dispute_record": "dispute_id",
    "royalty_cell_holdback_record": "holdback_id",
}

REF_TYPES = {
    "manifest": "royalty_cell_manifest",
    "origin_record": "royalty_cell_origin_record",
    "usage_record": "royalty_cell_usage_record",
    "derivative_record": "royalty_cell_derivative_record",
    "contribution_claim": "royalty_cell_contribution_claim",
    "weight_resolution": "royalty_cell_contribution_weight_resolution",
    "allocation_plan": "royalty_cell_allocation_plan",
    "royalty_receipt": "royalty_cell_royalty_receipt",
    "interoperability_link": "royalty_cell_interoperability_link",
    "dispute_record": "royalty_cell_dispute_record",
    "holdback_record": "royalty_cell_holdback_record",
}

Known = dict[str, dict[str, dict[str, Any]]]
Validators = dict[str, Draft202012Validator]
SemanticFn = Callable[[dict[str, Any], Known], list[str]]


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be an object")
    return data


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be a mapping")
    return data


def yaml_files(directory: Path) -> list[Path]:
    return sorted(set(directory.glob("*.yaml")) | set(directory.glob("*.yml")))


def err_path(parts: list[Any]) -> str:
    if not parts:
        return "<root>"
    out = ""
    for part in parts:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += ("." if out else "") + str(part)
    return out


def iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    value = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def dec(value: Any) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def close(a: Decimal, b: Decimal, tolerance: Decimal = Decimal("0")) -> bool:
    return abs(a - b) <= tolerance


def strings(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def missing(mapping: Mapping[str, Any], fields: list[str], prefix: str) -> list[str]:
    return [f"{prefix}.{field}: required" for field in fields if not mapping.get(field)]


def external_ref(
    mapping: Mapping[str, Any],
    *,
    status_field: str = "resolution_status",
    ref_field: str = "record_ref",
    prefix: str,
) -> list[str]:
    if mapping.get(status_field) == "externally_resolved" and not mapping.get(ref_field):
        return [
            f"{prefix}.{ref_field}: required when {status_field} is 'externally_resolved'"
        ]
    return []


def evidence_errors(document: dict[str, Any], field: str = "evidence") -> list[str]:
    items = document.get(field, [])
    if not isinstance(items, list):
        return []
    ids = [item.get("evidence_id") for item in items if isinstance(item, dict)]
    return [f"{field}: duplicate evidence_id '{value}'" for value in duplicates(strings(ids))]


def resolve(ref_type: Any, record_id: Any, known: Known) -> dict[str, Any] | None:
    internal = REF_TYPES.get(ref_type) if isinstance(ref_type, str) else None
    if internal is None or not isinstance(record_id, str):
        return None
    return known.get(internal, {}).get(record_id)


# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------


def load_validators() -> Validators:
    validators: Validators = {}
    for record_type, path in SCHEMAS.items():
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        validators[record_type] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )
    return validators


def schema_errors(document: dict[str, Any], validators: Validators) -> list[str]:
    record_type = document.get("record_type")
    if not isinstance(record_type, str):
        return ["record_type: missing or not a string"]
    validator = validators.get(record_type)
    if validator is None:
        return [f"record_type: unsupported record type '{record_type}'"]
    return [
        f"{err_path(list(error.absolute_path))}: {error.message}"
        for error in sorted(
            validator.iter_errors(document),
            key=lambda item: list(item.absolute_path),
        )
    ]


def collect_known(pass_files: list[Path], validators: Validators) -> Known:
    known: Known = {record_type: {} for record_type in ID_FIELDS}
    for path in pass_files:
        try:
            document = load_yaml(path)
        except (OSError, ValueError, yaml.YAMLError):
            continue
        record_type = document.get("record_type")
        if record_type not in ID_FIELDS or schema_errors(document, validators):
            continue
        record_id = document.get(ID_FIELDS[record_type])
        if isinstance(record_id, str):
            known[record_type][record_id] = document
    return known


# ---------------------------------------------------------------------------
# v0.1 — Manifest
# ---------------------------------------------------------------------------


def validate_manifest(document: dict[str, Any], _known: Known) -> list[str]:
    errors: list[str] = []
    created = iso_datetime(document.get("created_at"))
    updated = iso_datetime(document.get("updated_at"))
    if created and updated and updated < created:
        errors.append("updated_at: must be equal to or later than created_at")

    governance = document.get("governance", {})
    if isinstance(governance, dict):
        decision = governance.get("decision_policy", {})
        if isinstance(decision, dict):
            if decision.get("approval_rule") == "external" and not decision.get("policy_ref"):
                errors.append(
                    "governance.decision_policy.policy_ref: required when approval_rule is 'external'"
                )
            if governance.get("mode") == "external_policy" and not decision.get("policy_ref"):
                errors.append(
                    "governance.decision_policy.policy_ref: required when governance mode is 'external_policy'"
                )

    membership = document.get("membership", {})
    if isinstance(membership, dict):
        if membership.get("admission_mode") in {"request", "invite_only"} and not membership.get(
            "admission_policy_ref"
        ):
            errors.append(
                "membership.admission_policy_ref: required when admission_mode is 'request' or 'invite_only'"
            )
        roles = membership.get("roles", [])
        if isinstance(roles, list):
            role_ids = [role.get("role_id") for role in roles if isinstance(role, dict)]
            for value in duplicates(strings(role_ids)):
                errors.append(f"membership.roles: duplicate role_id '{value}'")
            if not any(
                "administer_cell" in strings(role.get("permissions"))
                for role in roles
                if isinstance(role, dict)
            ):
                errors.append(
                    "membership.roles: at least one role must include the 'administer_cell' permission"
                )

    recording = document.get("recording_policy", {})
    if isinstance(recording, dict):
        requirement = recording.get("evidence_requirement")
        if requirement == "required" and not strings(recording.get("accepted_evidence_types")):
            errors.append(
                "recording_policy.accepted_evidence_types: required when evidence_requirement is 'required'"
            )
        if requirement == "policy_defined" and not recording.get("evidence_policy_ref"):
            errors.append(
                "recording_policy.evidence_policy_ref: required when evidence_requirement is 'policy_defined'"
            )
        retention = recording.get("retention", {})
        if isinstance(retention, dict):
            mode = retention.get("mode")
            if mode == "fixed_period":
                days = retention.get("duration_days")
                if not isinstance(days, int) or days < 1:
                    errors.append(
                        "recording_policy.retention.duration_days: positive integer required for fixed_period"
                    )
            if mode == "external_policy" and not retention.get("policy_ref"):
                errors.append(
                    "recording_policy.retention.policy_ref: required for external_policy"
                )

    allocation = document.get("allocation_policy", {})
    if isinstance(allocation, dict):
        status = allocation.get("status")
        policy_ref = allocation.get("policy_ref")
        if status in {"internal", "external"} and not policy_ref:
            errors.append(
                "allocation_policy.policy_ref: required when allocation-policy status is 'internal' or 'external'"
            )
        if status == "not_configured" and policy_ref:
            errors.append(
                "allocation_policy.policy_ref: must be omitted when allocation-policy status is 'not_configured'"
            )
    return errors


# ---------------------------------------------------------------------------
# v0.2 — Origin and Usage
# ---------------------------------------------------------------------------


def validate_origin(document: dict[str, Any], _known: Known) -> list[str]:
    errors: list[str] = []
    created = iso_datetime(document.get("origin_created_at"))
    declared = iso_datetime(document.get("declared_at"))
    if created and declared and created > declared:
        errors.append("origin_created_at: must not be later than declared_at")

    basis = document.get("claim_basis")
    status = document.get("claim_status")
    if basis == "imported_record" and not document.get("imported_from_ref"):
        errors.append("imported_from_ref: required when claim_basis is 'imported_record'")
    if status == "contested" and not strings(document.get("contest_refs")):
        errors.append("contest_refs: required when claim_status is 'contested'")
    if status == "withdrawn" and not document.get("status_reason"):
        errors.append("status_reason: required when claim_status is 'withdrawn'")
    if status == "superseded" and not document.get("superseded_by_ref"):
        errors.append("superseded_by_ref: required when claim_status is 'superseded'")
    errors.extend(evidence_errors(document))
    return errors


def validate_usage(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    status = document.get("usage_status")
    if status == "completed" and not document.get("occurred_at"):
        errors.append("occurred_at: required when usage_status is 'completed'")
    if status == "disputed" and not strings(document.get("dispute_refs")):
        errors.append("dispute_refs: required when usage_status is 'disputed'")
    if status == "withdrawn" and not document.get("status_reason"):
        errors.append("status_reason: required when usage_status is 'withdrawn'")

    authorization = document.get("authorization", {})
    if isinstance(authorization, dict):
        auth_status = authorization.get("status")
        if auth_status == "granted" and not authorization.get("authorization_ref"):
            errors.append(
                "authorization.authorization_ref: required when authorization status is 'granted'"
            )
        if auth_status == "not_required" and not authorization.get("policy_ref"):
            errors.append(
                "authorization.policy_ref: required when authorization status is 'not_required'"
            )
        if auth_status == "denied" and status == "completed":
            errors.append("usage_status: completed Usage cannot have denied authorization")

    links = document.get("origin_links", [])
    origin_ids: list[str] = []
    cell_id = document.get("cell_id")
    if isinstance(links, list):
        for index, link in enumerate(links):
            if not isinstance(link, dict):
                continue
            origin_id = link.get("origin_id")
            if isinstance(origin_id, str):
                origin_ids.append(origin_id)
            errors.extend(external_ref(link, prefix=f"origin_links[{index}]"))
            if (
                link.get("resolution_status") == "resolved"
                and link.get("source_cell_id") == cell_id
                and origin_id not in known["royalty_cell_origin_record"]
            ):
                errors.append(
                    f"origin_links[{index}].origin_id: locally resolved Origin '{origin_id}' was not found among passing local Origin examples"
                )
    for value in duplicates(origin_ids):
        errors.append(f"origin_links: duplicate origin_id '{value}'")

    attribution = document.get("attribution")
    if isinstance(attribution, dict) and attribution.get("status") == "provided":
        if not attribution.get("display_text") and not attribution.get("target_ref"):
            errors.append(
                "attribution: display_text or target_ref is required when attribution status is 'provided'"
            )

    scope = document.get("usage_scope", {})
    if isinstance(scope, dict):
        start = iso_datetime(scope.get("start_at"))
        end = iso_datetime(scope.get("end_at"))
        if start and end and end < start:
            errors.append("usage_scope.end_at: must be equal to or later than usage_scope.start_at")
    errors.extend(evidence_errors(document))
    return errors


# ---------------------------------------------------------------------------
# v0.3 — Derivative and Contribution
# ---------------------------------------------------------------------------


def validate_derivative(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    derivative_id = document.get("derivative_id")
    cell_id = document.get("cell_id")
    derivative_type = document.get("derivative_type")
    status = document.get("derivative_status")

    created = iso_datetime(document.get("created_at"))
    declared = iso_datetime(document.get("declared_at"))
    if created and declared and created > declared:
        errors.append("created_at: must not be later than declared_at")
    if status == "contested" and not strings(document.get("contest_refs")):
        errors.append("contest_refs: required when derivative_status is 'contested'")
    if status == "withdrawn" and not document.get("status_reason"):
        errors.append("status_reason: required when derivative_status is 'withdrawn'")
    if status == "superseded" and not document.get("superseded_by_ref"):
        errors.append("superseded_by_ref: required when derivative_status is 'superseded'")

    parents = document.get("parent_links", [])
    source_ids: list[str] = []
    primary_count = 0
    if isinstance(parents, list):
        for index, parent in enumerate(parents):
            if not isinstance(parent, dict):
                continue
            source_id = parent.get("source_id")
            source_type = parent.get("source_record_type")
            if isinstance(source_id, str):
                source_ids.append(source_id)
            if parent.get("dependency_level") == "primary":
                primary_count += 1
            if source_id == derivative_id:
                errors.append(
                    f"parent_links[{index}].source_id: a Derivative Record cannot reference itself as a parent"
                )
            expected_prefix = {
                "origin_record": "urn:royalty-origin:",
                "derivative_record": "urn:royalty-derivative:",
            }.get(source_type)
            if isinstance(source_id, str) and expected_prefix and not source_id.startswith(expected_prefix):
                errors.append(
                    f"parent_links[{index}].source_id: identifier does not match source_record_type '{source_type}'"
                )
            errors.extend(external_ref(parent, prefix=f"parent_links[{index}]"))
            if (
                parent.get("resolution_status") == "resolved"
                and parent.get("source_cell_id") == cell_id
                and source_type in REF_TYPES
                and resolve(source_type, source_id, known) is None
            ):
                errors.append(
                    f"parent_links[{index}].source_id: locally resolved {source_type} '{source_id}' was not found among passing local examples"
                )
    for value in duplicates(source_ids):
        errors.append(f"parent_links: duplicate source_id '{value}'")
    if primary_count == 0:
        errors.append("parent_links: at least one parent must have dependency_level 'primary'")
    if derivative_type == "combination" and len(set(source_ids)) < 2:
        errors.append("parent_links: derivative_type 'combination' requires at least two distinct parents")
    errors.extend(evidence_errors(document))
    return errors


def validate_contribution(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    status = document.get("claim_status")
    cell_id = document.get("cell_id")
    target = document.get("target", {})

    if isinstance(target, dict):
        target_id = target.get("target_id")
        target_type = target.get("target_record_type")
        expected_prefix = {
            "origin_record": "urn:royalty-origin:",
            "usage_record": "urn:royalty-usage:",
            "derivative_record": "urn:royalty-derivative:",
        }.get(target_type)
        if isinstance(target_id, str) and expected_prefix and not target_id.startswith(expected_prefix):
            errors.append(
                f"target.target_id: identifier does not match target_record_type '{target_type}'"
            )
        errors.extend(external_ref(target, prefix="target"))
        if (
            target.get("resolution_status") == "resolved"
            and target.get("source_cell_id") == cell_id
            and target_type in REF_TYPES
            and resolve(target_type, target_id, known) is None
        ):
            errors.append(
                f"target.target_id: locally resolved {target_type} '{target_id}' was not found among passing local examples"
            )

    period = document.get("contribution_period", {})
    if isinstance(period, dict):
        start = iso_datetime(period.get("start_at"))
        end = iso_datetime(period.get("end_at"))
        if start and end and end < start:
            errors.append(
                "contribution_period.end_at: must be equal to or later than contribution_period.start_at"
            )

    recognition = document.get("recognition")
    expected = {
        "recognized": "recognized",
        "partially_recognized": "partially_recognized",
        "rejected": "rejected",
    }.get(status)
    if expected:
        if not isinstance(recognition, dict):
            errors.append(f"recognition: required when claim_status is '{status}'")
        elif recognition.get("status") != expected:
            errors.append(
                f"recognition.status: expected '{expected}' when claim_status is '{status}'"
            )
    if status in {"submitted", "acknowledged"} and isinstance(recognition, dict):
        if recognition.get("status") != "pending":
            errors.append(
                "recognition.status: submitted or acknowledged claims may only have pending recognition"
            )
    if isinstance(recognition, dict):
        recognition_status = recognition.get("status")
        if recognition_status in {"recognized", "partially_recognized", "rejected"}:
            errors.extend(
                missing(
                    recognition,
                    ["recognized_by_refs", "decided_at", "rationale", "policy_ref"],
                    "recognition",
                )
            )
        if recognition_status in {"recognized", "partially_recognized"} and not recognition.get(
            "recognized_significance"
        ):
            errors.append(
                "recognition.recognized_significance: required for recognized or partially recognized claims"
            )

    if status == "disputed" and not strings(document.get("dispute_refs")):
        errors.append("dispute_refs: required when claim_status is 'disputed'")
    if status == "withdrawn" and not document.get("status_reason"):
        errors.append("status_reason: required when claim_status is 'withdrawn'")
    if status == "superseded" and not document.get("superseded_by_ref"):
        errors.append("superseded_by_ref: required when claim_status is 'superseded'")
    errors.extend(evidence_errors(document))
    return errors


# ---------------------------------------------------------------------------
# v0.4 — Weights, Allocation, Receipt
# ---------------------------------------------------------------------------


def validate_weight(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    cell_id = document.get("cell_id")
    status = document.get("resolution_status")
    method = document.get("method")
    target = document.get("target", {})

    if isinstance(target, dict):
        errors.extend(external_ref(target, prefix="target"))
        if (
            target.get("resolution_status") == "resolved"
            and target.get("source_cell_id") == cell_id
            and target.get("target_record_type") == "derivative_record"
            and target.get("target_id") not in known["royalty_cell_derivative_record"]
        ):
            errors.append("target.target_id: locally resolved Derivative was not found")

    assignments = document.get("assignments", [])
    assignment_ids: list[str] = []
    claim_refs: list[str] = []
    total = Decimal("0")
    if isinstance(assignments, list):
        for index, assignment in enumerate(assignments):
            if not isinstance(assignment, dict):
                continue
            assignment_id = assignment.get("assignment_id")
            claim_ref = assignment.get("contribution_claim_ref")
            if isinstance(assignment_id, str):
                assignment_ids.append(assignment_id)
            if isinstance(claim_ref, str):
                claim_refs.append(claim_ref)
            weight = dec(assignment.get("normalized_weight"))
            if weight is not None:
                total += weight
            errors.extend(external_ref(assignment, prefix=f"assignments[{index}]"))
            if (
                assignment.get("resolution_status") == "resolved"
                and assignment.get("source_cell_id") == cell_id
            ):
                claim = known["royalty_cell_contribution_claim"].get(claim_ref)
                if claim is None:
                    errors.append(
                        f"assignments[{index}].contribution_claim_ref: locally resolved claim '{claim_ref}' was not found"
                    )
                else:
                    if status == "finalized" and claim.get("claim_status") not in {
                        "recognized",
                        "partially_recognized",
                    }:
                        errors.append(
                            f"assignments[{index}]: finalized Weight Resolution may only use recognized claims"
                        )
                    if assignment.get("contributor_ref") != claim.get("contributor_ref"):
                        errors.append(
                            f"assignments[{index}].contributor_ref: does not match Contribution Claim"
                        )
    for value in duplicates(assignment_ids):
        errors.append(f"assignments: duplicate assignment_id '{value}'")
    for value in duplicates(claim_refs):
        errors.append(f"assignments: duplicate Contribution Claim '{value}'")

    normalization = document.get("normalization", {})
    tolerance = dec(normalization.get("tolerance")) if isinstance(normalization, dict) else None
    tolerance = tolerance if tolerance is not None else Decimal("0")
    if status == "finalized":
        if not close(total, Decimal("1"), tolerance):
            errors.append(f"assignments.normalized_weight: finalized weights must sum to 1; got {total}")
        decision = document.get("decision")
        if not isinstance(decision, dict):
            errors.append("decision: required for finalized Weight Resolution")
        else:
            errors.extend(
                missing(decision, ["decided_by_refs", "decided_at", "policy_ref", "rationale"], "decision")
            )
            if method == "external" and not decision.get("external_result_ref"):
                errors.append("decision.external_result_ref: required when method is 'external'")
    if status == "revoked":
        if not document.get("revoked_at"):
            errors.append("revoked_at: required for revoked Weight Resolution")
        if not document.get("revocation_reason"):
            errors.append("revocation_reason: required for revoked Weight Resolution")
    errors.extend(evidence_errors(document))
    return errors


def validate_allocation(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    cell_id = document.get("cell_id")
    status = document.get("plan_status")
    weight_ref = document.get("weight_resolution", {})
    weight_doc: dict[str, Any] | None = None

    if isinstance(weight_ref, dict):
        errors.extend(external_ref(weight_ref, prefix="weight_resolution"))
        if weight_ref.get("resolution_status") == "resolved" and weight_ref.get("source_cell_id") == cell_id:
            resolution_id = weight_ref.get("resolution_id")
            weight_doc = known["royalty_cell_contribution_weight_resolution"].get(resolution_id)
            if weight_doc is None:
                errors.append(
                    f"weight_resolution.resolution_id: locally resolved Weight Resolution '{resolution_id}' was not found"
                )
            elif weight_doc.get("resolution_status") != "finalized":
                errors.append("weight_resolution: Allocation Plan requires a finalized Weight Resolution")

    rounding = document.get("rounding", {})
    tolerance = dec(rounding.get("tolerance")) if isinstance(rounding, dict) else None
    tolerance = tolerance if tolerance is not None else Decimal("0")

    value_event = document.get("source_value_event", {})
    gross = dec(value_event.get("gross_units")) if isinstance(value_event, dict) else None
    gross = gross if gross is not None else Decimal("0")

    deductions = document.get("deductions", [])
    deduction_ids: list[str] = []
    deduction_total = Decimal("0")
    if isinstance(deductions, list):
        for deduction in deductions:
            if not isinstance(deduction, dict):
                continue
            if isinstance(deduction.get("deduction_id"), str):
                deduction_ids.append(deduction["deduction_id"])
            units = dec(deduction.get("units"))
            if units is not None:
                deduction_total += units
    for value in duplicates(deduction_ids):
        errors.append(f"deductions: duplicate deduction_id '{value}'")

    distributable = dec(document.get("distributable_units"))
    if distributable is not None and not close(gross - deduction_total, distributable, tolerance):
        errors.append(
            f"distributable_units: gross units minus deductions equals {gross - deduction_total}, not {distributable}"
        )

    claim_weights: dict[str, Decimal] = {}
    if weight_doc is not None and isinstance(weight_doc.get("assignments"), list):
        for assignment in weight_doc["assignments"]:
            if not isinstance(assignment, dict):
                continue
            claim_ref = assignment.get("contribution_claim_ref")
            weight = dec(assignment.get("normalized_weight"))
            if isinstance(claim_ref, str) and weight is not None:
                claim_weights[claim_ref] = weight

    allocations = document.get("allocations", [])
    line_ids: list[str] = []
    claim_refs_all: list[str] = []
    allocation_total = Decimal("0")
    weight_total = Decimal("0")
    if isinstance(allocations, list):
        for index, line in enumerate(allocations):
            if not isinstance(line, dict):
                continue
            if isinstance(line.get("allocation_line_id"), str):
                line_ids.append(line["allocation_line_id"])
            units = dec(line.get("allocated_units"))
            weight = dec(line.get("applied_weight"))
            if units is not None:
                allocation_total += units
            if weight is not None:
                weight_total += weight
            claim_refs = strings(line.get("contribution_claim_refs"))
            claim_refs_all.extend(claim_refs)
            if weight_doc is not None and weight is not None:
                expected = sum((claim_weights.get(ref, Decimal("0")) for ref in claim_refs), Decimal("0"))
                if not close(expected, weight, tolerance):
                    errors.append(
                        f"allocations[{index}].applied_weight: expected {expected} from referenced claims, got {weight}"
                    )
    for value in duplicates(line_ids):
        errors.append(f"allocations: duplicate allocation_line_id '{value}'")
    for value in duplicates(claim_refs_all):
        errors.append(f"allocations: Contribution Claim '{value}' is assigned more than once")
    if distributable is not None and not close(allocation_total, distributable, tolerance):
        errors.append(
            f"allocations.allocated_units: allocation total {allocation_total} does not equal distributable units {distributable}"
        )
    if not close(weight_total, Decimal("1"), tolerance):
        errors.append(f"allocations.applied_weight: weights must sum to 1; got {weight_total}")
    if weight_doc is not None:
        expected_claims = set(claim_weights)
        actual_claims = set(claim_refs_all)
        for ref in sorted(expected_claims - actual_claims):
            errors.append(f"allocations: Weight Resolution claim '{ref}' was not allocated")
        for ref in sorted(actual_claims - expected_claims):
            errors.append(f"allocations: claim '{ref}' is not present in the Weight Resolution")

    if status in {"approved", "partially_executed", "executed"}:
        approval = document.get("approval")
        if not isinstance(approval, dict):
            errors.append(f"approval: required when plan_status is '{status}'")
        else:
            errors.extend(
                missing(approval, ["approved_by_refs", "approved_at", "policy_ref", "rationale"], "approval")
            )
    if status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append("cancelled_at: required for cancelled Allocation Plan")
        if not document.get("cancellation_reason"):
            errors.append("cancellation_reason: required for cancelled Allocation Plan")
    errors.extend(evidence_errors(document))
    return errors


def validate_receipt(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    cell_id = document.get("cell_id")
    plan_ref = document.get("allocation_plan", {})
    plan_doc: dict[str, Any] | None = None
    if isinstance(plan_ref, dict):
        errors.extend(external_ref(plan_ref, prefix="allocation_plan"))
        if plan_ref.get("resolution_status") == "resolved" and plan_ref.get("source_cell_id") == cell_id:
            plan_id = plan_ref.get("allocation_plan_id")
            plan_doc = known["royalty_cell_allocation_plan"].get(plan_id)
            if plan_doc is None:
                errors.append(
                    f"allocation_plan.allocation_plan_id: locally resolved Allocation Plan '{plan_id}' was not found"
                )

    allocated = dec(document.get("allocated_units"))
    settled = dec(document.get("settled_units"))
    remaining = dec(document.get("balance_remaining_units"))
    if allocated is not None and settled is not None and remaining is not None:
        if settled > allocated:
            errors.append("settled_units: must not exceed allocated_units")
        if allocated - settled != remaining:
            errors.append(f"balance_remaining_units: expected {allocated - settled}, got {remaining}")

    if plan_doc is not None:
        line_id = document.get("allocation_line_id")
        line = next(
            (
                item
                for item in plan_doc.get("allocations", [])
                if isinstance(item, dict) and item.get("allocation_line_id") == line_id
            ),
            None,
        )
        if line is None:
            errors.append("allocation_line_id: line was not found in Allocation Plan")
        else:
            expected_beneficiary = line.get("beneficiary_ref")
            if document.get("beneficiary_ref") != expected_beneficiary:
                errors.append(
                    f"beneficiary_ref: expected '{expected_beneficiary}' from Allocation Plan, got '{document.get('beneficiary_ref')}'"
                )
            expected_type = line.get("settlement_type")
            if document.get("settlement_type") != expected_type:
                errors.append(
                    f"settlement_type: expected '{expected_type}' from Allocation Plan, got '{document.get('settlement_type')}'"
                )
            line_units = dec(line.get("allocated_units"))
            if allocated is not None and line_units is not None and allocated != line_units:
                errors.append("allocated_units: does not match Allocation Plan line")
            event = plan_doc.get("source_value_event", {})
            if isinstance(event, dict) and document.get("unit") != event.get("unit"):
                errors.append("unit: does not match Allocation Plan unit")

    status = document.get("settlement_status")
    settlement_evidence = document.get("settlement_evidence")
    if status == "settled":
        if not document.get("settled_at"):
            errors.append("settled_at: required for settled Royalty Receipt")
        if not isinstance(settlement_evidence, list) or not settlement_evidence:
            errors.append("settlement_evidence: required for settled receipt")
        if remaining is not None and remaining != Decimal("0"):
            errors.append("balance_remaining_units: settled receipt must have zero balance")
    if status == "partially_settled":
        if allocated is not None and settled is not None and not (Decimal("0") < settled < allocated):
            errors.append("settled_units: partial settlement requires 0 < settled_units < allocated_units")
        if not isinstance(settlement_evidence, list) or not settlement_evidence:
            errors.append("settlement_evidence: required for partial settlement")
    if status == "pending" and settled is not None and settled != Decimal("0"):
        errors.append("settled_units: pending receipt must have zero settled units")
    if status == "failed" and not document.get("status_reason"):
        errors.append("status_reason: required for failed receipt")
    if status == "held" and not document.get("hold_ref"):
        errors.append("hold_ref: required for held receipt")
    if status == "waived" and not document.get("waiver_ref"):
        errors.append("waiver_ref: required for waived receipt")
    if status == "reversed" and not document.get("reversal_ref"):
        errors.append("reversal_ref: required for reversed receipt")
    errors.extend(evidence_errors(document, "settlement_evidence"))
    return errors


# ---------------------------------------------------------------------------
# v0.5 — Interoperability, Dispute, Holdback
# ---------------------------------------------------------------------------


def validate_interop(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    local_cell = document.get("local_cell_id")
    remote = document.get("remote_cell", {})
    remote_cell = remote.get("cell_id") if isinstance(remote, dict) else None
    if local_cell == remote_cell:
        errors.append("remote_cell.cell_id: must differ from local_cell_id")

    status = document.get("link_status")
    if status == "active" and not document.get("activated_at"):
        errors.append("activated_at: required for active Link")
    if status == "suspended":
        if not document.get("suspended_at"):
            errors.append("suspended_at: required for suspended Link")
        if not document.get("status_reason"):
            errors.append("status_reason: required for suspended Link")
    if status == "retired":
        if not document.get("retired_at"):
            errors.append("retired_at: required for retired Link")
        if not document.get("status_reason"):
            errors.append("status_reason: required for retired Link")

    mappings = document.get("identifier_mappings", [])
    mapping_ids: list[str] = []
    pairs: list[str] = []
    if isinstance(mappings, list):
        for index, mapping in enumerate(mappings):
            if not isinstance(mapping, dict):
                continue
            if isinstance(mapping.get("mapping_id"), str):
                mapping_ids.append(mapping["mapping_id"])
            pairs.append(
                f"{mapping.get('local_record_type')}|{mapping.get('local_id')}|{mapping.get('remote_record_type')}|{mapping.get('remote_id')}"
            )
            if mapping.get("local_resolution_status") == "resolved":
                local_type = mapping.get("local_record_type")
                local_id = mapping.get("local_id")
                if local_type in REF_TYPES and resolve(local_type, local_id, known) is None:
                    errors.append(
                        f"identifier_mappings[{index}].local_id: local record '{local_id}' was not found"
                    )
            if mapping.get("remote_resolution_status") == "externally_resolved" and not mapping.get(
                "remote_record_ref"
            ):
                errors.append(
                    f"identifier_mappings[{index}].remote_record_ref: required when remote_resolution_status is 'externally_resolved'"
                )
    for value in duplicates(mapping_ids):
        errors.append(f"identifier_mappings: duplicate mapping_id '{value}'")
    for value in duplicates(pairs):
        errors.append(f"identifier_mappings: duplicate local/remote mapping pair '{value}'")

    compatibility = document.get("policy_compatibility", {})
    if isinstance(compatibility, dict):
        comp_status = compatibility.get("status")
        if comp_status == "adapter_required" and not strings(compatibility.get("adapter_refs")):
            errors.append("policy_compatibility.adapter_refs: required when status is 'adapter_required'")
        if comp_status == "conflict":
            if not strings(compatibility.get("conflict_refs")):
                errors.append("policy_compatibility.conflict_refs: required when status is 'conflict'")
            if status == "active" and not document.get("activation_override_ref"):
                errors.append("activation_override_ref: required for active Link with policy conflict")
    errors.extend(evidence_errors(document))
    return errors


def validate_dispute(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    dispute_id = document.get("dispute_id")
    cell_id = document.get("cell_id")

    filers = set(strings(document.get("filed_by_refs")))
    respondents = set(strings(document.get("respondent_refs")))
    for party in sorted(filers & respondents):
        errors.append(f"respondent_refs: party '{party}' also appears in filed_by_refs")

    contested = document.get("contested_refs", [])
    keys: list[str] = []
    if isinstance(contested, list):
        for index, item in enumerate(contested):
            if not isinstance(item, dict):
                continue
            record_type = item.get("record_type")
            record_id = item.get("record_id")
            keys.append(f"{record_type}|{record_id}")
            if record_id == dispute_id:
                errors.append(f"contested_refs[{index}].record_id: Dispute cannot contest itself")
            errors.extend(external_ref(item, prefix=f"contested_refs[{index}]"))
            if (
                item.get("resolution_status") == "resolved"
                and item.get("source_cell_id") == cell_id
                and record_type in REF_TYPES
                and resolve(record_type, record_id, known) is None
            ):
                errors.append(f"contested_refs[{index}].record_id: local record '{record_id}' was not found")
    for value in duplicates(keys):
        errors.append(f"contested_refs: duplicate contested record '{value}'")

    status = document.get("dispute_status")
    decision = document.get("decision")
    if status in {"decided", "dismissed"} and not isinstance(decision, dict):
        errors.append(f"decision: required when dispute_status is '{status}'")
    if isinstance(decision, dict):
        errors.extend(
            missing(
                decision,
                ["outcome", "decided_by_refs", "decided_at", "policy_refs", "rationale"],
                "decision",
            )
        )
        if "remedy_actions" not in decision:
            errors.append("decision.remedy_actions: required")
        actions = decision.get("remedy_actions", [])
        action_ids: list[str] = []
        if isinstance(actions, list):
            for action in actions:
                if not isinstance(action, dict):
                    continue
                if isinstance(action.get("action_id"), str):
                    action_ids.append(action["action_id"])
                if action.get("action_status") == "completed" and not action.get("execution_ref"):
                    errors.append(
                        "decision.remedy_actions.execution_ref: required for completed remedy action"
                    )
        for value in duplicates(action_ids):
            errors.append(f"decision.remedy_actions: duplicate action_id '{value}'")

    if status == "withdrawn":
        if not document.get("withdrawn_at"):
            errors.append("withdrawn_at: required for withdrawn dispute")
        if not document.get("status_reason"):
            errors.append("status_reason: required for withdrawn dispute")
    if status == "escalated":
        if not document.get("escalated_at"):
            errors.append("escalated_at: required for escalated dispute")
        if not document.get("escalation_ref"):
            errors.append("escalation_ref: required for escalated dispute")
        if not document.get("status_reason"):
            errors.append("status_reason: required for escalated dispute")
    errors.extend(evidence_errors(document))
    return errors


def validate_holdback(document: dict[str, Any], known: Known) -> list[str]:
    errors: list[str] = []
    cell_id = document.get("cell_id")

    dispute_ref = document.get("dispute", {})
    dispute_doc: dict[str, Any] | None = None
    if isinstance(dispute_ref, dict):
        errors.extend(external_ref(dispute_ref, prefix="dispute"))
        if dispute_ref.get("resolution_status") == "resolved" and dispute_ref.get("source_cell_id") == cell_id:
            dispute_id = dispute_ref.get("dispute_id")
            dispute_doc = known["royalty_cell_dispute_record"].get(dispute_id)
            if dispute_doc is None:
                errors.append(f"dispute.dispute_id: locally resolved Dispute '{dispute_id}' was not found")

    plan_ref = document.get("allocation_plan", {})
    plan_doc: dict[str, Any] | None = None
    if isinstance(plan_ref, dict):
        errors.extend(external_ref(plan_ref, prefix="allocation_plan"))
        if plan_ref.get("resolution_status") == "resolved" and plan_ref.get("source_cell_id") == cell_id:
            plan_id = plan_ref.get("allocation_plan_id")
            plan_doc = known["royalty_cell_allocation_plan"].get(plan_id)
            if plan_doc is None:
                errors.append(
                    f"allocation_plan.allocation_plan_id: locally resolved Allocation Plan '{plan_id}' was not found"
                )

    held = dec(document.get("held_units"))
    released = dec(document.get("released_units"))
    remaining = dec(document.get("remaining_held_units"))
    if held is not None and released is not None and remaining is not None:
        if released > held:
            errors.append("released_units: must not exceed held_units")
        if held - released != remaining:
            errors.append(f"remaining_held_units: expected {held - released}, got {remaining}")

    release_events = document.get("release_events", [])
    release_ids: list[str] = []
    release_total = Decimal("0")
    if isinstance(release_events, list):
        for event in release_events:
            if not isinstance(event, dict):
                continue
            if isinstance(event.get("release_id"), str):
                release_ids.append(event["release_id"])
            units = dec(event.get("released_units"))
            if units is not None:
                release_total += units
    for value in duplicates(release_ids):
        errors.append(f"release_events: duplicate release_id '{value}'")
    if released is not None and release_total != released:
        errors.append(
            f"release_events.released_units: total {release_total} does not equal released_units {released}"
        )

    if plan_doc is not None:
        line_id = document.get("allocation_line_id")
        line = next(
            (
                item
                for item in plan_doc.get("allocations", [])
                if isinstance(item, dict) and item.get("allocation_line_id") == line_id
            ),
            None,
        )
        if line is None:
            errors.append("allocation_line_id: line was not found in Allocation Plan")
        else:
            expected_beneficiary = line.get("beneficiary_ref")
            if document.get("beneficiary_ref") != expected_beneficiary:
                errors.append(
                    f"beneficiary_ref: expected '{expected_beneficiary}' from Allocation Plan, got '{document.get('beneficiary_ref')}'"
                )
            line_units = dec(line.get("allocated_units"))
            if held is not None and line_units is not None and held > line_units:
                errors.append("held_units: exceeds Allocation Plan line units")
            event = plan_doc.get("source_value_event", {})
            if isinstance(event, dict) and document.get("unit") != event.get("unit"):
                errors.append("unit: does not match Allocation Plan unit")

    status = document.get("holdback_status")
    if status in {"active", "partially_released", "released"}:
        if not document.get("imposed_at"):
            errors.append(f"imposed_at: required for {status} Holdback")
        if not strings(document.get("imposed_by_refs")):
            errors.append(f"imposed_by_refs: required for {status} Holdback")
    if status == "active":
        if released is not None and released != Decimal("0"):
            errors.append("released_units: active Holdback must have zero released units")
        if held is not None and remaining is not None and held != remaining:
            errors.append("remaining_held_units: active Holdback must equal held_units")
    if status == "partially_released":
        if held is not None and released is not None and not (Decimal("0") < released < held):
            errors.append(
                "released_units: partially released Holdback requires 0 < released_units < held_units"
            )
        if not isinstance(release_events, list) or not release_events:
            errors.append("release_events: required for partially released Holdback")
    if status == "released":
        if held is not None and released is not None and released != held:
            errors.append("released_units: released Holdback must equal held_units")
        if remaining is not None and remaining != Decimal("0"):
            errors.append("remaining_held_units: released Holdback must be zero")
        if not document.get("released_at"):
            errors.append("released_at: required for released Holdback")
        if not isinstance(release_events, list) or not release_events:
            errors.append("release_events: required for released Holdback")
        if dispute_doc is not None and dispute_doc.get("dispute_status") not in {
            "decided",
            "dismissed",
            "withdrawn",
        }:
            errors.append("dispute: released Holdback requires a resolved dispute state")
    if status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append("cancelled_at: required for cancelled Holdback")
        if not document.get("cancellation_reason"):
            errors.append("cancellation_reason: required for cancelled Holdback")
        if remaining is not None and remaining != Decimal("0"):
            errors.append("remaining_held_units: cancelled Holdback must be zero")
    errors.extend(evidence_errors(document))
    return errors


SEMANTIC: dict[str, SemanticFn] = {
    "royalty_cell_manifest": validate_manifest,
    "royalty_cell_origin_record": validate_origin,
    "royalty_cell_usage_record": validate_usage,
    "royalty_cell_derivative_record": validate_derivative,
    "royalty_cell_contribution_claim": validate_contribution,
    "royalty_cell_contribution_weight_resolution": validate_weight,
    "royalty_cell_allocation_plan": validate_allocation,
    "royalty_cell_royalty_receipt": validate_receipt,
    "royalty_cell_interoperability_link": validate_interop,
    "royalty_cell_dispute_record": validate_dispute,
    "royalty_cell_holdback_record": validate_holdback,
}


def semantic_errors(document: dict[str, Any], known: Known) -> list[str]:
    record_type = document.get("record_type")
    validator = SEMANTIC.get(record_type) if isinstance(record_type, str) else None
    if validator is None:
        return [f"record_type: no semantic validator for '{record_type}'"]
    return validator(document, known)


def validate(path: Path, validators: Validators, known: Known) -> list[str]:
    try:
        document = load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"<load>: {error}"]
    errors = schema_errors(document, validators)
    if errors:
        return [f"[schema] {error}" for error in errors]
    return [f"[semantic] {error}" for error in semantic_errors(document, known)]


def print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"  - {error}")


def main() -> int:
    print("=== Royalty Cell Protocol Validation ===")
    print()

    try:
        validators = load_validators()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"[fatal] unable to load schemas: {error}")
        return 1
    except Exception as error:
        print(f"[fatal] invalid JSON Schema: {error}")
        return 1

    for record_type, path in SCHEMAS.items():
        print(f"schema [{record_type}]: {path.relative_to(ROOT)}")
    print()

    pass_files = yaml_files(PASS_DIR)
    fail_files = yaml_files(FAIL_DIR)
    if not pass_files:
        print("[fatal] no pass examples found")
        return 1
    if not fail_files:
        print("[fatal] no fail examples found")
        return 1

    known = collect_known(pass_files, validators)
    failed = False

    print("[validate-pass]")
    for path in pass_files:
        print(f"  {path.relative_to(ROOT)}")
        errors = validate(path, validators, known)
        if errors:
            failed = True
            print("  [failed]")
            print_errors(errors)
        else:
            print("  [schema-ok]")
            print("  [semantic-ok]")
        print()

    print("[validate-expected-fail]")
    for path in fail_files:
        print(f"  {path.relative_to(ROOT)}")
        errors = validate(path, validators, known)
        if errors:
            print("  [expected-failure]")
            print_errors(errors)
        else:
            failed = True
            print("  [unexpected-pass]")
            print("  - invalid example passed all validation stages")
        print()

    if failed:
        print("Validation failed.")
        return 1

    print("Known local records:")
    for record_type in sorted(known):
        print(f"  [{record_type}]")
        for record_id in sorted(known[record_type]):
            print(f"    - {record_id}")
    print()
    print("All Royalty Cell Protocol examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
