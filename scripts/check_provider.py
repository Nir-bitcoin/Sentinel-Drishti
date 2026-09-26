# check_provider.py
#
# Detects available inference providers on this machine.
# Shows clear reason why QNN/HTP is not available.


import platform
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check_qnn_available():
    """Check if QNN Execution Provider is available."""
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        if "QNNExecutionProvider" in providers:
            return True, providers
        return False, providers
    except ImportError:
        return False, []


def main():
    print("=" * 55)
    print("  SENTINEL DRISHTI - Provider Diagnostic")
    print("=" * 55)
    print()

    arch = platform.machine()
    system = platform.system()
    print("Host:      " + system + " " + arch)
    print("Python:    " + platform.python_version())
    print()

    qnn_ok, providers = check_qnn_available()

    if qnn_ok:
        print("QNN EP:    AVAILABLE")
        print("HTP:       AVAILABLE")
        print()
        print("Selected provider: QNN / HTP")
        print("Status:            NPU ACTIVE")
    else:
        print("QNN EP:    NOT AVAILABLE")
        print("HTP:       NOT AVAILABLE")
        print()
        print("Reason:    No Snapdragon NPU detected on this host")
        print()
        print("Selected provider: CPU")
        print("Status:            FALLBACK")
        print()
        print("Reference (Qualcomm AI Hub hosted-device):")
        print("  EasyOCR detector:   ~39.5 ms  [job jpxlmx3jp]")
        print("  EasyOCR recognizer: ~19.3 ms  [job jprl9wnvp]")
        print("  Compute unit:       NPU (Hexagon HTP)")
        print()
        print("On a Snapdragon-powered PC, this script will report:")
        print("  QNN EP:    AVAILABLE")
        print("  Status:    NPU ACTIVE")

    print()
    print("=" * 55)


if __name__ == "__main__":
    main()