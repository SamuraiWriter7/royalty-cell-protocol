#!/usr/bin/env python3
"""
Validate Royalty Cell Protocol examples.

Supported records:

- v0.1 Royalty Cell Manifest
- v0.2 Royalty Cell Origin Record
- v0.2 Royalty Cell Usage Record
- v0.3 Royalty Cell Derivative Record
- v0.3 Royalty Cell Contribution Claim

Validation stages:

1. YAML loading
2. Record-type-specific JSON Schema validation
3. Record-type-specific semantic validation
4. Local record-reference validation

Files under examples/pass must pass all stages.

Files under examples/fail must fail at least one stage.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT_DIR = Path(__file__).resolve().parents[1]

SCHEMA_PATHS = {
    "royalty_cell_manifest": (
        ROOT_DIR
        / "schemas"
        / "royalty-cell-manifest.schema.json"
    ),
    "royalty_cell_origin_record": (
        ROOT_DIR
        / "schemas"
        / "royalty-cell-origin-record.schema.json"
    ),
    "royalty_cell_usage_record": (
        ROOT_DIR
        / "schemas"
        / "royalty-cell-usage-record.schema.json"
    ),
    "royalty_cell_derivative_record": (
        ROOT_DIR
        / "schemas"
        / "royalty-cell-derivative-record.schema.json"
    ),
    "royalty_cell_contribution_claim": (
        ROOT_DIR
        / "schemas"
        / "royalty-cell-contribution-claim.schema.json"
    ),
}

ID_FIELDS = {
    "royalty_cell_origin_record": "origin_id",
    "royalty_cell_usage_record": "usage_id",
    "royalty_cell_derivative_record": "derivative_id",
    "royalty_cell_contribution_claim": "claim_id",
}

TARGET_TYPE_TO_RECORD_TYPE = {
    "origin_record": "royalty_cell_origin_record",
    "usage_record": "royalty_cell_usage_record",
    "derivative_record": "royalty_cell_derivative_record",
}

PASS_DIR = ROOT_DIR / "examples" / "pass"
FAIL_DIR = ROOT_DIR / "examples" / "fail"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be a JSON object")

    return data


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from disk."""
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be a YAML mapping")

    return data


def collect_yaml_files(directory: Path) -> list[Path]:
    """Return YAML files in stable order."""
    files = list(directory.glob("*.yaml"))
    files.extend(directory.glob("*.yml"))
    return sorted(set(files))


def format_error_path(parts: list[Any]) -> str:
    """Convert a jsonschema path into a readable dotted path."""
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
    """Parse an ISO-8601 datetime when possible."""
    if not isinstance(value, str):
        return None

    normalized = value

    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def duplicate_values(values: list[str]) -> list[str]:
    """Return duplicated values in stable order."""
    return sorted(
        {
            value
            for value in values
            if values.count(value) > 1
        }
    )


def load_validators() -> dict[str, Draft202012Validator]:
    """Load and compile all JSON Schema validators."""
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
    """Return JSON Schema errors for a document."""
    record_type = document.get("record_type")

    if not isinstance(record_type, str):
        return ["record_type: missing or not a string"]

    validator = validators.get(record_type)

    if validator is None:
        return [f"record_type: unsupported record type '{record_type}'"]

    errors: list[str] = []

    sorted_errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )

    for error in sorted_errors:
        path = format_error_path(list(error.absolute_path))
        errors.append(f"{path}: {error.message}")

    return errors


