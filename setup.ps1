# Microduck RL 路线 A 环境搭建脚本
# 由 Doubao 生成：安装后执行 uv sync（下载依赖约 2GB），日志写入 uv-sync.log
$ErrorActionPreference = "Continue"
Set-Location "D:\robot\microduck\src\microduck_rl"
$env:UV_HTTP_TIMEOUT = "600"
$uv = Join-Path $env:USERPROFILE ".local\bin\uv.exe"

Write-Host "=== uv sync 开始: $(Get-Date) ==="
& $uv sync *> "D:\robot\microduck\uv-sync.log"
Write-Host "=== uv sync 结束: $(Get-Date) ==="
Write-Host "日志: D:\robot\microduck\uv-sync.log"
