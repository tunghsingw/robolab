# 阶段 0:会用命令 —— 训练、回放、看曲线、导出

**目标**:不查别处,能自己完成「选一个自带任务 → 冒烟测试 → 正式训练 → 中断续训 → 回放 → 看曲线 → 导出 ONNX」这一整套。
**完成标准**:给你一个没训过的自带任务名(如 `Mjlab-SitStand-Flat-MicroDuck`),你能自己写出它的冒烟、训练、回放、导出四条命令,并知道每条跑起来后先看哪一行。

本文件是**命令的唯一权威出处**。README 和阶段 1/2 笔记里只留指向这里的链接。
命令以 **Windows PowerShell** 为主(日常在这边看回放);WSL 写法见每节末尾,只是根目录和变量语法不同。

---

## 一、开工前的两行(每开一个 PowerShell 窗口先敲)

```powershell
$env:WANDB_MODE="offline"
cd D:\robot\robolab\src\microduck_rl
```

| 行 | 为什么 |
|---|---|
| `WANDB_MODE=offline` | 不登录 wandb(云端记录服务)。本地 TensorBoard 不受影响 |
| `cd ...\microduck_rl` | 所有命令都在这个目录下执行,`logs\` 也在这里 |

WSL 对应:`wsl -d Ubuntu` 进入后 `cd ~/robolab/src/microduck_rl`,变量写法是 `RUN=...`、引用 `$RUN`。

**uv 与项目环境**:uv 是全机一份的工具(Windows 在 `%USERPROFILE%\.local\bin\uv.exe`,已在 PATH,版本 0.12.13);项目环境 `.venv` 是每个项目各一份(本项目在 `src\microduck_rl\.venv`)。`uv run` 从**当前目录**往上找 `pyproject.toml`,用那个项目的 `.venv`——所以**进对目录就用对环境**,这就是每次先 `cd` 的原因。测试 uv 是否可用用 `uv --version`;别敲 `uv v`(那是 `uv venv`,会在当前目录新建一个虚拟环境)。【换机器人也一样】

⚠️ **PowerShell 粘贴长命令会被截断**(实测 160 多字符后的参数直接丢失,程序照样按默认值跑,不报错)。所以:路径放进变量;**每次开跑先看 `Learning iteration 0/N` 的分母**。

---

## 二、命令的通用结构

```
uv run  train  Mjlab-Velocity-Flat-MicroDuck  --env.xxx ...   --agent.xxx ...
工具     做什么   哪个任务(任务 ID)            改环境配置      改算法/运行配置
```

- **做什么**:`train` 训练、`play` 回放、`list-envs` 列任务、`tensorboard` 看曲线;导出是 `scripts/export.py`。
- **任务 ID**:见第三节。
- **选项**:`--env.` 开头改环境配置(机器人、奖励、环境数…),`--agent.` 开头改算法和运行配置(轮数、种子、run 名…)。层级用点号,字段名里的下划线可写成连字符。`--help` 列出全部可改字段。
- 训练和回放都是这个结构,**学会一条等于学会一族**。

---

## 三、自带任务怎么指定

### 列出所有任务

```powershell
uv run list-envs
```

会列出 microduck 注册的全部任务,外加 mjlab 自带的演示任务(Unitree G1 人形、Go1 四足、倒立摆等)。以你的实际输出为准。

### 任务 ID 怎么读

`Mjlab-Velocity-Flat-MicroDuck` = 框架前缀 `Mjlab` + 任务类型 `Velocity` + 地形 `Flat` + 机器人 `MicroDuck`。
一个 ID 在注册时绑定了**环境配置**(奖励、观测、课程、随机化…)和**算法配置**(PPO 超参、存档间隔、日志目录名)。**换任务 = 换 ID,命令其余部分不变。**

### microduck 的 18 个基础任务

| 任务 ID | 做什么 | 日志目录(`logs\rsl_rl\` 下) |
|---|---|---|
| `Mjlab-Velocity-Flat-MicroDuck` | 按速度指令走路(**本项目主线**) | `velocity` |
| `Mjlab-Velocity-Rough-MicroDuck` | 同上,崎岖地形 | `velocity` |
| `Mjlab-VelStand-Flat/Rough-MicroDuck` | 走路 + 摔倒爬起 + 身体姿态控制,一个策略 | `velstand` |
| `Mjlab-StandUp-Flat/Rough-MicroDuck` | 从仰躺站起来 | `microduck_stand` |
| `Mjlab-SitStand-Flat/Rough-MicroDuck` | 按指令坐下 ↔ 站起,头可控 | `microduck_sitstand` |
| `Mjlab-GroundPick-Flat/Rough-MicroDuck` | 蹲下用嘴尖碰地再站回 | `ground_pick` |
| `Mjlab-BallKick-Flat-MicroDuck` | 站姿起步,右脚把球踢远 | `ball_kick_right`(按踢球脚命名) |
| `Mjlab-Roulade-Flat-MicroDuck` | 前滚翻,落回双脚 | `microduck_roulade` |
| `Mjlab-Velocity-Flat-MicroDuck-Rollers` | 穿轮滑鞋按速度指令滑行 | `velocity_rollers` |
| `Mjlab-Velocity-Swizzle-MicroDuck` | 轮滑"剪刀步"滑行 | `velocity_swizzle` |
| `Mjlab-RollerCrouch/RollerSlope/RollerStandUp-Flat-MicroDuck` | 轮滑下蹲 / 坡道 / 倒地站起(从名字看,未读配置) | `roller_crouch` / `roller_slope` / `roller_standup` |
| `Mjlab-Spin-Flat-MicroDuck` | 轮滑原地快速旋转 | `spin` |

另有每个任务的 **`-Backlash-` 变体**(如 `Mjlab-Velocity-Flat-Backlash-MicroDuck`):同一任务,舵机加了齿隙模型,用来做"有无齿隙"对照。

**Flat / Rough 两版共用同一个日志目录**,靠 run 目录的时间戳和 `--agent.run-name` 区分。

【任务 ID 命名是 mjlab 约定;「任务 = 环境配置 + 算法配置」换机器人也一样】

---

## 四、训练 `train`

### 冒烟测试(大 run 前必跑,上游铁律)

```powershell
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 64 --agent.max-iterations 5
```

64 个环境跑 5 轮,1 分钟内结束。通过标准:不报错;`Episode_Reward` 下惩罚项全 ≤ 0;`nan_state` 为 0。能拦下约 95% 的配置错误。

### 正式训练

```powershell
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024 --agent.max-iterations 1000 --agent.run-name baseline
```

### 常用选项

| 选项 | 作用 | 备注 |
|---|---|---|
| `--env.scene.num-envs N` | 并行环境数 | 6 GB 显存从 1024 起步,别开 4096 |
| `--agent.max-iterations N` | 本次跑 N 轮 | **不写 = 50000 轮(约 33 小时)**。续训时是"再跑 N 轮" |
| `--agent.run-name xxx` | run 目录后缀 | 目录名 = `<时间戳>_xxx`;不写则是任务默认名 |
| `--agent.seed N` | 随机种子 | 默认 42。对照实验要一致;量随机波动时换它 |
| `--env.rewards.<项>.weight V` | 改一项奖励权重 | 阶段 2 用。例 `--env.rewards.air-time.weight 0.0` |

### 一轮(iteration)做了什么

1024 只鸭子各走 24 步(共 24,576 步经验)→ 用这批经验做一次 PPO 更新 → 写一次 TensorBoard;每 250 轮存一个 `model_XXXX.pt`。1000 轮 ≈ 2500 万步经验。

### 开跑后终端里先看什么

| 位置 | 看什么 |
|---|---|
| 开头几张表 | `Active Reward Terms`:奖励项和权重,**改过参数就核对这里**;还有观测、终止条件、课程学习、域随机化 |
| `Learning iteration k/N` | **分母 N 对不对** |
| `Mean reward` / `Mean episode length` | 与 TensorBoard 的 Train 组同一个数 |
| `Iteration time` / `ETA` | 每轮耗时(Windows 1024 环境约 2.4 s)/ 预计剩余时间 |

### 产物在哪

`logs\rsl_rl\<日志目录>\<时间戳>_<run名>\`:`model_*.pt` 存档、`events.out.tfevents.*` 曲线数据、`params\` 当时的完整配置、`git\` 当时的代码版本。

WSL 写法完全相同。

---

## 五、中断与续训

随时 **Ctrl+C** 中断,最多丢最近 250 轮。续训:

```powershell
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024 --agent.resume True --agent.load-run 2026-09-15_12-26-40_velocity --agent.load-checkpoint model_12500.pt --agent.max-iterations 1000
```

| 选项 | 作用 | 注意 |
|---|---|---|
| `--agent.resume True` | 声明续训:恢复权重、优化器状态、迭代计数、课程进度 | 不加它,只加 load-checkpoint 没用 |
| `--agent.load-run <run目录名>` | 从哪个 run 续 | 不写 = 该任务最新的 run |
| `--agent.load-checkpoint model_X.pt` | 从哪个存档续,**只写文件名** | |
| `--agent.max-iterations N` | **再跑 N 轮** | 例:从 12500 续 50000 轮,最后一个存档是 `model_62499` |
| `--env.scene.num-envs` | **与原训练一致** | |

续训会新建一个 run 目录,迭代数接着往上计;TensorBoard 里是两条 run,横轴接上。

---

## 六、回放 `play`

```powershell
$RUN = "logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity"
Test-Path "$RUN\model_0.pt"
uv run play Mjlab-Velocity-Flat-MicroDuck --checkpoint-file "$RUN\model_0.pt" --num-envs 2 --viewer viser
```

浏览器开 **`http://localhost:8080`**。看完 **Ctrl+C**(和训练共用显存)。

