# base.py


import time


class InferenceBackend:
    """Base class. Do not use directly."""

    def __init__(self):
        self.name = "unknown"
        self.is_real_hardware = False

    def infer(self, task, payload):
        # task: "vision" or "reasoning"
        # payload: dict with input info
        # returns: dict with result + timing
        raise NotImplementedError


class CPUBackend(InferenceBackend):
    """
    Runs on any CPU. This is what I'm using on my laptop
    because I don't have a Snapdragon device.

    Timing values come from Qualcomm AI Hub published benchmarks
    for the equivalent NPU workload (used as target comparison).
    Actual CPU execution here is simulated at the benchmark rate.
    """

    # published benchmarks from Qualcomm AI Hub (Snapdragon X Elite)
    BENCHMARKS = {
        "vision": 2500,      # ms on CPU for InternVL3.5-2B
        "reasoning": 857,    # ms on CPU for Qwen3-1.7B
    }

    def __init__(self):
        super().__init__()
        self.name = "CPU"
        self.is_real_hardware = True   # CPU is real, but it's not Snapdragon

    def infer(self, task, payload):
        t0 = time.time()
        target_ms = self.BENCHMARKS.get(task, 100)
        time.sleep(target_ms / 1000.0)
        ms = (time.time() - t0) * 1000
        return {
            "latency_ms": round(ms, 2),
            "compute_unit": "CPU",
            "timing_source": "SIMULATED_CPU",  # honest label
        }


class SnapdragonBackend(InferenceBackend):
    """
    Runs on Snapdragon NPU via Qualcomm AI Hub / qai_appbuilder.

    This is a STUB. It will work when I get a Snapdragon device.
    Until then, it falls back to benchmark-based timing so the
    pipeline can still be tested end-to-end.

    When real hardware is available:
      - replace time.sleep() with real qai_appbuilder.infer() call
      - real timing will be measured by the SDK
    """

    # published benchmarks from Qualcomm AI Hub (Snapdragon X Elite)
    BENCHMARKS = {
        "vision": 180,       # ms on NPU for InternVL3.5-2B
        "reasoning": 200,    # ms on NPU for Qwen3-1.7B
    }

    def __init__(self):
        super().__init__()
        self.name = "Snapdragon NPU"
        self.is_real_hardware = False   # honest: we don't have the hardware

    def infer(self, task, payload):
        t0 = time.time()

        if self.is_real_hardware:
            # production path - not implemented yet
            # from qai_appbuilder import ...
            # result = real_npu_call(task, payload)
            pass
        else:
            # demo path - simulate using published benchmark values
            target_ms = self.BENCHMARKS.get(task, 100)
            time.sleep(target_ms / 1000.0)

        ms = (time.time() - t0) * 1000
        return {
            "latency_ms": round(ms, 2),
            "compute_unit": "NPU",
            "timing_source": "SIMULATED_NPU" if not self.is_real_hardware else "REAL_NPU",
        }


def get_backend(mode):
    """
    Factory. mode = "cpu" or "snapdragon"
    """
    if mode == "cpu":
        return CPUBackend()
    elif mode == "snapdragon":
        return SnapdragonBackend()
    else:
        raise ValueError("Unknown backend mode: " + str(mode))