def evidence_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Validate Evidence identifier uniqueness."""
    errors: list[str] = []
    evidence = document.get("evidence", [])

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
            f"evidence: duplicate evidence_id '{evidence_id}'"
        )

    return errors


def collect_known_record_ids(
    pass_files: list[Path],
    validators: dict[str, Draft202012Validator],
) -> dict[str, set[str]]:
    """
    Collect schema-valid record identifiers from passing examples.

    Semantic validation later uses these identifiers to verify local links.
    """
    known_ids: dict[str, set[str]] = {
        record_type: set()
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
            known_ids[record_type].add(record_id)

    return known_ids


def manifest_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Validate Royalty Cell Manifest semantics."""
    errors: list[str] = []

    created_at = parse_datetime(document.get("created_at"))
    updated_at = parse_datetime(document.get("updated_at"))

    if created_at is not None and updated_at is not None:
        if updated_at < created_at:
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
                    "governance.decision_policy.policy_ref: "
                    "required when approval_rule is 'external'"
                )

            if mode == "external_policy" and not policy_ref:
                errors.append(
                    "governance.decision_policy.policy_ref: "
                    "required when governance mode is 'external_policy'"
                )

    membership = document.get("membership", {})

    if isinstance(membership, dict):
        admission_mode = membership.get("admission_mode")
        admission_policy_ref = membership.get("admission_policy_ref")

        if admission_mode in {"request", "invite_only"}:
            if not admission_policy_ref:
                errors.append(
                    "membership.admission_policy_ref: required when "
                    "admission_mode is 'request' or 'invite_only'"
                )

        roles = membership.get("roles", [])

        if isinstance(roles, list):
            role_ids: list[str] = []
            has_administrator = False

            for role in roles:
                if not isinstance(role, dict):
                    continue

                role_id = role.get("role_id")

                if isinstance(role_id, str):
                    role_ids.append(role_id)

                permissions = role.get("permissions", [])

                if isinstance(permissions, list):
                    if "administer_cell" in permissions:
                        has_administrator = True

            for role_id in duplicate_values(role_ids):
                errors.append(
                    f"membership.roles: duplicate role_id '{role_id}'"
                )

            if not has_administrator:
                errors.append(
                    "membership.roles: at least one role must include "
                    "the 'administer_cell' permission"
                )

    recording_policy = document.get("recording_policy", {})

    if isinstance(recording_policy, dict):
        evidence_requirement = recording_policy.get(
            "evidence_requirement"
        )
        accepted_evidence_types = recording_policy.get(
            "accepted_evidence_types"
        )
        evidence_policy_ref = recording_policy.get(
            "evidence_policy_ref"
        )

        if evidence_requirement == "required":
            if not isinstance(accepted_evidence_types, list):
                errors.append(
                    "recording_policy.accepted_evidence_types: "
                    "required when evidence_requirement is 'required'"
                )
            elif not accepted_evidence_types:
                errors.append(
                    "recording_policy.accepted_evidence_types: "
                    "must not be empty when evidence is required"
                )

        if evidence_requirement == "policy_defined":
            if not evidence_policy_ref:
                errors.append(
                    "recording_policy.evidence_policy_ref: "
                    "required when evidence_requirement is "
                    "'policy_defined'"
                )

        retention = recording_policy.get("retention", {})

        if isinstance(retention, dict):
            retention_mode = retention.get("mode")

            if retention_mode == "fixed_period":
                duration_days = retention.get("duration_days")

                if not isinstance(duration_days, int):
                    errors.append(
                        "recording_policy.retention.duration_days: "
                        "required when retention mode is 'fixed_period'"
                    )

            if retention_mode == "external_policy":
                if not retention.get("policy_ref"):
                    errors.append(
                        "recording_policy.retention.policy_ref: "
                        "required when retention mode is "
                        "'external_policy'"
                    )

    allocation_policy = document.get("allocation_policy", {})

    if isinstance(allocation_policy, dict):
        status = allocation_policy.get("status")
        policy_ref = allocation_policy.get("policy_ref")

        if status in {"internal", "external"} and not policy_ref:
            errors.append(
                "allocation_policy.policy_ref: required when "
                "allocation-policy status is 'internal' or 'external'"
            )

        if status == "not_configured" and policy_ref:
            errors.append(
                "allocation_policy.policy_ref: must be omitted when "
                "allocation-policy status is 'not_configured'"
            )

    return errors


