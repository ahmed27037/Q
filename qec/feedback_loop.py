"""
Real-Time Quantum Error Correction Feedback Loop

Implements a feedback loop that simulates real-time error correction with
low-latency processing (simulating FPGA performance).
"""

import time
import numpy as np
from typing import Dict, List, Tuple, Optional
from .decoder import SteaneDecoder, SurfaceCodeDecoder
from .simulator import ErrorSimulator


class QECFeedbackLoop:
    """
    Real-time QEC feedback loop with latency measurements.
    
    This simulates the complete error correction cycle:
    1. Errors occur
    2. Syndrome measurement
    3. Decoder processes syndrome (low latency)
    4. Correction applied
    """
    
    def __init__(self, code_type: str = "steane", decoder_type: str = "steane",
                 error_rate: float = 0.1):
        """
        Initialize QEC feedback loop.
        
        Args:
            code_type: Type of code ("steane" or "surface")
            decoder_type: Type of decoder ("steane" or "surface")
            error_rate: Probability of error per qubit
        """
        self.code_type = code_type
        self.error_rate = error_rate
        
        # Initialize decoder
        if decoder_type == "steane":
            self.decoder = SteaneDecoder()
            code_size = 7
        elif decoder_type == "surface":
            self.decoder = SurfaceCodeDecoder(code_size=3)
            code_size = 9
        else:
            raise ValueError(f"Unknown decoder type: {decoder_type}")
        
        # Initialize error simulator
        self.simulator = ErrorSimulator(
            code_type=code_type,
            code_size=code_size,
            error_rate=error_rate
        )
        
        # Statistics
        self.stats = {
            'total_cycles': 0,
            'successful_corrections': 0,
            'failed_corrections': 0,
            'total_decoding_time': 0.0,
            'min_decoding_time': float('inf'),
            'max_decoding_time': 0.0,
        }
    
    def run_cycle(self) -> Tuple[bool, float]:
        """
        Run one QEC cycle.
        
        Returns:
            Tuple of (success, decoding_time)
        """
        # Introduce errors
        self.simulator.introduce_errors()
        
        # Measure syndrome
        syndrome_x, syndrome_z = self.simulator.measure_syndrome()
        
        # Decode (measure latency)
        start_time = time.perf_counter()
        correction = self.decoder.decode(syndrome_x, syndrome_z)
        decoding_time = time.perf_counter() - start_time
        
        # Apply correction
        success = self.simulator.apply_correction(correction)
        
        # Update statistics
        self.stats['total_cycles'] += 1
        if success:
            self.stats['successful_corrections'] += 1
        else:
            self.stats['failed_corrections'] += 1
        
        self.stats['total_decoding_time'] += decoding_time
        self.stats['min_decoding_time'] = min(self.stats['min_decoding_time'], decoding_time)
        self.stats['max_decoding_time'] = max(self.stats['max_decoding_time'], decoding_time)
        
        return success, decoding_time
    
    def run_multiple_cycles(self, num_cycles: int = 1000) -> Dict:
        """
        Run multiple QEC cycles and collect statistics.
        
        Args:
            num_cycles: Number of cycles to run
            
        Returns:
            Dictionary with statistics
        """
        print(f"Running {num_cycles} QEC cycles...")
        
        for i in range(num_cycles):
            if (i + 1) % 100 == 0:
                print(f"  Completed {i+1}/{num_cycles} cycles")
            self.run_cycle()
        
        # Calculate averages
        avg_decoding_time = self.stats['total_decoding_time'] / self.stats['total_cycles']
        success_rate = self.stats['successful_corrections'] / self.stats['total_cycles']
        
        results = {
            'total_cycles': self.stats['total_cycles'],
            'successful_corrections': self.stats['successful_corrections'],
            'failed_corrections': self.stats['failed_corrections'],
            'success_rate': success_rate,
            'avg_decoding_time_us': avg_decoding_time * 1e6,  # Convert to microseconds
            'min_decoding_time_us': self.stats['min_decoding_time'] * 1e6,
            'max_decoding_time_us': self.stats['max_decoding_time'] * 1e6,
        }
        
        return results
    
    def reset(self):
        """Reset the feedback loop."""
        self.simulator.reset()
        self.stats = {
            'total_cycles': 0,
            'successful_corrections': 0,
            'failed_corrections': 0,
            'total_decoding_time': 0.0,
            'min_decoding_time': float('inf'),
            'max_decoding_time': 0.0,
        }
    
    def get_statistics(self) -> Dict:
        """Get current statistics."""
        if self.stats['total_cycles'] == 0:
            return self.stats.copy()
        
        avg_decoding_time = self.stats['total_decoding_time'] / self.stats['total_cycles']
        success_rate = self.stats['successful_corrections'] / self.stats['total_cycles']
        
        return {
            **self.stats,
            'success_rate': success_rate,
            'avg_decoding_time_us': avg_decoding_time * 1e6,
            'min_decoding_time_us': self.stats['min_decoding_time'] * 1e6,
            'max_decoding_time_us': self.stats['max_decoding_time'] * 1e6,
        }

