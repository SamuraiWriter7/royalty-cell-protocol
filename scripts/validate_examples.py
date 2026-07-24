#!/usr/bin/env python3
"""
Validate Royalty Cell Protocol v0.1 examples.

Validation is performed in two stages:

1. JSON Schema validation
2. Protocol-specific semantic validation

Files under examples/pass must pass both stages.

Files under examples/fail must fail at least one stage. This allows the
repository to verify that invalid protocol states are rejected intentionally.
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

SCHEMA_PATH = (
    ROOT_DIR
    / "schemas"
    / "royalty-cell-manifest.schema.json"
)

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


def schema_errors(
    document: dict[str, Any],
    validator: Draft202012Validator,
) -> list[str]:
    """Return all JSON Schema validation errors."""
    errors: list[str] = []

    sorted_errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )

    for error in sorted_errors:
        path = format_error_path(list(error.absolute_path))
        errors.append(f"{path}: {error.message}")

    return errors


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


def semantic_errors(document: dict[str, Any]) -> list[str]:
    """
    Validate semantic requirements that are difficult or undesirable
    to express entirely in JSON Schema.
    """
    errors: list[str] = []

    if document.get("schema_version") != "0.1.0":
        errors.append(
            "schema_version: expected protocol version '0.1.0'"
        )

    if document.get("record_type") != "royalty_cell_manifest":
        errors.append(
            "record_type: expected 'royalty_cell_manifest'"
        )

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

            for index, role in enumerate(roles):
                if not isinstance(role, dict):
                    continue

                role_id = role.get("role_id")

                if isinstance(role_id, str):
                    role_ids.append(role_id)

                permissions = role.get("permissions", [])

                if isinstance(permissions, list):
                    if "administer_cell" in permissions:
                        has_administrator = True

            duplicate_role_ids = sorted(
                {
                    role_id
                    for role_id in role_ids
                    if role_ids.count(role_id) > 1
                }
            )

            for role_id in duplicate_role_ids:
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
            elif len(accepted_evidence_types) == 0:
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
                elif duration_days < 1:
                    errors.append(
                        "recording_policy.retention.duration_days: "
                        "must be at least 1"
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
        allocation_status = allocation_policy.get("status")
        allocation_policy_ref = allocation_policy.get("policy_ref")

        if allocation_status in {"internal", "external"}:
            if not allocation_policy_ref:
                errors.append(
                    "allocation_policy.policy_ref: required when "
                    "allocation-policy status is 'internal' or 'external'"
                )

        if allocation_status == "not_configured":
            if allocation_policy_ref:
                errors.append(
                    "allocation_policy.policy_ref: must be omitted when "
                    "allocation-policy status is 'not_configured'"
                )

    interoperability = document.get("interoperability", {})

    if isinstance(interoperability, dict):
        export_enabled = interoperability.get("export_enabled")
        record_formats = interoperability.get("record_formats")

        if export_enabled is True:
            if not isinstance(record_formats, list):
                errors.append(
                    "interoperability.record_formats: required when "
                    "record export is enabled"
                )
            elif len(record_formats) == 0:
                errors.append(
                    "interoperability.record_formats: must not be empty "
                    "when record export is enabled"
                )

    return errors


def validate_document(
    path: Path,
    validator: Draft202012Validator,
) -> list[str]:
    """Return all schema and semantic errors for one example."""
    try:
        document = load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"<load>: {error}"]

    errors = schema_errors(document, validator)

    if errors:
        return [f"[schema] {error}" for error in errors]

    return [
        f"[semantic] {error}"
        for error in semantic_errors(document)
    ]


def print_errors(errors: list[str]) -> None:
    """Print formatted validation errors."""
    for error in errors:
        print(f"  - {error}")


def main() -> int:
    """Run repository validation."""
    print("=== Royalty Cell Protocol Validation ===")
    print(f"schema: {SCHEMA_PATH.relative_to(ROOT_DIR)}")
    print()

    try:
        schema = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"[fatal] unable to load schema: {error}")
        return 1
    except Exception as error:
        print(f"[fatal] invalid JSON Schema: {error}")
        return 1

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    pass_files = collect_yaml_files(PASS_DIR)
    fail_files = collect_yaml_files(FAIL_DIR)

    if not pass_files:
        print("[fatal] no pass examples found")
        return 1

    if not fail_files:
        print("[fatal] no fail examples found")
        return 1

    validation_failed = False

    print("[validate-pass]")

    for path in pass_files:
        relative_path = path.relative_to(ROOT_DIR)
        print(f"  {relative_path}")

        errors = validate_document(path, validator)

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

        errors = validate_document(path, validator)

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

    print("All Royalty Cell Protocol examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
