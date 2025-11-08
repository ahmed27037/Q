"""
Quantum Machine Learning Classifier Demo

Demonstrates a quantum machine learning classifier using PennyLane
and the FPGA simulator, showcasing quantum kernel methods.
"""

import numpy as np
import pennylane as qml
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from pennylane_device import FPGADevice


def quantum_kernel(x1, x2, n_qubits=2, n_layers=2):
    """
    Compute quantum kernel between two data points.
    
    Uses a parameterized quantum circuit to encode data and compute
    the overlap between encoded states.
    
    Args:
        x1, x2: Data points
        n_qubits: Number of qubits
        n_layers: Number of encoding layers
        
    Returns:
        Kernel value
    """
    dev = FPGADevice(wires=n_qubits, use_jax=True)
    
    @qml.qnode(dev)
    def kernel_circuit(x1, x2):
        # Encode x1
        for layer in range(n_layers):
            for i in range(n_qubits):
                qml.RY(x1[i % len(x1)] * np.pi, wires=i)
                if i < n_qubits - 1:
                    qml.CNOT(wires=[i, i+1])
        
        # Encode x2 (inverse)
        for layer in range(n_layers):
            for i in range(n_qubits - 1, -1, -1):
                if i < n_qubits - 1:
                    qml.CNOT(wires=[i, i+1])
                qml.RY(-x2[i % len(x2)] * np.pi, wires=i)
        
        # Measure overlap
        return qml.probs(wires=list(range(n_qubits)))
    
    # Compute overlap (probability of |00...0⟩)
    probs = kernel_circuit(x1, x2)
    return probs[0]  # Return probability of all zeros


def create_quantum_kernel_matrix(X, n_qubits=2, n_layers=2):
    """
    Create quantum kernel matrix for dataset.
    
    Args:
        X: Dataset (n_samples, n_features)
        n_qubits: Number of qubits
        n_layers: Number of encoding layers
        
    Returns:
        Kernel matrix (n_samples, n_samples)
    """
    n_samples = X.shape[0]
    kernel_matrix = np.zeros((n_samples, n_samples))
    
    print("Computing quantum kernel matrix...")
    for i in range(n_samples):
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{n_samples} samples")
        for j in range(i, n_samples):
            kernel_val = quantum_kernel(X[i], X[j], n_qubits, n_layers)
            kernel_matrix[i, j] = kernel_val
            kernel_matrix[j, i] = kernel_val
    
    return kernel_matrix


def run_qml_classifier_demo():
    """Run quantum machine learning classifier demonstration."""
    print("=" * 60)
    print("Quantum Machine Learning Classifier Demo")
    print("=" * 60)
    
    # Generate synthetic dataset
    print("\n1. Generating synthetic dataset...")
    X, y = make_classification(
        n_samples=50,
        n_features=4,
        n_informative=2,
        n_redundant=0,
        n_classes=2,
        random_state=42
    )
    
    # Normalize features
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    print(f"  Training samples: {X_train.shape[0]}")
    print(f"  Test samples: {X_test.shape[0]}")
    
    # Compute quantum kernel matrix
    print("\n2. Computing quantum kernel matrix...")
    n_qubits = 2
    n_layers = 2
    
    # For demonstration, use subset for kernel computation
    # (Full kernel computation can be slow)
    X_train_subset = X_train[:20]  # Use subset for speed
    kernel_train = create_quantum_kernel_matrix(
        X_train_subset, n_qubits=n_qubits, n_layers=n_layers
    )
    
    # Train SVM with quantum kernel
    print("\n3. Training SVM classifier with quantum kernel...")
    svm = SVC(kernel='precomputed')
    svm.fit(kernel_train, y_train[:20])
    
    # Compute test kernel
    print("\n4. Computing test kernel...")
    kernel_test = np.zeros((X_test.shape[0], X_train_subset.shape[0]))
    for i in range(X_test.shape[0]):
        for j in range(X_train_subset.shape[0]):
            kernel_test[i, j] = quantum_kernel(
                X_test[i], X_train_subset[j], n_qubits, n_layers
            )
    
    # Predict
    y_pred = svm.predict(kernel_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n5. Results:")
    print(f"  Test accuracy: {accuracy:.4f}")
    print(f"  Number of support vectors: {svm.n_support_}")
    
    # Compare with classical RBF kernel
    print("\n6. Comparing with classical RBF kernel...")
    svm_classical = SVC(kernel='rbf', gamma='scale')
    svm_classical.fit(X_train, y_train)
    y_pred_classical = svm_classical.predict(X_test)
    accuracy_classical = accuracy_score(y_test, y_pred_classical)
    
    print(f"  Classical RBF accuracy: {accuracy_classical:.4f}")
    print(f"  Quantum kernel accuracy: {accuracy:.4f}")
    
    return accuracy, accuracy_classical


if __name__ == "__main__":
    run_qml_classifier_demo()

