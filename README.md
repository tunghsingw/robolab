# Microduck 具身智能学习笔记

> 目的:记录环境现状和学习路线,避免每次会话从头摸索。只写"现在是什么样",不记变更日期。

## 学习目标

**用 microduck 入门具身智能,目标是掌握可迁移的技术理解,为以后给第三方设备做训练做准备。**
microduck 是教具不是终点——重点是"换一台机器人时这套方法怎么用",不是读懂这个仓库的源码。

本人无具身智能基础,**实践优先**:先动手跑、看现象,再回头理解原理。

两个共用的基线文件,和本文档一起看:

- **[`GLOSSARY.md`](GLOSSARY.md)** —— 技术名词中英对照 + 中文解释。看不懂某个词先查它。
- **[`REFERENCES.md`](REFERENCES.md)** —— 外部资料清单,每条注明"它能回答什么"。

⚠️ 规矩:**领域常识(技术分类、现状、缩写全称、论文结论)不许凭记忆答,先查 `REFERENCES.md`,查不到就联网核实。**
这条是踩坑立的——本文档最初那版"两条技术栈"的分类就是凭记忆写的,三处硬伤,核实后才改对(详见 `AGENTS.md` 第二节第 7 条)。

### 这个领域的地图

**三种方法是叠在一起用的栈,不是互相取代的阵营:**

| 方法 | 干什么 | 现状 |
|---|---|---|
| **模型控制**(MPC / WBC) | 人建模型,在线求解最优控制 | 远没过时。提供稳定性保证和安全兜底;**还常被当作"生成示教数据的机器"**——腿足机器人模仿学习最常用的训练数据来源已经是 MPC 日志,超过了动捕 |
| **强化学习**(RL) | 仿真里按奖励试错 | 运动控制的主力;在操作上更多作为"后训练"精修 |
| **模仿学习**(IL) | 从示教数据学,绕开奖励设计 | 操作的主力(行为克隆占近一半工作);也用于人形全身控制 |

真机系统基本都混着用。例:Atlas 用 MPC 做底层全身控制**和遥操作底座**,上面叠 Large Behavior Model
(扩散 Transformer,30 Hz,图像+本体+语言→动作)。**说某家公司"是 RL 派"通常是误解。**

**运动控制适合入门,真正的原因是任务难度梯度,不是技术路线不同:**

| 维度 | 运动控制(走、跑、平衡) | 操作(抓取、装配、精细动作) |
|---|---|---|
| 仿真准不准 | 准。刚体动力学 + 接触建模成熟 | 差。接触、摩擦、柔性物体难建模 |
| 奖励好不好写 | 好。"走路"一套奖励能改出很多任务 | 难。几乎一个任务一套,难泛化 |
| 依不依赖视觉 | 可以"盲走",本体感知够用 | 基本离不开视觉 |
| 成熟度 | 已有野外部署 | 多数停留在演示 |

所以运动控制的主流配方是**仿真 RL + 域随机化**(不必采数据),操作更依赖**真机示教 + 模仿学习**
——**这是难度差异导致的选择,不是门派之分。**

⚠️ 三个容易踩的误解:

- **"运动控制不需要数据"** —— 人形全身控制普遍用动捕重定向做参考动作;纯从零 RL 容易学出别扭姿态,奖励调参量也巨大。
  microduck 这种小型双足任务够简单,才能纯靠奖励硬train。
- **"操作用不了仿真 RL"** —— 能枚举的子问题(抓取、手内操作、装配)已经能零样本 sim2real。
- **"两边是分开的"** —— loco-manipulation(边走边操作)正在把它们缝起来,是当前热点。

**本项目的定位**:运动控制 + 仿真 RL + 域随机化,是目前 sim2real 最成熟、最不依赖数据采集的一条路。
作为入门是对的选择——有 CAD 模型就能开工,不用先有真机采数据。但要知道它不是具身智能的全部。

