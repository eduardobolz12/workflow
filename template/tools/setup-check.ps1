param(
    [string]$Repo = ".",
    [string]$Workspace = "",
    [switch]$RunTests
)

$ErrorActionPreference = 'Continue'
$script:falhas = 0

function Ok    { param($m) Write-Host "  OK    $m" -ForegroundColor Green }
function Falta { param($m) Write-Host "  FALTA $m" -ForegroundColor Yellow; $script:falhas++ }
function Info  { param($m) Write-Host "  ....  $m" -ForegroundColor DarkGray }

function Invoke-Silent {
    param([string]$Exe, [string[]]$Arguments)
    $null = & $Exe @Arguments 2>&1
    return $LASTEXITCODE
}

if (-not (Test-Path $Repo)) { Write-Host "repo nao existe: $Repo" -ForegroundColor Red; exit 2 }
$repo = (Resolve-Path $Repo).Path
if (-not $Workspace) { $Workspace = (Get-Location).Path }
if (Test-Path $Workspace) { $Workspace = (Resolve-Path $Workspace).Path }

Write-Host "=== setup-check ===" -ForegroundColor White
Write-Host "repo: $repo"
Write-Host ""

# 1. localizacao
if ($repo.StartsWith($Workspace, [StringComparison]::OrdinalIgnoreCase)) {
    Ok "dentro do workspace informado"
} else {
    Info "fora do workspace ($Workspace) - o DSH nao conseguira gravar evidencia"
}
if ($repo -match 'OneDrive') {
    Falta "repo dentro do OneDrive (git + sync = lock em worktree)"
} else {
    Ok "fora do OneDrive"
}

# 2. git
$code = Invoke-Silent 'git' @('-C', $repo, 'rev-parse', '--abbrev-ref', 'HEAD')
if ($code -ne 0) {
    Falta "nao e repositorio git"
} else {
    $branch = (& git -C $repo rev-parse --abbrev-ref HEAD 2>&1 | Out-String).Trim()
    Ok "repositorio git (branch atual: $branch)"
    if ((Invoke-Silent 'git' @('-C', $repo, 'rev-parse', '--verify', 'main')) -eq 0) {
        Ok "branch main existe"
    } else {
        Falta "branch main ausente"
    }
}

# 3. gitignore
$gi = Join-Path $repo ".gitignore"
if (Test-Path $gi) {
    $txt = Get-Content $gi -Raw
    if ($txt -match '(?m)^\.dsh/?\s*$') { Ok ".gitignore cobre .dsh/" } else { Falta ".gitignore sem .dsh/" }
    if ($txt -match '(?m)^docs/manifesto/?\s*$') { Ok ".gitignore cobre docs/manifesto/" } else { Falta ".gitignore sem docs/manifesto/" }
} else {
    Falta ".gitignore ausente"
}

# 4. dsh.json
$cfgPath = Join-Path $repo "dsh.json"
$cfg = $null
if (-not (Test-Path $cfgPath)) {
    Falta "dsh.json ausente"
} else {
    $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
    if ($cfg.acceptance_cmd) { Ok "acceptance_cmd definido" } else { Falta "acceptance_cmd ausente" }
    if ($cfg.report_path -and $cfg.report_format) {
        Ok "relatorio configurado ($($cfg.report_format))"
    } else {
        Falta "report_path/report_format ausentes"
    }
    if ($cfg.start_cmd) { Ok "start_cmd definido" } else { Info "start_cmd ausente - verify roda sem transporte real" }
    if ($cfg.base_url) { Ok "base_url definido" } else { Info "base_url ausente - sem espera de app" }
}

# 5. harness
$dsh = Join-Path $repo "tools\dsh.py"
if (Test-Path $dsh) {
    if ((Invoke-Silent 'python' @($dsh, '--help')) -eq 0) {
        Ok "tools/dsh.py responde"
    } else {
        Falta "tools/dsh.py nao executa"
    }
} else {
    Falta "tools/dsh.py ausente no repo"
}

# 6. teste real (opcional)
if ($RunTests -and $cfg) {
    $report = Join-Path $repo ($cfg.report_path -replace '\{nnn\}', '001')
    $argList = @()
    foreach ($part in $cfg.acceptance_cmd) { $argList += ($part -replace '\{report\}', $report) }
    if (Test-Path $report) { Remove-Item $report -Force }
    Info "rodando: $($argList -join ' ')"
    if ($argList.Count -gt 1) {
        $null = & $argList[0] @($argList[1..($argList.Count - 1)]) 2>&1
    } else {
        $null = & $argList[0] 2>&1
    }
    if (Test-Path $report) { Ok "suite gerou relatorio legivel" } else { Falta "suite nao gerou relatorio em $report" }
}

Write-Host ""
if ($script:falhas -eq 0) {
    Write-Host "=== ambiente pronto ===" -ForegroundColor Green
    exit 0
} else {
    Write-Host "=== $($script:falhas) pendencia(s) ===" -ForegroundColor Yellow
    exit 1
}
