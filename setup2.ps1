$ErrorActionPreference = "Continue"
$env:UV_HTTP_TIMEOUT = "600"
$uv = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
$log = Join-Path $env:TEMP "uv-sync.log"
Write-Host ("sync start: " + (Get-Date))
Set-Location "D:\robot\microduck\src\microduck_rl"
if ($?) { Write-Host "cd ok" } else { Write-Host "cd FAILED"; exit 1 }
& $uv sync *> $log
Write-Host ("sync end: " + (Get-Date))
Write-Host ("log: " + $log)