延伸阅读(核实过的综述):
[腿足机器人模仿学习综述](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1678567/full) ·
[机器人 RL 分类与趋势](https://arxiv.org/html/2510.21758v3) ·
[深度 RL 真实世界落地综述](https://arxiv.org/html/2408.03539v1)

一句话理解这条路线:传统控制是"人建模型→推导控制律";学习控制是"人定义什么算好→几千个仿真分身试错→压成一个小 MLP"。
**难题没消失,只是从『设计控制器』搬到了『设计奖励 + 把仿真做准』。** 这就是为什么本项目的经验手册
(`src/microduck_rl/AGENTS.md`)九成篇幅在讲奖励和物理对齐,网络结构一句话带过(四层 MLP,约 20 万参数)。

### 实践路线(四阶段)

| 阶段 | 练什么 | 产出 | 碰代码吗 |
|---|---|---|---|
| **1. 学会看** | 回放不同 checkpoint 看行为演化,同时对着 TensorBoard 找对应指标 | 「数字 ↔ 行为」映射表 | 否 |
| **2. 学会改** | 奖励消融:一次只改一项权重,跑 200–500 轮看变化 | 自己的实验记录表 | 改一个数字 |
| **3. 学会定义任务** | 挑个没训过的任务(SitStand / BallKick)走完整闭环 | 独立完成"定义→训练→部署" | 读配置 |
| **4. 换机器人** | URDF 导出、执行器辨识 | —— | 以后再说 |

适合这套方法的第三方设备:**有 CAD 模型、执行器可建模、任务是运动控制类**(走、平衡、简单动作)。
不适合的:需要精细操作或视觉语义理解的——那要走模仿学习那一支,得先有真机采数据,是另一套工程。
四个阶段走完再往外扩,下一站就是它。

阶段 1 的现成素材:`2026-09-16_09-07-17_velocity` 这个 run 有 **201 个 checkpoint(12499 → 62499,间隔 250)**,
是一部完整的"学习过程录像"。建议挑 `model_12499` / `24999` / `39999` / `62499` 四个依次回放。

### 早先的阶段目标(已完成)

先本机 CPU 推理 → 再本机 GPU 训练。两步都已打通。

## 运行环境:Windows 11 + WSL2(实际跑命令的地方)

**本项目的实际运行环境是 Windows 11 主机 + 其上的 WSL2(Ubuntu 24.04)**,不是纯 Windows,也不是一台独立的 Linux 机器。两边各管一摊,下文代码块的语言标签标明该命令在哪边敲:`powershell` = Windows,`bash` = WSL。

| 环境 | 负责什么 | 仓库位置 | 怎么进 |
|---|---|---|---|
| **Windows 11 原生**(PowerShell) | 推理:`run_infer*.ps1`,弹原生 MuJoCo 窗口看鸭子;**GPU 训练也能跑**(已实测) | `D:\robot\microduck\` | 开 PowerShell |
| **WSL2 Ubuntu 24.04** | GPU 训练、`play` 回放、导出 ONNX、TensorBoard;以后的 duck-sim 全栈模拟只能在这 | `~/robot/microduck/src/microduck_rl`(WSL 自己的文件系统,**不是** `/mnt/d`) | PowerShell 里 `wsl -d Ubuntu` |

**两边训练速度实测基本相同**(同机同卡、torch 2.9.1+cu128、warp 1.12.0、seed 42、1024 envs × 200 迭代):WSL **7:28**(2.24 s/iter)vs Windows **7:56**(2.38 s/iter),差 6%,在散热波动范围内。所以选哪边不看速度,看别的:

| | Windows 原生 | WSL2 |
|---|---|---|
| 看画面 | 原生 MuJoCo 窗口,`play` 不用 viser | 只能开网页查看器 |
| 文件搬运 | 训练/导出/推理同一个盘,`policies\` 直接可用 | 导出的 onnx 要拷过 `/mnt/d` |
| 上游支持 | 自己补的(`pyproject.toml` 加了 win32 的 cu128 索引),出怪问题没人兜底,`git pull` 还可能冲突 | 官方支持的路线 |
| duck-sim | 跑不了(Rust + Linux) | 只能在这 |

⚠️ 基准测试要用**真实规模**:64 envs 下测出"Windows 慢 35%"是假象(小批量时开销占主导),1024 envs 才是真实工况。

要点:

- 发行版名就叫 `Ubuntu`(rootfs 导入在 `D:/wsl/Ubuntu`),默认用户 `robot`,免密 sudo
- 两边是**两份独立的仓库副本**,改了一边另一边不会变;跨环境传文件走 `/mnt/d/...`(例如把导出的 ONNX 拷回 Windows 的 `policies\`)
- 仓库放在 WSL 内部而不是 `/mnt/d` 是故意的:跨文件系统 I/O 慢好几倍
- WSL 里没有显示器,原生 MuJoCo 窗口开不了 → 在 WSL 中一律用网页查看器(`play` 的 viser、TensorBoard),Windows 浏览器开 `localhost:<端口>`(已切 mirrored 网络模式,端口互通)
- GPU 两边都直接可用(RTX 3060 Laptop):WSL 和 Windows 的 venv 里都是 torch `2.9.1+cu128` + warp 1.12.0,都认得到 sm_86
- 从 Git Bash 调 `wsl.exe` 要加 `MSYS_NO_PATHCONV=1`,否则路径参数会被改坏(详见下文)
- 另有第三处**讨论沙箱**(一台独立的 Ubuntu,AI 助手在那儿读代码、写文档和脚本,**不跑任何真实负载**)。它够不到这台机器,文件靠 XFTP 手动同步——三处环境的分工、路径换算和同步约定见根目录 `AGENTS.md`

## 两个仓库的分工

| 目录 | 是什么 | 技术栈 |
|---|---|---|
| `src/microduck/` | 真机机载运行时("大脑"):守护进程、50 Hz 控制回路、加载 ONNX 策略 | Rust |
| `src/microduck_rl/` | 策略训练("学校"):MuJoCo Warp + PPO,13 个任务,导出 ONNX | Python (uv 管理) |

关键概念:训练 = 4096 只仿真鸭子试错学新动作(吃 GPU);推理 = 拿训练好的 `policy.onnx` 照本执行(CPU 就够)。策略共享 61 维观测契约(48 本体感知 + 13 指令),输入 `[1,61]` → 输出 `[1,14]` 舵机目标。

## 三个核心词汇的关系

- **模拟(仿真)**:MuJoCo 算出来的假物理世界,练功房。存在意义 = 真机试错太贵,假鸭子摔一百万次零成本。
- **训练**:在模拟里让几千只假鸭子试错,对了加分错了扣分,把"会走路"压缩成一个 policy.onnx 文件(= 策略)。训练离不开模拟。
- **推理**:拿 policy.onnx 照本执行,每秒 50 次输入状态→输出 14 舵机目标,不学习纯执行。推理不挑场地:喂假鸭子 = 现在玩的,喂真鸭子 = 机器人上岗。

```
模拟(场地) → ①训练 → policy.onnx(本事) → ②推理@模拟(验货,现在这步) → ③推理@真机(上岗)
```

一句话:**模拟是场地,训练是学,推理是用**。②→③那道坎叫 **sim2real**(模拟到现实的差距),本项目一半功夫(BAM 舵机模型、域随机化)都在缩小它。

## 本机环境现状(已核实)

硬件(两个环境共用同一台机器):

- Windows 11,RTX 3060 Laptop **6GB 显存**,驱动 591.86

Windows 侧(推理):

- Python 3.12.6;`uv` 装在 `%USERPROFILE%\.local\bin\uv.exe`,**不在 PATH 里**
- `D:\robot\microduck\src\microduck_rl\.venv` 已通过 `uv sync` 建好(之前 Doubao 的 setup.ps1/setup2.ps1 干的)
- torch 已换成 **CUDA 版 `2.9.1+cu128`**:`pyproject.toml` 里给 `sys_platform == 'win32'` 加了 `pytorch-cu128` 索引(不加的话 Windows 上 PyPI 默认给 CPU 轮子 `2.9.1+cpu`,`cuda.is_available()==False`)。日常用法仍是根目录三个 `run_infer*.ps1`(ONNX 推理);torch 换 GPU 版之后,Windows 在技术上也具备跑 `play` 回放的条件(有原生显示器,不用 viser),但没实测过

WSL 侧(训练):

- WSL2 **Ubuntu 24.04 已装好**(rootfs 导入到 `D:/wsl/Ubuntu`,搭建过程见第二步),`~/robot/microduck/src/microduck_rl` 下 `uv sync` 完成
- torch `2.9.1+cu128`,CUDA 可用;warp 1.12.0 认到 RTX 3060(sm_86)
- 网络已切 mirrored 模式,Windows 系统代理(127.0.0.1:7890)在 WSL 内可用(详见「WSL 使用本机系统代理」)

## 路线规划

### 第一步:CPU 推理 ✅ 已搭好

**日常使用:在 PowerShell 里跑一条命令即可**

```powershell
D:\robot\microduck\run_infer.ps1
```

MuJoCo 窗口弹出、鸭子站好后按键控制。**已打补丁:MuJoCo 窗口和终端里按键都有效**(在窗口里按字母键会顺带触发 MuJoCo 自带的显示开关,画面样式可能变化,无伤大雅;想干净就在终端里按)。

| 按键 | 作用(注意:速度是"一步到位"不是逐渐加减) |
|---|---|
| ↑ | 前进(直接给最大前进速度) |
| ↓ | 后退(直接给最大后退速度) |
| ← / → | 左/右横移(螃蟹步,不是转弯!) |
| A / E | 左转 / 右转(转弯用这个) |
| 空格 | 停(速度清零,自动切回站立策略) |
| Y | 坐下 ↔ 站起 |
| R | 前滚翻 |
| P | 随机推一把(测抗扰) |
| T | 暂停/恢复策略推理 |
| B / H | 切到身体姿态 / 头部控制模式(方向键含义随之改变,再按一次退出) |
| Q | 退出 |

**在 MuJoCo 窗口里按其它字母键会触发查看器自带的可视化调试开关**——只改显示、不影响物理和策略,**再按一次同一键即恢复**。已实测对照(MuJoCo 3.10 官方快捷键表,`mujoco.mjVISSTRING/mjRNDSTRING`):

| 键 | 功能 | 现象 |
|---|---|---|
| W | Wireframe 线框渲染 | 地面/物体变线条 |
| T | Transparent 透明化 | 鸭子变透明(⚠️ T 同时也是"暂停策略推理"键,两个功能都会触发) |
| A | Auto Connect 关节连线 | 部件间出现蓝色连线 |
| S | Shadow 阴影 | 场景变暗 |
| D | Static Body 静态物体显隐 | 地板消失(地板是静态物体) |
| F | Contact Force 接触力箭头 | 接触处长出力箭头(躺地时头上也有) |
| G | Fog 雾效 | 顶部/远处变暗 |
| X | Texture 纹理开关 | 变平面亮色,像过曝 |
| C | Contact Point 接触点 | 接触处黄色标记 |
| N | Island 约束孤岛着色 | 整鸭变黄 |
| H / J / M / I | 凸包 / 关节轴 / 重心 / 惯量 | 学习物理仿真时挺有用,可玩 |

想画面干净就只在**终端**里按控制键(终端按键不经过 MuJoCo 窗口,不会误触这些开关)。

#### 当时的搭建步骤(已完成,重装才需要)

1. `uv sync` 建好 `src\microduck_rl\.venv`(CPU 版 torch 即可满足推理)
2. 下载官方策略到 `D:\robot\microduck\policies\`(9 个 onnx:走路/站立/坐站/捡地/踢球 ×2/翻滚/轮滑 ×2,外加 manifest.json 等):
   ```powershell
   # 直连 HF 被墙且本机代理(127.0.0.1:7890)常不在线 → 用国内镜像并绕过代理
   $env:HF_ENDPOINT="https://hf-mirror.com"; $env:NO_PROXY="*"; $env:HTTP_PROXY=""; $env:HTTPS_PROXY=""
   & "D:\robot\microduck\src\microduck_rl\.venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('pollen-robotics/microduck-policies', local_dir=r'D:\robot\microduck\policies')"
   ```
3. **给 `scripts/infer_policy.py` 打了 Windows 补丁**(两处):① 原脚本用 Linux 专用 `termios` 读键盘,Windows 崩 → `termios` 导入失败时回退 `msvcrt`;② 原脚本只收终端按键、MuJoCo 窗口按键无效(窗口还常抢焦点,导致"按键没反应") → 给 viewer 加了 `key_callback`,窗口内按键同样生效。补丁在本地仓库,`git diff` 可查。⚠️ 若 `git pull` 覆盖该文件需重打(症状:`No module named 'termios'` 或窗口按键无效)
4. 验证通过:standing 策略下鸭子稳定站立(trunk_z≈116mm),4 个策略均加载,输入 `[1,61]` → 输出 `[1,14]`

⚠️ **写 .ps1 脚本的坑**:Windows PowerShell 5.1 会把无 BOM 的 UTF-8 当 ANSI 读,中文变乱码。根目录曾叫"具身智能"(已改名为 robot,路径不再含中文),当时就是中文路径乱码导致 `Set-Location` 静默失败。现有脚本的注释/输出仍含中文,所有含中文的 `.ps1` 仍必须存成 **UTF-8 带 BOM**(报错特征:`无法加载模块".venv"`之类的莫名 CommandNotFound)。

### 第二步:本机训练 ✅ 已搭好(WSL2 Ubuntu 24.04)

**日常使用:在 PowerShell 里进 WSL 跑训练**

```powershell
wsl -d Ubuntu                     # 进入 Ubuntu(默认用户 robot,免密 sudo)
```

```bash
cd ~/robot/microduck/src/microduck_rl
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024   # 训练(6GB 显存从 1024 起步,别开 4096)
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 64 --agent.max-iterations 5   # 冒烟测试(仓库铁律:大 run 前必跑)
```

已验证:torch 2.9.1+cu128 CUDA 可用,warp 1.12.0 认到 RTX 3060(sm_86);冒烟测试通过(所有惩罚项 ≤ 0,nan_state=0,1.33s/iter)。一个能走的步态预计 4~8 小时;正式大 run 可加 `--hf-jobs` 扔 Hugging Face 云 GPU。

**也可以在 Windows 原生跑训练**(速度和 WSL 一样,见上文对比)。`uv.exe` 不在 PATH 里,所以要写全路径;先设一次变量,本窗口内后续都能用:

```powershell
$env:WANDB_MODE="offline"
$uv = "$env:USERPROFILE\.local\bin\uv.exe"
cd D:\robot\microduck\src\microduck_rl
& $uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 64 --agent.max-iterations 5   # 冒烟
& $uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024                          # 正式训练
```

⚠️ **PowerShell 粘贴长命令会被截断**(实测 160 多个字符就被切掉,后面的参数直接丢失,于是闷头按默认值跑)。所以命令要拆短、用变量;**每次开跑先看一眼 `Learning iteration 0/N` 的分母对不对**,不对立刻 Ctrl+C。

#### 已有的训练履历(阶段 1 的素材)

WSL `~/robot/microduck/src/microduck_rl/logs/rsl_rl/velocity/` 下:

| run 目录 | 存档 | 是什么 |
|---|---|---|
| `2026-09-15_11-53-46` / `12-01-54` / `12-10-04` | `model_4`(各 2 个) | 冒烟测试 |
| `2026-09-15_12-01-14` | 0 个 | 起了就停 |
| `2026-09-15_12-26-40` | `model_12500`(51 个) | 第一次正式训练,到 12500 |
| `2026-09-16_09-07-17` | **`model_62499`(201 个)** | 从 12499 续训,再跑满 50000 |

所以"6 万多轮" = 12500 + 50000 两段拼起来(201 个存档 × 250 间隔 = 50000,62499 − 50000 = 12499 正好接上)。
第二段停在 62499 是因为 `--agent.max-iterations` 默认 50000 跑满了。

Windows 侧 `logs\rsl_rl\velocity\` 下另有 3 个 run(2026-09-18),最多到 `model_1750`,是验证 Windows 能否训练时留下的。

#### 训练统计界面:TensorBoard(本机网页,看曲线)

每次训练自动往 `logs/rsl_rl/velocity/<run目录>/` 写 TensorBoard 事件文件,纯本地、不依赖外网。想看训练曲线,另开一个 WSL 终端:

```bash
cd ~/robot/microduck/src/microduck_rl
uv run tensorboard --logdir logs/rsl_rl
```

然后 **Windows 浏览器打开 `http://localhost:6006`**(mirrored 网络下 WSL 端口即 Windows localhost)。停止:终端 Ctrl+C;后台残留用 `pkill -f tensorboard` 清。

SCALARS 页按前缀分组,训练时重点盯三条(AGENTS.md 的读法):

| 看什么 | 在哪 | 判据 |
|---|---|---|
| 总奖励在涨 | `Train/mean_reward` | 持续上升 |
| **主任务项**在涨 | `Episode_Reward/track_linear_velocity` | 总奖励光靠正则项涨是假象,主任务项必须自己在涨 |
| 惩罚项符号正确 | `Episode_Reward/` 下的 `action_rate_l2`、`body_ang_vel` 等 | **全部 ≤ 0**,出现正值 = 奖励符号写反,策略在刷漏洞 |

另外 `Episode_Termination/nan_state` 应恒为 0(物理数值没爆炸),`fell_over` 前期高后期降是正常学习轨迹。

说明:TensorBoard 是纯监控,只能看不能改;中途调参的方式是 Ctrl+C 停训练→改配置→按上面"继续训练"续跑。wandb(云端,项目名 `mjlab_microduck`)功能更强但要注册账号,不想用就 `export WANDB_MODE=offline`,不影响训练和 TensorBoard。

#### 中断与继续训练

训练可以随时 **Ctrl+C** 中断:每 250 迭代自动存一个 checkpoint(`logs/rsl_rl/velocity/<run目录>/model_XXXX.pt`),最多损失最近 250 迭代的进度,已存的档不会作废。

继续训练(复制即用,自动找最新 run 的最新存档):

```bash
cd ~/robot/microduck/src/microduck_rl
RUN=$(ls -td logs/rsl_rl/velocity/*/ | head -1)
CKPT=$(basename $(ls $RUN/model_*.pt | sort -V | tail -1))
echo "从 $RUN 的 $CKPT 继续"
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024 \
    --agent.load-checkpoint "$CKPT" --agent.resume True
```

参数说明:

| 参数 | 作用 | 注意 |
|---|---|---|
| `--agent.resume True` | 声明"这是续训不是新训练":恢复网络权重、优化器状态和迭代计数 | 不加这个只加 load-checkpoint 是没用的 |
| `--agent.load-checkpoint model_XXXX.pt` | 从哪个存档继续,**只写文件名**(如 `model_12000.pt`),不带目录 | 默认到本实验最新的 run 目录里找;想从旧 run 续,加 `--agent.load-run <run目录名>` |
| `--env.scene.num-envs 1024` | 并行环境数,**要和原训练保持一致** | 改了数值上也能跑,但学习节奏会变,续训尽量不改 |
| `--agent.run-name xxx`(可选) | 给续训段起个名字,方便在日志/TensorBoard 里区分 | 官方示例用 `--agent.run-name resume` |
| `--agent.max-iterations N`(可选) | **再跑 N 轮**(不是"跑到第 N 轮"):续训时是从当前存档往后加 N | 本任务默认 50000。WSL 那次 62499 = 12499 存档 + 50000,正是这个语义。⚠️ 参数名是**连字符**(`--help` 里列的是 `--agent.max-iterations`);漏掉这个参数就会闷头跑满默认值,所以开跑后**第一眼看 `Learning iteration 0/N` 的分母对不对** |

续训会新建一个 run 目录(时间戳命名),从加载的迭代数继续往上计——TensorBoard 里新旧曲线会分成两条 run,横轴迭代数是接上的。

#### 训练中/训练后看效果:`uv run play`(3D 查看器)

训练是 1024 个环境在 GPU 里无渲染地刷数据(开渲染会慢几个数量级),所以**训练本身看不到画面**;想直观看"鸭子现在学成什么样",用 `play` 指令——它加载一个 checkpoint,放几只鸭子进带 3D 画面的仿真里跑给你看。**纯观看,不训练**,训练不用停,另开一个 WSL 终端即可。

复制即用(自动找最新 run 的最新 checkpoint):

```bash
cd ~/robot/microduck/src/microduck_rl
RUN=$(ls -td logs/rsl_rl/velocity/*/ | head -1)
CKPT=$(ls $RUN/model_*.pt | sort -V | tail -1)
echo "回放: $CKPT"
WANDB_MODE=offline uv run play Mjlab-Velocity-Flat-MicroDuck \
    --checkpoint-file "$CKPT" --num-envs 2 --viewer viser
```

然后 **Windows 浏览器打开 `http://localhost:8080`** 就能看到 3D 画面。看完在终端 **Ctrl+C 关掉**——play 和训练共用 6GB 显存,别让它一直挂着。

说明:
- `--checkpoint-file` 指定回放哪个存档;checkpoint 每 250 迭代存一个在 run 目录下(`model_5250.pt` = 第 5250 迭代),想看进化过程可以隔一两千迭代换新档看一次
- `--num-envs 2` 只放 2 只鸭子,省显存
- `--viewer viser` 用网页 3D 查看器(WSL 里没显示器,原生 MuJoCo 窗口开不了,必须用这个)
- `WANDB_MODE=offline` 跳过 wandb 登录(play 默认想从 wandb 拉 run,本地文件回放用不到)
- 换任务时把 `Mjlab-Velocity-Flat-MicroDuck` 和 `velocity` 目录名对应换掉(`uv run list-envs` 看任务列表)

预期管理:5000 迭代左右还早(稳定步态要 4000–6000+),看到走得歪歪扭扭是正常进度。

#### 训练结果导出与使用(把自己的策略装进 run_infer.ps1)

训练产出两种文件,关系像"学员档案"和"驾照":

- **`model_XXXX.pt`**(存档):PyTorch 格式,在 run 目录下每 250 迭代存一个。只有训练代码认识,用于 play 回放和续训,不用于部署。
- **`policy.onnx`**(成品):开放行业标准格式,CPU 可跑、跨语言跨平台。官方 `policies/` 里那 9 个就是这种。训练的终点就是产出自己的 ONNX。

对某个存档满意后,三步用起来(前两步在 WSL 终端):

```bash
# ① 导出 ONNX(必须用这个脚本——它把观测归一化参数烤进文件,漏了则策略部署即废,AGENTS.md 铁律)
cd ~/robot/microduck/src/microduck_rl
RUN=$(ls -td logs/rsl_rl/velocity/*/ | head -1)
CKPT=$(ls $RUN/model_*.pt | sort -V | tail -1)
echo "导出: $CKPT"
uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck \
    --checkpoint-file "$CKPT" --onnx-file my_walking.onnx

# ② 拷到 Windows 的策略目录
cp my_walking.onnx /mnt/d/robot/microduck/policies/
```

③ 编辑 `run_infer.ps1`,把 `--walking` 行换成自己的文件:

```powershell
--walking  "$P\my_walking.onnx" `
```

然后照常跑 `run_infer.ps1`——同一个 MuJoCo 窗口、同一套按键,只是走路的"本事"换成了自己训练的。改回官方文件即可对比效果。

对照实验:四个脚本对比"训练到底训练了什么"(建议按 0 → 1 → 2 → 官方的顺序看,先看最差的,后面的进步才有参照):

| 脚本 | 跑的策略 | 现象 |
|---|---|---|
| `run_infer0.ps1` | **未训练基准**(默认 random;`.\run_infer0.ps1 zero` 切 zero 模式) | random = 随机初始网络,触电式抽搐瘫倒;zero = 输出恒 0,僵在默认姿势 |
| `run_infer1.ps1` | 自训早期版 `my_walking.onnx` | 来源存疑,见下 |
| `run_infer2.ps1` | 自训最终版 `2026-09-16_09-07-17_velocity.onnx` | 文件内嵌 `model_62499.pt` 标记,**确认是 62499 迭代的成果** |
| `run_infer.ps1` | 官方训练好的策略 | 正常听指挥走路 |

⚠️ `my_walking.onnx` **查不出是哪个 checkpoint 导出的**(文件里没留标记,不像 `2026-09-16_09-07-17_velocity.onnx`
内嵌了 `model_62499.pt`),推测来自 12500 那次 run,未证实。
**以后导出一律把迭代数写进文件名**(`my_walking_62499.onnx`),否则过两轮就分不清哪个是哪个。

基准文件的来历(重装才需要):`export.py` 的 `--agent random/zero` 导出路径有上游 bug(`runner` 未定义),实际做法是——`untrained_random.onnx` 用正常导出路径导 `model_0.pt`(第 0 迭代存档 = 训练的真实起点);`untrained_zero.onnx` 是把它的输出层权重清零制成(onnx 库改图,验证输出恒 0)。两个文件在 `policies\` 下。

以后可选:`uv run publish` 把策略发布到 Hugging Face(像官方那 9 个那样);真机通过 `robotctl policy add` 加载同一个 ONNX——仿真和真机用的是同一张"驾照",这就是 sim2real。

#### 当时的搭建步骤(已完成,重装才需要)

1. 商店版 Ubuntu 26.04 注册失败(`0x80071772`,WSL 2.2.4 太旧且 `wsl --update` 被网络/权限挡住)→ 改用 **rootfs 导入**:从 USTC 镜像下载 Ubuntu 24.04 WSL rootfs 到 `D:/wsl/`,`wsl --import Ubuntu D:/wsl/Ubuntu <rootfs.tar.gz> --version 2`
2. 建默认用户 robot(`/etc/wsl.conf` 设 `default=robot` + `systemd=true`),apt 换 USTC 源
3. 仓库复制到 **WSL 自己的文件系统** `~/robot/microduck/src/microduck_rl`(不能放 `/mnt/d`,跨文件系统 I/O 慢好几倍;排除 `.venv`/`__pycache__`/`logs`)
4. GitHub 在 WSL 里直连不通(bam 是 git 依赖)→ git 全局 URL 重写走代理:`git config --global url."https://gh-proxy.com/https://github.com/".insteadOf "https://github.com/"`(uv 调系统 git,所以对 uv 生效且不用改 uv.lock)
5. `UV_HTTP_TIMEOUT=600 uv sync` —— Linux x86_64 上 PyPI 的 torch 轮子自带 CUDA(nvidia-* 依赖),不用像 Windows 那样换索引

#### WSL 使用本机系统代理

本机系统代理挂在 `127.0.0.1:7890`。WSL 默认 NAT 网络模式下 WSL 里的 127.0.0.1 是它自己,够不着 Windows 的代理(每次调 wsl 都弹的"检测到 localhost 代理配置,但未镜像到 WSL"警告就是在说这个)。已在 `%USERPROFILE%\.wslconfig` 切换到 **mirrored 镜像网络**:

```ini
[wsl2]
networkingMode=mirrored   # WSL 与 Windows 共享网络栈,localhost 代理可用
autoProxy=true            # 自动把 Windows 系统代理注入 WSL 环境变量(http_proxy 等)
dnsTunneling=true
```

改完 `wsl --shutdown` 重启生效。已验证:代理在线时 WSL 里 GitHub、HuggingFace 均可直连;`http_proxy`/`https_proxy`/`no_proxy` 随 Windows 代理设置自动同步,代理关掉时这些变量也会消失。

由此形成两层网络容错,**不需要手动切换**:
- 代理在线 → 一切直连(走 autoProxy 注入的代理)
- 代理离线 → git 走 gh-proxy.com 重写(上面第 4 步,仍然保留),pip/apt 走 USTC 源,HF 走 hf-mirror

镜像模式的额外好处:Windows 和 WSL 互通 localhost——以后在 WSL 里开 tensorboard / viser 查看器,Windows 浏览器直接访问 `localhost:<端口>` 就行;wandb 也可以在线记录了(之前冒烟测试用的 `WANDB_MODE=offline` 不再是必须)。

⚠️ **从 Git Bash 调 `wsl.exe` 的坑**:MSYS 路径转换会把 `/mnt/d/...`、URL 等参数改坏(症状:`No such file or directory` 带 Git 安装路径前缀、循环变量神秘变空)。加 `MSYS_NO_PATHCONV=1` 前缀,复杂命令写成 `.sh` 脚本放 `D:/wsl/` 再 `wsl -d Ubuntu -- bash /mnt/d/wsl/xxx.sh`。(AI 助手在独立 Ubuntu 沙箱里工作,够不到 `wsl.exe`,这条只在你自己用 Git Bash 时适用。)

⚠️ Windows 原生路线后来也补齐了(torch 换成 cu128,warp 的 Windows 轮子本来就认 GPU),技术上已无障碍,但没实测过。训练仍走 WSL2——那是官方支持的路线。

### 以后可选:duck-sim 全栈模拟(WSL2 已就绪)

主仓库 `scripts/duck-sim`:真机的全套 Rust 守护进程 + MuJoCo 身体,用 `robotctl` 像操作真鸭子一样操作,用于学习机载软件架构。

## 重要文档入口

- `AGENTS.md`(根目录) — 三处环境(讨论沙箱 / Windows / WSL)的分工、路径换算、XFTP 同步约定;给 AI 助手看的操作规则
- `src/microduck_rl/AGENTS.md` — 训练/奖励设计/sim2real 的经验手册(精华,必读)
- `src/microduck_rl/README.md` — 任务列表、命令速查、发布流程
- `src/microduck/docs/robot/simulation.md` — duck-sim 用法
- `src/microduck/docs/design/architecture.md` — 机载系统架构

## 进度记录

- [x] clone 两仓库;`uv sync` 完成(但 torch 为 CPU 版);了解项目结构与训练/推理区别
- [x] 跑通 CPU 推理:官方策略已下载到 `policies\`,infer_policy.py 打了 Windows 键盘补丁,`run_infer.ps1` 一键启动
- [x] 根目录由"具身智能"改名为 robot:已更新 README、run_infer.ps1、setup*.ps1 里的路径;`.venv` 因 uv 入口 exe 内嵌旧绝对路径而失效,用 `uv sync --reinstall` 重建后恢复
- [x] 训练环境就绪:WSL2 Ubuntu 24.04(rootfs 导入到 `D:/wsl/Ubuntu`),仓库在 WSL 内 `~/robot/microduck/src/microduck_rl`,torch 2.9.1+cu128 CUDA 可用
- [x] 冒烟测试通过(64 envs × 5 iters,惩罚项全 ≤ 0,nan_state=0,1.33s/iter)
- [x] WSL 网络切换 mirrored 模式(`.wslconfig`),本机系统代理(127.0.0.1:7890)在 WSL 内可用,GitHub/HF 可直连;gh-proxy/USTC/hf-mirror 作为代理离线时的兜底
- [x] 讨论环境迁到独立 Ubuntu 沙箱(AI 助手不再跑在 Windows 侧);三处环境分工与 XFTP 同步约定写入根目录 `AGENTS.md`
- [x] Windows 原生训练打通并与 WSL 实测对比(1024 envs × 200 迭代:WSL 7:28 / Windows 7:56,差 6%),两边都能训练
- [ ] 第一个自己训练的步态(从 `--env.scene.num-envs 1024` 起步)
