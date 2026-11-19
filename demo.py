"""Run a deterministic, messy-code demonstration of LangFix repairs."""
from __future__ import annotations
import random
from dataclasses import dataclass
from fixer import fix_code

@dataclass(frozen=True)
class DemoCase:
    name: str
    language: str
    source: str
    expect_repair: bool

def build_cases(seed: int = 2026) -> list[DemoCase]:
    """Create repeatable messy examples plus deliberately invalid inputs."""
    rng = random.Random(seed)
    cases = []
    for index in range(1, 5):
        padding = " " * rng.randint(1, 5)
        source = f"def calculate_{index}(value):{padding}\n"
        source += f"    doubled = value * 2{padding}\n"
        source += "    return doubled"
        cases.append(DemoCase(f"python-valid-{index}", "python", source, True))
    json_source = '{"project": "LangFix", "active": true, "version": 1}     '
    cases.append(DemoCase("json-valid", "json", json_source, True))
    broken_python = "def broken(value)\\n    return value + 1   "
    cases.append(DemoCase("python-invalid", "python", broken_python, False))
    cases.append(DemoCase("json-invalid", "json", '{"project": , "active": true}   ', False))
    rng.shuffle(cases)
    return cases

def run_demo(*, show: bool = True, seed: int = 2026) -> list[dict]:
    """Run examples and return results; never write source files."""
    results = []
    if show:
        print("\n=== LANGFIX MESSY-CODE DEMO ===")
        print("Preview only: no files are created or overwritten.\n")
    for case in build_cases(seed):
        result = fix_code(case.source, case.language)
        passed = result["changed"] if case.expect_repair else result["fixed"] == case.source
        if case.expect_repair:
            passed = passed and result["validation_after"]["valid"] is True
        else:
            passed = passed and result["validation_before"]["valid"] is False
        record = {
            "name": case.name, "language": case.language,
            "expected_repair": case.expect_repair, "changed": result["changed"],
            "valid_before": result["validation_before"]["valid"],
            "valid_after": result["validation_after"]["valid"],
            "passed": passed, "diff": result["diff"],
        }
        results.append(record)
        if show:
            status = "PASS" if passed else "FAIL"
            print("[{}] {} ({})".format(status, case.name, case.language))
            print("  validation: {} -> {}".format(record["valid_before"], record["valid_after"]))
            print("  changed: {}".format(record["changed"]))
            if record["diff"]:
                print(record["diff"], end="" if record["diff"].endswith("\n") else "\n")
            elif not case.expect_repair:
                print("  Original preserved: no unsafe repair attempted.")
            print()
    if show:
        passed_count = sum(item["passed"] for item in results)
        print("RESULT: {}/{} cases passed".format(passed_count, len(results)))
    if not all(item["passed"] for item in results):
        raise AssertionError("LangFix demo failed; inspect the case output above.")
    return results

if __name__ == "__main__":
    run_demo()