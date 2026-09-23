# Microduck 未训练基准对比:看"训练到底训练了什么"
# 用法:  .\run_infer0.ps1          → random 模式(未训练的随机网络,鸭子触电式抽搐瘫倒)
#        .\run_infer0.ps1 zero     → zero 模式(输出恒为 0,鸭子僵在默认姿势不动)
# 对比:  run_infer.ps1 = 官方训练好的策略;run_infer1.ps1 = 自己训练的策略
# 说明:  基准文件喂给了 walking 和 standing 两个槽位,所以一启动就能看到效果,不用按键;
#        untrained_random.onnx 就是本机训练 run 的 model_0.pt(第 0 迭代)导出的——训练的真实起点
param(
    [ValidateSet("random", "zero")]
    [string]$Mode = "random"
)
$RL = (Join-Path $PSScriptRoot "src\microduck_rl")
$P  = (Join-Path $PSScriptRoot "policies")
$B  = "$P\untrained_$Mode.onnx"
Write-Host "基准模式: $Mode  ($B)"
Set-Location $RL   # infer_policy.py 内部用相对路径找机器人模型,必须在 RL 仓库目录下运行
& "$RL\.venv\Scripts\python.exe" "$RL\scripts\infer_policy.py" `
    --walking  $B `
    --standing $B `
    --sitstand "$P\alpha_sitstand.onnx" `
    --roulade  "$P\roulade.onnx" `
    --new-cmd-obs