| 选项 | 作用 |
|---|---|
| `--checkpoint-file` | 回放哪个存档。**任务 ID 必须和训练时一致** |
| `--num-envs 2` | 放几只鸭子,省显存 |
| `--viewer viser` | 网页查看器。**Windows 上也要写**:只有它有 Rewards(奖励条)和 Checkpoints(存档热切换)标签页 |
| `--agent zero` / `--agent random` | 不加载存档,用"输出全零"/"随机输出"做对照 |

**启动成功的标志**:终端出现 viser 网址、浏览器能打开 8080。终端停在转圈的包名(如 `⠧ cycler==0.12.1`)是 `uv run` 在同步依赖、网络卡住,**不是 play 在跑**:先 `uv sync --dry-run` 看它想装什么。
面板怎么用见阶段 1 笔记第二节。

存档在 WSL 训练的,先复制到 Windows(WSL 里执行一次即可,`-n` 不覆盖):

```bash
cd ~/robolab/src/microduck_rl
mkdir -p /mnt/d/robot/robolab/src/microduck_rl/logs
cp -rn logs/rsl_rl /mnt/d/robot/robolab/src/microduck_rl/logs/
```

---

## 七、看曲线 `tensorboard`

```powershell
uv run tensorboard --logdir logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity
```

浏览器开 **`http://localhost:6006`**。`--logdir` 指单个 run = 只看它;指 `logs\rsl_rl\velocity` = 该任务所有 run 叠在一起(对比实验用)。
它只读事件文件,不跑仿真,训练中也能开着看(刷新即更新)。停止:Ctrl+C。面板怎么读见阶段 1 笔记第三节。

