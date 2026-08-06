"""AMD Radeon / ROCm environment detection and reproducible evidence helpers."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def collect_amd_environment(
    runner: Runner | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> dict[str, Any]:
    """Collect non-secret hardware/runtime facts suitable for submission evidence."""
    run = runner or _run
    gpu_names = _gpu_names(run)
    commands: dict[str, dict[str, Any]] = {}
    for name, args in {
        "rocminfo": ["rocminfo"],
        "rocm-smi": ["rocm-smi", "--showproductname"],
        "hipcc": ["hipcc", "--version"],
        "ollama": ["ollama", "--version"],
    }.items():
        executable = which(args[0])
        commands[name] = _command_fact(run, [executable, *args[1:]]) if executable else {
            "available": False,
            "returncode": None,
            "summary": "not found",
        }

    torch_fact = _torch_fact()
    amd_gpu_detected = any("amd" in name.casefold() or "radeon" in name.casefold() for name in gpu_names)
    rocm_runtime_detected = bool(
        commands["rocminfo"]["available"]
        or commands["rocm-smi"]["available"]
        or torch_fact.get("hip_version")
    )
    ready = bool(amd_gpu_detected and rocm_runtime_detected)
    return {
        "schema_version": 1,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "gpu_names": gpu_names,
        "amd_gpu_detected": amd_gpu_detected,
        "rocm_runtime_detected": rocm_runtime_detected,
        "ready_for_rocm_inference": ready,
        "commands": commands,
        "torch": torch_fact,
        "environment": {
            "ROCM_PATH_set": bool(os.environ.get("ROCM_PATH")),
            "HIP_PATH_set": bool(os.environ.get("HIP_PATH")),
            "HSA_OVERRIDE_GFX_VERSION_set": bool(os.environ.get("HSA_OVERRIDE_GFX_VERSION")),
        },
        "verdict": (
            "AMD Radeon GPU and ROCm runtime detected."
            if ready
            else "AMD Radeon GPU and ROCm runtime were not both detected; run this check on Radeon Cloud or a supported AMD host."
        ),
    }


def write_amd_evidence(path: str | Path, report: dict[str, Any]) -> Path:
    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return destination


def _gpu_names(run: Runner) -> list[str]:
    if os.name == "nt":
        completed = run([
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
        ])
    else:
        completed = run(["sh", "-lc", "lspci 2>/dev/null | grep -Ei 'vga|3d|display' || true"])
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()][:16]


def _command_fact(run: Runner, args: list[str]) -> dict[str, Any]:
    completed = run(args)
    output = "\n".join((completed.stdout, completed.stderr)).strip()
    return {
        "available": completed.returncode == 0,
        "returncode": completed.returncode,
        "summary": output[:4000],
    }


def _torch_fact() -> dict[str, Any]:
    try:
        import torch

        hip_version = str(getattr(torch.version, "hip", "") or "")
        available = bool(torch.cuda.is_available())
        devices = [torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())] if available else []
        return {
            "installed": True,
            "version": str(torch.__version__),
            "hip_version": hip_version,
            "accelerator_available": available,
            "devices": devices,
        }
    except Exception as exc:
        return {
            "installed": False,
            "version": "",
            "hip_version": "",
            "accelerator_available": False,
            "devices": [],
            "note": type(exc).__name__,
        }


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=20, errors="replace")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(args, 127, "", f"{type(exc).__name__}: {exc}")
