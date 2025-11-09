# PowerShell script to generate PNG diagrams from Mermaid files
# Requires: npm install -g @mermaid-js/mermaid-cli

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Diagram PNG Generator" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if mmdc is installed
try {
    $null = Get-Command mmdc -ErrorAction Stop
    Write-Host "✓ Mermaid CLI found" -ForegroundColor Green
} catch {
    Write-Host "✗ Mermaid CLI not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install it first:" -ForegroundColor Yellow
    Write-Host "  npm install -g @mermaid-js/mermaid-cli" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Change to the diagrams directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Define diagrams to generate
$diagrams = @(
    @{Name="System Architecture"; File="system_architecture"},
    @{Name="Hardware-Software Integration"; File="hardware_software_integration"},
    @{Name="Circuit Execution Flow"; File="circuit_execution_flow"},
    @{Name="QEC Feedback Loop"; File="qec_feedback"}
)

$success = 0
$failed = 0

foreach ($diagram in $diagrams) {
    Write-Host "Generating: $($diagram.Name)..." -ForegroundColor Yellow
    
    $inputFile = "$($diagram.File).mmd"
    $outputFile = "$($diagram.File).png"
    
    try {
        $output = & mmdc -i $inputFile -o $outputFile -b transparent 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Success: $outputFile" -ForegroundColor Green
            $success++
        } else {
            Write-Host "  ✗ Failed: $($diagram.Name)" -ForegroundColor Red
            Write-Host "    $output" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "  ✗ Error: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Generated: $success" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($success -gt 0) {
    Write-Host "PNG files saved in: $scriptPath" -ForegroundColor Cyan
    Write-Host "These files are gitignored and won't be committed." -ForegroundColor Yellow
}

