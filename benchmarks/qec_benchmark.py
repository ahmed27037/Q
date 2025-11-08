"""
QEC Performance Benchmarks

Benchmarks the performance of quantum error correction decoders,
demonstrating low-latency processing suitable for FPGA implementation.
"""

import time
import numpy as np
from typing import Dict, List
from qec.decoder import SteaneDecoder, SurfaceCodeDecoder
from qec.simulator import ErrorSimulator
from qec.feedback_loop import QECFeedbackLoop


def benchmark_decoder_latency(decoder, num_tests: int = 1000) -> Dict:
    """
    Benchmark decoder latency.
    
    Args:
        decoder: Decoder instance
        num_tests: Number of test cases
        
    Returns:
        Dictionary with timing statistics
    """
    times = []
    
    # Generate random syndromes
    if isinstance(decoder, SteaneDecoder):
        syndrome_size = 6  # 3 X + 3 Z
    else:
        # Surface code (simplified)
        syndrome_size = 8
    
    for _ in range(num_tests):
        # Random syndrome
        syndrome_x = [np.random.randint(0, 2) for _ in range(syndrome_size // 2)]
        syndrome_z = [np.random.randint(0, 2) for _ in range(syndrome_size // 2)]
        
        # Measure decoding time
        start = time.perf_counter()
        correction = decoder.decode(syndrome_x, syndrome_z)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return {
        'mean_us': np.mean(times) * 1e6,
        'std_us': np.std(times) * 1e6,
        'min_us': np.min(times) * 1e6,
        'max_us': np.max(times) * 1e6,
        'median_us': np.median(times) * 1e6,
        'p95_us': np.percentile(times, 95) * 1e6,
        'p99_us': np.percentile(times, 99) * 1e6,
    }


def benchmark_qec_feedback_loop(code_type: str = "steane", 
                                num_cycles: int = 1000,
                                error_rate: float = 0.1) -> Dict:
    """
    Benchmark complete QEC feedback loop.
    
    Args:
        code_type: Type of code
        num_cycles: Number of cycles to run
        error_rate: Error rate
        
    Returns:
        Dictionary with performance statistics
    """
    loop = QECFeedbackLoop(
        code_type=code_type,
        decoder_type=code_type,
        error_rate=error_rate
    )
    
    results = loop.run_multiple_cycles(num_cycles=num_cycles)
    return results


def compare_decoders():
    """Compare different decoder implementations."""
    print("=" * 60)
    print("QEC Decoder Performance Comparison")
    print("=" * 60)
    
    # Steane decoder
    print("\n1. Steane Code Decoder")
    print("-" * 60)
    steane_decoder = SteaneDecoder()
    steane_stats = benchmark_decoder_latency(steane_decoder, num_tests=1000)
    
    print(f"  Mean latency:    {steane_stats['mean_us']:.3f} μs")
    print(f"  Std deviation:   {steane_stats['std_us']:.3f} μs")
    print(f"  Min latency:     {steane_stats['min_us']:.3f} μs")
    print(f"  Max latency:     {steane_stats['max_us']:.3f} μs")
    print(f"  Median latency:  {steane_stats['median_us']:.3f} μs")
    print(f"  95th percentile: {steane_stats['p95_us']:.3f} μs")
    print(f"  99th percentile: {steane_stats['p99_us']:.3f} μs")
    
    # Surface code decoder
    print("\n2. Surface Code Decoder")
    print("-" * 60)
    surface_decoder = SurfaceCodeDecoder(code_size=3)
    surface_stats = benchmark_decoder_latency(surface_decoder, num_tests=1000)
    
    print(f"  Mean latency:    {surface_stats['mean_us']:.3f} μs")
    print(f"  Std deviation:   {surface_stats['std_us']:.3f} μs")
    print(f"  Min latency:     {surface_stats['min_us']:.3f} μs")
    print(f"  Max latency:     {surface_stats['max_us']:.3f} μs")
    print(f"  Median latency:  {surface_stats['median_us']:.3f} μs")
    print(f"  95th percentile: {surface_stats['p95_us']:.3f} μs")
    print(f"  99th percentile: {surface_stats['p99_us']:.3f} μs")
    
    return {
        'steane': steane_stats,
        'surface': surface_stats
    }


def benchmark_feedback_loops():
    """Benchmark complete QEC feedback loops."""
    print("\n" + "=" * 60)
    print("QEC Feedback Loop Performance")
    print("=" * 60)
    
    # Steane code feedback loop
    print("\n1. Steane Code Feedback Loop (1000 cycles)")
    print("-" * 60)
    steane_results = benchmark_qec_feedback_loop(
        code_type="steane",
        num_cycles=1000,
        error_rate=0.1
    )
    
    print(f"  Success rate:           {steane_results['success_rate']:.4f}")
    print(f"  Successful corrections: {steane_results['successful_corrections']}")
    print(f"  Failed corrections:     {steane_results['failed_corrections']}")
    print(f"  Avg decoding time:      {steane_results['avg_decoding_time_us']:.3f} μs")
    print(f"  Min decoding time:      {steane_results['min_decoding_time_us']:.3f} μs")
    print(f"  Max decoding time:      {steane_results['max_decoding_time_us']:.3f} μs")
    
    # Surface code feedback loop
    print("\n2. Surface Code Feedback Loop (1000 cycles)")
    print("-" * 60)
    surface_results = benchmark_qec_feedback_loop(
        code_type="surface",
        num_cycles=1000,
        error_rate=0.1
    )
    
    print(f"  Success rate:           {surface_results['success_rate']:.4f}")
    print(f"  Successful corrections: {surface_results['successful_corrections']}")
    print(f"  Failed corrections:     {surface_results['failed_corrections']}")
    print(f"  Avg decoding time:      {surface_results['avg_decoding_time_us']:.3f} μs")
    print(f"  Min decoding time:      {surface_results['min_decoding_time_us']:.3f} μs")
    print(f"  Max decoding time:      {surface_results['max_decoding_time_us']:.3f} μs")
    
    return {
        'steane': steane_results,
        'surface': surface_results
    }


def run_qec_benchmark_suite():
    """Run complete QEC benchmark suite."""
    print("Running QEC Performance Benchmarks")
    print("=" * 60)
    
    # Compare decoders
    decoder_stats = compare_decoders()
    
    # Benchmark feedback loops
    loop_stats = benchmark_feedback_loops()
    
    print("\n" + "=" * 60)
    print("QEC Benchmark Suite Completed")
    print("=" * 60)
    
    return {
        'decoders': decoder_stats,
        'feedback_loops': loop_stats
    }


if __name__ == "__main__":
    run_qec_benchmark_suite()

