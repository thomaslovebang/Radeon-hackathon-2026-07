# Final Submission Steps

AutoFlow's software, documentation, test suite and presentation are prepared. The remaining steps require your AMD environment, identity, registrations or GitHub account.

## 1. Fill participant information

Copy `submission/submission-info.template.json` to `submission/submission-info.json`, then fill:

- Team or participant name.
- Every member's name and contribution.
- Demo video URL after recording.
- Both registration confirmations.
- License confirmation after choosing the repository license.

Replace the matching placeholders in `submission/PR_BODY.md` and use this title:

```text
Track 2, Your Team or Participant Name, AutoFlow
```

## 2. Obtain an AMD Radeon + ROCm environment

Use Radeon Cloud or a supported AMD Radeon ROCm host. Follow the official [Radeon Cloud User Guide](https://github.com/AMD-DEV-CONTEST/Radeon-hackathon-2026-07/blob/main/Radeon-Cloud-User%20Guide/README.md).

Do not use the current Intel Iris Xe development machine as AMD evidence.

## 3. Capture AMD hardware evidence

On the AMD inference host, copy or clone AutoFlow, install it, and run:

```bash
python -m pip install -e .
python scripts/collect_amd_evidence.py --output submission/evidence/amd-environment.json
```

The second command must exit with code `0`. Open the JSON and confirm:

```json
"ready_for_rocm_inference": true
```

## 4. Connect AutoFlow to AMD inference

On the Windows client:

1. Open AutoFlow Model Center.
2. Select **AMD Radeon Cloud / ROCm**.
3. Enter the Radeon endpoint Base URL, model ID and API key.
4. Connect and run:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_amd_endpoint.py --runs 5 --output submission\evidence\amd-endpoint-benchmark.json
```

Never paste the API key into GitHub, a video description, JSON evidence, or chat.

## 5. Record the 3-5 minute demo

Follow `submission/DEMO_SCRIPT.md`. The recording must visibly show:

- The Radeon GPU and ROCm/HIP environment.
- The AMD provider selected in AutoFlow.
- A real task executed with AMD-backed model inference.
- The completed task and AutoFlow's final response.

Upload the video somewhere reviewers can access without requesting permission, then add its URL to the participant info and PR body.

## 6. Run the final gate

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe examples\demo_mvp.py
.\.venv\Scripts\python.exe scripts\check_submission_readiness.py
```

Do not submit until the last command prints `READY`.

## 7. Submit through GitHub

1. Confirm both the Luma and AMD Developer Program registrations.
2. Fork `AMD-DEV-CONTEST/Radeon-hackathon-2026-07` while signed in to GitHub.
3. Create a new branch in your fork.
4. Add the final AutoFlow project folder and materials.
5. Commit and push the branch.
6. Open a Pull Request to the official repository's default branch.
7. Use the required PR title and the completed `submission/PR_BODY.md`.
8. Verify every link from a signed-out/private browser window.
9. Submit before the official deadline.
