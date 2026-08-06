"""Fail-closed readiness check for the AMD Track 2 submission package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def collect_problems() -> list[str]:
    problems: list[str] = []
    required = [
        ROOT / "README.md",
        ROOT / "pyproject.toml",
        SUBMISSION / "PROJECT_SPECIFICATION.md",
        SUBMISSION / "AMD_ROCM_DEPLOYMENT.md",
        SUBMISSION / "DEMO_SCRIPT.md",
        SUBMISSION / "PR_BODY.md",
        SUBMISSION / "AutoFlow-AMD-Track2.pptx",
    ]
    for path in required:
        if not path.is_file():
            problems.append(f"Missing required file: {path.relative_to(ROOT)}")

    environment_path = SUBMISSION / "evidence" / "amd-environment.json"
    environment = load_json(environment_path)
    if not environment:
        problems.append("Run scripts/collect_amd_evidence.py on the AMD Radeon + ROCm host.")
    elif environment.get("ready_for_rocm_inference") is not True:
        problems.append("AMD environment evidence does not confirm both Radeon GPU and ROCm/HIP.")

    benchmark_path = SUBMISSION / "evidence" / "amd-endpoint-benchmark.json"
    benchmark = load_json(benchmark_path)
    if not benchmark:
        problems.append("Run scripts/benchmark_amd_endpoint.py after selecting the AMD provider.")
    else:
        if benchmark.get("provider") != "amd_radeon_cloud":
            problems.append("Endpoint benchmark was not captured with the AMD Radeon provider.")
        if benchmark.get("credentials_included") is not False:
            problems.append("Endpoint benchmark must explicitly confirm that credentials are excluded.")
        if int(benchmark.get("runs") or 0) < 5:
            problems.append("Endpoint benchmark needs at least five runs.")

    info_path = SUBMISSION / "submission-info.json"
    info = load_json(info_path)
    if not info:
        problems.append("Copy submission-info.template.json to submission-info.json and fill it in.")
    else:
        if not str(info.get("team_name") or "").strip():
            problems.append("Add the team or participant name to submission-info.json.")
        members = info.get("members")
        if not isinstance(members, list) or not members or any(
            not isinstance(member, dict)
            or not str(member.get("name") or "").strip()
            or not str(member.get("contribution") or "").strip()
            for member in members
        ):
            problems.append("Add every member name and contribution to submission-info.json.")
        video = str(info.get("demo_video_url") or "").strip()
        if not video.startswith(("https://", "http://")):
            problems.append("Add the public 3-5 minute demo video URL to submission-info.json.")
        registrations = info.get("registrations") or {}
        if not isinstance(registrations, dict) or registrations.get("luma") is not True:
            problems.append("Confirm Luma registration in submission-info.json.")
        if not isinstance(registrations, dict) or registrations.get("amd_developer_program") is not True:
            problems.append("Confirm AMD Developer Program registration in submission-info.json.")
        if info.get("license_confirmed") is not True:
            problems.append("Choose/confirm the repository license before public submission.")

    pr_body = (SUBMISSION / "PR_BODY.md").read_text(encoding="utf-8")
    if "<" in pr_body or ">" in pr_body:
        problems.append("Replace the remaining angle-bracket placeholders in submission/PR_BODY.md.")
    return problems


def main() -> int:
    problems = collect_problems()
    if problems:
        print("NOT READY")
        for index, problem in enumerate(problems, 1):
            print(f"{index}. {problem}")
        return 2
    print("READY: all locally verifiable AMD Track 2 submission requirements are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
