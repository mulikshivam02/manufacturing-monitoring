"""
Phase 0 separation-enforcement check (design doc, "Separation enforcement" section).

Fails the build if anything under part_a/ imports from part_b/, or vice versa.
This turns "Part A and Part B are permanently separate" from a stated design
intent into something CI actually verifies on every commit.

Run: pytest tests/test_import_boundary.py -v
"""
import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PART_A = REPO_ROOT / "part_a"
PART_B = REPO_ROOT / "part_b"


def _imported_module_roots(py_file: Path) -> set[str]:
    """Return the top-level package name of every import in a .py file."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.add(node.module.split(".")[0])
            # relative imports (from . import x) never cross part_a/part_b,
            # since they stay within whichever package the file lives in.
    return roots


def _check_no_cross_import(source_dir: Path, forbidden_root: str) -> list[str]:
    violations = []
    for py_file in source_dir.rglob("*.py"):
        roots = _imported_module_roots(py_file)
        if forbidden_root in roots:
            violations.append(str(py_file.relative_to(REPO_ROOT)))
    return violations


def test_part_a_does_not_import_part_b():
    violations = _check_no_cross_import(PART_A, forbidden_root="part_b")
    assert not violations, (
        "part_a/ must never import from part_b/ (permanent design separation, "
        f"Section 1). Violating files: {violations}"
    )


def test_part_b_does_not_import_part_a():
    violations = _check_no_cross_import(PART_B, forbidden_root="part_a")
    assert not violations, (
        "part_b/ must never import from part_a/ except through Part A's "
        f"*trained-model outputs* (artifact dependency, not code). Violating files: {violations}"
    )


if __name__ == "__main__":
    # Allow `python tests/test_import_boundary.py` as a quick standalone check
    a_violations = _check_no_cross_import(PART_A, "part_b")
    b_violations = _check_no_cross_import(PART_B, "part_a")
    if a_violations or b_violations:
        print("FAIL — cross-imports found:")
        for f in a_violations:
            print(f"  part_a file importing part_b: {f}")
        for f in b_violations:
            print(f"  part_b file importing part_a: {f}")
        raise SystemExit(1)
    print("OK — part_a/ and part_b/ are fully separated.")
