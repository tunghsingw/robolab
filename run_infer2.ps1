# Microduck CPU 推理一键启动(自训练 62499 迭代版)
# 键盘控制在【本终端】输入(不是 MuJoCo 窗口):方向键=速度, A/E=转向, Y=坐/站, R=翻滚, 空格=停, Q=退出
$env:HF_ENDPOINT = "https://hf-mirror.com"
$RL = (Join-Path $PSScriptRoot "src\microduck_rl")
$P  = (Join-Path $PSScriptRoot "policies")
Set-Location $RL   # infer_policy.py 内部用相对路径找机器人模型,必须在 RL 仓库目录下运行
& "$RL\.venv\Scripts\python.exe" "$RL\scripts\infer_policy.py" `
    --walking  "$P\2026-09-16_09-07-17_velocity.onnx" `
    --standing "$P\alpha_stand.onnx" `
    --sitstand "$P\alpha_sitstand.onnx" `
    --roulade  "$P\roulade.onnx" `
    --new-cmd-obs