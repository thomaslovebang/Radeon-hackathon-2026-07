import json
import subprocess

from autoflow.amd import collect_amd_environment, write_amd_evidence


def test_amd_environment_report_detects_radeon_and_rocm(tmp_path):
    def runner(args):
        command = args[0].lower()
        if "powershell" in command:
            return subprocess.CompletedProcess(args, 0, "AMD Radeon PRO W7900\n", "")
        if "rocminfo" in command:
            return subprocess.CompletedProcess(args, 0, "Name: gfx1100\n", "")
        if "rocm-smi" in command:
            return subprocess.CompletedProcess(args, 0, "Radeon PRO W7900\n", "")
        return subprocess.CompletedProcess(args, 0, "version test\n", "")

    report = collect_amd_environment(runner=runner, which=lambda name: name)

    assert report["amd_gpu_detected"] is True
    assert report["rocm_runtime_detected"] is True
    assert report["ready_for_rocm_inference"] is True
    destination = write_amd_evidence(tmp_path / "amd.json", report)
    assert json.loads(destination.read_text(encoding="utf-8"))["ready_for_rocm_inference"] is True


def test_amd_environment_report_fails_closed_without_rocm():
    def runner(args):
        if "powershell" in args[0].lower():
            return subprocess.CompletedProcess(args, 0, "Intel Iris Xe\n", "")
        return subprocess.CompletedProcess(args, 127, "", "not found")

    report = collect_amd_environment(runner=runner, which=lambda name: None)

    assert report["amd_gpu_detected"] is False
    assert report["rocm_runtime_detected"] is False
    assert report["ready_for_rocm_inference"] is False
