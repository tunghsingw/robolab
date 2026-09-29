# 阶段 0:会用命令 —— 训练、回放、看曲线、导出

## 〇、这一阶段学什么

**目标**:不查别处,能自己完成「选一个自带任务 → 冒烟测试 → 正式训练 → 中断续训 → 回放 → 看曲线 → 导出 ONNX」这一整套。

**完成标准**:做完第十二节的 7 道练习。每道题只用到本文件前面的内容,题后标了对应章节。

**怎么读**:从头往后读,前一节是后一节的基础。命令以 **Windows PowerShell** 为主;WSL 的差别在每节末尾单独说明。

本文件是本项目**所有命令的唯一出处**,README 和其它阶段的笔记只链接到这里。

---

## 一、先认识五个东西

整个流程是一条流水线:

```
选任务 ──train──▶ 存档 model_*.pt ──play──▶ 看行为(3D 画面)
                  │                  └──export──▶ policy.onnx ──▶ 推理脚本 / 真机
                  └─ 曲线数据 events.* ──tensorboard──▶ 看分数变化
```

| 名字 | 是什么 |
|---|---|
| **任务** | "让哪台机器人学什么"的完整定义,用一个**任务 ID** 指定,如 `Mjlab-Velocity-Flat-MicroDuck`(第四节) |
| **训练 train** | 几百上千只仿真鸭子同时试错,按奖励改进一个神经网络(策略)。训练本身**没有画面** |
| **轮 / 迭代 iteration** | 训练的一个循环:每只鸭子先走 24 步收集经验,再用这批经验更新一次网络 |
| **存档 checkpoint** | 训练中途保存的网络权重,文件名 `model_<轮数>.pt`,**每 250 轮存一个**。每个存档都是独立完整的快照 |
| **run 目录** | 一次训练的所有产物放在一个目录里:存档、曲线数据、当时的配置 |
| **回放 play** | 加载一个存档,在带 3D 画面的仿真里跑给你看。只看不学 |
| **曲线面板 TensorBoard** | 把训练时每一轮记下的分数画成曲线,在浏览器里看。它没有官方中文名(字面是"张量看板",tensor = 张量),本项目统一叫**曲线面板** |
| **导出 export** | 把 `.pt` 存档转成 `.onnx` 文件。`.pt` 只有训练代码认识;`.onnx` 是部署用的通用格式,CPU 能跑,真机加载的就是它 |

---

## 二、开工准备

### 每开一个 PowerShell 窗口,先敲这两行

```powershell
$env:WANDB_MODE="offline"
cd D:\robot\robolab\src\microduck_rl
```

