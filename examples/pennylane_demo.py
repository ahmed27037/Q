"""
PennyLane Integration Demo

Demonstrates using the FPGA simulator as a PennyLane device.
"""

import pennylane as qml
import numpy as np
from pennylane_device import FPGADevice


def demo_basic_circuit():
    """Basic PennyLane circuit using FPGA device."""
    print("=" * 60)
    print("PennyLane Basic Circuit Demo")
    print("=" * 60)
    
    # Create device
    dev = FPGADevice(wires=2, use_jax=True)
    
    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.state()
    
    # Execute
    state = circuit()
    print("\nFinal statevector:")
    print(state)
    
    # Probability distribution
    @qml.qnode(dev)
    def circuit_prob():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.probs(wires=[0, 1])
    
    probs = circuit_prob()
    print("\nMeasurement probabilities:")
    states = ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]
    for s, p in zip(states, probs):
        print(f"  {s}: {p:.4f}")


def demo_expectation_value():
    """Demonstrate expectation value computation."""
    print("\n" + "=" * 60)
    print("PennyLane Expectation Value Demo")
    print("=" * 60)
    
    dev = FPGADevice(wires=2, use_jax=True)
    
    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(0))
    
    expval = circuit()
    print(f"\n<Z₀> = {expval:.4f}")


def demo_parameterized_circuit():
    """Demonstrate parameterized circuits."""
    print("\n" + "=" * 60)
    print("PennyLane Parameterized Circuit Demo")
    print("=" * 60)
    
    dev = FPGADevice(wires=2, use_jax=True)
    
    @qml.qnode(dev)
    def circuit(theta):
        qml.RY(theta, wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(1))
    
    # Test different angles
    angles = [0, np.pi/4, np.pi/2, np.pi]
    print("\nExpectation values for different angles:")
    for theta in angles:
        expval = circuit(theta)
        print(f"  θ = {theta:.3f}: <Z₁> = {expval:.4f}")


if __name__ == "__main__":
    demo_basic_circuit()
    demo_expectation_value()
    demo_parameterized_circuit()

