#!/usr/bin/env python3
"""
Validate Royalty Cell Protocol examples.

Supported records:

- v0.1 Royalty Cell Manifest
- v0.2 Royalty Cell Origin Record
- v0.2 Royalty Cell Usage Record
- v0.3 Royalty Cell Derivative Record
- v0.3 Royalty Cell Contribution Claim
- v0.4 Contribution Weight Resolution
- v0.4 Allocation Plan
- v0.4 Royalty Receipt
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT_DIR = Path(__file__).resolve().parents[1]

SCHEMA_PATHS = {
    "royalty_cell_manifest": (
        ROOT_DIR / "schemas" / "royalty-cell-manifest.schema.json"
    ),
    "royalty_cell_origin_record": (
        ROOT_DIR / "schemas" / "royalty-cell-origin-record.schema.json"
    ),
    "royalty_cell_usage_record": (
        ROOT_DIR / "schemas" / "royalty-cell-usage-record.schema.json"
    ),
    "royalty_cell_derivative_record": (
        ROOT_DIR / "schemas" / "royalty-cell-derivative-record.schema.json"
    ),
    "royalty_cell_contribution_claim": (
        ROOT_DIR / "schemas" / "royalty-cell-contribution-claim.schema.json"
    ),
    "royalty_cell_contribution_weight_resolution": (
        ROOT_DIR
        / "schemas"
        / "royalty-cell-contribution-weight-resolution.schema.json"
    ),
    "royalty_cell_allocation_plan": (
        ROOT_DIR / "schemas" / "royalty-cell-allocation-plan.schema.json"
    ),
    "royalty_cell_royalty_receipt": (
        ROOT_DIR / "schemas" / "royalty-cell-royalty-receipt.schema.json"
    ),
}

ID_FIELDS = {
    "royalty_cell_origin_record": "origin_id",
    "royalty_cell_usage_record": "usage_id",
    "royalty_cell_derivative_record": "derivative_id",
    "royalty_cell_contribution_claim": "claim_id",
    "royalty_cell_contribution_weight_resolution": "resolution_id",
    "royalty_cell_allocation_plan": "allocation_plan_id",
    "royalty_cell_royalty_receipt": "receipt_id",
}

TARGET_TYPE_TO_RECORD_TYPE = {
    "origin_record": "royalty_cell_origin_record",
    "usage_record": "royalty_cell_usage_record",
    "derivative_record": "royalty_cell_derivative_record",
}

PASS_DIR = ROOT_DIR / "examples" / "pass"
FAIL_DIR = ROOT_DIR / "examples" / "fail"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be an object")

    return data


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be a mapping")

    return data


def collect_yaml_files(directory: Path) -> list[Path]:
    files = list(directory.glob("*.yaml"))
    files.extend(directory.glob("*.yml"))
    return sorted(set(files))


def format_error_path(parts: list[Any]) -> str:
    if not parts:
        return "<root>"

    result = ""

    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            if result:
                result += "."
            result += str(part)

    return result


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None

    normalized = value

    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def to_decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool):
        return None

    if not isinstance(value, (int, float, str, Decimal)):
        return None

    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def decimal_equal(
    left: Decimal,
    right: Decimal,
    tolerance: Decimal,
) -> bool:
    return abs(left - right) <= tolerance


def duplicate_values(values: list[str]) -> list[str]:
    return sorted(
        {
            value
            for value in values
            if values.count(value) > 1
        }
    )


def load_validators() -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}

    for record_type, schema_path in SCHEMA_PATHS.items():
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)

        validators[record_type] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    return validators


def schema_errors(
    document: dict[str, Any],
    validators: dict[str, Draft202012Validator],
) -> list[str]:
    record_type = document.get("record_type")

    if not isinstance(record_type, str):
        return ["record_type: missing or not a string"]

    validator = validators.get(record_type)

    if validator is None:
        return [f"record_type: unsupported record type '{record_type}'"]

    errors: list[str] = []

    for error in sorted(
        validator.iter_errors(document),
        key=lambda item: list(item.absolute_path),
    ):
        path = format_error_path(list(error.absolute_path))
        errors.append(f"{path}: {error.message}")

    return errors


def collect_known_records(
    pass_files: list[Path],
    validators: dict[str, Draft202012Validator],
) -> dict[str, dict[str, dict[str, Any]]]:
    known: dict[str, dict[str, dict[str, Any]]] = {
        record_type: {}
        for record_type in ID_FIELDS
    }

    for path in pass_files:
        try:
            document = load_yaml(path)
        except (OSError, ValueError, yaml.YAMLError):
            continue

        record_type = document.get("record_type")

        if record_type not in ID_FIELDS:
            continue

        if schema_errors(document, validators):
            continue

        id_field = ID_FIELDS[record_type]
        record_id = document.get(id_field)

        if isinstance(record_id, str):
            known[record_type][record_id] = document

    return known


def evidence_semantic_errors(
    document: dict[str, Any],
    field_name: str = "evidence",
) -> list[str]:
    errors: list[str] = []
    evidence = document.get(field_name, [])

    if not isinstance(evidence, list):
        return errors

    evidence_ids: list[str] = []

    for item in evidence:
        if not isinstance(item, dict):
            continue

        evidence_id = item.get("evidence_id")

        if isinstance(evidence_id, str):
            evidence_ids.append(evidence_id)

    for evidence_id in duplicate_values(evidence_ids):
        errors.append(
            f"{field_name}: duplicate evidence_id '{evidence_id}'"
        )

    return errors


def manifest_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    created_at = parse_datetime(document.get("created_at"))
    updated_at = parse_datetime(document.get("updated_at"))

    if created_at and updated_at and updated_at < created_at:
        errors.append(
            "updated_at: must be equal to or later than created_at"
        )

    governance = document.get("governance", {})

    if isinstance(governance, dict):
        mode = governance.get("mode")
        decision_policy = governance.get("decision_policy", {})

        if isinstance(decision_policy, dict):
            approval_rule = decision_policy.get("approval_rule")
            policy_ref = decision_policy.get("policy_ref")

            if approval_rule == "external" and not policy_ref:
                errors.append(
                    "governance.decision_policy.policy_ref: required "
                    "when approval_rule is 'external'"
                )

            if mode == "external_policy" and not policy_ref:
                errors.append(
                    "governance.decision_policy.policy_ref: required "
                    "when governance mode is 'external_policy'"
                )

    membership = document.get("membership", {})

    if isinstance(membership, dict):
        admission_mode = membership.get("admission_mode")

        if admission_mode in {"request", "invite_only"}:
            if not membership.get("admission_policy_ref"):
                errors.append(
                    "membership.admission_policy_ref: required for "
                    "request or invite_only admission"
                )

        roles = membership.get("roles", [])

        if isinstance(roles, list):
            role_ids: list[str] = []
            has_admin = False

            for role in roles:
                if not isinstance(role, dict):
                    continue

                role_id = role.get("role_id")

                if isinstance(role_id, str):
                    role_ids.append(role_id)

                permissions = role.get("permissions", [])

                if (
                    isinstance(permissions, list)
                    and "administer_cell" in permissions
                ):
                    has_admin = True

            for role_id in duplicate_values(role_ids):
                errors.append(
                    f"membership.roles: duplicate role_id '{role_id}'"
                )

            if not has_admin:
                errors.append(
                    "membership.roles: at least one role must include "
                    "the 'administer_cell' permission"
                )

    allocation_policy = document.get("allocation_policy", {})

    if isinstance(allocation_policy, dict):
        status = allocation_policy.get("status")
        policy_ref = allocation_policy.get("policy_ref")

        if status in {"internal", "external"} and not policy_ref:
            errors.append(
                "allocation_policy.policy_ref: required when status "
                "is 'internal' or 'external'"
            )

        if status == "not_configured" and policy_ref:
            errors.append(
                "allocation_policy.policy_ref: must be omitted when "
                "status is 'not_configured'"
            )

    return errors


def origin_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    origin_created_at = parse_datetime(
        document.get("origin_created_at")
    )
    declared_at = parse_datetime(document.get("declared_at"))

    if (
        origin_created_at
        and declared_at
        and origin_created_at > declared_at
    ):
        errors.append(
            "origin_created_at: must not be later than declared_at"
        )

    claim_basis = document.get("claim_basis")
    claim_status = document.get("claim_status")

    if claim_basis == "imported_record":
        if not document.get("imported_from_ref"):
            errors.append(
                "imported_from_ref: required for imported_record"
            )

    if claim_status == "contested":
        if not document.get("contest_refs"):
            errors.append(
                "contest_refs: required when claim_status is contested"
            )

    if claim_status == "withdrawn":
        if not document.get("status_reason"):
            errors.append(
                "status_reason: required when claim_status is withdrawn"
            )

    if claim_status == "superseded":
        if not document.get("superseded_by_ref"):
            errors.append(
                "superseded_by_ref: required when claim_status is "
                "superseded"
            )

    errors.extend(evidence_semantic_errors(document))
    return errors


def usage_semantic_errors(
    document: dict[str, Any],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []
    usage_status = document.get("usage_status")

    if usage_status == "completed" and not document.get("occurred_at"):
        errors.append(
            "occurred_at: required when usage_status is completed"
        )

    authorization = document.get("authorization", {})

    if isinstance(authorization, dict):
        authorization_status = authorization.get("status")

        if (
            authorization_status == "granted"
            and not authorization.get("authorization_ref")
        ):
            errors.append(
                "authorization.authorization_ref: required when "
                "authorization is granted"
            )

        if (
            authorization_status == "not_required"
            and not authorization.get("policy_ref")
        ):
            errors.append(
                "authorization.policy_ref: required when authorization "
                "is not_required"
            )

        if (
            authorization_status == "denied"
            and usage_status == "completed"
        ):
            errors.append(
                "usage_status: completed Usage cannot have denied "
                "authorization"
            )

    origin_links = document.get("origin_links", [])
    linked_ids: list[str] = []
    cell_id = document.get("cell_id")

    if isinstance(origin_links, list):
        for index, link in enumerate(origin_links):
            if not isinstance(link, dict):
                continue

            origin_id = link.get("origin_id")
            source_cell_id = link.get("source_cell_id")
            resolution_status = link.get("resolution_status")

            if isinstance(origin_id, str):
                linked_ids.append(origin_id)

            if (
                resolution_status == "externally_resolved"
                and not link.get("record_ref")
            ):
                errors.append(
                    f"origin_links[{index}].record_ref: required for "
                    "externally_resolved Origin"
                )

            if (
                resolution_status == "resolved"
                and source_cell_id == cell_id
                and origin_id
                not in known["royalty_cell_origin_record"]
            ):
                errors.append(
                    f"origin_links[{index}].origin_id: locally "
                    f"resolved Origin '{origin_id}' was not found"
                )

    for origin_id in duplicate_values(linked_ids):
        errors.append(
            f"origin_links: duplicate origin_id '{origin_id}'"
        )

    errors.extend(evidence_semantic_errors(document))
    return errors


def derivative_semantic_errors(
    document: dict[str, Any],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []

    derivative_id = document.get("derivative_id")
    cell_id = document.get("cell_id")
    status = document.get("derivative_status")
    derivative_type = document.get("derivative_type")

    created_at = parse_datetime(document.get("created_at"))
    declared_at = parse_datetime(document.get("declared_at"))

    if created_at and declared_at and created_at > declared_at:
        errors.append(
            "created_at: must not be later than declared_at"
        )

    if status == "contested" and not document.get("contest_refs"):
        errors.append(
            "contest_refs: required for contested Derivative"
        )

    if status == "withdrawn" and not document.get("status_reason"):
        errors.append(
            "status_reason: required for withdrawn Derivative"
        )

    if status == "superseded" and not document.get(
        "superseded_by_ref"
    ):
        errors.append(
            "superseded_by_ref: required for superseded Derivative"
        )

    parent_links = document.get("parent_links", [])
    source_ids: list[str] = []
    primary_count = 0

    if isinstance(parent_links, list):
        for index, parent in enumerate(parent_links):
            if not isinstance(parent, dict):
                continue

            source_id = parent.get("source_id")
            source_type = parent.get("source_record_type")
            source_cell_id = parent.get("source_cell_id")
            resolution_status = parent.get("resolution_status")

            if isinstance(source_id, str):
                source_ids.append(source_id)

            if parent.get("dependency_level") == "primary":
                primary_count += 1

            if source_id == derivative_id:
                errors.append(
                    f"parent_links[{index}].source_id: Derivative "
                    "cannot reference itself"
                )

            if (
                resolution_status == "externally_resolved"
                and not parent.get("record_ref")
            ):
                errors.append(
                    f"parent_links[{index}].record_ref: required for "
                    "externally_resolved parent"
                )

            if (
                resolution_status == "resolved"
                and source_cell_id == cell_id
            ):
                local_type = TARGET_TYPE_TO_RECORD_TYPE.get(
                    source_type
                )

                if (
                    local_type
                    and source_id not in known[local_type]
                ):
                    errors.append(
                        f"parent_links[{index}].source_id: locally "
                        f"resolved parent '{source_id}' was not found"
                    )

        for source_id in duplicate_values(source_ids):
            errors.append(
                f"parent_links: duplicate source_id '{source_id}'"
            )

        if primary_count == 0:
            errors.append(
                "parent_links: at least one primary parent is required"
            )

        if (
            derivative_type == "combination"
            and len(set(source_ids)) < 2
        ):
            errors.append(
                "parent_links: combination requires two distinct parents"
            )

    errors.extend(evidence_semantic_errors(document))
    return errors


def contribution_semantic_errors(
    document: dict[str, Any],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []

    claim_status = document.get("claim_status")
    cell_id = document.get("cell_id")
    target = document.get("target", {})

    if isinstance(target, dict):
        target_id = target.get("target_id")
        target_type = target.get("target_record_type")
        source_cell_id = target.get("source_cell_id")
        resolution_status = target.get("resolution_status")

        if (
            resolution_status == "externally_resolved"
            and not target.get("record_ref")
        ):
            errors.append(
                "target.record_ref: required for externally_resolved target"
            )

        if (
            resolution_status == "resolved"
            and source_cell_id == cell_id
        ):
            local_type = TARGET_TYPE_TO_RECORD_TYPE.get(
                target_type
            )

            if local_type and target_id not in known[local_type]:
                errors.append(
                    f"target.target_id: locally resolved target "
                    f"'{target_id}' was not found"
                )

    expected_recognition = {
        "recognized": "recognized",
        "partially_recognized": "partially_recognized",
        "rejected": "rejected",
    }

    recognition = document.get("recognition")
    expected_status = expected_recognition.get(claim_status)

    if expected_status is not None:
        if not isinstance(recognition, dict):
            errors.append(
                f"recognition: required when claim_status is "
                f"'{claim_status}'"
            )
        elif recognition.get("status") != expected_status:
            errors.append(
                f"recognition.status: expected '{expected_status}'"
            )

    if isinstance(recognition, dict):
        recognition_status = recognition.get("status")

        if recognition_status in {
            "recognized",
            "partially_recognized",
            "rejected",
        }:
            required = [
                "recognized_by_refs",
                "decided_at",
                "rationale",
                "policy_ref",
            ]

            for field in required:
                if not recognition.get(field):
                    errors.append(
                        f"recognition.{field}: required for completed "
                        "recognition decision"
                    )

        if recognition_status in {
            "recognized",
            "partially_recognized",
        }:
            if not recognition.get("recognized_significance"):
                errors.append(
                    "recognition.recognized_significance: required"
                )

    if claim_status == "disputed" and not document.get(
        "dispute_refs"
    ):
        errors.append(
            "dispute_refs: required for disputed Contribution Claim"
        )

    if claim_status == "withdrawn" and not document.get(
        "status_reason"
    ):
        errors.append(
            "status_reason: required for withdrawn Contribution Claim"
        )

    if claim_status == "superseded" and not document.get(
        "superseded_by_ref"
    ):
        errors.append(
            "superseded_by_ref: required for superseded claim"
        )

    errors.extend(evidence_semantic_errors(document))
    return errors


def weight_resolution_semantic_errors(
    document: dict[str, Any],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []

    cell_id = document.get("cell_id")
    status = document.get("resolution_status")
    method = document.get("method")
    target = document.get("target", {})

    if isinstance(target, dict):
        if (
            target.get("resolution_status") == "externally_resolved"
            and not target.get("record_ref")
        ):
            errors.append(
                "target.record_ref: required for externally_resolved target"
            )

        if (
            target.get("resolution_status") == "resolved"
            and target.get("source_cell_id") == cell_id
            and target.get("target_record_type") == "derivative_record"
            and target.get("target_id")
            not in known["royalty_cell_derivative_record"]
        ):
            errors.append(
                "target.target_id: locally resolved Derivative was not found"
            )

    assignments = document.get("assignments", [])
    assignment_ids: list[str] = []
    claim_refs: list[str] = []
    weight_total = Decimal("0")

    if isinstance(assignments, list):
        for index, assignment in enumerate(assignments):
            if not isinstance(assignment, dict):
                continue

            assignment_id = assignment.get("assignment_id")
            claim_ref = assignment.get("contribution_claim_ref")
            resolution_status = assignment.get("resolution_status")
            source_cell_id = assignment.get("source_cell_id")
            weight = to_decimal(
                assignment.get("normalized_weight")
            )

            if isinstance(assignment_id, str):
                assignment_ids.append(assignment_id)

            if isinstance(claim_ref, str):
                claim_refs.append(claim_ref)

            if weight is not None:
                weight_total += weight

            if (
                resolution_status == "externally_resolved"
                and not assignment.get("record_ref")
            ):
                errors.append(
                    f"assignments[{index}].record_ref: required for "
                    "externally_resolved claim"
                )

            if (
                resolution_status == "resolved"
                and source_cell_id == cell_id
            ):
                claim_document = known[
                    "royalty_cell_contribution_claim"
                ].get(claim_ref)

                if claim_document is None:
                    errors.append(
                        f"assignments[{index}].contribution_claim_ref: "
                        f"locally resolved claim '{claim_ref}' was not found"
                    )
                elif status == "finalized":
                    if claim_document.get("claim_status") not in {
                        "recognized",
                        "partially_recognized",
                    }:
                        errors.append(
                            f"assignments[{index}]: finalized Weight "
                            "Resolution may only use recognized claims"
                        )

                    expected_contributor = claim_document.get(
                        "contributor_ref"
                    )

                    if (
                        expected_contributor
                        and assignment.get("contributor_ref")
                        != expected_contributor
                    ):
                        errors.append(
                            f"assignments[{index}].contributor_ref: "
                            "does not match Contribution Claim"
                        )

    for assignment_id in duplicate_values(assignment_ids):
        errors.append(
            f"assignments: duplicate assignment_id '{assignment_id}'"
        )

    for claim_ref in duplicate_values(claim_refs):
        errors.append(
            f"assignments: duplicate Contribution Claim '{claim_ref}'"
        )

    normalization = document.get("normalization", {})
    tolerance = Decimal("0")

    if isinstance(normalization, dict):
        parsed_tolerance = to_decimal(
            normalization.get("tolerance")
        )

        if parsed_tolerance is not None:
            tolerance = parsed_tolerance

    if status == "finalized":
        if not decimal_equal(
            weight_total,
            Decimal("1"),
            tolerance,
        ):
            errors.append(
                "assignments.normalized_weight: finalized weights "
                f"must sum to 1; got {weight_total}"
            )

        decision = document.get("decision")

        if not isinstance(decision, dict):
            errors.append(
                "decision: required for finalized Weight Resolution"
            )
        elif (
            method == "external"
            and not decision.get("external_result_ref")
        ):
            errors.append(
                "decision.external_result_ref: required for external method"
            )

    if status == "revoked":
        if not document.get("revoked_at"):
            errors.append(
                "revoked_at: required for revoked Weight Resolution"
            )

        if not document.get("revocation_reason"):
            errors.append(
                "revocation_reason: required for revoked Weight Resolution"
            )

    errors.extend(evidence_semantic_errors(document))
    return errors


def allocation_plan_semantic_errors(
    document: dict[str, Any],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []

    cell_id = document.get("cell_id")
    plan_status = document.get("plan_status")
    weight_ref = document.get("weight_resolution", {})

    weight_document: dict[str, Any] | None = None

    if isinstance(weight_ref, dict):
        resolution_id = weight_ref.get("resolution_id")

        if (
            weight_ref.get("resolution_status")
            == "externally_resolved"
            and not weight_ref.get("record_ref")
        ):
            errors.append(
                "weight_resolution.record_ref: required for "
                "externally_resolved Weight Resolution"
            )

        if (
            weight_ref.get("resolution_status") == "resolved"
            and weight_ref.get("source_cell_id") == cell_id
        ):
            weight_document = known[
                "royalty_cell_contribution_weight_resolution"
            ].get(resolution_id)

            if weight_document is None:
                errors.append(
                    "weight_resolution.resolution_id: locally resolved "
                    "Weight Resolution was not found"
                )
            elif (
                weight_document.get("resolution_status")
                != "finalized"
            ):
                errors.append(
                    "weight_resolution: Allocation Plan requires a "
                    "finalized Weight Resolution"
                )

    rounding = document.get("rounding", {})
    tolerance = Decimal("0")

    if isinstance(rounding, dict):
        parsed_tolerance = to_decimal(rounding.get("tolerance"))

        if parsed_tolerance is not None:
            tolerance = parsed_tolerance

    value_event = document.get("source_value_event", {})
    gross_units = Decimal("0")

    if isinstance(value_event, dict):
        parsed_gross = to_decimal(value_event.get("gross_units"))

        if parsed_gross is not None:
            gross_units = parsed_gross

    deduction_total = Decimal("0")
    deduction_ids: list[str] = []

    deductions = document.get("deductions", [])

    if isinstance(deductions, list):
        for deduction in deductions:
            if not isinstance(deduction, dict):
                continue

            deduction_id = deduction.get("deduction_id")

            if isinstance(deduction_id, str):
                deduction_ids.append(deduction_id)

            units = to_decimal(deduction.get("units"))

            if units is not None:
                deduction_total += units

    for deduction_id in duplicate_values(deduction_ids):
        errors.append(
            f"deductions: duplicate deduction_id '{deduction_id}'"
        )

    distributable = to_decimal(
        document.get("distributable_units")
    )

    if distributable is not None:
        expected_distributable = gross_units - deduction_total

        if not decimal_equal(
            expected_distributable,
            distributable,
            tolerance,
        ):
            errors.append(
                "distributable_units: gross units minus deductions "
                f"equals {expected_distributable}, not {distributable}"
            )

    allocations = document.get("allocations", [])
    line_ids: list[str] = []
    allocation_total = Decimal("0")
    applied_weight_total = Decimal("0")
    allocated_claim_refs: list[str] = []

    if isinstance(allocations, list):
        for index, line in enumerate(allocations):
            if not isinstance(line, dict):
                continue

            line_id = line.get("allocation_line_id")

            if isinstance(line_id, str):
                line_ids.append(line_id)

            units = to_decimal(line.get("allocated_units"))
            weight = to_decimal(line.get("applied_weight"))

            if units is not None:
                allocation_total += units

            if weight is not None:
                applied_weight_total += weight

            claim_refs = line.get("contribution_claim_refs", [])

            if isinstance(claim_refs, list):
                allocated_claim_refs.extend(
                    item
                    for item in claim_refs
                    if isinstance(item, str)
                )

                if weight_document is not None:
                    assignments = weight_document.get(
                        "assignments",
                        [],
                    )

                    claim_weight_map: dict[str, Decimal] = {}

                    if isinstance(assignments, list):
                        for assignment in assignments:
                            if not isinstance(assignment, dict):
                                continue

                            claim_ref = assignment.get(
                                "contribution_claim_ref"
                            )
                            assignment_weight = to_decimal(
                                assignment.get("normalized_weight")
                            )

                            if (
                                isinstance(claim_ref, str)
                                and assignment_weight is not None
                            ):
                                claim_weight_map[
                                    claim_ref
                                ] = assignment_weight

                    expected_weight = sum(
                        (
                            claim_weight_map.get(
                                claim_ref,
                                Decimal("0"),
                            )
                            for claim_ref in claim_refs
                        ),
                        Decimal("0"),
                    )

                    if (
                        weight is not None
                        and not decimal_equal(
                            expected_weight,
                            weight,
                            tolerance,
                        )
                    ):
                        errors.append(
                            f"allocations[{index}].applied_weight: "
                            f"expected {expected_weight} from referenced "
                            f"claims, got {weight}"
                        )

    for line_id in duplicate_values(line_ids):
        errors.append(
            f"allocations: duplicate allocation_line_id '{line_id}'"
        )

    for claim_ref in duplicate_values(allocated_claim_refs):
        errors.append(
            f"allocations: Contribution Claim '{claim_ref}' is "
            "assigned more than once"
        )

    if distributable is not None:
        if not decimal_equal(
            allocation_total,
            distributable,
            tolerance,
        ):
            errors.append(
                "allocations.allocated_units: allocation total "
                f"{allocation_total} does not equal distributable "
                f"units {distributable}"
            )

    if not decimal_equal(
        applied_weight_total,
        Decimal("1"),
        tolerance,
    ):
        errors.append(
            "allocations.applied_weight: weights must sum to 1; "
            f"got {applied_weight_total}"
        )

    if weight_document is not None:
        assignments = weight_document.get("assignments", [])

        expected_claim_refs = {
            assignment.get("contribution_claim_ref")
            for assignment in assignments
            if isinstance(assignment, dict)
            and isinstance(
                assignment.get("contribution_claim_ref"),
                str,
            )
        }

        actual_claim_refs = set(allocated_claim_refs)

        missing_claims = sorted(
            expected_claim_refs - actual_claim_refs
        )
        unexpected_claims = sorted(
            actual_claim_refs - expected_claim_refs
        )

        for claim_ref in missing_claims:
            errors.append(
                f"allocations: Weight Resolution claim '{claim_ref}' "
                "was not allocated"
            )

        for claim_ref in unexpected_claims:
            errors.append(
                f"allocations: claim '{claim_ref}' is not present in "
                "the Weight Resolution"
            )

    if plan_status in {
        "approved",
        "partially_executed",
        "executed",
    }:
        if not isinstance(document.get("approval"), dict):
            errors.append(
                f"approval: required when plan_status is '{plan_status}'"
            )

    if plan_status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append(
                "cancelled_at: required for cancelled Allocation Plan"
            )

        if not document.get("cancellation_reason"):
            errors.append(
                "cancellation_reason: required for cancelled Plan"
            )

    errors.extend(evidence_semantic_errors(document))
    return errors


def royalty_receipt_semantic_errors(
    document: dict[str, Any],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []

    cell_id = document.get("cell_id")
    plan_ref = document.get("allocation_plan", {})
    plan_document: dict[str, Any] | None = None

    if isinstance(plan_ref, dict):
        plan_id = plan_ref.get("allocation_plan_id")

        if (
            plan_ref.get("resolution_status")
            == "externally_resolved"
            and not plan_ref.get("record_ref")
        ):
            errors.append(
                "allocation_plan.record_ref: required for "
                "externally_resolved Allocation Plan"
            )

        if (
            plan_ref.get("resolution_status") == "resolved"
            and plan_ref.get("source_cell_id") == cell_id
        ):
            plan_document = known[
                "royalty_cell_allocation_plan"
            ].get(plan_id)

            if plan_document is None:
                errors.append(
                    "allocation_plan.allocation_plan_id: locally "
                    "resolved Allocation Plan was not found"
                )

    allocated_units = to_decimal(
        document.get("allocated_units")
    )
    settled_units = to_decimal(document.get("settled_units"))
    remaining_units = to_decimal(
        document.get("balance_remaining_units")
    )

    if (
        allocated_units is not None
        and settled_units is not None
        and remaining_units is not None
    ):
        if settled_units > allocated_units:
            errors.append(
                "settled_units: must not exceed allocated_units"
            )

        expected_remaining = allocated_units - settled_units

        if expected_remaining != remaining_units:
            errors.append(
                "balance_remaining_units: expected "
                f"{expected_remaining}, got {remaining_units}"
            )

    if plan_document is not None:
        line_id = document.get("allocation_line_id")
        allocations = plan_document.get("allocations", [])
        matching_line: dict[str, Any] | None = None

        if isinstance(allocations, list):
            for line in allocations:
                if (
                    isinstance(line, dict)
                    and line.get("allocation_line_id") == line_id
                ):
                    matching_line = line
                    break

        if matching_line is None:
            errors.append(
                "allocation_line_id: line was not found in "
                "Allocation Plan"
            )
        else:
            comparisons = [
                (
                    "beneficiary_ref",
                    document.get("beneficiary_ref"),
                    matching_line.get("beneficiary_ref"),
                ),
                (
                    "settlement_type",
                    document.get("settlement_type"),
                    matching_line.get("settlement_type"),
                ),
            ]

            for field, actual, expected in comparisons:
                if actual != expected:
                    errors.append(
                        f"{field}: expected '{expected}' from "
                        f"Allocation Plan, got '{actual}'"
                    )

            line_units = to_decimal(
                matching_line.get("allocated_units")
            )

            if (
                allocated_units is not None
                and line_units is not None
                and allocated_units != line_units
            ):
                errors.append(
                    "allocated_units: does not match Allocation Plan line"
                )

            plan_unit = plan_document.get(
                "source_value_event",
                {},
            )

            if isinstance(plan_unit, dict):
                expected_unit = plan_unit.get("unit")

                if document.get("unit") != expected_unit:
                    errors.append(
                        "unit: does not match Allocation Plan unit"
                    )

    status = document.get("settlement_status")
    settlement_evidence = document.get("settlement_evidence")

    if status == "settled":
        if not document.get("settled_at"):
            errors.append(
                "settled_at: required for settled Royalty Receipt"
            )

        if (
            not isinstance(settlement_evidence, list)
            or not settlement_evidence
        ):
            errors.append(
                "settlement_evidence: required for settled receipt"
            )

        if (
            remaining_units is not None
            and remaining_units != Decimal("0")
        ):
            errors.append(
                "balance_remaining_units: settled receipt must have "
                "zero balance"
            )

    if status == "partially_settled":
        if (
            allocated_units is not None
            and settled_units is not None
            and not (
                Decimal("0")
                < settled_units
                < allocated_units
            )
        ):
            errors.append(
                "settled_units: partial settlement requires "
                "0 < settled_units < allocated_units"
            )

        if (
            not isinstance(settlement_evidence, list)
            or not settlement_evidence
        ):
            errors.append(
                "settlement_evidence: required for partial settlement"
            )

    if status == "pending":
        if (
            settled_units is not None
            and settled_units != Decimal("0")
        ):
            errors.append(
                "settled_units: pending receipt must have zero "
                "settled units"
            )

    if status == "failed" and not document.get("status_reason"):
        errors.append(
            "status_reason: required for failed receipt"
        )

    if status == "held" and not document.get("hold_ref"):
        errors.append(
            "hold_ref: required for held receipt"
        )

    if status == "waived" and not document.get("waiver_ref"):
        errors.append(
            "waiver_ref: required for waived receipt"
        )

    if status == "reversed" and not document.get("reversal_ref"):
        errors.append(
            "reversal_ref: required for reversed receipt"
        )

    errors.extend(
        evidence_semantic_errors(
            document,
            field_name="settlement_evidence",
        )
    )

    return errors


def semantic_errors(
    document: dict[str, Any],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    record_type = document.get("record_type")

    if record_type == "royalty_cell_manifest":
        return manifest_semantic_errors(document)

    if record_type == "royalty_cell_origin_record":
        return origin_semantic_errors(document)

    if record_type == "royalty_cell_usage_record":
        return usage_semantic_errors(document, known)

    if record_type == "royalty_cell_derivative_record":
        return derivative_semantic_errors(document, known)

    if record_type == "royalty_cell_contribution_claim":
        return contribution_semantic_errors(document, known)

    if (
        record_type
        == "royalty_cell_contribution_weight_resolution"
    ):
        return weight_resolution_semantic_errors(
            document,
            known,
        )

    if record_type == "royalty_cell_allocation_plan":
        return allocation_plan_semantic_errors(
            document,
            known,
        )

    if record_type == "royalty_cell_royalty_receipt":
        return royalty_receipt_semantic_errors(
            document,
            known,
        )

    return [
        f"record_type: no semantic validator for '{record_type}'"
    ]


def validate_document(
    path: Path,
    validators: dict[str, Draft202012Validator],
    known: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    try:
        document = load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"<load>: {error}"]

    errors = schema_errors(document, validators)

    if errors:
        return [f"[schema] {error}" for error in errors]

    return [
        f"[semantic] {error}"
        for error in semantic_errors(document, known)
    ]


def print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"  - {error}")


def main() -> int:
    print("=== Royalty Cell Protocol Validation ===")
    print()

    try:
        validators = load_validators()
    except Exception as error:
        print(f"[fatal] unable to load schemas: {error}")
        return 1

    for record_type, schema_path in SCHEMA_PATHS.items():
        print(
            f"schema [{record_type}]: "
            f"{schema_path.relative_to(ROOT_DIR)}"
        )

    print()

    pass_files = collect_yaml_files(PASS_DIR)
    fail_files = collect_yaml_files(FAIL_DIR)

    if not pass_files:
        print("[fatal] no pass examples found")
        return 1

    if not fail_files:
        print("[fatal] no fail examples found")
        return 1

    known = collect_known_records(
        pass_files,
        validators,
    )

    validation_failed = False

    print("[validate-pass]")

    for path in pass_files:
        print(f"  {path.relative_to(ROOT_DIR)}")

        errors = validate_document(
            path,
            validators,
            known,
        )

        if errors:
            validation_failed = True
            print("  [failed]")
            print_errors(errors)
        else:
            print("  [schema-ok]")
            print("  [semantic-ok]")

        print()

    print("[validate-expected-fail]")

    for path in fail_files:
        print(f"  {path.relative_to(ROOT_DIR)}")

        errors = validate_document(
            path,
            validators,
            known,
        )

        if not errors:
            validation_failed = True
            print("  [unexpected-pass]")
            print(
                "  - invalid example passed all validation stages"
            )
        else:
            print("  [expected-failure]")
            print_errors(errors)

        print()

    if validation_failed:
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
