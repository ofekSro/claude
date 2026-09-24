# Copies agents/ and skills/ into ~/.claude so they are available in every project.
$ErrorActionPreference = "Stop"
$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$dst = Join-Path $env:USERPROFILE ".claude"

New-Item -ItemType Directory -Force (Join-Path $dst "agents") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $dst "skills") | Out-Null

Copy-Item (Join-Path $src "agents\*.md") (Join-Path $dst "agents") -Force
Get-ChildItem (Join-Path $src "skills") -Directory | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $dst "skills") -Recurse -Force
}

Write-Host "Installed to $dst"
Write-Host "Agents:" (Get-ChildItem (Join-Path $src "agents") -Filter *.md | ForEach-Object { $_.BaseName }) -Separator " "
Write-Host "Skills:" (Get-ChildItem (Join-Path $src "skills") -Directory | ForEach-Object { $_.Name }) -Separator " "
