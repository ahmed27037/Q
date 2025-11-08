"""
Quantum Error Correction (QEC) Module

Real-time quantum error correction decoders with FPGA-optimized processing.
"""

from .decoder import SteaneDecoder, SurfaceCodeDecoder
from .simulator import ErrorSimulator
from .feedback_loop import QECFeedbackLoop

__version__ = "0.1.0"
__all__ = [
    "SteaneDecoder",
    "SurfaceCodeDecoder",
    "ErrorSimulator",
    "QECFeedbackLoop",
]