| 行 | 为什么 |
|---|---|
| `$env:WANDB_MODE="offline"` | wandb 是一个云端记录服务,要注册登录。设成 offline 就不连它,本地的 TensorBoard 照常可用。只对当前窗口有效 |
| `cd ...\microduck_rl` | 后面所有命令都在这个目录下执行。训练产物也写在这里的 `logs\` 下 |

### uv 和项目环境

- **uv** 是一个 Python 工具,全机一份(Windows 装在 `%USERPROFILE%\.local\bin\uv.exe`,已在 PATH,直接敲 `uv`)。
- **项目环境 `.venv`** 是这个项目自己的 Python 和全部依赖(torch、mjlab 等),每个项目一份,本项目在 `src\microduck_rl\.venv`。
- `uv run <命令>` 会从**当前目录**往上找项目配置文件 `pyproject.toml`,用那个项目的 `.venv` 执行命令。所以**进对目录就用对环境**——这就是上面必须先 `cd` 的原因。【换机器人也一样】
- 想确认 uv 可用,敲 `uv --version`。**别敲 `uv v`**,那是 `uv venv` 的简写,会在当前目录新建一个虚拟环境。
- `uv run` 每次执行前会先检查环境是否和项目锁定的版本一致,不一致就下载补齐。**终端停在一个转圈的包名上**(如 `⠧ cycler==0.12.1`)= 正在下载依赖、网络卡住了,不是你的命令在跑。这时 Ctrl+C,敲 `uv sync --dry-run` 看它想装什么。

### 两个 PowerShell 小技巧

- **变量**:`$RUN = "logs\rsl_rl\..."` 把一段长路径存进变量,后面写 `"$RUN\model_0.pt"` 就会展开成完整路径。
- **检查文件在不在**:`Test-Path "$RUN\model_0.pt"`,输出 `True` 表示存在,`False` 表示路径写错了或文件没有。
- **长参数放进数组**:`$a = @("--agent.resume","True","--agent.max-iterations","250")` 把一串参数存进数组;命令末尾写 `@a`,会逐项展开接在后面。每行都短,不怕截断(下一小节)。第七节续训就用到它。

### ⚠️ PowerShell 会截断长命令

粘贴超过 160 多个字符的命令时,后面的参数会被**悄悄丢掉**,程序照样按默认值跑,不报错。应对:

1. 长路径放进变量、长参数放进数组,让每一行都变短。
2. 训练开跑后第一眼看终端的 `Learning iteration 0/N`,**分母 N 是不是你要的轮数**(第六节)。不对立刻 Ctrl+C。

**WSL 的差别**:先 `wsl -d Ubuntu` 进入,再 `cd ~/robolab/src/microduck_rl`。WSL 里不用设 WANDB 也行(想设就 `export WANDB_MODE=offline`);变量写法是 `RUN=logs/rsl_rl/...`(等号两边不能有空格),引用写 `$RUN`;路径分隔符用 `/`。

---

## 三、命令的通用结构

```
uv run  train  Mjlab-Velocity-Flat-MicroDuck  --env.xxx ...   --agent.xxx ...
工具     做什么   哪个任务(任务 ID)            改环境配置      改算法/运行配置
```

- **做什么**:`train` 训练、`play` 回放、`list-envs` 列任务、`tensorboard` 看曲线。导出是运行一个脚本 `scripts/export.py`,位置也写在这里。
- **任务 ID**:第四节讲。
- **选项**:
  - `--env.` 开头的改**环境配置**:机器人、奖励、并行环境数等。
  - `--agent.` 开头的改**算法和运行配置**:训练轮数、随机种子、run 名等。
  - 层级用点号连接,比如 `--env.scene.num-envs` 就是"环境配置 → 场景 → 环境数"。字段名里的下划线可以写成连字符。
  - 任何命令后面加 `--help`,会列出它的全部选项。
- 训练、回放用的是同一套结构,**学会一条等于学会一族**。

---

## 四、任务:怎么指定用哪个自带任务

### 列出所有任务

```powershell
uv run list-envs
```

输出一张带编号的表,每行一个任务 ID。其中包括 microduck 的全部任务,也包括 mjlab 框架自带的演示任务(Unitree G1 人形、Unitree Go1 四足、倒立摆等)。

### 任务 ID 怎么读

`Mjlab-Velocity-Flat-MicroDuck` 分四段:

| 段 | 含义 | 同位置的其它取值 |
|---|---|---|
| `Mjlab` | 用 mjlab 框架注册的任务 | — |
| `Velocity` | 任务类型:速度跟踪,按指令走 | SitStand、StandUp、BallKick… 见下表 |
| `Flat` | 地形:平地 | `Rough`(崎岖地形) |
| `MicroDuck` | 机器人 | `Unitree-G1`、`Unitree-Go1` |

一些任务还有 **`-Backlash-` 变体**,如 `Mjlab-SitStand-Flat-Backlash-MicroDuck`:同一个任务,舵机多了一段齿轮间隙(齿隙)模型,用来对比"有无齿隙"的效果。**平时用不带 Backlash 的基础版。**

一个任务 ID 背后绑定了两份配置:**环境配置**(机器人模型、观测、动作、奖励、终止条件、课程学习、随机化)和**算法配置**(PPO 参数、存档间隔、默认轮数、日志目录名)。所以**换任务 = 换 ID,命令其余部分不变**。【ID 写法是 mjlab 约定;"任务 = 环境配置 + 算法配置"换机器人也一样】

### microduck 的基础任务一览

"日志目录"是这个任务训练产物所在的文件夹,位于 `logs\rsl_rl\` 下。**同一任务的 Flat、Rough、Backlash 各版共用一个日志目录。**

| 任务 ID | 做什么 | 日志目录 |
|---|---|---|
| `Mjlab-Velocity-Flat-MicroDuck` | 按速度指令走路(**本项目主线**) | `velocity` |
| `Mjlab-Velocity-Rough-MicroDuck` | 同上,崎岖地形 | `velocity` |
| `Mjlab-VelStand-Flat-MicroDuck` / `-Rough-` | 走路 + 摔倒爬起 + 身体姿态控制,一个策略 | `velstand` |
| `Mjlab-StandUp-Flat-MicroDuck` / `-Rough-` | 从仰躺站起来 | `microduck_stand` |
| `Mjlab-SitStand-Flat-MicroDuck` / `-Rough-` | 按指令坐下 ↔ 站起,头可控 | `microduck_sitstand` |
| `Mjlab-GroundPick-Flat-MicroDuck` / `-Rough-` | 蹲下用嘴尖碰地再站回 | `ground_pick` |
| `Mjlab-BallKick-Flat-MicroDuck` | 站着起步,右脚把球踢远 | `ball_kick_right` |
| `Mjlab-Roulade-Flat-MicroDuck` | 前滚翻,落回双脚 | `microduck_roulade` |
| `Mjlab-Velocity-Flat-MicroDuck-Rollers` | 穿轮滑鞋按速度指令滑行(左右交替蹬) | `velocity_rollers` |
| `Mjlab-Velocity-Swizzle-MicroDuck` | 轮滑"剪刀步":双脚不离地,张开再收拢往前滑 | `velocity_swizzle` |
| `Mjlab-RollerCrouch-Flat-MicroDuck` | 轮滑中蹲下滑行约 1 秒,再站起 | `roller_crouch` |
| `Mjlab-RollerSlope-Flat-MicroDuck` | 轮滑从坡道上溜下,保持站立 | `roller_slope` |
| `Mjlab-RollerStandUp-Flat-MicroDuck` | 穿轮滑鞋从趴着或仰躺站起 | `roller_standup` |
| `Mjlab-Spin-Flat-MicroDuck` | 轮滑原地快速转一圈再停住 | `spin` |

---

## 五、冒烟测试(大训练前必跑)

**冒烟测试** = 用很少的环境跑几轮,只为确认"这个任务能正常启动、每项计算都不出错"。上游作者的铁律是大训练前必跑一次,它能拦下约 95% 的配置错误。

```powershell
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 64 --agent.max-iterations 5
```

64 只鸭子跑 5 轮,1 分钟内结束。换别的任务,只换任务 ID。

### 终端输出怎么看

**开头**会打印几张配置表。最重要的是 `Active Reward Terms`(当前生效的奖励项),每行一项:名字(Name)和权重(Weight)。数一数有几行,就是这个任务有几项奖励。

**之后每一轮**打印一块,形如:

```
                   Learning iteration 1/5
                      Mean reward: 1.15
              Mean episode length: 17.33
      Episode_Reward/body_ang_vel: -0.0552
