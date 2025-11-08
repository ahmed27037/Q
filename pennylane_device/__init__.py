"""
PennyLane Device Plugin for FPGA Simulator

Enables seamless integration of the FPGA-accelerated simulator with PennyLane.
"""

from .fpga_device import FPGADevice

__version__ = "0.1.0"
__all__ = ["FPGADevice"]

# Register device with PennyLane
try:
    import pennylane as qml
    qml.register_device(FPGADevice, short_name="fpga.simulator", name="FPGA Simulator")
except ImportError:
    pass  # PennyLane not available

