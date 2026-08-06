# AMD Evidence Directory

Generate the two machine-readable evidence files on an AMD Radeon + ROCm host before submission:

```bash
python scripts/collect_amd_evidence.py
python scripts/benchmark_amd_endpoint.py --runs 5
```

Expected outputs:

- `amd-environment.json` — GPU, ROCm/HIP tools, and runtime readiness.
- `amd-endpoint-benchmark.json` — endpoint host, model, latency, and response size without credentials.

Do not add API keys, access tokens, or fabricated hardware results to this directory.
