# 阶段 0 结构图:会用命令

复习用:一张图回忆阶段 0 的知识结构。图里的「§五」指课程 [`stage0_commands.md`](stage0_commands.md) 第五节,细节回那里查。

在 VS Code 里看:先装预览插件 Markdown Preview Mermaid Support(扩展 ID `bierner.markdown-mermaid`),打开本文件后按 Ctrl+Shift+V 预览。

```mermaid
flowchart TB
  prep["<b>§二 开工准备</b><br/>WANDB_MODE=offline<br/>cd 到 microduck_rl<br/>进对目录 = 用对 .venv"]
  syntax["<b>§三 命令结构</b><br/>uv run 动词 任务ID<br/>--env.… 改环境<br/>--agent.… 改算法/运行"]
  task["<b>§四 选任务</b><br/>list-envs 找任务 ID<br/>Mjlab-类型-地形-机器人<br/>任务 = 环境 + 算法配置"]
  smoke["<b>§五 冒烟测试</b> 64 只 × 5 轮<br/>✔ 跑到 4/5<br/>✔ nan_state = 0<br/>✔ 惩罚项符号没写反<br/>(A/B/C 三类)"]
  train["<b>§六 正式训练</b><br/>1024 只 × N 轮<br/>约 2.4 秒一轮<br/>盯 iteration 0/N 的分母<br/>reward、episode<br/>length 往上走"]
  run[("<b>run 目录</b><br/>日志目录/时间_run名<br/>model_*.pt 每 250 轮<br/>events.* 曲线数据<br/>params 当时配置")]
  resume["<b>§七 中断与续训</b><br/>Ctrl+C:末个存档<br/>之后的轮次丢失<br/>resume True<br/>load-run 只写目录名<br/>load-checkpoint<br/>只写文件名<br/>max-iterations<br/>= 再跑 N 轮"]
  play["<b>§八 回放</b><br/>--checkpoint-file 单个 .pt<br/>--viewer viser → :8080<br/>random / zero 作对照"]
  tb["<b>§九 曲线面板</b><br/>--logdir 任务目录 → :6006<br/>多个 run 叠一张图<br/>刷新即更新"]
  export["<b>§十 导出</b><br/>必须用 scripts/export.py<br/>输出到根目录 policies<br/>文件名带轮数"]
  infer["<b>推理 / 提交</b><br/>run_infer.ps1<br/>换 --walking 那一行<br/>git add 前还原<br/>policies/.gitattributes"]
  s1(["<b>阶段 1:学会看</b><br/>回放和曲线怎么判读"])

  prep --> syntax --> task --> smoke
  smoke -- 通过 --> train --> run
  smoke -. 不通过,修配置 .-> task
  run -- 存档 --> resume
  resume -- 新 run 目录<br/>轮数接着往上 --> run
  run -- model_*.pt --> play
  run -- events.* --> tb
  run -- model_*.pt --> export --> infer
  play -.-> s1
  tb -.-> s1
```

主线是从上到下的一条流水线；虚线是「回头」或者「通往下一阶段」。【这条流水线换机器人也一样：选任务 → 冒烟 → 训练 → 存档 → 回放 / 曲线 / 导出。图里的命令和数字是 microduck 特有的】