Episode_Reward/posture_pose_legs: 0.1579
                              ...
      Episode_Termination/nan_state: 0.0000
                     Iteration time: 2.47s
```

| 行 | 含义 |
|---|---|
| `Learning iteration k/N` | 第 k 轮,共 N 轮 |
| `Mean reward` | 平均每个回合得的总分 |
| `Mean episode length` | 平均每个回合撑了多少步(回合 = 从重置到结束的一次尝试;50 步 = 1 秒) |
| `Episode_Reward/<项名>` | 每一项奖励各自贡献了多少分 |
| `Episode_Termination/<原因>` | 回合因为什么结束:`time_out` 时间到、`fell_over` 摔倒(有些任务没有这一项)、`nan_state` 物理计算出了无效数值 |
| `Iteration time` | 这一轮用了多久 |

冒烟测试里这些数值的大小**没有意义**(64 只鸭子 5 轮什么也学不会),只看下面的通过标准。

### 奖励项和惩罚项:三条明确的规则

**先说结论:`Active Reward Terms` 表里的权重,负数一定是惩罚;正数不一定是奖励。** 下面讲清为什么,以及怎么判断。

#### 规则 1:每一项的得分 = 函数值 × 权重

每一项奖励背后是一个函数,每一步根据鸭子的状态算出一个数(函数值);再乘上表里的权重,就是这一项这一步的得分。终端里 `Episode_Reward/<项名>` 打印的,是这个得分在一个回合里的累计。

- 打印值 **> 0**:这一项在**加分**,是**奖励**。
- 打印值 **< 0**:这一项在**扣分**,是**惩罚**。
- 打印值 **= 0**:权重是 0(还没启用),或者这一项的条件没被触发。

**奖励还是惩罚,最终看打印值的正负,不看权重的正负。**

#### 规则 2:函数值本身有两种符号,所以权重正负不能直接判断

| 函数的写法 | 函数值 | 权重 | 得分 | 角色 |
|---|---|---|---|---|
| A. 衡量"好状态"(跟上指令、身体端正、姿势到位) | ≥ 0 | **正** | ≥ 0 | 奖励 |
| B. 衡量"坏动作的代价"(动作抖、身体晃、关节顶极限、撞到自己) | ≥ 0 | **负** | ≤ 0 | 惩罚 |
| C. 函数**自带负号**的惩罚(microduck 自己写的,函数名常以 `_penalty`、`_l1` 结尾) | ≤ 0 | **正** | ≤ 0 | 惩罚 |

所以:
- **权重为负** → 只可能是 B,**一定是惩罚**。
- **权重为正** → 可能是 A(奖励),也可能是 C(惩罚)。**光看表分不出来**,因为表里只显示项名,不显示函数名。要看打印值:正的是 A,负的是 C。

写法 C 的例子:SitStand 的 `descent_speed`(下降速度),权重 **+10**,函数自己返回负数,打印值为负,是惩罚。

#### 规则 3:冒烟测试时这样查"符号写反"

符号写反 = 该扣分的项变成了加分,策略会专门去做那个坏动作。有两种写反法,查法不同:

| 检查 | 看到什么 | 说明 |
|---|---|---|
| ① 权重为负的项 | 打印值**必须 ≤ 0**。出现正值就是写反 | 把 C 类函数(自带负号)配了负权重,负负得正 |
| ② 权重为正、打印值也为正的项 | 看**项名的意思**:名字表示好状态(tracking、upright、posture、pose)才对;名字表示坏动作(rate、collision、limit、slip、speed、accel)却在加分,就是写反 | 把 B 类函数(代价)配了正权重。这一种数字上看不出来,只能靠名字判断 |
| ③ 权重为正、打印值为负的项 | 正常,这是 C 类惩罚 | |
| ④ 权重为 0 的项 | 恒为 0,正常 | 多为课程学习后期才启用的项 |

【"惩罚项符号必须对"换机器人也一样;A/B/C 三种写法是本项目上游的约定】

#### 实例:SitStand 平地版冒烟测试的 20 项

| 项名 | 权重 | 打印值 | 写法 | 角色 |
|---|---|---|---|---|
| posture_pose_legs、posture_height、posture_height_sharp、upright_linear、upright_while_tall、posture_composite、posture_stillness、head_pose_tracking、rise_bootstrap | 正 | 正 | A | 奖励(9 项) |
| body_ang_vel、angular_momentum、dof_pos_limits、action_rate_l2、self_collisions | **负** | 负(或 0) | B | 惩罚(5 项) |
| posture_pose_l1(+1)、posture_height_l1(+6)、descent_speed(+10)、gentle_motion(+0.05) | **正** | **负** | C | 惩罚(4 项) |
| rise_speed、joint_torque_rate_l2 | 0 | 0 | C | 惩罚,尚未启用(2 项) |

对照走路任务 `Mjlab-Velocity-Flat-MicroDuck`:它的惩罚项几乎全是 B 类(权重为负),只有 `head_pose_bias` 是 C 类。所以在走路任务里"负权重 = 惩罚、正权重 = 奖励"看起来总是对的,换到 SitStand 就不够用了。

### 通过标准

1. 没有报错,跑到 `Learning iteration 4/5`,分母是 5。
2. 按上面规则 3 查过:没有负权重项打印出正值;没有"坏动作"名字的项在加分。
3. `Episode_Termination/nan_state` 为 0。

结尾出现几行以 `wandb:` 开头的汇总是正常的(离线模式下它也会在本地记一份)。

**实例**(SitStand 平地版冒烟):20 项按规则 3 查过无写反(见上表);`nan_state` 为 0 → 通过。

---

## 六、正式训练

```powershell
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024 --agent.max-iterations 1000 --agent.run-name baseline
```

### 常用选项

| 选项 | 作用 | 注意 |
|---|---|---|
| `--env.scene.num-envs N` | 同时训练几只鸭子 | 本机显卡 6 GB,从 1024 起步,别开 4096 |
| `--agent.max-iterations N` | 这次跑 N 轮 | **不写就是 50000 轮(约 33 小时)**。续训时是"再跑 N 轮"(第七节) |
| `--agent.run-name xxx` | 给这次训练起个名字 | 会成为 run 目录名的后缀(见下) |
| `--agent.seed N` | 随机种子 | 默认 42。两次训练要严格可比时保持一致 |
| `--env.rewards.<项名>.weight V` | 改某一项奖励的权重 | 阶段 2 才用。例 `--env.rewards.air-time.weight 0.0` |

### 一轮做了什么、要跑多久

1024 只鸭子各走 24 步(共 24,576 步经验)→ 用这批经验更新一次网络 → 记一次曲线数据;每 250 轮存一个存档。本机 Windows 1024 环境**约 2.4 秒一轮**,1000 轮约 40 分钟。

### 开跑后先看什么

| 位置 | 看什么 |
|---|---|
| 开头 `Active Reward Terms` 表 | 改过权重的话,核对这里显示的是新值 |
| `Learning iteration 0/N` | **分母 N 对不对** |
| `Mean reward`、`Mean episode length` | 随训练逐渐上升 |
| `Iteration time`、`ETA` | 每轮耗时、预计剩余时间 |

### 产物在哪:run 目录

每次训练(包括冒烟测试)都会新建一个 run 目录:

```
logs\rsl_rl\<日志目录>\<开始时间>_<run名>\
```

- `<日志目录>` 由任务决定(第四节的表)。
- `<开始时间>` 形如 `2026-09-28_22-44-24`。
- `<run名>` 是 `--agent.run-name` 的值;不写则是任务的默认名(如 SitStand 默认是 `microduck_sitstand`)。

例:`uv run train Mjlab-SitStand-Flat-MicroDuck ... --agent.run-name sitstand_try` 在 22:50:10 启动,run 目录就是 `logs\rsl_rl\microduck_sitstand\2026-09-28_22-50-10_sitstand_try\`。

目录里有:

| 文件 | 是什么 |
|---|---|
| `model_0.pt`、`model_250.pt`… | 存档 |
| `events.out.tfevents.*` | 曲线数据,TensorBoard 读它 |
| `params\` | 这次训练的完整配置 |
| `git\` | 这次训练时的代码版本 |

**WSL 的差别**:命令完全相同,产物在 `~/robolab/src/microduck_rl/logs/rsl_rl/` 下。

---

## 七、中断与续训

### 中断

训练随时可以按 **Ctrl+C** 停下。停下后:

| 产物 | 状态 |
|---|---|
| 已经存下的 `model_*.pt` | **全部可用**:回放、导出、续训都行 |
| 曲线数据 | 记到停下那一轮,完整可看 |
| 最后一个存档之后跑的轮次 | **丢失**,最多 249 轮。按 Ctrl+C 不会额外补存 |

所以想停时,**等终端刚过一个 250 的整数倍轮次**(刚存完档)再按,损失最小。
没跑满 `max-iterations` 不影响存档的可用性:存档好不好看回放行为,不看训练有没有跑满。

### 训练已经在跑,想让它停在某个轮次

运行中的训练**改不了** `max-iterations`(只在启动时读一次)。办法是等目标轮次的存档写好再按 Ctrl+C,效果和一开始就设成那个轮数相同。目标轮次要是 250 的整数倍(那一轮才会存档)。

另开一个 PowerShell 窗口,运行下面的等待命令(把路径和轮数换成自己的):

```powershell
$RUN = "D:\robot\robolab\src\microduck_rl\logs\rsl_rl\velocity\<run目录名>"
while (-not (Test-Path "$RUN\model_15000.pt")) { Start-Sleep 5 }
Start-Sleep 10; "model_15000.pt 已存好,可以停了"; [console]::beep(1000,800)
```

- `while (-not (Test-Path ...)) { Start-Sleep 5 }`:文件不存在就每 5 秒再查一次。
- 出现后再等 10 秒,保证文件写完;然后打印提示、响一声。
- 听到后回训练窗口按 Ctrl+C。
- 确认存档完整:`Get-Item "$RUN\model_15000.pt" | Select-Object Name, Length`,大小应和前一个存档接近(本项目约 4.7 MB)。

**另一种做法:停掉,再带上限续训。** 等下一个存档写好后 Ctrl+C,再按下面"续训"的写法从这个存档续,`--agent.max-iterations` 设成"目标轮数 − 存档轮数"。训练跑到上限会自己停。

| | 等到目标存档再停 | 停掉再带上限续训 |
|---|---|---|
| 白跑的轮次 | 0 | 上一个存档之后已跑的部分(最多 249 轮) |
| 额外开销 | 无 | 重新启动一两分钟 |
| 最后一个存档 | `model_<目标>.pt` | `model_<目标−1>.pt`(续训最后一个存档编号 = 起点 + 轮数 − 1) |
| 曲线 | 一个 run,一条线 | 两个 run 目录,两条线首尾相接 |
| 要不要守着 | 要,到点手动按 | 不用 |

**怎么选:离目标只差几分钟就等着;离目标还有几个小时、又不想守着,就停掉重设上限。**

### 续训

从某个存档接着训练:

```powershell
$R = "2026-09-15_12-26-40_velocity"
$a = @("--agent.resume","True","--agent.load-run",$R,"--agent.load-checkpoint","model_12500.pt","--agent.max-iterations","1000")
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024 @a
```

续训命令很长,所以参数放进数组 `$a`(第二节)。开跑后第一行应显示 `Learning iteration <起点>/<起点+轮数>`,这里是 `12500/13500`;分母不对就 Ctrl+C。

| 选项 | 作用 | 注意 |
|---|---|---|
| `--agent.resume True` | 声明这是续训:恢复网络权重、优化器状态、轮数计数、课程学习进度 | 必须写,只写下面两项没用 |
| `--agent.load-run <run目录名>` | 从哪个 run 续 | **只写目录名**,不写路径。程序只在该任务自己的日志目录里找。不写 = 该任务最新的 run |
| `--agent.load-checkpoint <文件名>` | 从哪个存档续 | **只写文件名**,如 `model_12500.pt` |
| `--agent.max-iterations N` | **再跑 N 轮** | 例:从 12500 续 1000 轮,存档编号接着往上走 |
| `--env.scene.num-envs` | 和原训练保持一致 | |

续训会新建一个 run 目录,轮数从加载的存档接着往上计。

---

## 八、回放 play

### 回放一个存档

```powershell
$RUN = "logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity"
Test-Path "$RUN\model_0.pt"
uv run play Mjlab-Velocity-Flat-MicroDuck --checkpoint-file "$RUN\model_0.pt" --num-envs 2 --viewer viser
```

| 选项 | 作用 |
|---|---|
| `--checkpoint-file` | 回放哪个存档,写完整路径。**任务 ID 必须和训练这个存档时用的一致** |
| `--num-envs 2` | 放几只鸭子,少放省显存 |
| `--viewer viser` | 用网页查看器。**Windows 上也要写**:它才有奖励实时条形图和存档切换功能 |

**启动成功的标志**:终端打印出查看器的网址。然后在浏览器打开 **`http://localhost:8080`**,看到鸭子就成功了。
看完在终端按 **Ctrl+C** 关掉——回放和训练共用显卡显存,别一直开着。

