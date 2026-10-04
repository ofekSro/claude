# Copies agents/ and skills/ (and thesis-writing/agents, thesis-writing/skills) into ~/.claude
# so they are available in every project.
$ErrorActionPreference = "Stop"
$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$dst = Join-Path $env:USERPROFILE ".claude"
$roots = @($src, (Join-Path $src "thesis-writing"))

New-Item -ItemType Directory -Force (Join-Path $dst "agents") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $dst "skills") | Out-Null

$agents = @(); $skills = @()
foreach ($r in $roots) {
    $a = Join-Path $r "agents"
    $s = Join-Path $r "skills"
    if (Test-Path $a) {
        Copy-Item (Join-Path $a "*.md") (Join-Path $dst "agents") -Force
        $agents += Get-ChildItem $a -Filter *.md | ForEach-Object { $_.BaseName }
    }
    if (Test-Path $s) {
        Get-ChildItem $s -Directory | ForEach-Object {
            Copy-Item $_.FullName (Join-Path $dst "skills") -Recurse -Force
            $skills += $_.Name
        }
    }
}

Write-Host "Installed to $dst"
Write-Host "Agents:" ($agents | Sort-Object) -Separator " "
Write-Host "Skills:" ($skills | Sort-Object) -Separator " "
