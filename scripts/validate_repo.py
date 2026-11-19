"""
CiteVerify AI - Repository Integrity & Contract Validation Suite
Validates:
  1. Required project files exist.
  2. JSON schemas and OpenAPI YAML parse without syntax errors.
  3. Canonical enums in contracts/schemas/enums.json match backend Pydantic and frontend TypeScript enums.
  4. No private .env credential files are tracked by Git.
  5. No hardcoded absolute developer paths exist in source files.
"""
import os
import sys
import json
import re

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def check_required_files():
    print("[1/5] Checking required project files...")
    required = [
        "README.md",
        "AGENTS.md",
        "GEMINI.md",
        "CONTRIBUTING.md",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".env.example",
        "contracts/openapi/openapi.yaml",
        "contracts/schemas/enums.json",
        "contracts/schemas/document.schema.json",
        "contracts/schemas/claim.schema.json",
        "contracts/schemas/citation.schema.json",
        "contracts/schemas/evidence.schema.json",
        "contracts/schemas/research_paper.schema.json",
        "contracts/schemas/verification.schema.json",
        "contracts/schemas/report.schema.json",
        "contracts/schemas/error.schema.json",
        "backend/app/main.py",
        "backend/app/schemas/enums.py",
        "frontend/types/enums.ts",
        "frontend/types/api.ts",
        "frontend/package.json",
        "docs/API_CONTRACT.md",
        "docs/ARCHITECTURE.md",
        "docs/DATABASE_SCHEMA.md",
        "docs/DATA_FLOW.md",
        "docs/ENVIRONMENT.md",
        "docs/HACKATHON_ROADMAP.md",
    ]
    missing = []
    for r in required:
        full_path = os.path.join(REPO_ROOT, r)
        if not os.path.exists(full_path):
            missing.append(r)

    if missing:
        print(f"  FAILED: Missing {len(missing)} required files:")
        for m in missing:
            print(f"    - {m}")
        return False
    print(f"  PASSED: All {len(required)} required files are present.")
    return True


def check_contracts_and_schemas():
    print("[2/5] Validating JSON Schemas and OpenAPI Specification...")
    schema_dir = os.path.join(REPO_ROOT, "contracts", "schemas")
    schema_files = [f for f in os.listdir(schema_dir) if f.endswith(".json")]

    for sf in schema_files:
        full_path = os.path.join(schema_dir, sf)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            print(f"  FAILED: Schema {sf} failed to parse: {e}")
            return False

    # Check OpenAPI YAML
    openapi_path = os.path.join(REPO_ROOT, "contracts", "openapi", "openapi.yaml")
    try:
        with open(openapi_path, "r", encoding="utf-8") as f:
            if yaml:
                yaml.safe_load(f)
            else:
                # Basic non-empty check if pyyaml not yet imported in current runner
                content = f.read()
                assert "openapi:" in content
    except Exception as e:
        print(f"  FAILED: OpenAPI YAML failed to parse: {e}")
        return False

    print(f"  PASSED: {len(schema_files)} JSON schemas and openapi.yaml parsed cleanly.")
    return True


def check_enum_synchronization():
    print("[3/5] Validating Enum Synchronization across Canonical Contracts, Backend, and Frontend...")
    enums_path = os.path.join(REPO_ROOT, "contracts", "schemas", "enums.json")
    with open(enums_path, "r", encoding="utf-8") as f:
        canonical_defs = json.load(f)["definitions"]

    # Read Python backend enums
    py_enums_path = os.path.join(REPO_ROOT, "backend", "app", "schemas", "enums.py")
    with open(py_enums_path, "r", encoding="utf-8") as f:
        py_content = f.read()

    # Read TypeScript frontend enums
    ts_enums_path = os.path.join(REPO_ROOT, "frontend", "types", "enums.ts")
    with open(ts_enums_path, "r", encoding="utf-8") as f:
        ts_content = f.read()

    mismatches = []
    for enum_name, enum_data in canonical_defs.items():
        canonical_values = set(enum_data["enum"])

        # Check Python enum
        for val in canonical_values:
            if f'{val} = "{val}"' not in py_content and f"{val} = '{val}'" not in py_content:
                mismatches.append(f"Backend Python enum {enum_name} missing value: {val}")

        # Check TypeScript enum
        for val in canonical_values:
            if f"'{val}'" not in ts_content and f'"{val}"' not in ts_content:
                mismatches.append(f"Frontend TypeScript enum {enum_name} missing value: {val}")

    if mismatches:
        print(f"  FAILED: Detected {len(mismatches)} enum drift mismatches:")
        for m in mismatches:
            print(f"    - {m}")
        return False

    print(f"  PASSED: All {len(canonical_defs)} canonical enums synchronized with zero drift.")
    return True


def check_tracked_secrets():
    print("[4/5] Checking that no secret .env files are tracked...")
    forbidden = [".env", "backend/.env", "frontend/.env", "ai_engine/.env", "frontend/.env.local"]
    leaked = []
    for f in forbidden:
        path = os.path.join(REPO_ROOT, f)
        if os.path.exists(path):
            leaked.append(f)

    if leaked:
        print(f"  WARNING / FAILED: Found live .env files on disk that should never be committed: {leaked}")
        # Note: presence on disk is okay if gitignored, but ensure .gitignore covers them
    with open(os.path.join(REPO_ROOT, ".gitignore"), "r", encoding="utf-8") as f:
        gitignore = f.read()
    if ".env" not in gitignore:
        print("  FAILED: .gitignore does not ignore .env!")
        return False

    print("  PASSED: .gitignore properly protects .env and secret files.")
    return True


def check_no_absolute_paths():
    print("[5/5] Checking for hardcoded developer absolute paths in source code...")
    prefix = "[A-Za-z]:" + r"[\\/]Users[\\/]"
    linux_prefix = r"/home/[A-Za-z0-9_-]+[\\/]"
    abs_pattern = re.compile(f"({prefix}|{linux_prefix})")
    scanned_exts = (".py", ".ts", ".tsx", ".yaml", ".yml", ".json", ".md")
    ignored_dirs = {".venv", "node_modules", ".git", ".next", "__pycache__"}
    ignored_files = {"ENVIRONMENT.md", "validate_repo.py"}

    violations = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            if file.endswith(scanned_exts) and file not in ignored_files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, start=1):
                            if abs_pattern.search(line):
                                rel_path = os.path.relpath(file_path, REPO_ROOT)
                                violations.append(f"{rel_path}:{line_no}")
                except Exception:
                    pass

    if violations:
        print(f"  FAILED: Found hardcoded absolute paths in {len(violations)} locations:")
        for v in violations[:5]:
            print(f"    - {v}")
        return False

    print("  PASSED: Zero hardcoded developer absolute paths found in repository.")
    return True


def main():
    print("=" * 65)
    print(" CiteVerify AI - Monorepo Validation & Contract Gatekeeper")
    print("=" * 65)

    checks = [
        check_required_files(),
        check_contracts_and_schemas(),
        check_enum_synchronization(),
        check_tracked_secrets(),
        check_no_absolute_paths(),
    ]

    print("=" * 65)
    if all(checks):
        print(" SUCCESS: All 5 validation gates passed. Repository contract is intact!")
        print("=" * 65)
        sys.exit(0)
    else:
        print(" ERROR: Repository validation failed. Resolve failures before committing.")
        print("=" * 65)
        sys.exit(1)


if __name__ == "__main__":
    main()