---

## 八、导出 ONNX 并在推理脚本里用

```powershell
$RUN = "logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity"
uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck --checkpoint-file "$RUN\model_12500.pt" --onnx-file ..\..\policies\my_walking_12500.onnx
```

- **必须用这个脚本导出**:它把观测归一化参数烤进 ONNX,手工转换的文件在仿真里看不出问题、上真机即废(上游铁律)。
- **输出直接写到根目录的 `policies\`**,不留在 `src\` 里(`src\` 不进仓库,重装即失)。
- **文件名带迭代数**,否则过两轮就分不清是哪个存档导出的。
- 用法:编辑根目录 `run_infer.ps1`,把 `--walking` 那一行换成 `"$P\my_walking_12500.onnx"`,再运行它。键位见 README「第一步:CPU 推理」。
- 自训的 ONNX 可以 `git add` 提交,另外两处 pull 即得。提交前 `git status` 确认 `policies\.gitattributes` 没被改(见 AGENTS.md 第三节的坑)。

`.pt` 与 `.onnx` 的关系:`.pt` 是训练存档,只有训练代码认识,用于回放和续训;`.onnx` 是部署成品,CPU 可跑、跨语言,真机加载的就是它。

---

## 九、收尾与清理

| 情况 | 做法 |
|---|---|
| 训练、play、tensorboard 都要停 | 各自终端 Ctrl+C |
| 显存不够 / 训练变慢 | 先关 play;`nvidia-smi` 看谁占着 |
| 改过上游代码做临时实验 | `git -C D:\robot\robolab\src\microduck_rl checkout .` 还原 |

---

## 十、练习(做完即阶段 0 完成)

1. 用 `list-envs` 找到 SitStand 任务的平地版 ID。
2. 对它跑一次冒烟测试,记下开头 `Active Reward Terms` 表里有几项奖励、日志落在哪个目录。
3. 写出它训练 1000 轮、run 名为 `sitstand_try` 的命令(不必真跑完,看到分母是 1000 就 Ctrl+C)。
4. 用 `--agent random` 回放它,看一只"随机策略"的鸭子在这个任务里是什么样。
5. 假设第 3 步那个 run 跑到了 `model_500.pt`,写出从它续训 500 轮的命令。
