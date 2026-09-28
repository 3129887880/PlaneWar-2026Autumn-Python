# export_pdf.ps1
# Export the newest Jupyter notebook in this folder to PDF.
#
# Pipeline: notebook -> HTML (nbconvert) -> PDF (headless Microsoft Edge).
# No LaTeX is required, and the cells are NOT executed during export.
#
# One-time setup of the converter environment (already done on this machine):
#   C:\python\python.exe -m venv "$env:USERPROFILE\.report-export-venv"
#   "$env:USERPROFILE\.report-export-venv\Scripts\python.exe" -m pip install nbconvert

$ErrorActionPreference = 'Stop'

$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py  = Join-Path $env:USERPROFILE '.report-export-venv\Scripts\python.exe'

if (-not (Test-Path $py)) {
    Write-Host "Converter environment not found:" -ForegroundColor Red
    Write-Host "  $py"
    Write-Host "Create it once, then run this script again:"
    Write-Host "  C:\python\python.exe -m venv `"$env:USERPROFILE\.report-export-venv`""
    Write-Host "  `"$env:USERPROFILE\.report-export-venv\Scripts\python.exe`" -m pip install nbconvert"
    exit 1
}

# The newest notebook wins, so the backup copy is never picked by accident.
$nb = Get-ChildItem -Path $dir -Filter *.ipynb |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 1
if (-not $nb) {
    Write-Host "No .ipynb file found in $dir" -ForegroundColor Red
    exit 1
}
Write-Host "Notebook : $($nb.Name)"

# Step 1: notebook -> HTML
$htmlName = 'plane_report'
& $py -m nbconvert --to html --output-dir=$dir --output=$htmlName $nb.FullName
if ($LASTEXITCODE -ne 0) {
    Write-Host "nbconvert failed." -ForegroundColor Red
    exit 1
}
$html = Join-Path $dir "$htmlName.html"

# Step 2: HTML -> PDF with headless Edge
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if (-not (Test-Path $edge)) {
    $edge = 'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
}
if (-not (Test-Path $edge)) {
    Write-Host "Microsoft Edge not found." -ForegroundColor Red
    exit 1
}

$tmp = Join-Path $env:TEMP 'plane_report.pdf'
$out = Join-Path $dir ($nb.BaseName + '.pdf')
$url = 'file:///' + ($html -replace '\\', '/')

& $edge --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 --print-to-pdf="$tmp" $url | Out-Null

if (-not (Test-Path $tmp)) {
    Write-Host "Edge did not produce a PDF." -ForegroundColor Red
    exit 1
}

Copy-Item $tmp $out -Force
Remove-Item $tmp  -Force
Remove-Item $html -Force

Write-Host "PDF done : $out" -ForegroundColor Green
