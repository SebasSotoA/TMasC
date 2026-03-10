#!/usr/bin/env python3
"""
Threat Model Validation Script — TMasC Lab
Validates that the threat model file has required structure and mitigations.
Validates that all routes in api-routes manifest have components in the threat model.
"""

import sys
import yaml
from pathlib import Path


def load_yaml(path: Path) -> dict:
    """Load and parse a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_threat_model(path: str) -> dict:
    """Load and parse the threat model YAML file."""
    return load_yaml(Path(path))


def validate_threat_model(model: dict) -> list[str]:
    """Validate the threat model and return a list of errors."""
    errors = []

    if not model:
        return ["Threat model file is empty or invalid"]

    if "system" not in model:
        errors.append("Missing required field: system")

    if "components" not in model:
        errors.append("Missing required field: components")
    elif not model["components"]:
        errors.append("At least one component must be defined")

    if "threats" not in model:
        errors.append("Missing required field: threats")
    else:
        for i, threat in enumerate(model["threats"]):
            if "id" not in threat:
                errors.append(f"Threat {i + 1}: missing 'id'")
            if "name" not in threat:
                errors.append(f"Threat {i + 1}: missing 'name'")
            if "component" not in threat:
                errors.append(f"Threat {i + 1}: missing 'component'")
            if "mitigation" not in threat or not threat["mitigation"]:
                errors.append(f"Threat {i + 1}: missing or empty 'mitigation' (security requirement)")

    # Rule: Exposed APIs must require authentication
    for comp in model.get("components", []):
        if comp.get("type") == "api" and comp.get("exposed") is True:
            if comp.get("auth_required") is not True:
                errors.append(
                    f"Se encontró una API expuesta sin autenticación obligatoria: '{comp.get('name', 'unknown')}'"
                )

    return errors


def validate_routes_against_model(routes_path: Path, model: dict) -> list[str]:
    """
    Validate that every route's component exists in the threat model.
    Regla: cada ruta en el manifiesto debe tener su componente documentado.
    """
    errors = []
    routes_data = load_yaml(routes_path)

    if not routes_data or "routes" not in routes_data:
        return errors  # No routes to validate

    component_names = {c.get("name") for c in model.get("components", []) if c.get("name")}

    for route in routes_data["routes"]:
        path = route.get("path", "?")
        component = route.get("component")
        if not component:
            errors.append(f"Route '{path}' has no 'component' defined")
            continue
        if component not in component_names:
            errors.append(
                f"Route '{path}' references component '{component}' which is not in the threat model. "
                "Add it to the threat model for security analysis."
            )

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python threat_check.py <threat-model.yaml> [api-routes.yaml]")
        sys.exit(1)

    model_path = Path(sys.argv[1])
    if not model_path.exists():
        print(f"Error: File not found: {model_path}")
        sys.exit(1)

    # Routes file: explicit arg, or convention (threat-model-auth-example.yaml -> api-routes-auth-example.yaml)
    routes_path = None
    if len(sys.argv) >= 3:
        routes_path = Path(sys.argv[2])
    else:
        stem = model_path.stem  # e.g. "threat-model-auth-example"
        candidate = model_path.parent / f"api-routes-{stem.replace('threat-model-', '')}.yaml"
        if stem != "threat-model" and candidate.exists():
            routes_path = candidate
        else:
            default_routes = model_path.parent / "api-routes.yaml"
            if default_routes.exists():
                routes_path = default_routes

    try:
        model = load_threat_model(model_path)
        errors = validate_threat_model(model)

        # Validate routes manifest if present
        if routes_path and routes_path.exists():
            errors.extend(validate_routes_against_model(routes_path, model))

        if errors:
            print("Security validation FAILED")
            print("-" * 40)
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)

        print("Security validation PASSED")
        print(f"  System: {model.get('system', 'N/A')}")
        print(f"  Components: {len(model.get('components', []))}")
        print(f"  Threats with mitigations: {len(model.get('threats', []))}")
        sys.exit(0)

    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
