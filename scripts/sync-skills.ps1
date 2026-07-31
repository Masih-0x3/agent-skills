[CmdletBinding()]
param(
    [ValidateSet('Agents', 'Codex', 'Both', 'All', 'Claude', 'Grok', 'Hermes', 'Cursor', 'Copilot', 'Custom')]
    [string]$Target = 'Both',
    [string]$Destination,
    [switch]$DryRun,
    [switch]$IncludeBlocked
)

$ErrorActionPreference = 'Stop'
$Installer = Join-Path $PSScriptRoot 'install_skills.py'
$ConfiguredPython = $env:PYTHON
$Py = Get-Command py -ErrorAction SilentlyContinue
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($ConfiguredPython) {
    $Executable = $ConfiguredPython
    $Arguments = @($Installer, '--target', $Target.ToLowerInvariant())
} elseif ($Py) {
    $Executable = $Py.Source
    $Arguments = @('-3', $Installer, '--target', $Target.ToLowerInvariant())
} elseif ($Python) {
    $Executable = $Python.Source
    $Arguments = @($Installer, '--target', $Target.ToLowerInvariant())
} else {
    throw 'Python 3 is required.'
}
if ($Destination) { $Arguments += @('--destination', $Destination) }
if ($DryRun) { $Arguments += '--dry-run' }
if ($IncludeBlocked) { $Arguments += '--include-blocked' }
& $Executable @Arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Restart the coding tool or open a new session to refresh skill discovery.'
