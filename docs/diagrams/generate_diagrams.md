# Generate PNG Diagrams

## Method 1: Using Mermaid CLI (Recommended)

### Install Mermaid CLI:
```bash
npm install -g @mermaid-js/mermaid-cli
```

### Generate all diagrams:

**PowerShell:**
```powershell
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\docs\diagrams

# System Architecture
mmdc -i system_architecture.mmd -o system_architecture.png

# Hardware-Software Integration
mmdc -i hardware_software_integration.mmd -o hardware_software_integration.png

# Circuit Execution Flow
mmdc -i circuit_execution_flow.mmd -o circuit_execution_flow.png

# QEC Feedback Loop
mmdc -i qec_feedback.mmd -o qec_feedback.png
```

## Method 2: Online (Quick)

1. Go to: https://mermaid.live
2. Copy diagram code from `.mmd` files below
3. Click "Actions" → "PNG" → Download

## Method 3: VS Code Extension

1. Install "Markdown Preview Mermaid Support" extension
2. Open any `.mmd` file
3. Right-click diagram → "Export as PNG"

---

## Diagram Files are in this directory

All `.mmd` files contain the Mermaid code.
Run the commands above to generate `.png` files (which are gitignored).