### 不加载存档:看"没训练过"是什么样

作对照用。**去掉 `--checkpoint-file`**,换成 `--agent random` 或 `--agent zero`:

```powershell
uv run play Mjlab-Velocity-Flat-MicroDuck --agent random --num-envs 2 --viewer viser
```

- `random`:每一步输出随机动作,鸭子会抽搐乱动。
- `zero`:输出恒为 0,鸭子僵在默认姿势。

### 查看器最基本的操作

右侧是控制面板,分几个标签页:

- **Controls(控制)**:`Pause` 暂停 / `Play` 继续;`Step` 暂停时单步前进;`Reset Environment` 让鸭子回到初始状态重来。
- **Checkpoints(存档)**:下拉框里列出同一 run 目录下的所有存档,选一个就立刻换上,不用重启。用 `random` / `zero` 模式时没有这个标签页。
- **Rewards(奖励)**:每项奖励的实时条形图,绿色加分、红色扣分。

每个面板怎么用于判读,是阶段 1 的内容(`stage1_checkpoint_behavior_map.md`)。

### 存档在 WSL,想在 Windows 回放

在 WSL 里执行一次,把所有训练产物复制到 Windows 相同的相对位置(`-n` 表示不覆盖已有文件,可重复执行):

```bash
cd ~/robolab/src/microduck_rl
mkdir -p /mnt/d/robot/robolab/src/microduck_rl/logs
cp -rn logs/rsl_rl /mnt/d/robot/robolab/src/microduck_rl/logs/
```

