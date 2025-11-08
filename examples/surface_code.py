"""
Surface Code QEC Demo

Demonstrates quantum error correction using the surface code.
"""

import numpy as np
from qec.decoder import SurfaceCodeDecoder
from qec.simulator import ErrorSimulator
from qec.feedback_loop import QECFeedbackLoop


def demo_surface_code():
    """Demonstrate surface code QEC."""
    print("=" * 60)
    print("Surface Code Quantum Error Correction Demo")
    print("=" * 60)
    
    # Create decoder and simulator
    decoder = SurfaceCodeDecoder(code_size=3)
    simulator = ErrorSimulator(code_type="surface", code_size=3, error_rate=0.1)
    
    print("\n1. Simulating errors...")
    errors = simulator.introduce_errors()
    print(f"  X errors on qubits: {errors['x']}")
    print(f"  Z errors on qubits: {errors['z']}")
    
    print("\n2. Measuring syndrome...")
    syndrome_x, syndrome_z = simulator.measure_syndrome()
    print(f"  X stabilizer syndrome: {syndrome_x}")
    print(f"  Z stabilizer syndrome: {syndrome_z}")
    
    print("\n3. Decoding syndrome...")
    correction = decoder.decode(syndrome_x, syndrome_z)
    print(f"  X corrections on qubits: {correction['x']}")
    print(f"  Z corrections on qubits: {correction['z']}")
    
    print("\n4. Applying corrections...")
    success = simulator.apply_correction(correction)
    print(f"  Correction successful: {success}")
    
    print("\n5. Remaining errors:")
    print(f"  X errors: {simulator.errors['x']}")
    print(f"  Z errors: {simulator.errors['z']}")
    
    return success


def demo_feedback_loop():
    """Demonstrate QEC feedback loop."""
    print("\n" + "=" * 60)
    print("QEC Feedback Loop Demo")
    print("=" * 60)
    
    loop = QECFeedbackLoop(
        code_type="surface",
        decoder_type="surface",
        error_rate=0.1
    )
    
    print("\nRunning 100 QEC cycles...")
    results = loop.run_multiple_cycles(num_cycles=100)
    
    print("\nResults:")
    print(f"  Total cycles:           {results['total_cycles']}")
    print(f"  Successful corrections: {results['successful_corrections']}")
    print(f"  Failed corrections:     {results['failed_corrections']}")
    print(f"  Success rate:           {results['success_rate']:.4f}")
    print(f"  Avg decoding time:      {results['avg_decoding_time_us']:.3f} μs")
    print(f"  Min decoding time:      {results['min_decoding_time_us']:.3f} μs")
    print(f"  Max decoding time:      {results['max_decoding_time_us']:.3f} μs")
    
    return results


if __name__ == "__main__":
    demo_surface_code()
    demo_feedback_loop()

