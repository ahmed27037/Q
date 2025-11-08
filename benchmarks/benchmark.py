"""
Performance Benchmark Suite

Compares the FPGA simulator performance against CPU-only implementations
(Qiskit and NumPy) to demonstrate speedup achieved through parallel processing.
"""

import time
import numpy as np
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from simulator.circuit import QuantumCircuit
from simulator import quantum_gates

# Try to import Qiskit for comparison
try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit.quantum_info import Statevector
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not available. Qiskit benchmarks will be skipped.")


def benchmark_bell_state(num_qubits: int = 2, num_runs: int = 100) -> Dict[str, float]:
    """
    Benchmark Bell state creation: |00⟩ + |11⟩
    
    Args:
        num_qubits: Number of qubits (should be 2 for Bell state)
        num_runs: Number of runs to average
        
    Returns:
        Dictionary with timing results
    """
    results = {}
    
    # FPGA Simulator (JAX)
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        circuit = QuantumCircuit(num_qubits, use_jax=True)
        circuit.h(0)
        circuit.cnot(0, 1)
        state = circuit.execute()
        times.append(time.perf_counter() - start)
    results['fpga_jax'] = np.mean(times)
    results['fpga_jax_std'] = np.std(times)
    
    # FPGA Simulator (NumPy fallback)
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        circuit = QuantumCircuit(num_qubits, use_jax=False)
        circuit.h(0)
        circuit.cnot(0, 1)
        state = circuit.execute()
        times.append(time.perf_counter() - start)
    results['fpga_numpy'] = np.mean(times)
    results['fpga_numpy_std'] = np.std(times)
    
    # Qiskit comparison
    if QISKIT_AVAILABLE:
        times = []
        for _ in range(num_runs):
            start = time.perf_counter()
            qc = QiskitCircuit(num_qubits)
            qc.h(0)
            qc.cx(0, 1)
            state = Statevector.from_instruction(qc)
            times.append(time.perf_counter() - start)
        results['qiskit'] = np.mean(times)
        results['qiskit_std'] = np.std(times)
    
    return results


def benchmark_ghz_state(num_qubits: int, num_runs: int = 50) -> Dict[str, float]:
    """
    Benchmark GHZ state creation: |00...0⟩ + |11...1⟩
    
    Args:
        num_qubits: Number of qubits
        num_runs: Number of runs to average
        
    Returns:
        Dictionary with timing results
    """
    results = {}
    
    # FPGA Simulator (JAX)
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        circuit = QuantumCircuit(num_qubits, use_jax=True)
        circuit.h(0)
        for i in range(num_qubits - 1):
            circuit.cnot(i, i + 1)
        state = circuit.execute()
        times.append(time.perf_counter() - start)
    results['fpga_jax'] = np.mean(times)
    results['fpga_jax_std'] = np.std(times)
    
    # FPGA Simulator (NumPy fallback)
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        circuit = QuantumCircuit(num_qubits, use_jax=False)
        circuit.h(0)
        for i in range(num_qubits - 1):
            circuit.cnot(i, i + 1)
        state = circuit.execute()
        times.append(time.perf_counter() - start)
    results['fpga_numpy'] = np.mean(times)
    results['fpga_numpy_std'] = np.std(times)
    
    # Qiskit comparison
    if QISKIT_AVAILABLE:
        times = []
        for _ in range(num_runs):
            start = time.perf_counter()
            qc = QiskitCircuit(num_qubits)
            qc.h(0)
            for i in range(num_qubits - 1):
                qc.cx(i, i + 1)
            state = Statevector.from_instruction(qc)
            times.append(time.perf_counter() - start)
        results['qiskit'] = np.mean(times)
        results['qiskit_std'] = np.std(times)
    
    return results


