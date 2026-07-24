#!/usr/bin/env python3
"""
Validate Royalty Cell Protocol examples.

Supported protocol records:

- v0.1 Royalty Cell Manifest
- v0.2 Royalty Cell Origin Record
- v0.2 Royalty Cell Usage Record

Validation stages:

1. YAML loading
2. Record-type-specific JSON Schema validation
3. Record-type-specific semantic validation
4. Local Origin-reference validation for Usage examples

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
    """Return YAML example files in stable order."""
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


def load_validators() -> dict[str, Draft202012Validator]:
    """Load and compile all record-type-specific validators."""
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
    """Return schema errors for the document's record type."""
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


def duplicate_values(values: list[str]) -> list[str]:
    """Return duplicated string values in stable order."""
    return sorted(
        {
            value
            for value in values
            if values.count(value) > 1
        }
    )


def evidence_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Check Evidence identifier uniqueness."""
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


def manifest_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Validate v0.1 Royalty Cell Manifest semantics."""
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
    """Validate v0.2 Origin Record semantics."""
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
    known_local_origin_ids: set[str],
) -> list[str]:
    """Validate v0.2 Usage Record semantics."""
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
                if origin_id not in known_local_origin_ids:
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


def semantic_errors(
    document: dict[str, Any],
    known_local_origin_ids: set[str],
) -> list[str]:
    """Dispatch semantic validation by record type."""
    record_type = document.get("record_type")

    if record_type == "royalty_cell_manifest":
        return manifest_semantic_errors(document)

    if record_type == "royalty_cell_origin_record":
        return origin_semantic_errors(document)

    if record_type == "royalty_cell_usage_record":
        return usage_semantic_errors(
            document,
            known_local_origin_ids,
        )

    return [f"record_type: no semantic validator for '{record_type}'"]


def collect_known_origin_ids(
    pass_files: list[Path],
    validators: dict[str, Draft202012Validator],
) -> set[str]:
    """
    Collect schema-valid Origin identifiers from passing examples.

    These identifiers are used to verify locally resolved Usage references.
    """
    origin_ids: set[str] = set()

    for path in pass_files:
        try:
            document = load_yaml(path)
        except (OSError, ValueError, yaml.YAMLError):
            continue

        if document.get("record_type") != "royalty_cell_origin_record":
            continue

        if schema_errors(document, validators):
            continue

        origin_id = document.get("origin_id")

        if isinstance(origin_id, str):
            origin_ids.add(origin_id)

    return origin_ids


def validate_document(
    path: Path,
    validators: dict[str, Draft202012Validator],
    known_local_origin_ids: set[str],
) -> list[str]:
    """Return all schema and semantic errors for one example."""
    try:
        document = load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"<load>: {error}"]

    errors = schema_errors(document, validators)

    if errors:
        return [f"[schema] {error}" for error in errors]

    return [
        f"[semantic] {error}"
        for error in semantic_errors(
            document,
            known_local_origin_ids,
        )
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

    known_local_origin_ids = collect_known_origin_ids(
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
            known_local_origin_ids,
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
            known_local_origin_ids,
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

    print("Known local Origins:")
    for origin_id in sorted(known_local_origin_ids):
        print(f"  - {origin_id}")

    print()
    print("All Royalty Cell Protocol examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
