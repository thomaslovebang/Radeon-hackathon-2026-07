"""Benchmark the configured AMD Radeon Cloud OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from openai import OpenAI

from autoflow.deepseek import ProviderCredentials


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", default="submission/evidence/amd-endpoint-benchmark.json")
    args = parser.parse_args()
    runs = max(1, min(args.runs, 20))
    config = ProviderCredentials().get_config()
    if config.get("provider") != "amd_radeon_cloud":
        raise SystemExit("Select AMD Radeon Cloud / ROCm in AutoFlow Model Center first.")
    client = OpenAI(
        api_key=str(config.get("api_key") or "not-required"),
        base_url=str(config["base_url"]),
        timeout=60.0,
        max_retries=0,
    )
    latencies: list[float] = []
    outputs: list[int] = []
    for _ in range(runs):
        started = time.perf_counter()
        response = client.chat.completions.create(
            model=str(config["model"]),
            messages=[{"role": "user", "content": "Reply with exactly: AMD Radeon ready"}],
            max_tokens=20,
            temperature=0,
        )
        latencies.append(round((time.perf_counter() - started) * 1000, 2))
        outputs.append(len(response.choices[0].message.content or ""))
    report = {
        "schema_version": 1,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "provider": "amd_radeon_cloud",
        "base_url_host": urlparse(str(config["base_url"])).hostname or "",
        "model": str(config["model"]),
        "runs": runs,
        "latency_ms": {
            "values": latencies,
            "mean": round(statistics.mean(latencies), 2),
            "median": round(statistics.median(latencies), 2),
            "min": min(latencies),
            "max": max(latencies),
        },
        "response_character_counts": outputs,
        "credentials_included": False,
    }
    destination = Path(args.output).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
