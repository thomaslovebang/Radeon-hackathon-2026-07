# 3–5 Minute Demo Recording Script

## 0:00–0:30 — Problem and product

- Show the AutoFlow home page.
- Explain that fixed coordinate recording breaks when windows move.
- State the goal: a private desktop agent using AMD Radeon inference and silent execution.

## 0:30–1:10 — AMD Radeon / ROCm proof

- Show the Radeon Cloud instance or AMD host terminal.
- Run `rocminfo` or `rocm-smi`.
- Show the vLLM model endpoint configuration without revealing the API key.
- Run `scripts/collect_amd_evidence.py`.

## 1:10–1:40 — Connect the private model

- Open Model Center.
- Select **AMD Radeon Cloud / ROCm**.
- Show the endpoint hostname and model ID; keep the API key masked.
- Connect and show the active AMD model status.

## 1:40–2:40 — Silent web task

- Enable Smart silent mode.
- Ask AutoFlow to search for AMD ROCm and report the page title and URL.
- Keep another window active to demonstrate that the mouse is not taken over.
- Show the final evidence-backed response.

## 2:40–3:30 — Local desktop/file value

- Convert PDFs from an explicit folder to TXT, or open a desktop application.
- Explain the routing: headless browser → file tools → Windows UI Automation.

## 3:30–4:15 — Safety and benchmark

- Show that credentials remain in Windows Credential Manager.
- Mention same-origin local API protection and goal-scoped risky actions.
- Run or display `amd-endpoint-benchmark.json` latency results.

## 4:15–4:45 — Closing

- Summarize target users, practical value and future work.
- Show repository README and reproduction commands.
