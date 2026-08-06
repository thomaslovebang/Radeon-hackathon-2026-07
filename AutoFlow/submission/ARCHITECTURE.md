# AutoFlow Architecture

```mermaid
flowchart TB
    UI["Local Web UI\n127.0.0.1 only"] --> RT["Agent Runtime"]
    RT --> POLICY["Risk and Goal Authorization"]
    RT --> MODEL["OpenAI-compatible Planner"]
    MODEL --> AMD["Private vLLM\nAMD Radeon + ROCm"]
    RT --> ROUTER{"Smart silent router"}
    ROUTER --> WEB["Headless Chromium"]
    ROUTER --> FILES["Local file/PDF tools"]
    ROUTER --> WIN["Windows UI Automation"]
    WEB --> OBS["Evidence"]
    FILES --> OBS
    WIN --> OBS
    OBS --> RT
    RT --> REPORT["Evidence-enriched final response"]
```

## Trust boundaries

| Boundary | Protection |
|---|---|
| Browser page → Agent | Page text is untrusted and cannot override the goal |
| Web UI → local API | Exact Origin/Host and JSON content type |
| Agent → model endpoint | HTTPS for remote credentials; explicit AMD endpoint field |
| Model → computer tools | Registered tools only; risk classification before execution |
| PowerShell → filesystem | Literal goal-scoped paths; compound/opaque commands blocked |
| Credentials → storage | Windows Credential Manager; excluded from project and logs |
