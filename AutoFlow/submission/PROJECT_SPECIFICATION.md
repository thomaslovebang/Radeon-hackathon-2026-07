# AutoFlow — Track 2 Project Specification

## 1. Application scenarios

AutoFlow is a private AI desktop agent for users who need practical computer work completed without learning scripting or recording fragile mouse coordinates. Representative tasks include:

- Researching a topic on the web and returning evidence-backed results.
- Downloading a report through a headless browser.
- Converting local PDF files to text and saving them to an explicit destination.
- Opening applications, files, folders and URLs.
- Filling forms or operating Windows applications through semantic accessibility controls.

## 2. Target users

- Office workers who repeat cross-application workflows.
- Small teams that need a private agent without sending desktop data to a general automation SaaS.
- Developers evaluating local or privately deployed models on AMD Radeon GPUs.
- Users with limited automation experience who can describe outcomes in natural language.

## 3. Agent architecture

AutoFlow uses an iterative execution loop:

1. **Observe:** read the current browser page, local filesystem or Windows accessibility tree.
2. **Plan:** ask the selected model for exactly one registered tool action.
3. **Authorize:** calculate action risk and compare sensitive effects with the original user goal.
4. **Act:** execute through the quietest applicable backend.
5. **Verify:** observe again and attach the real tool result to history.
6. **Report:** finish only when evidence exists, then generate a concrete final response.

Only one agent session can own the computer at a time. A task that pauses for user input retains its session lock, while task-scoped browser resources are safely released between worker threads.

## 4. Core capabilities

### Smart silent routing

- Web tasks use a headless Chromium browser.
- File tasks use dedicated Python tools or restricted PowerShell.
- Desktop applications use Windows UI Automation.
- Foreground keyboard or coordinate input is a last resort.

### General model tool use

The model chooses from a registered vocabulary instead of a fixed list of natural-language intents. The current browser vocabulary includes opening, observing, clicking, typing, selecting, returning and downloading. Desktop and file tools remain composable in the same loop.

### Safety

- Exact local same-origin API checks.
- HTTPS required for remote endpoints carrying credentials.
- API keys stored in Windows Credential Manager.
- Page content treated as untrusted data.
- High-risk effects blocked unless the original goal explicitly authorizes them.
- PowerShell paths must be literal and present in the original request.

## 5. Model and private deployment

AutoFlow accepts OpenAI-compatible model servers. The competition deployment uses the dedicated **AMD Radeon Cloud / ROCm** provider:

- Shared Radeon model endpoint for initial functional validation, or
- Private vLLM endpoint on a dedicated Radeon Cloud instance for final demonstration.

The endpoint URL, model ID and API key are supplied at runtime. Credentials never enter the repository. The same interface supports a vLLM server on a private LAN AMD ROCm host.

## 6. AMD Radeon / ROCm adaptation

The model boundary is deliberately OpenAI-compatible, allowing the agent runtime to remain stable while inference moves to AMD hardware. Adaptation work includes:

- A first-class AMD Radeon Cloud / ROCm provider with editable HTTPS endpoint and explicit model ID.
- A hardware/runtime diagnostic that checks Radeon GPU visibility, `rocminfo`, `rocm-smi`, HIP and PyTorch HIP state.
- A credential-safe endpoint benchmark that records latency without recording API keys.
- A split client/server architecture: Windows accessibility automation stays close to the user, while private inference runs on Radeon ROCm.
- Reproducible evidence JSON for hardware and endpoint performance.

## 7. Inference optimization plan

Optimization is evidence-driven rather than claimed without measurement:

1. Establish a five-run latency baseline using the supplied benchmark.
2. Compare candidate model sizes and precision supported by the selected vLLM ROCm image.
3. Bound Agent responses with JSON output and conservative token limits.
4. Reuse the model endpoint across Agent steps while releasing headless browser processes at task end.
5. Record median and tail latency, then select the smallest model that reliably returns valid tool JSON.

Final parameter values and performance numbers must be filled from the Radeon run in `submission/evidence/amd-endpoint-benchmark.json`.

## 8. Evaluation

- Automated Python regression suite.
- Real headless-browser integration test.
- Real model routing test (`browser_open` selected for a web goal).
- AMD host environment evidence.
- AMD endpoint latency benchmark.
- Recorded end-to-end GUI demonstration on AMD-backed inference.

## 9. Innovation and practical value

AutoFlow focuses on a useful boundary between general agents and deterministic automation. The model selects the next tool from live evidence, but execution remains observable, risk-scoped and locally controlled. Headless web execution makes common research and form tasks silent, while semantic Windows controls remove dependence on prerecorded coordinates.

## 10. Known limitations

- Windows desktop control requires a Windows client and matching privilege level for elevated applications.
- CAPTCHA, first-time login and browser permission prompts may require a user.
- Some websites block headless browsers.
- AMD performance claims are valid only after the included evidence scripts run on the actual Radeon environment.