**WSL 的差别**:命令相同,路径用 `/`;浏览器仍在 Windows 上开 `localhost:8080`。

---

## 九、看曲线:曲线面板 TensorBoard

```powershell
uv run tensorboard --logdir logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity
```

浏览器打开 **`http://localhost:6006`**。

- `--logdir` 指到**一个 run 目录** = 只看这次训练;指到**日志目录**(如 `logs\rsl_rl\velocity`)= 这个任务的所有训练叠在一张图上,左侧勾选显示哪些。
- 它只读曲线数据文件,不跑仿真。训练进行中也能开着看,刷新页面就更新。
- 停止:终端 Ctrl+C。

曲线分组和读法见阶段 1 笔记第三节。

---

## 十、导出 ONNX 并使用

### 导出

```powershell
$RUN = "logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity"
uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck --checkpoint-file "$RUN\model_12500.pt" --onnx-file ..\..\policies\my_walking_12500.onnx
```

| 部分 | 说明 |
|---|---|
| `scripts/export.py` | 导出脚本。**必须用它**:它会把观测归一化参数一起写进 ONNX;手工转换的文件在仿真里看不出问题,上真机就不能用 |
| 任务 ID | 和训练这个存档时的一致 |
| `--checkpoint-file` | 导出哪个存档 |
| `--onnx-file` | 输出到哪。`..\..\policies\` = 从 `src\microduck_rl` 往上两级到工作区根目录,再进 `policies\`。**不要输出在 `src\` 里**:`src\` 不进本仓库,重装就没了 |
| 文件名 | **带上轮数**,否则过几天就分不清是哪个存档导出的 |

### 在推理脚本里用

根目录的 `run_infer.ps1` 是 CPU 推理的一键启动脚本:弹出 MuJoCo 窗口,用键盘指挥鸭子。里面有一行指定走路策略:

```powershell
    --walking  "$P\alpha_walking.onnx" `
```