def benchmark_random_circuit(num_qubits: int, depth: int, num_runs: int = 20) -> Dict[str, float]:
    """
    Benchmark random quantum circuit.
    
    Args:
        num_qubits: Number of qubits
        depth: Circuit depth (number of layers)
        num_runs: Number of runs to average
        
    Returns:
        Dictionary with timing results
    """
    np.random.seed(42)  # For reproducibility
    results = {}
    
    # Generate random circuit pattern
    gates_single = [quantum_gates.H, quantum_gates.X, quantum_gates.Y, quantum_gates.Z, 
                    quantum_gates.S, quantum_gates.T]
    
    # FPGA Simulator (JAX)
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        circuit = QuantumCircuit(num_qubits, use_jax=True)
        for d in range(depth):
            # Apply random single-qubit gates
            for q in range(num_qubits):
                gate = np.random.choice(gates_single)
                circuit.apply(gate, q)
            # Apply random CNOTs
            if num_qubits > 1:
                for _ in range(num_qubits // 2):
                    ctrl = np.random.randint(num_qubits)
                    target = np.random.randint(num_qubits)
                    if ctrl != target:
                        circuit.cnot(ctrl, target)
        state = circuit.execute()
        times.append(time.perf_counter() - start)
    results['fpga_jax'] = np.mean(times)
    results['fpga_jax_std'] = np.std(times)
    
    # FPGA Simulator (NumPy fallback)
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        circuit = QuantumCircuit(num_qubits, use_jax=False)
        for d in range(depth):
            for q in range(num_qubits):
                gate = np.random.choice(gates_single)
                circuit.apply(gate, q)
            if num_qubits > 1:
                for _ in range(num_qubits // 2):
                    ctrl = np.random.randint(num_qubits)
                    target = np.random.randint(num_qubits)
                    if ctrl != target:
                        circuit.cnot(ctrl, target)
        state = circuit.execute()
        times.append(time.perf_counter() - start)
    results['fpga_numpy'] = np.mean(times)
    results['fpga_numpy_std'] = np.std(times)
    
    # Qiskit comparison
    if QISKIT_AVAILABLE:
        times = []
        for _ in range(num_runs):
            start = time.perf_counter()
            qc = QiskitCircuit(num_qubits)
            for d in range(depth):
                for q in range(num_qubits):
                    gate_name = np.random.choice(['h', 'x', 'y', 'z', 's', 't'])
                    getattr(qc, gate_name)(q)
                if num_qubits > 1:
                    for _ in range(num_qubits // 2):
                        ctrl = np.random.randint(num_qubits)
                        target = np.random.randint(num_qubits)
                        if ctrl != target:
                            qc.cx(ctrl, target)
            state = Statevector.from_instruction(qc)
            times.append(time.perf_counter() - start)
        results['qiskit'] = np.mean(times)
        results['qiskit_std'] = np.std(times)
    
    return results


def run_benchmark_suite(max_qubits: int = 8) -> Dict:
    """
    Run comprehensive benchmark suite.
    
    Args:
        max_qubits: Maximum number of qubits to test
        
    Returns:
        Dictionary with all benchmark results
    """
    print("Running FPGA Simulator Benchmark Suite")
    print("=" * 60)
    
    all_results = {}
    
    # Bell state benchmark
    print("\n1. Bell State Benchmark (2 qubits)")
    print("-" * 60)
    bell_results = benchmark_bell_state(num_qubits=2, num_runs=100)
    all_results['bell_state'] = bell_results
    print(f"FPGA (JAX):     {bell_results['fpga_jax']*1000:.3f} ms ± {bell_results['fpga_jax_std']*1000:.3f} ms")
    print(f"FPGA (NumPy):   {bell_results['fpga_numpy']*1000:.3f} ms ± {bell_results['fpga_numpy_std']*1000:.3f} ms")
    if QISKIT_AVAILABLE and 'qiskit' in bell_results:
        print(f"Qiskit:         {bell_results['qiskit']*1000:.3f} ms ± {bell_results['qiskit_std']*1000:.3f} ms")
        speedup = bell_results['qiskit'] / bell_results['fpga_jax']
        print(f"Speedup (JAX vs Qiskit): {speedup:.2f}x")
    
    # GHZ state scaling
    print("\n2. GHZ State Scaling Benchmark")
    print("-" * 60)
    ghz_results = {}
    for n in range(3, min(max_qubits + 1, 9)):
        print(f"Testing {n} qubits...", end=" ")
        result = benchmark_ghz_state(num_qubits=n, num_runs=30)
        ghz_results[n] = result
        print(f"JAX: {result['fpga_jax']*1000:.3f} ms")
    all_results['ghz_scaling'] = ghz_results
    
    # Random circuit benchmark
    print("\n3. Random Circuit Benchmark")
    print("-" * 60)
    random_results = {}
    for n in range(3, min(max_qubits + 1, 9)):
        print(f"Testing {n} qubits, depth 5...", end=" ")
        result = benchmark_random_circuit(num_qubits=n, depth=5, num_runs=10)
        random_results[n] = result
        print(f"JAX: {result['fpga_jax']*1000:.3f} ms")
    all_results['random_circuit'] = random_results
    
    print("\n" + "=" * 60)
    print("Benchmark suite completed!")
    
    return all_results


def plot_benchmark_results(results: Dict, save_path: str = "benchmarks/benchmark_results.png"):
    """
    Plot benchmark results.
    
    Args:
        results: Dictionary with benchmark results
        save_path: Path to save the plot
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # GHZ scaling plot
    if 'ghz_scaling' in results:
        ax1 = axes[0]
        qubit_counts = sorted(results['ghz_scaling'].keys())
        jax_times = [results['ghz_scaling'][n]['fpga_jax'] * 1000 for n in qubit_counts]
        numpy_times = [results['ghz_scaling'][n]['fpga_numpy'] * 1000 for n in qubit_counts]
        
        ax1.plot(qubit_counts, jax_times, 'o-', label='FPGA Simulator (JAX)', linewidth=2)
        ax1.plot(qubit_counts, numpy_times, 's--', label='FPGA Simulator (NumPy)', linewidth=2)
        
        if QISKIT_AVAILABLE:
            qiskit_times = [results['ghz_scaling'][n].get('qiskit', 0) * 1000 for n in qubit_counts]
            if any(t > 0 for t in qiskit_times):
                ax1.plot(qubit_counts, qiskit_times, '^-.', label='Qiskit', linewidth=2)
        
        ax1.set_xlabel('Number of Qubits', fontsize=12)
        ax1.set_ylabel('Time (ms)', fontsize=12)
        ax1.set_title('GHZ State Creation Scaling', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
    
    # Random circuit plot
    if 'random_circuit' in results:
        ax2 = axes[1]
        qubit_counts = sorted(results['random_circuit'].keys())
        jax_times = [results['random_circuit'][n]['fpga_jax'] * 1000 for n in qubit_counts]
        numpy_times = [results['random_circuit'][n]['fpga_numpy'] * 1000 for n in qubit_counts]
        
        ax2.plot(qubit_counts, jax_times, 'o-', label='FPGA Simulator (JAX)', linewidth=2)
        ax2.plot(qubit_counts, numpy_times, 's--', label='FPGA Simulator (NumPy)', linewidth=2)
        
        if QISKIT_AVAILABLE:
            qiskit_times = [results['random_circuit'][n].get('qiskit', 0) * 1000 for n in qubit_counts]
            if any(t > 0 for t in qiskit_times):
                ax2.plot(qubit_counts, qiskit_times, '^-.', label='Qiskit', linewidth=2)
        
        ax2.set_xlabel('Number of Qubits', fontsize=12)
        ax2.set_ylabel('Time (ms)', fontsize=12)
        ax2.set_title('Random Circuit (Depth=5)', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\nBenchmark plots saved to {save_path}")


if __name__ == "__main__":
    results = run_benchmark_suite(max_qubits=7)
    plot_benchmark_results(results)

