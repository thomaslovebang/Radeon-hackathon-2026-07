"""Collect AMD Radeon / ROCm evidence on the machine that runs inference."""

from __future__ import annotations

import argparse
import json

from autoflow.amd import collect_amd_environment, write_amd_evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="submission/evidence/amd-environment.json")
    args = parser.parse_args()
    report = collect_amd_environment()
    destination = write_amd_evidence(args.output, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Evidence written to {destination}")
    return 0 if report["ready_for_rocm_inference"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