`$P` 就是根目录的 `policies\`。把文件名换成自己的(如 `my_walking_12500.onnx`),保存后运行 `D:\robot\robolab\run_infer.ps1`,走路的"本事"就换成了自己训练的。

### 提交自训的 ONNX

自训 ONNX(约 800 KB)可以 `git add` 进仓库,另外两处 `git pull` 就能拿到。提交前先 `git status`:如果 `policies\.gitattributes` 显示被修改(从 Hugging Face 下载官方策略时会被覆盖),先执行 `git checkout policies/.gitattributes` 还原,否则 ONNX 会被存成一个坏掉的占位文件。

---

## 十一、收尾与清理

| 情况 | 做法 |
|---|---|
| 训练、回放、TensorBoard 要停 | 各自终端按 Ctrl+C |
| 显存不够、训练变慢 | 先关回放;`nvidia-smi` 看谁占着显卡 |
| 临时改过 `src\` 里的代码做实验 | `git -C D:\robot\robolab\src\microduck_rl checkout .` 还原 |

---

## 十二、练习(做完即阶段 0 完成)

以 SitStand 任务为对象。题目顺序就是第四到十节的顺序,也是一次完整训练的流水线;第 3、4、7 题用的是同一个 run。每题后面是要用到的章节,以及"做对了是什么样"。

1. **找任务 ID**:用命令列出所有任务,找到 SitStand 平地、不带齿隙的版本。(第四节)
   自查:ID 以 `Mjlab-` 开头、含 `Flat`、不含 `Backlash`。
2. **冒烟测试**:对它跑一次冒烟测试。记下奖励项有几项、run 目录的完整路径、是否通过,以及你判断"通过"的依据。(第五、六节)
   自查:能把全部奖励项分进规则 2 的 A、B、C 三类,并按规则 3 说明为什么没有写反。
3. **正式训练**:写出训练 1000 轮、run 名为 `sitstand_try` 的命令并运行。看到 `Learning iteration 1/1000` 后按 Ctrl+C。(第三、六节)
   自查:第一行分母是 1000;日志目录下多了一个以 `_sitstand_try` 结尾的 run 目录,里面有 `model_0.pt`(用 `Test-Path` 确认)。
4. **续训**:从第 3 题那个 run 的 `model_0.pt` 续训 500 轮。看到第一行后按 Ctrl+C。(第六节"run 目录",第七节)
   自查:`--agent.load-run` 后面只有目录名,没有路径;第一行显示 `Learning iteration 0/500`;日志目录下又多了一个新的 run 目录。
5. **看未训练的样子**:不加载存档,用随机策略回放这个任务。(第八节)
   自查:浏览器 8080 能看到鸭子乱动;查看器里没有 Checkpoints 标签页。
6. **看曲线**:用曲线面板打开第 2 题冒烟测试那个 run。(第九节)
   自查:浏览器 6006 能看到曲线,横轴只有 0 到 4。
7. **导出**:把第 3 题那个 run 的 `model_0.pt` 导出到根目录 `policies\`,文件名带轮数。(第十节)
   自查:任务 ID 是 SitStand 的;输出路径以 `..\..\policies\` 开头;命令结束后 `policies\` 下出现这个 `.onnx` 文件。这是未训练的策略,只用来练命令,**不要提交**,练完可以删掉。
