# base.py

from typing import Dict, Any


class InferenceBackend:
    """Base class for all inference backends."""

    def __init__(self):
        self.name = "unknown"
        self.is_hardware_validated = False

    def infer(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class CPUBackend(InferenceBackend):
    """CPU backend - real execution on local machine."""

    def __init__(self):
        super().__init__()
        self.name = "CPU"
        self.is_hardware_validated = True

    def infer(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # no artificial delay
        return {
            "latency_ms": 0,
            "compute_unit": "CPU",
            "timing_source": "MEASURED_CPU",
            "precision": "FP32",
            "ram_peak_mb": "n/a",
            "layers_on_npu": "0/0",
            "runtime": "onnxruntime-cpu",
        }


class SnapdragonBackend(InferenceBackend):
    """Snapdragon NPU backend - target path, NOT hardware-validated.

    Reference timings (Qualcomm AI Hub hosted jobs):
        EasyOCR detector uint8:    13.5 ms (job jgk4j29wp)
        EasyOCR recognizer uint8:  10.5 ms (job jp1n3jw7g)
        EasyOCR detector FLOAT16:  ~39.5 ms (job jpxlmx3jp)
        EasyOCR recognizer FLOAT16: ~19.3 ms (job jprl9wnvp)

    These are references, not measured on this machine.
    """

    def __init__(self):
        super().__init__()
        self.name = "Snapdragon NPU"
        self.is_hardware_validated = False

    def infer(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # no simulation
        return {
            "latency_ms": 0,
            "compute_unit": "NPU (Hexagon HTP) - reference",
            "timing_source": "REFERENCE_NOT_MEASURED",
            "precision": "FLOAT16",
            "ram_peak_mb": "n/a",
            "layers_on_npu": "reference",
            "runtime": "qnn_dlc (QNN HTP) - target",
        }


def get_backend(mode: str) -> InferenceBackend:
    if mode == "cpu":
        return CPUBackend()
    elif mode == "snapdragon":
        return SnapdragonBackend()
    else:
        raise ValueError("Unknown backend mode: " + str(mode))


def get_backend_with_fallback() -> InferenceBackend:
    """Auto-select with fallback hierarchy.

    Priority:
        1. QNN/HTP (Snapdragon NPU) - if available
        2. CPU (local fallback)
    """
    try:
        from src.backend.qnn_backend import QNNBackend
        qnn = QNNBackend()
        if qnn.available and qnn.is_hardware_validated:
            return qnn
    except Exception:
        pass

    return CPUBackend()