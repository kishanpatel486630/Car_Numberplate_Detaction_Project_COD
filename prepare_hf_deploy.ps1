# Hugging Face Spaces Deployment - Quick Setup Script
# Run this to prepare all files for upload

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HUGGING FACE SPACES - FILE PREP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create HF deployment folder
$hfFolder = "hf_deployment"
Write-Host "[1/6] Creating deployment folder..." -ForegroundColor Yellow
if (Test-Path $hfFolder) {
    Remove-Item $hfFolder -Recurse -Force
}
New-Item -ItemType Directory -Path $hfFolder | Out-Null

# Copy and rename files
Write-Host "[2/6] Copying app.py..." -ForegroundColor Yellow
Copy-Item "app_hf.py" "$hfFolder/app.py"

Write-Host "[3/6] Copying requirements.txt..." -ForegroundColor Yellow
Copy-Item "requirements-hf.txt" "$hfFolder/requirements.txt"

Write-Host "[4/6] Copying README.md..." -ForegroundColor Yellow
Copy-Item "README_HF.md" "$hfFolder/README.md"

Write-Host "[5/6] Copying utility files..." -ForegroundColor Yellow
Copy-Item "util.py" "$hfFolder/"
if (Test-Path "license_plate_detector.pt") {
    Copy-Item "license_plate_detector.pt" "$hfFolder/"
    Write-Host "   - license_plate_detector.pt copied" -ForegroundColor Green
} else {
    Write-Host "   - license_plate_detector.pt not found (upload manually)" -ForegroundColor Yellow
}

Write-Host "[6/6] Copying sort folder..." -ForegroundColor Yellow
Copy-Item "sort" "$hfFolder/sort" -Recurse

Write-Host ""
Write-Host "All files prepared successfully!" -ForegroundColor Green
Write-Host ""

# Show folder contents
Write-Host "Files ready for upload:" -ForegroundColor Cyan
Get-ChildItem $hfFolder -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Replace((Get-Location).Path + "\$hfFolder\", "")
    Write-Host "   * $relativePath" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Go to: https://huggingface.co/new-space" -ForegroundColor White
Write-Host "2. Create a new Space:" -ForegroundColor White
Write-Host "   - Name: platevision-ai" -ForegroundColor Gray
Write-Host "   - SDK: Streamlit" -ForegroundColor Gray
Write-Host "   - Hardware: CPU basic (free)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Upload all files from 'hf_deployment' folder" -ForegroundColor White
Write-Host ""
Write-Host "4. Your app will be live at:" -ForegroundColor White
Write-Host "   https://huggingface.co/spaces/YOUR_USERNAME/platevision-ai" -ForegroundColor Cyan
Write-Host ""

Write-Host "Full guide: See DEPLOYMENT_GUIDE_HF.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
