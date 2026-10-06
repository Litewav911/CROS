param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8501,

    [ValidateRange(1, 300)]
    [int]$StartupTimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$appPath = Join-Path $projectRoot "src\app.py"
$dashboardUrl = "http://127.0.0.1:$Port"
$healthUrl = "$dashboardUrl/_stcore/health"

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Project Python was not found at '$pythonPath'."
}

if (-not (Test-Path -LiteralPath $appPath -PathType Leaf)) {
    throw "Streamlit app was not found at '$appPath'."
}

function Test-DashboardReady {
    try {
        $response = Invoke-WebRequest `
            -Uri $healthUrl `
            -UseBasicParsing `
            -TimeoutSec 2

        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

if (Test-DashboardReady) {
    Write-Output "CROS dashboard is already ready at $dashboardUrl"
    return
}

$runId = "cros-streamlit-$Port-$PID"
$stdoutPath = Join-Path $env:TEMP "$runId.stdout.log"
$stderrPath = Join-Path $env:TEMP "$runId.stderr.log"

$process = Start-Process `
    -FilePath $pythonPath `
    -ArgumentList @(
        "-m",
        "streamlit",
        "run",
        $appPath,
        "--server.address=127.0.0.1",
        "--server.port=$Port",
        "--server.headless=true"
    ) `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden `
    -PassThru `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath

$deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)

while ((Get-Date) -lt $deadline) {
    if (Test-DashboardReady) {
        Write-Output "CROS dashboard is ready at $dashboardUrl"
        Write-Output "Startup logs: $stdoutPath and $stderrPath"
        return
    }

    $process.Refresh()

    if ($process.HasExited) {
        break
    }

    Start-Sleep -Milliseconds 500
}

$stdout = if (Test-Path -LiteralPath $stdoutPath) {
    Get-Content -LiteralPath $stdoutPath -Raw
}
else {
    "(no standard output)"
}

$stderr = if (Test-Path -LiteralPath $stderrPath) {
    Get-Content -LiteralPath $stderrPath -Raw
}
else {
    "(no standard error)"
}

if (-not $process.HasExited) {
    Stop-Process -Id $process.Id -Force
}

throw @"
CROS dashboard did not become ready at $dashboardUrl within $StartupTimeoutSeconds seconds.
Process ID: $($process.Id); exited: $($process.HasExited)
Standard output ($stdoutPath):
$stdout
Standard error ($stderrPath):
$stderr
"@
