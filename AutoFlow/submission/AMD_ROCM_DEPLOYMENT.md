# AMD Radeon / ROCm Deployment and Reproduction

## Supported competition topology

- **Client:** AutoFlow on Windows, controlling the user's desktop locally.
- **Inference host:** AMD Radeon Cloud or a supported AMD ROCm Linux machine.
- **Protocol:** authenticated OpenAI-compatible HTTPS API.

This preserves Windows UI Automation while moving private model inference to AMD Radeon hardware.

## Option A — AMD Radeon Cloud shared endpoint

1. Sign in to the AMD Radeon model API service.
2. Select a shared Qwen or DeepSeek model.
3. Copy the supplied Base URL, model ID and API key.
4. In AutoFlow Model Center select **AMD Radeon Cloud / ROCm**.
5. Enter the three supplied values and connect.

This path is suitable for early validation. The final demo should document which AMD service and model were used.

## Option B — private vLLM endpoint on Radeon Cloud

1. Create a Radeon Cloud template.
2. Choose the platform's vLLM model API deployment type.
3. Use a serve command that listens on `0.0.0.0:8000`, as required by the platform.
4. Launch the instance and wait for the private endpoint details.
5. Configure the endpoint, model ID and key in AutoFlow's AMD provider.

Follow the official [Radeon Cloud User Guide](https://github.com/AMD-DEV-CONTEST/Radeon-hackathon-2026-07/blob/main/Radeon-Cloud-User%20Guide/README.md) for the current platform workflow and image options.

## Collect server-side ROCm evidence

Upload or clone this repository on the AMD inference host, then run:

```bash
python scripts/collect_amd_evidence.py \
  --output submission/evidence/amd-environment.json
```

The command succeeds only when it detects both an AMD Radeon GPU and a ROCm/HIP runtime. Review the JSON before committing it; it contains system facts but no credentials.

## Benchmark from the AutoFlow client

After selecting the AMD provider:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_amd_endpoint.py `
  --runs 5 `
  --output submission\evidence\amd-endpoint-benchmark.json
```

The benchmark stores the endpoint hostname, model ID and latency statistics. It never stores the API key.

## Functional verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe examples\demo_mvp.py
```

Then run this GUI task with Smart silent mode enabled:

> Search the web for AMD ROCm, report the result page title and URL, and save no files.

The task history should contain `browser_open` followed by evidence-backed completion, while model inference is served by the selected AMD endpoint.

## Required final evidence

- `submission/evidence/amd-environment.json` from the Radeon host.
- `submission/evidence/amd-endpoint-benchmark.json` from the client.
- A 3-5 minute video showing the AMD environment, AutoFlow provider connection, task execution and final result.
- The model/endpoint name and hardware model in the project specification.

Do not claim hardware verification until these artifacts have been captured on the actual AMD environment.
