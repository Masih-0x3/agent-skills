[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("agent-skills-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $TempRoot | Out-Null

$ConfiguredPython = $env:PYTHON
$Py = Get-Command py -ErrorAction SilentlyContinue
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($ConfiguredPython) {
    $Executable = $ConfiguredPython
    $Prefix = @()
} elseif ($Py) {
    $Executable = $Py.Source
    $Prefix = @('-3')
} elseif ($Python) {
    $Executable = $Python.Source
    $Prefix = @()
} else {
    throw 'Python 3 is required.'
}

function Invoke-Python {
    & $Executable @Prefix @args
    if ($LASTEXITCODE -ne 0) { throw "Python command failed with exit code $LASTEXITCODE" }
}

try {
    Invoke-Python "$RepoRoot\scripts\validate_skills.py"
    Invoke-Python "$RepoRoot\scripts\build_catalog.py" '--check'
    $Orch = "$RepoRoot\skills\software-orchestrator"
    Invoke-Python '-m' 'py_compile' "$Orch\scripts\initialize_store.py" "$Orch\scripts\seed_model_priors.py" "$Orch\scripts\select_model.py" "$Orch\scripts\record_outcome.py"
    Invoke-Python "$Orch\scripts\initialize_store.py" '--path' "$TempRoot\orchestrator.db"
    Invoke-Python "$Orch\scripts\seed_model_priors.py" '--db' "$TempRoot\orchestrator.db" '--force'
    $Ptd = "$RepoRoot\skills\project-task-decomposer"
    $Corpus = "$Ptd\examples\example-corpus"
    Invoke-Python "$Ptd\scripts\validate_task_corpus.py" $Corpus '--json'
    Invoke-Python "$Ptd\scripts\detect_cycles.py" $Corpus
    Invoke-Python "$Ptd\scripts\check_readiness.py" $Corpus
    Invoke-Python "$RepoRoot\scripts\run_decomposer_tests.py"
    Write-Host 'ALL VALIDATION PASSED'
} finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