def origin_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Validate Origin Record semantics."""
    errors: list[str] = []

    origin_created_at = parse_datetime(
        document.get("origin_created_at")
    )
    declared_at = parse_datetime(document.get("declared_at"))

    if origin_created_at is not None and declared_at is not None:
        if origin_created_at > declared_at:
            errors.append(
                "origin_created_at: must not be later than declared_at"
            )

    claim_basis = document.get("claim_basis")
    claim_status = document.get("claim_status")

    if claim_basis == "imported_record":
        if not document.get("imported_from_ref"):
            errors.append(
                "imported_from_ref: required when claim_basis is "
                "'imported_record'"
            )

    if claim_status == "contested":
        contest_refs = document.get("contest_refs")

        if not isinstance(contest_refs, list) or not contest_refs:
            errors.append(
                "contest_refs: required when claim_status is "
                "'contested'"
            )

    if claim_status == "withdrawn":
        if not document.get("status_reason"):
            errors.append(
                "status_reason: required when claim_status is "
                "'withdrawn'"
            )

    if claim_status == "superseded":
        if not document.get("superseded_by_ref"):
            errors.append(
                "superseded_by_ref: required when claim_status is "
                "'superseded'"
            )

    errors.extend(evidence_semantic_errors(document))

    return errors


def usage_semantic_errors(
    document: dict[str, Any],
    known_ids: dict[str, set[str]],
) -> list[str]:
    """Validate Usage Record semantics."""
    errors: list[str] = []

    usage_status = document.get("usage_status")

    if usage_status == "completed":
        if not document.get("occurred_at"):
            errors.append(
                "occurred_at: required when usage_status is "
                "'completed'"
            )

    if usage_status == "disputed":
        dispute_refs = document.get("dispute_refs")

        if not isinstance(dispute_refs, list) or not dispute_refs:
            errors.append(
                "dispute_refs: required when usage_status is "
                "'disputed'"
            )

    if usage_status == "withdrawn":
        if not document.get("status_reason"):
            errors.append(
                "status_reason: required when usage_status is "
                "'withdrawn'"
            )

    authorization = document.get("authorization", {})

    if isinstance(authorization, dict):
        authorization_status = authorization.get("status")
        authorization_ref = authorization.get("authorization_ref")
        policy_ref = authorization.get("policy_ref")

        if authorization_status == "granted":
            if not authorization_ref:
                errors.append(
                    "authorization.authorization_ref: required when "
                    "authorization status is 'granted'"
                )

        if authorization_status == "not_required":
            if not policy_ref:
                errors.append(
                    "authorization.policy_ref: required when "
                    "authorization status is 'not_required'"
                )

        if authorization_status == "denied":
            if usage_status == "completed":
                errors.append(
                    "usage_status: completed Usage cannot have "
                    "denied authorization"
                )

    origin_links = document.get("origin_links", [])

    if isinstance(origin_links, list):
        linked_origin_ids: list[str] = []
        usage_cell_id = document.get("cell_id")

        for index, origin_link in enumerate(origin_links):
            if not isinstance(origin_link, dict):
                continue

            origin_id = origin_link.get("origin_id")
            source_cell_id = origin_link.get("source_cell_id")
            resolution_status = origin_link.get("resolution_status")
            record_ref = origin_link.get("record_ref")

            if isinstance(origin_id, str):
                linked_origin_ids.append(origin_id)

            if resolution_status == "externally_resolved":
                if not record_ref:
                    errors.append(
                        f"origin_links[{index}].record_ref: required "
                        "when resolution_status is "
                        "'externally_resolved'"
                    )

            is_local_resolved = (
                resolution_status == "resolved"
                and source_cell_id == usage_cell_id
            )

            if is_local_resolved:
                known_origins = known_ids[
                    "royalty_cell_origin_record"
                ]

                if origin_id not in known_origins:
                    errors.append(
                        f"origin_links[{index}].origin_id: locally "
                        f"resolved Origin '{origin_id}' was not found "
                        "among passing local Origin examples"
                    )

        for origin_id in duplicate_values(linked_origin_ids):
            errors.append(
                f"origin_links: duplicate origin_id '{origin_id}'"
            )

    attribution = document.get("attribution")

    if isinstance(attribution, dict):
        attribution_status = attribution.get("status")

        if attribution_status == "provided":
            if not (
                attribution.get("display_text")
                or attribution.get("target_ref")
            ):
                errors.append(
                    "attribution: display_text or target_ref is "
                    "required when attribution status is 'provided'"
                )

    usage_scope = document.get("usage_scope", {})

    if isinstance(usage_scope, dict):
        start_at = parse_datetime(usage_scope.get("start_at"))
        end_at = parse_datetime(usage_scope.get("end_at"))

        if start_at is not None and end_at is not None:
            if end_at < start_at:
                errors.append(
                    "usage_scope.end_at: must be equal to or later "
                    "than usage_scope.start_at"
                )

    errors.extend(evidence_semantic_errors(document))

    return errors


def derivative_semantic_errors(
    document: dict[str, Any],
    known_ids: dict[str, set[str]],
) -> list[str]:
    """Validate Derivative Record semantics."""
    errors: list[str] = []

    derivative_id = document.get("derivative_id")
    derivative_cell_id = document.get("cell_id")
    derivative_type = document.get("derivative_type")
    derivative_status = document.get("derivative_status")

    created_at = parse_datetime(document.get("created_at"))
    declared_at = parse_datetime(document.get("declared_at"))

    if created_at is not None and declared_at is not None:
        if created_at > declared_at:
            errors.append(
                "created_at: must not be later than declared_at"
            )

    if derivative_status == "contested":
        contest_refs = document.get("contest_refs")

        if not isinstance(contest_refs, list) or not contest_refs:
            errors.append(
                "contest_refs: required when derivative_status is "
                "'contested'"
            )

    if derivative_status == "withdrawn":
        if not document.get("status_reason"):
            errors.append(
                "status_reason: required when derivative_status is "
                "'withdrawn'"
            )

    if derivative_status == "superseded":
        if not document.get("superseded_by_ref"):
            errors.append(
                "superseded_by_ref: required when derivative_status "
                "is 'superseded'"
            )

    parent_links = document.get("parent_links", [])

    if isinstance(parent_links, list):
        source_ids: list[str] = []
        primary_parent_count = 0

        for index, parent in enumerate(parent_links):
            if not isinstance(parent, dict):
                continue

            source_id = parent.get("source_id")
            source_record_type = parent.get("source_record_type")
            source_cell_id = parent.get("source_cell_id")
            dependency_level = parent.get("dependency_level")
            resolution_status = parent.get("resolution_status")
            record_ref = parent.get("record_ref")

            if isinstance(source_id, str):
                source_ids.append(source_id)

            if dependency_level == "primary":
                primary_parent_count += 1

            if source_id == derivative_id:
                errors.append(
                    f"parent_links[{index}].source_id: a Derivative "
                    "Record cannot reference itself as a parent"
                )

            expected_prefix = None

            if source_record_type == "origin_record":
                expected_prefix = "urn:royalty-origin:"
            elif source_record_type == "derivative_record":
                expected_prefix = "urn:royalty-derivative:"

            if (
                isinstance(source_id, str)
                and expected_prefix is not None
                and not source_id.startswith(expected_prefix)
            ):
                errors.append(
                    f"parent_links[{index}].source_id: identifier "
                    f"does not match source_record_type "
                    f"'{source_record_type}'"
                )

            if resolution_status == "externally_resolved":
                if not record_ref:
                    errors.append(
                        f"parent_links[{index}].record_ref: required "
                        "when resolution_status is "
                        "'externally_resolved'"
                    )

            is_local_resolved = (
                resolution_status == "resolved"
                and source_cell_id == derivative_cell_id
            )

            if is_local_resolved:
                local_record_type = (
                    TARGET_TYPE_TO_RECORD_TYPE.get(
                        source_record_type
                    )
                )

                if local_record_type is not None:
                    known_sources = known_ids[local_record_type]

                    if source_id not in known_sources:
                        errors.append(
                            f"parent_links[{index}].source_id: "
                            f"locally resolved {source_record_type} "
                            f"'{source_id}' was not found among "
                            "passing local examples"
                        )

        for source_id in duplicate_values(source_ids):
            errors.append(
                f"parent_links: duplicate source_id '{source_id}'"
            )

        if primary_parent_count == 0:
            errors.append(
                "parent_links: at least one parent must have "
                "dependency_level 'primary'"
            )

        if derivative_type == "combination":
            if len(set(source_ids)) < 2:
                errors.append(
                    "parent_links: derivative_type 'combination' "
                    "requires at least two distinct parents"
                )

    errors.extend(evidence_semantic_errors(document))

    return errors


def contribution_semantic_errors(
    document: dict[str, Any],
    known_ids: dict[str, set[str]],
) -> list[str]:
    """Validate Contribution Claim semantics."""
    errors: list[str] = []

    claim_status = document.get("claim_status")
    contribution_cell_id = document.get("cell_id")

    target = document.get("target", {})

    if isinstance(target, dict):
        target_id = target.get("target_id")
        target_record_type = target.get("target_record_type")
        source_cell_id = target.get("source_cell_id")
        resolution_status = target.get("resolution_status")
        record_ref = target.get("record_ref")

        expected_prefixes = {
            "origin_record": "urn:royalty-origin:",
            "usage_record": "urn:royalty-usage:",
            "derivative_record": "urn:royalty-derivative:",
        }

        expected_prefix = expected_prefixes.get(
            target_record_type
        )

        if (
            isinstance(target_id, str)
            and expected_prefix is not None
            and not target_id.startswith(expected_prefix)
        ):
            errors.append(
                "target.target_id: identifier does not match "
                f"target_record_type '{target_record_type}'"
            )

        if resolution_status == "externally_resolved":
            if not record_ref:
                errors.append(
                    "target.record_ref: required when "
                    "resolution_status is 'externally_resolved'"
                )

        is_local_resolved = (
            resolution_status == "resolved"
            and source_cell_id == contribution_cell_id
        )

        if is_local_resolved:
            local_record_type = TARGET_TYPE_TO_RECORD_TYPE.get(
                target_record_type
            )

            if local_record_type is not None:
                known_targets = known_ids[local_record_type]

                if target_id not in known_targets:
                    errors.append(
                        "target.target_id: locally resolved "
                        f"{target_record_type} '{target_id}' was not "
                        "found among passing local examples"
                    )

    contribution_period = document.get(
        "contribution_period",
        {},
    )

    if isinstance(contribution_period, dict):
        start_at = parse_datetime(
            contribution_period.get("start_at")
        )
        end_at = parse_datetime(
            contribution_period.get("end_at")
        )

        if start_at is not None and end_at is not None:
            if end_at < start_at:
                errors.append(
                    "contribution_period.end_at: must be equal to "
                    "or later than contribution_period.start_at"
                )

    recognition = document.get("recognition")

    expected_recognition_status = {
        "recognized": "recognized",
        "partially_recognized": "partially_recognized",
        "rejected": "rejected",
    }

    expected_status = expected_recognition_status.get(
        claim_status
    )

    if expected_status is not None:
        if not isinstance(recognition, dict):
            errors.append(
                "recognition: required when claim_status is "
                f"'{claim_status}'"
            )
        else:
            actual_status = recognition.get("status")

            if actual_status != expected_status:
                errors.append(
                    "recognition.status: expected "
                    f"'{expected_status}' when claim_status is "
                    f"'{claim_status}'"
                )

    if claim_status in {"submitted", "acknowledged"}:
        if isinstance(recognition, dict):
            if recognition.get("status") != "pending":
                errors.append(
                    "recognition.status: submitted or acknowledged "
                    "claims may only have pending recognition"
                )

    if isinstance(recognition, dict):
        recognition_status = recognition.get("status")

        if recognition_status in {
            "recognized",
            "partially_recognized",
            "rejected",
        }:
            recognized_by_refs = recognition.get(
                "recognized_by_refs"
            )

            if (
                not isinstance(recognized_by_refs, list)
                or not recognized_by_refs
            ):
                errors.append(
                    "recognition.recognized_by_refs: required for "
                    "completed recognition decisions"
                )

            if not recognition.get("decided_at"):
                errors.append(
                    "recognition.decided_at: required for completed "
                    "recognition decisions"
                )

            if not recognition.get("rationale"):
                errors.append(
                    "recognition.rationale: required for completed "
                    "recognition decisions"
                )

            if not recognition.get("policy_ref"):
                errors.append(
                    "recognition.policy_ref: required for completed "
                    "recognition decisions"
                )

        if recognition_status in {
            "recognized",
            "partially_recognized",
        }:
            if not recognition.get("recognized_significance"):
                errors.append(
                    "recognition.recognized_significance: required "
                    "for recognized or partially recognized claims"
                )

    if claim_status == "disputed":
        dispute_refs = document.get("dispute_refs")

        if not isinstance(dispute_refs, list) or not dispute_refs:
            errors.append(
                "dispute_refs: required when claim_status is "
                "'disputed'"
            )

    if claim_status == "withdrawn":
        if not document.get("status_reason"):
            errors.append(
                "status_reason: required when claim_status is "
                "'withdrawn'"
            )

    if claim_status == "superseded":
        if not document.get("superseded_by_ref"):
            errors.append(
                "superseded_by_ref: required when claim_status is "
                "'superseded'"
            )

    errors.extend(evidence_semantic_errors(document))

    return errors


def semantic_errors(
    document: dict[str, Any],
    known_ids: dict[str, set[str]],
) -> list[str]:
    """Dispatch semantic validation by record type."""
    record_type = document.get("record_type")

    if record_type == "royalty_cell_manifest":
        return manifest_semantic_errors(document)

    if record_type == "royalty_cell_origin_record":
        return origin_semantic_errors(document)

    if record_type == "royalty_cell_usage_record":
        return usage_semantic_errors(document, known_ids)

    if record_type == "royalty_cell_derivative_record":
        return derivative_semantic_errors(
            document,
            known_ids,
        )

    if record_type == "royalty_cell_contribution_claim":
        return contribution_semantic_errors(
            document,
            known_ids,
        )

    return [
        f"record_type: no semantic validator for '{record_type}'"
    ]


def validate_document(
    path: Path,
    validators: dict[str, Draft202012Validator],
    known_ids: dict[str, set[str]],
) -> list[str]:
    """Return all schema and semantic errors for one example."""
    try:
        document = load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"<load>: {error}"]

    errors = schema_errors(document, validators)

    if errors:
        return [
            f"[schema] {error}"
            for error in errors
        ]

    return [
        f"[semantic] {error}"
        for error in semantic_errors(document, known_ids)
    ]


def print_errors(errors: list[str]) -> None:
    """Print formatted validation errors."""
    for error in errors:
        print(f"  - {error}")


def main() -> int:
    """Run repository validation."""
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

    known_ids = collect_known_record_ids(
        pass_files,
        validators,
    )

    validation_failed = False

    print("[validate-pass]")

    for path in pass_files:
        relative_path = path.relative_to(ROOT_DIR)
        print(f"  {relative_path}")

        errors = validate_document(
            path,
            validators,
            known_ids,
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
        relative_path = path.relative_to(ROOT_DIR)
        print(f"  {relative_path}")

        errors = validate_document(
            path,
            validators,
            known_ids,
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

    for record_type in sorted(known_ids):
        print(f"  [{record_type}]")

        for record_id in sorted(known_ids[record_type]):
            print(f"    - {record_id}")

    print()
    print("All Royalty Cell Protocol examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
