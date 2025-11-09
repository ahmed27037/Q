# Project Diagrams

This directory contains **Mermaid diagram source files** (`.mmd`) that visualize the project architecture.

## 🎯 Quick Start

### Option 1: HTML Viewer (Easiest - No Install!)

**Just double-click:**
```
view_diagrams.html
```

Then use **Windows Snipping Tool** (`Win + Shift + S`) to screenshot each diagram and save as PNG!

---

### Option 2: Automated CLI (Best Quality)

**Install Mermaid CLI once:**
```powershell
npm install -g @mermaid-js/mermaid-cli
```

**Generate all PNGs:**
```powershell
cd C:\Users\YOUR_USERNAME\Documents\next_gen\Q\docs\diagrams
.\generate_pngs.ps1
```

This creates PNG files in this directory that are **automatically gitignored**.

---

### Option 3: Online (Alternative)

1. Go to https://mermaid.live
2. Copy content from any `.mmd` file below
3. Click download PNG button

---

## 📊 Available Diagrams

### 1. **system_architecture.mmd**
Shows the three-layer architecture: User → PennyLane → Python/FPGA backends

### 2. **hardware_software_integration.mmd**
Detailed view of how PennyLane, Python simulator, and FPGA hardware integrate

### 3. **circuit_execution_flow.mmd**
Sequence diagram showing quantum circuit execution through JAX

### 4. **qec_feedback.mmd** 
Quantum error correction feedback loop diagram

---

## 📝 Note About PNG Files

- **PNG files are NOT committed to Git** (see `.gitignore`)
- Generate them locally when you need them
- This keeps the repo small and avoids binary file bloat
- PNGs are for presentations, documentation, etc.

---

## 🔄 Updating Diagrams

1. Edit the `.mmd` files
2. Re-run `.\generate_pngs.ps1`
3. Use the new PNGs locally

Commit only the `.mmd` source files, not the generated PNGs!

Double-click: docs\diagrams\view_diagrams.bat
Then screenshot with: Win + Shift + S