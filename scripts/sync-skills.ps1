[CmdletBinding()]
param(
    [ValidateSet('Agents', 'Codex', 'Both')]
    [string]$Target = 'Both'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$SourceRoot = Join-Path $RepoRoot 'skills'

if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
    throw "Could not find skills directory: $SourceRoot"
}

function Sync-SkillRoot {
    param([Parameter(Mandatory = $true)][string]$Destination)

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $packages = Get-ChildItem -LiteralPath $SourceRoot -Directory
    $skills = $packages |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf }

    foreach ($package in $packages) {
        Copy-Item -LiteralPath $package.FullName -Destination (Join-Path $Destination $package.Name) -Recurse -Force
    }

    Write-Host "Synced $($skills.Count) skills -> $Destination"
}

if ($Target -in @('Agents', 'Both')) {
    Sync-SkillRoot (Join-Path $HOME '.agents\skills')
}
if ($Target -in @('Codex', 'Both')) {
    Sync-SkillRoot (Join-Path $HOME '.codex\skills')
}

Write-Host 'Restart Codex or start a new session to refresh its skill inventory.'
