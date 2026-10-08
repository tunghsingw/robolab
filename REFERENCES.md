# REFERENCES.md — 资料库:内外信息来源与摘要

> **共同的资料库。** 每条资料记四件事:是什么(含可信度)、摘要、能回答什么(对应学习阶段)、注意。
>
> **用法**:查信息前先看这里有没有现成来源;用了新来源就按第七节格式记进来。
> 用户转来的文章不是见到就收:先判断对学习有没有价值,有价值才记(`AGENTS.md` 第二节第 11 条)。
> **规矩**:凡是"领域现状 / 技术分类 / 谁家用什么方法 / 论文结论"这类问题,**先查这里,查不到就联网核实,核实完记进来**。
> 不要凭记忆答——本项目 README 最初那版"两条技术栈"的分类就是凭记忆写的,三处硬伤;后来"行为克隆占比"又张冠李戴过一次(见三·7)。
>
> **收录范围:只收具身智能 / 机器人学习相关的资料。** 通用开发话题(git、包管理、工具链)查完就用,不进这个文件。
>
> **标记**:`✓` = 已核实、读过原文;`?` = 待核实,引用前先查。
> **可信度**分两种问题看:问"它是什么、怎么用",官方文档和源码最权威;问"效果如何、结论对不对",按
> 同行评审(期刊、会议论文)> 预印本 > 技术博客 / 观点文章 > 厂商自述、媒体报道 > 二手索引 排。每条的"是什么"里写明属于哪类。

## 〇、一页总览:问题 → 先看哪条

| 要解决的问题 | 先看 | 阶段 |
|---|---|---|
| 某个命令、某个任务 ID、当前配置 | 一·2 上游 README;一·5 训练日志开头的表 | 0–1 |
| TensorBoard 的 `--logdir` 该指到哪一级、怎么叠多次训练对比 | 二·9 | 0–1 |
| 为什么要几千个环境并行、mjlab + rsl_rl 这套范式从哪来 | 四·2 | 1–2 |
| 奖励怎么设计、为什么这项要 ≤ 0、课程怎么排 | 一·1 上游经验手册 | 2–3 |
| 某个奖励 / 观测项在框架里怎么注册 | 二·3 mjlab(以 1.3.0 为准) | 2–3 |
| PPO 超参数是什么意思 | 二·4 rsl_rl 源码 | 2 |
| actor 为什么不看线速度、critic 为什么能看 | 四·3 | 2–3 |
| MJCF 里某个属性(armature、condim…)的定义 | 二·2 MuJoCo XML 参考 | 1、4 |
| 舵机为什么要建到电压环、怎么给新舵机辨识 | 二·6 BAM 文档;三·8 BAM 论文;四·1、四·4 | 2、4 |
| sim2real 出问题从哪查起、仿真工具怎么分层(物理引擎 / 仿真平台 / 学习框架)、mjlab 和 Isaac Lab 的关系、怎么选型 | 五·2 | 领域地图、1、2、4 |
| 不同物理引擎(MuJoCo / MuJoCo Warp / PhysX / Genesis)差多少、换引擎评估要查什么 | 五·1 | 2、4 |
| 机器人仿真引擎和游戏 / 网页 3D 引擎的物理有什么不同 | 五·3;五·1 | 领域地图 |
| 想换个物理引擎训练同一只 microduck 做对照 | 六·2 | 2、4 |
| 别的"导入 URDF → 一键训练"平台怎么做(格物 / Unity ML-Agents)、前馈 + RL | 六·1 | 3、4 |
| 想给步态"自然感"、想用参考动作 | 四·5 AMP;三·1 | 3 |
| CAD 怎么导出成 MJCF | 二·5 onshape-to-robot | 4 |
| 换一台别的机器人,别人怎么配训练环境 | 三·9 知识库的 Locomotion 与工程部署分页 | 4 |
| 策略上真机后谁在调用它 | 一·3、一·4 机载文档 | 4 |
| 运动控制 vs 操作、RL vs IL vs MPC 的关系 | 三·1、三·3、三·5 | 领域地图 |
| RL 方法怎么分类、"我的策略处于哪个部署成熟度" | 三·2 | 领域地图 |
| 操作方向:能不能也用仿真 RL、模仿学习有哪些方法 | 三·4;三·7 | 领域地图 |
| 工业界怎么把大模型策略和 MPC 分层、动作块实例 | 三·6 | 领域地图 |
| "让 AI 编程智能体开发机器人"(Agentic Robotics)、逆物理 / Real2Sim 自动化 | 三·10 | 领域地图、4 |

## 一、项目内部(最优先,不用联网)

### 1. `src/microduck_rl/AGENTS.md` — 上游作者的经验手册 ✓
- **是什么**:Pollen Robotics 写给开发者和 agent 的手册,随 `upstream.repos` 锁定的 commit(3412ae5,2026-09-13)。每条规则都是踩坑换来的。
- **摘要**:九节——命令、仓库地图、不变量、建新环境流程、奖励设计规则、指令与观测、课程、训练运维、sim2real 坑。不变量:61 维观测(48 本体 + 13 指令)、14 舵机顺序、BAM 执行器、归一化器烤进 ONNX、策略无滤波、域随机化不累积。奖励铁律:每个惩罚项的 `Episode_Reward` 必须 ≤ 0;不设"到达即拿"的一次性大奖;正奖励不能以坏状态为门槛;正则项分"阻碍动作"和"平滑"两类,平滑项要在技能学会后再加;比较奖励看总量不看权重。指令槽永远不能全零,否则对应权重死掉。预算:简单动作约 1000 轮,步态 4000–6000 轮(4096 环境)。
- **能回答什么 / 阶段**:阶段 2 的主教材;阶段 3 建新任务的流程(挑最近的模板、先在仿真里验证物理假设、写配置测试、冒烟)。
- **注意**:【microduck 特有】和【通用】混写,读时要自己分开标。

### 2. `src/microduck_rl/README.md` — 上游用户手册 ✓
- **是什么**:同一 commit 的用户手册。
- **摘要**:五条快速命令(train / play / export / publish / infer_policy);任务表列了 13 个任务 + 齿隙变体(注册表实际 18 个基础任务,见阶段 0 第四节);执行器 BAM M6 XL330(电压控制、反电动势、摩擦)+ 电压 / 延迟 / 摩擦随机化;四个 MJCF 模型的分工表;发布时校验 `[1,61] → [1,14]`。
- **能回答什么 / 阶段**:阶段 0–1 查任务 ID、模型文件、命令。
- **注意**:`publish`、HF Jobs 本项目不用。

### 3. `src/microduck/docs/robot/simulation.md` — duck-sim 手册 ✓
- **是什么**:机载运行时仓库的"仿真鸭"使用手册(commit e9cca62,2026-09-13)。
- **摘要**:`robotd --sim` 通过 TCP 接一个 MuJoCo 身体(即 microduck_rl 的 duck-body),守护进程代码与真机一字不差;`up`(普通进程)与 `boot N`(容器)两种启动;实时率低于 1.0× 策略就站不稳,45 Hz 是健康门;`--sim` 不等于 `--fake`(后者无物理)。
- **能回答什么 / 阶段**:ONNX 在真实运行时里怎么被消费;以后在 WSL 跑 duck-sim 时看。
- **注意**:需要 Rust 构建 + microduck_rl 的 venv,只能在 Linux。

### 4. `src/microduck/docs/design/architecture.md` — 机载系统设计 ✓
- **是什么**:运行时 v1 设计文档(草稿,2026-07-22),写的是目标架构,不全是当前原型。
- **摘要**:7 个守护进程(robotd / configd / updaterd / btd / padd / mediad / tofd)+ `robotctl`,JSON-RPC over Unix socket;robotd 独占串口、跑 50 Hz 循环、掌握安全权,客户端只发意图;发布整目录原子切换 + 健康门 + 自动回滚。**真机 15 个舵机,第 15 个是嘴巴;策略只管 14 个关节,写回电机时嘴巴那一位由运行时另管**(细节在同目录 `robotd-design.md`)。
- **能回答什么 / 阶段**:阶段 4 部署认知——策略上机后谁调用它、谁保安全。
- **注意**:RL 学习阶段几乎不用读。

### 5. 训练日志开头的几张表 ✓
- **是什么**:每次 `train` 启动时打印的 ObservationManager、RewardManager、CurriculumManager、EventManager 表。
- **摘要**:当前**生效**的观测构成、奖励项与权重、课程项、随机化与扰动项。
- **能回答什么 / 阶段**:每次训练。改过参数是否生效、这个任务有几项奖励,看它最快也最准。
- **注意**:比读源码可靠,因为它反映的是运行时真实配置。

### 6. 本项目 `README.md` / `GLOSSARY.md` / `experiments/runs.md` / `policies/README.md` ✓
- **能回答什么**:学习目标与领域地图、进度 / 名词解释 / 有哪些训练存档 / 有哪些策略文件及来源。

## 二、官方文档

### 1. MuJoCo 文档 — https://mujoco.readthedocs.io/ ✓
- **是什么**:Google DeepMind 维护的官方文档,stable 对应 3.14(2026-09),更新活跃。
- **摘要**:Overview / Computation / Modeling / XML Reference / Programming / API / Python / MJX / MuJoCo Warp / Changelog。四个特色:广义坐标 + 凸优化软接触、腱、统一的抽象执行器模型、MJCF 建模语言。
- **能回答什么 / 阶段**:仿真器原理、接触怎么算、一步物理流水线是什么。阶段 1 看模型文件,阶段 4 建新模型。
- **注意**:本项目实际用 **mujoco 3.10.0**,与 stable 差几个小版本,行为有疑问查 Changelog。

### 2. MuJoCo XML 参考 — https://mujoco.readthedocs.io/en/stable/XMLreference.html ✓
- **是什么**:同上,单页约 1.3 MB,按元素逐一列属性。
- **摘要**:已确认定义:`joint/armature`(转子附加惯量,默认 0)、`joint/frictionloss`(干摩擦)、`geom/condim`(1 无摩擦、3 常规、4/6 加扭转 / 滚动)、`geom/contype` 与 `conaffinity`(32 位掩码,一方 contype 与另一方 conaffinity 有公共位才碰撞)、`body/freejoint`、`keyframe/key`。
- **能回答什么 / 阶段**:阶段 1–2 查机器人 XML 里的属性;阶段 4 写新 MJCF。
- **注意**:页面太大,用锚点(如 `#body-joint-armature`)直达。

### 3. mjlab — https://github.com/mujocolab/mjlab ✓
- **是什么**:mujocolab 的训练框架(Apache-2.0,论文 arXiv 2601.22074):Isaac Lab 风格的 manager 式 API + MuJoCo Warp(GPU)。
- **摘要**:docs 分四块——概念(entity、actuator、sensor、scene、terrain)、manager 层(observation、action、reward、termination、command、event、curriculum)、训练(rsl_rl、多卡、查看器、NaN 防护、导出场景)、迁移与 FAQ。`--agent zero|random` 可做 MDP 冒烟。
- **能回答什么 / 阶段**:阶段 2–3——奖励项 / 观测项怎么注册、环境配置长什么样。
- **注意**:**本项目训练用的是 PyPI 的 mjlab 1.3.0**(`microduck_rl` 写死 `mjlab==1.3.0`),`src/mjlab` 是参考 clone,已锁到 v1.3.0 与之对齐。读源码得出的结论以 1.3.0 为准。

### 4. rsl_rl — https://github.com/leggedrobotics/rsl_rl ✓
- **是什么**:ETH 机器人系统实验室的 RL 库(BSD-3),PyPI 名 `rsl-rl-lib`;提供 PPO、师生蒸馏、多卡。
- **摘要**:README 只有安装和引用,没有算法说明;要看 PPO 细节得读 `rsl_rl/algorithms/ppo.py`。
- **能回答什么 / 阶段**:阶段 2 看 PPO 超参数含义。
- **注意**:本项目锁 **5.0.1**(随 mjlab 1.3.0);没有本地 clone,源码在 `.venv` 里。

### 5. onshape-to-robot — https://onshape-to-robot.readthedocs.io/ ✓
- **是什么**:Rhoban 的 CAD 导出工具与文档,v1.8.3(2026-08)。
- **摘要**:章节:入门、设计期约定(自由度、命名、坐标系)、Configuration、URDF、SDF、MuJoCo、闭链、Processors。字段已确认:`ignore`、`post_import_commands` 在 Configuration 页;`joint_properties`、`geom_properties`、`equalities`、`additional_xml` 在 MuJoCo 页。本项目每个 `config_mjcf_*.json` 就是这些字段。
- **能回答什么 / 阶段**:阶段 4——自己的机器人从 CAD 到 MJCF。
- **注意**:本地配置用驼峰写法(`outputFormat`),文档是下划线(`output_format`),导出时用的工具版本可能更旧;复现导出前先核对版本。

### 6. BAM 文档与代码 — https://bam.readthedocs.io/ · https://github.com/Rhoban/bam ✓
- **是什么**:Rhoban 的舵机扩展摩擦模型库,配 ICRA 2025 论文(三·8)。
- **摘要**:Usage(MuJoCo CPU 控制器;mjlab 接入 `BamActuatorCfg` + 启动事件,`vin` / `kp_fw` 覆盖,`vin_range` 随机化)、Identification(单摆台架)、Theory(M1 库仑加粘性 → M2 Stribeck → M3 负载相关 → … → M6)。内置电机:XL330-M288-T、XL-320、MX-64/106、STS3215、eRob80。
- **能回答什么 / 阶段**:阶段 2 理解 sim2real 里执行器为什么要建到电压环;阶段 4 给新舵机做辨识,照它搭台架。
- **注意**:本项目用的是 git 分支 `mjlab_frictionloss` 的 1.0.1,不是 PyPI 版;文档写明兼容 mjlab 1.3。

### 7. microduck 上游 — https://github.com/pollen-robotics/microduck ✓
- **是什么**:Pollen Robotics 的 Rust 机载运行时,本地 clone 2026-09-13。
- **摘要**:约 25 cm、800 g,RK3566,50 Hz 控制环,总线上 15 个 XL330;策略契约固定 `obs[1,61] → act[1,14]`,加载时校验。docs 三层:robot(cheatsheet、duckctl、simulation、install-dev)、design(architecture、robotd-design、policy-channel、updater)、project。`policy-manifest.md` 定义策略清单格式(episodic / perpetual / scripted)。
- **能回答什么 / 阶段**:阶段 0–1 看 ONNX 在真机怎么被消费;阶段 3 发布策略。
- **注意**:全是【microduck 特有】。

### 8. microduck_rl 上游 — https://github.com/pollen-robotics/microduck_rl ✓
- **是什么**:训练仓库(Apache-2.0,3D 模型 CC BY-SA-NC),本地 clone 2026-09-13。
- **摘要**:mjlab 1.3.0 + PPO;任务见阶段 0 第四节;61 维观测 = 48 本体 + [twist 3, head_pose 4, body_pose 6];14 舵机布局 0–4 左腿、5–8 颈头、9–13 右腿;BAM M6 + 电压 / 延迟 / 摩擦随机化。代码:`tasks/mdp.py`(所有自定义奖励 / 事件 / 观测)、`microduck_*_env_cfg.py`(各任务配置)、`actuator/friction_dr_bam.py`;脚本 `export.py`、`infer_policy.py`。
- **能回答什么 / 阶段**:阶段 0–3 的主战场。
- **注意**:导出必须走 `scripts/export.py`;上游 develop 分支活跃,升级前看 diff。

### 9. TensorBoard README — https://github.com/tensorflow/tensorboard/blob/master/README.md ✓
- **是什么**:TensorBoard 官方仓库说明(Google),一手资料。
- **摘要**:`--logdir` 会**递归**遍历整棵目录树,凡是含 tfevents 曲线文件的子目录都当成一个 run 载入;所以可以指到单个 run、任务目录,或更上层的任意祖先目录。多个互不相干的目录可用 `--logdir_spec 名字1:路径1,名字2:路径2`,但官方不推荐(部分功能不可用),建议改用符号链接把它们归到一个目录下。后台默认每 5 秒(`--reload_interval`)重新扫描目录并读新数据,新出现的 run 也会被发现;2.3.0 起网页不再自动刷新,要手动刷新或在右上角齿轮里开 Reload data(自动重载)。
- **能回答什么 / 阶段**:阶段 0–1——`--logdir` 该指到哪一级、怎么把多次训练叠在一张图上对比。
- **注意**:目录越高、run 越多,启动时扫描越慢,左侧列表也越长。

## 三、领域地图:综述与观点

### 1. 腿足机器人模仿学习综述 — Frontiers in Robotics and AI, 2025 ✓
- **是什么**:期刊综述(同行评审,Frontiers 审稿偏宽),Mirza & Singh,2025-10 上线。https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1678567/full
- **摘要**:分析 35 篇四足 / 人形模仿学习工作。方法族:行为克隆 15 篇(43%)、AMP 23%、扩散 14%、MPC 蒸馏 9%。数据源:MPC 日志 11 篇(31%)、人类动捕 23%、动物动捕 14%、机器人自采 17%、视频 6%。结论之一:专家数据质量是 sim2real 成功最强的预测因子。
- **能回答什么 / 阶段**:领域地图;阶段 3 选参考动作 / 专家数据源。
- **注意**:"MPC 日志已成为最常用数据源、超过动捕"按**单类**计成立(31% > 23%、14%);两类动捕合计 37%,反而高于 MPC 日志。引用时说清口径。样本只有 35 篇。

### 2. 机器人 RL 分类与趋势 — arXiv 2510.21758 ✓(仅供分类参考)
- **是什么**:预印本,尼日利亚空军技术学院等,v1 2025-10,教科书式综述,原创结论少。
- **摘要**:MDP 到 DDPG / TD3 / PPO / SAC;四维分类:任务域(locomotion、导航、操作、人机交互、多机器人)、RL 形式、训练流水线、部署成熟度 L0(仅仿真)到 L5(商用)。
- **能回答什么 / 阶段**:领域地图;判断"我的策略处于哪个成熟度级别"。
- **注意**:"与控制论的结合方式"只有一段,想看控制 + 学习怎么混用看三·5。

### 3. 深度 RL 真实世界落地综述 — arXiv 2408.03539 ✓
- **是什么**:Tang 等,Peter Stone 组,2024-08,录用于 Annual Review of Control, Robotics, and Autonomous Systems(同行评审)。
- **摘要**:按真实世界成功度分四级评估各方向。四足 RL 已被 ANYbotics、Boston Dynamics 商用,主流是 PPO 零样本 sim2real;双足、无人机成熟度低;操作只在任务空间受限(抓取、手内操作、装配)时成功。成功模式 = 动力学易仿真 + 密集奖励 + 零样本迁移。
- **能回答什么 / 阶段**:领域地图;阶段 2 理解"运动控制为什么密集奖励加 sim2real 就够"。**"运动控制比操作成熟"的论据出自这里。**
- **注意**:截至 2024 年中,人形进展未涵盖。

### 4. 人形视觉灵巧操作 sim2real — arXiv 2502.20396 ✓
- **是什么**:Lin、Sachdev、Fan、Malik、Zhu,CoRL 2025。
- **摘要**:Fourier GR1 加多指手,Isaac Gym 训练零样本上真机;三任务(抓取放置、双手抬箱、双手交接);配方 = 自动 real-to-sim 调参 + 基于接触 / 物体目标的通用奖励 + 分而治之蒸馏 + 混合物体表征。已见物体 90%,新物体 60–80%。
- **能回答什么 / 阶段**:**操作方向也能做仿真 RL 的证据**;阶段 3 看"按接触 / 物体目标写奖励"的思路。
- **注意**:依赖摄像头,成功率不高。

### 5. 控制 + 机器学习融合分类 — Actuators 2026, 15(5):235 ✓
- **是什么**:期刊综述(MDPI,同行评审),Zhang 等,2026-04。https://www.mdpi.com/2076-0825/15/5/235
- **摘要**:三范式——学习辅助控制(控制器为主,学习做残差动力学 / 扰动估计 / MPC 调参)、控制辅助学习(策略为主,控制做监督:安全滤波、轨迹优化器当教师)、协同设计(可微规划器)。腿足常用"残差学习 + MPC / WBC"。
- **能回答什么 / 阶段**:领域地图;"MPC 蒸馏、残差 RL 各属哪类"。
- **注意**:直接抓取会被拦,需代理。

### 6. Atlas + TRI 大行为模型 — The Robot Report, 2025-08 ✓
- **是什么**:媒体报道,转述 Boston Dynamics 博客,无独立评测。https://www.therobotreport.com/boston-dynamics-tri-use-large-behavior-models-train-atlas-humanoid/
- **摘要**:遥操作建在 Atlas 的 MPC 之上;策略输入图像 / 本体 / 语言,30 Hz 控制全身;450M 参数扩散 Transformer,流匹配损失;每次预测 48 步动作块、执行 24 步;神经策略与遥操作共用同一控制接口。
- **能回答什么 / 阶段**:领域地图——工业界 MPC 与学习策略怎么分层。
- **注意**:厂商宣传口径。

### 7. 操作模仿学习综述 — arXiv 2508.17449 ✓
- **是什么**:预印本,Li 等(里昂中央理工、北航、大连理工),2025-08。
- **摘要**:精选 82 篇 2021–2025 操作 IL 工作,按动作生成(扩散、流匹配、回归、自回归)与任务规划(关键位姿、affordance)分类,逐篇给输入、先验、优缺点;汇总 CALVIN 等基准。
- **能回答什么 / 阶段**:领域地图——操作方向 IL 的方法谱系;与本项目的运动控制关系远。
- **注意**:**此文没有"行为克隆占比"的统计**;那个 43% 出自三·1 的腿足综述。本文件曾把它记错在这里。

### 8. BAM 论文 — arXiv 2410.08650,Duclusaud 等,ICRA 2025 ✓
- **是什么**:预印本(会议版 ICRA 2025),波尔多大学 / Inria / Rhoban。
- **摘要**:MuJoCo、Isaac Gym 默认的库仑 + 粘性摩擦忽略 Stribeck 效应和负载相关性;提出 5 / 3 / 7 参数的扩展模型;单摆台架记录轨迹辨识参数;MX-64、MX-106、eRob80 两型上误差降 1.5–2.9 倍;二连杆臂上误差不到默认模型的一半。
- **能回答什么 / 阶段**:阶段 2 理解 sim2real 差距来源;阶段 4 换舵机建模。
- **注意**:只测了四款舵机,microduck 的 XL330 模型在二·6 的库里,换别的舵机要自己辨识。

### 9. 人形机器人运动智能知识库(中文)— https://github.com/RealXiaoze/humanoid-motion-intelligence ✓(二手索引)
- **是什么**:中文知识库,作者署名"具身智能研究室 / 元泽";2026-07-19 建库,2026-09-28 仍在更新,600+ star;许可 CC BY-NC-SA 4.0(可引用、不可商用)。**是索引不是结论来源**:它自己的 AGENTS.md 就要求回原始论文、官方仓库核实。
- **仓库结构**:顶层是主页、`公司与产品主表.md`、`具身智能公司的开源项目.md`;四个目录——`技术与研究/`(六条技术路线各一个文件 01–06,`论文逐篇解读/` 按 P 编号的单篇解读,`双轮足机器人训练开源方案表.md`)、`数据集/`(数据集清单、第一人称采集设备、数据来源与本体依赖)、`强化学习开发者必备开源资料/`(RL 框架与仿真工具一览、书籍与课程)、`求职与岗位/`。
- **六条技术路线**:01 动作数据与重定向;02 Locomotion 与运动先验;03 动作跟踪与全身控制;04 LocoManip;05 世界模型、VLA 与 Agent;06 工程与实机部署。每条路线下是论文清单(附解读链接)和相关开源项目表。
- **它推荐的学习路径**(与本项目四阶段对得上):共同基础(编程、坐标变换、机器人模型、正逆运动学、反馈控制)→ 选一条线:自主运动(搭观测、动作、奖励,训练站立、行走、抗扰,再学地形感知与运动先验)或动作跟踪(重定向、全身跟踪)→ 部署与测试(导出、仿真回放、观测与关节映射、控制接口、实机)→ 按需扩展(移动操作、视觉语言策略、世界模型)。阶段 3、4 规划时可对照。
- **已读分页**:
  - 主页、`技术与研究/README.md`(系统能力栈图、六条路线总表、学习路径表)。
  - `技术与研究/02_Locomotion与运动先验.md`:腿足 RL 论文清单(基础行走、地形感知、技能表示、抗扰、训练框架)+ 几十个"按机器人配训练环境"的项目(含基于 mjlab 的 Unitree RL Mjlab、AMP_mjlab;各厂商基于 Isaac Lab / legged_gym 的)。阶段 4 看别人怎么给自己的本体写观测 / 奖励 / 随机化。
  - `技术与研究/06_工程与实机部署.md`:URDF / MJCF / USD 模型资源(MuJoCo Menagerie、robot_descriptions.py、在线 URDF 比较器)、系统辨识与 sim2real 工具(PACE Sim2Real、PRIME、ASAP)、策略推理运行框架、评测基准。阶段 4 的工具箱。
  - `强化学习开发者必备开源资料/README.md` 与 `书籍与课程.md`:RL 框架与仿真平台一览(RSL-RL、legged_gym、Isaac Lab、K-Sim 等);中文 RL 入门材料(Easy-RL、动手学强化学习、王树森课程、JoyRL)与机器人学 / 动力学 / 足式机器人书单。补基础时从这里挑。
  - `技术与研究/双轮足机器人训练开源方案表.md`:6 个双轮足方案对照(框架、"RL 直接出关节动作 vs RL + VMC"两种动作接口、任务能力)。第三方设备若是轮足形态,从这里起步。
- **未读分页**(用到再补):01 动作数据与重定向、03 动作跟踪与全身控制、04 LocoManip、05 世界模型 / VLA / Agent、`数据集/`、公司与产品主表、求职与岗位、`论文逐篇解读/` 的具体篇目。
- **它自己的使用规则**(其 AGENTS.md,引用它时照做):先读 `技术与研究/README.md` 判断问题属于哪条路线;论文用 P 编号定位,项目用名称和官方链接定位;区分论文明确结论、项目 README 声明、公司自述、媒体报道和推断;"有开源仓库"不等于能完整复现,"有真机视频"不等于经过评测;调试算法先查坐标系、关节顺序、单位、观测与动作定义、PD 参数、频率、延迟,再归因于网络结构。
- **怎么用**:可整个 clone 到本地让 agent 读;它建议提问时带上机器人型号、仿真环境、观测和动作定义、训练曲线或运行日志,让检索结果对应到实际实验。
- **能回答什么 / 阶段**:找入口用——某个方向有哪些论文和项目、换机器人时有哪些现成工具和别人的配置。阶段 4 为主,阶段 3 选参考动作 / 运动先验时也用。
- **注意**:只用它找入口,结论回原文;它的项目描述是二手转述,不展示开源状态、权重发布情况等维护字段,能不能跑要自己验证。

### 10. Ken Goldberg《Goosebumps: a Paradigm Shift is Occurring in Robotics》+ GaP 论文 — 2026-09 ✓(观点文章 + 预印本)
- **是什么**:伯克利教授、Ambi Robotics 联合创始人 Ken Goldberg 在 X 上的长文(https://x.com/Ken_Goldberg/status/2100986412762087909;中文整理:微信公众号 SourceMind《智能体机器人学(Agentic Robotics,AR)》https://mp.weixin.qq.com/s/ngf6utVMsQ0BX18PgeHmqQ)。配套论文 GaP(arXiv 2607.05369,伯克利 / NVIDIA / Bosch,CoRL 2026 待发表;项目页 https://graph-robots.github.io/gap/ ,代码 github.com/graph-robots/graph-as-policy)。**观点文章是个人判断,带作者自家创业公司立场**。
- **摘要**:
  - 机器人开发的三种文化:基于模型的手工工程(快、可靠、每个新任务都要大量人工)、无模型 / VLA(通用但吃数据、可靠性不足)、AR(LLM 编程智能体组合模块化技能库,离线在仿真里测试迭代,导出可解释的轻量程序)。
  - GaP:策略 = 由技能节点组成的计算图;多个编程智能体分别改节点,在 Isaac 仿真里并行试跑、定位失败节点再修改。真机抓放类任务 18/20–28/30;单个 LLM 直接写整段代码(没有图)成功率为零。局限:节拍仍慢于工业要求、以准静态抓放为主。
  - 逆物理:给智能体一段真机视频 + Newton 仿真调参工具,一小时内重建出含海绵形变的仿真;真机失败(推倒金属条,因为视频推不出质量)作为新证据回流修正仿真。
- **能回答什么 / 阶段**:领域地图——除了 RL 和模仿学习,"让 AI 写机器人程序"这条新路线是什么、边界在哪;阶段 2、4 对照:系统辨识 / Real2Sim 这类费人力的工作,正在被尝试交给智能体。
- **注意**:GaP 不是 RL,也不做腿足运动,方法不能直接搬到 microduck;作者自己说实时适应有限、能否扩展到人形 / 通用机器人未知;海绵实验是个人叙述,不是系统评测。

## 四、奠基论文(标题、作者、日期均查自 arXiv 摘要页)

### 1. Hwangbo 等 2019,*Learning agile and dynamic motor skills for legged robots* — Science Robotics ✓
- **摘要**:仿真训练神经网络策略迁移到 ANYmal 四足,精确省能地跟踪速度指令、跑得更快、摔倒能恢复。关键机制**执行器网络**(用真机数据训一个小网络当执行器模型)在正文,摘要未提。https://arxiv.org/abs/1901.08652
- **能回答什么 / 阶段**:阶段 4——执行器模型为什么是 sim2real 核心;与本项目 BAM(解析式)对照。
- **注意**:四足 + 串联弹性执行器,思路可迁移、模型不能直接用。

### 2. Rudin 等 2021,*Learning to Walk in Minutes Using Massively Parallel Deep RL* — CoRL 2021 ✓
- **摘要**:单卡上几千个仿真机器人并行,分析并行体制下各算法组件的影响,"游戏式"地形课程;ANYmal 平地不到 4 分钟、崎岖地形 20 分钟学会。代码即 legged_gym。https://arxiv.org/abs/2109.11978
- **能回答什么 / 阶段**:阶段 1–2——为什么要几千个环境并行、课程为什么分级;mjlab + rsl_rl 这套范式的源头。
- **注意**:legged_gym 基于 Isaac Gym,本项目用 MuJoCo Warp,思想同、接口异。

### 3. Lee 等 2020,*Learning Quadrupedal Locomotion over Challenging Terrain* — Science Robotics ✓
- **摘要**:控制器只用本体感知、无视觉;仿真训练零样本泛化到泥、雪、碎石、植被等训练未见环境。**特权信息教师 → 本体历史学生**在正文,摘要未提。https://arxiv.org/abs/2010.11251
- **能回答什么 / 阶段**:阶段 2–3——actor 为什么不看线速度而 critic 能看、观测为什么带历史。
- **注意**:本项目用非对称 Actor-Critic,不是显式师生蒸馏。

### 4. Tan 等 2018,*Sim-to-Real: Learning Agile Locomotion For Quadruped Robots* ✓
- **摘要**:从零用简单奖励学四足步态;缩小 reality gap 两手抓——改仿真器(系统辨识、精确执行器模型、模拟延迟)+ 学鲁棒策略(随机化物理参数、加扰动、紧凑观测)。https://arxiv.org/abs/1804.10332
- **能回答什么 / 阶段**:阶段 2、4——本项目的随机化开关、指令延迟随机化、BAM 电压 / 摩擦随机化都对应这四件套。
- **注意**:Google Brain 的小四足,方法通用。

### 5. Peng 等 2021,*AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control* ✓
- **摘要**:任务目标用简单奖励,风格由动作片段数据指定;对抗判别器输出"风格奖励",无需手写模仿目标;能吃大数据集。https://arxiv.org/abs/2104.02180
- **能回答什么 / 阶段**:阶段 3——没手写正则项时怎么让步态自然;知识库里大量人形项目基于它。
- **注意**:面向仿真角色,需要动作数据;microduck 上游没用。

## 五、仿真与物理引擎

### 1. 四款物理引擎横向对比 — Manda Robotics 博客,2026-10-05 ✓(博客,未经同行评审)
- **是什么**:Manda Robotics 的技术博客 *Comparing physics engines for robotics simulation*(https://mandarobotics.com/blog/comparing-physics-engines/index.html),未署个人作者;中文译文见微信公众号 human five《机器人仿真物理引擎对比》(https://mp.weixin.qq.com/s/QeeL85xEQuWA-o1Pu2XfDg)。对比 PhysX(Isaac Sim 6.1,CPU)、Newton 1.5.2 + MuJoCo Warp 3.11(GPU)、MuJoCo 3.11(CPU)、Genesis 1.4.1(GPU),同一个 Franka Panda 机械臂、同一个显式力矩控制器。**只做引擎之间横比,没有真机真值**。
- **摘要**:
  - 对齐配置后,宏观结果基本一致(滑块停止位置差 0.05 mm,自由空间机械臂轨迹差 < 0.2 mm,抓取 / 堆叠 / 推物成败判定一致);但**接触力峰值可差十倍**,成功率相同时轨迹仍可差到厘米级。
  - 接触模型分两类:MuJoCo、MuJoCo Warp、Genesis 是软接触(允许毫米级穿透),PhysX 是硬约束。小间隙插销装配最能区分两类:软接触三家能装进去,PhysX 触发力过载。
  - 柔性物体分歧最大:材料参数标称一致,结果从稳定夹持到打滑、网格失效都有;加密网格、缩小步长都不能让结果趋同。
  - 很多"引擎差异"其实是**导入问题**:Genesis 导入时给关节偷偷加了 0.1 kg·m² 的 armature(MJCF 里写的是 0),单摆偏差达 51°,改正后与 MuJoCo 浮点级一致;另有基座固定设置错、全局阻尼没覆盖导入几何体的阻尼等。
  - 仿真步长减半带来的变化可以比换引擎还大;峰值力随步长变(冲量不变),只比峰值会误导。GPU 引擎在部分接触密集场景**同输入重复运行结果不同**(15 物体扫掠:Newton 11/8/7 个入托盘),同引擎内部波动可与引擎间差异相当。
  - 性能:单环境 MuJoCo CPU 最快;8192 个并行世界时 MuJoCo Warp 2160 万步/秒、Genesis 1180 万步/秒,批量再大差距缩小。
  - 建议的工作流:先单物体后多物体、先无接触后接触;每一步导入后回读质量 / 惯量 / 关节坐标系 / armature;步长减半重跑;除成功率外还报告力、轨迹、失败严重程度;用第二款引擎再评估一遍做低成本鲁棒性检查;区分"修正模型规格"和"为成功率调参"。
- **能回答什么 / 阶段**:阶段 2 理解"同样的奖励 / 策略换个仿真设置结果就不同",为什么要做步长、扰动敏感性对照;阶段 4 导入新机器人后先核对哪些参数(armature、碰撞掩码、几何体标签)、要不要用第二款引擎做评估。
- **注意**:场景是**机械臂操作**,不是腿足行走,结论对 microduck 只能类推(行走同样是持续接触,软接触穿透、步长敏感性的道理通用);大多数配置只跑了一次;部分场景在 MuJoCo CPU 上开发,有选择偏差;作者说后续两篇会讲策略跨引擎迁移和 sim2real 精度。

### 2. 《Isaac Sim/Lab、MuJoCo、Genesis、mjlab:机器人仿真走到哪一步了?》— 微信公众号"具身智能研究室",2026 ✓(二手综述,关键事实已抽查)
- **是什么**:https://mp.weixin.qq.com/s/P9O1o6XME9wlTHlGGNLj4Q ,作者同三·9 知识库。仿真工具全景综述,不含新实验。抽查核实:Isaac Lab 3.0 EA 的后端拆分(GitHub release v3.0.0-EA)、MJX 不支持 flex(MuJoCo MJX 文档功能表)、MuJoCo Playground 真机数字(arXiv 2502.08844)均与原始出处一致。
- **摘要**:
  - **三层分工**:物理引擎(算运动与接触:MuJoCo、PhysX、Newton)→ 仿真平台(组织场景、渲染、传感器、软件连接:Isaac Sim、Gazebo、SAPIEN、Genesis)→ 学习框架(观测、动作、奖励、随机化、训练评测:Isaac Lab、mjlab、MuJoCo Playground、ManiSkill)。同一个项目可跨层。
  - "快"要分清:总吞吐量(所有环境合计每秒多少步)≠ 单步延迟;物理步进快也推不出整个训练多快。真正该问的是"多久得到一个通过真机测试的策略"。
  - 换物理后端后,接触、执行器、数值设置都要重新检查,接口复用不等于结果可复用。
  - 软接触 ≠ 软体;原生 MuJoCo 的 flex 能力不等于每个 GPU 实现都支持。
  - 判断 sim2real 三问:物理过程对不对得上 → 真机能否完成任务 → 换条件后能否持续稳定。gap 来源 = 物理参数 + 感知 + 任务变化;观测 / 动作接口(关节顺序、坐标系、动作缩放、控制频率、延迟)必须与真机对齐。"零样本迁移"只是不在真机上再学习,团队仍可能做过硬件测量和校准。
  - 选型从任务出发:系统联调看传感器和 ROS 接口;大规模运动控制看并行物理、执行器建模和现成部署项目;视觉操作看物体多样性与渲染;软体看材料模型。再问四个问题:多久跑通第一个任务、失败能否定位、换设备要改什么、有没有人持续维护。
- **能回答什么 / 阶段**:mjlab 在整个仿真生态里处于哪一层、和 Isaac Lab 是什么关系(领域地图);阶段 1 读训练速度时分清吞吐与延迟;阶段 2 判断 sim2real 问题出在哪一环;阶段 4 选仿真工具、对齐观测动作接口。
- **注意**:综述性质,观点和归纳以作者为准,具体数字回原始出处(上面三处已核);文中 GPT-6 Astra、PhysTwin 等只是顺带提及,未展开。

### 3. Erez、Tassa、Todorov 2015,*Simulation tools for model-based robotics: Comparison of Bullet, Havok, MuJoCo, ODE and PhysX* — ICRA 2015 ✓
- **是什么**:会议论文(https://roboti.us/lab/papers/ErezICRA15.pdf),作者是 MuJoCo 的开发者,**有立场偏向**。
- **摘要**:游戏引擎(PhysX、Bullet、Havok、ODE)传统上用最大坐标 + 数值约束表示关节,机器人引擎用广义坐标;在关节型机器人上,广义坐标在速度和精度上明显占优(Bullet 的 multibody 模式比 MuJoCo 慢约 3 倍,但仍胜过所有最大坐标引擎);大量自由漂浮的刚体则是最大坐标更合适。
- **能回答什么 / 阶段**:"机器人仿真引擎和游戏 / 网页 3D 引擎的物理有什么不同"、为什么本项目用 MuJoCo 而不是游戏引擎。领域地图、阶段 4 选仿真器。
- **注意**:2015 年的结论,之后 PhysX 4 起加了广义坐标的 articulation(Isaac Sim 用的就是它),Bullet 也有了 multibody;不要拿它判断今天各引擎的优劣,最新横比看五·1。

## 六、其他训练平台(对照用)

和 mjlab 同一层的别家框架。不在本项目主线上,做对照实验或换机器人选型时看。

### 1. 格物 / Unity RL Playground — arXiv 2503.05146 · https://github.com/loongOpen/Unity-RL-Playground ✓
- **是什么**:预印本(2025-03,Linqi Ye 等,上海大学 / 国地共建人形机器人创新中心 / 清华)+ 开源仓库(OpenLoong 社区,C#,Apache-2.0)。媒体报道(如微信公众号"话匣子"《机器人1小时学会走路!……》https://mp.weixin.qq.com/s/tjEp1-bakmAjYQKSuP7k1Q)是宣传口径,**数字以论文和 README 为准**。
- **摘要**:建在 Unity ML-Agents 上(物理是 Unity 的 PhysX,关节用 ArticulationBody);流程 = 把 URDF 放进 Unity → 锁掉腿以外的关节 → 设机器人类型、观测 / 动作维度 → `mlagents-learn` 训练 → 导出 `gewu.onnx`。腿部关节加**前馈参考动作**(髋、膝、踝),策略在其上学习,符号要按各机器人关节方向手改。README 称示例约 200 万步够用,URDF 测试约 40 万步、2–5 分钟出效果;论文称训练不需要 GPU。支持青龙、宇树 G1/H1/Go2、加速进化 T1、众擎 SA01、Tinker 等。
- **能回答什么 / 阶段**:另一种"导入新机器人 → 训练"的流水线长什么样,和 mjlab 对照;前馈 + RL 的做法。阶段 3、4 参考。
- **注意**:论文摘要只说"有潜力"迁移到真机;README 里 sim2real 目前**只支持 Go2**(ROS2 + Unitree_ROS2,仅 Ubuntu 20/22)。报道里"自动优化奖励函数""一套代码适配百款机器人""打破国外垄断"在论文和 README 里找不到对应依据;README 没写奖励函数怎么设计。

### 2. MotrixLab / MotrixSim — https://github.com/Motphys/MotrixLab · https://github.com/Motphys/motrixsim-docs ✓(厂商开源项目)
- **是什么**:北京谋先飞(Motphys)的开源 RL 训练框架(Apache-2.0)和自研物理引擎 MotrixSim(只以软件形式引用,没有独立论文)。CEO 访谈见微信公众号"商业与生活"《对话谋先飞CEO崔汉青》https://mp.weixin.qq.com/s/NLZ_mxXAsUQb9F5KvAvsrg ——访谈里"比英伟达快 3–10 倍、精度更高"是**自述,没有可查的对比数据**。
- **摘要**:一次定义环境,在几千个并行环境里训练;算法可选 SKRL、RSL-RL 或内置 FastSAC;训完用插件放进 MuJoCo 做 sim2sim,或经宇树 SDK2 上真机。Linux / Windows,NVIDIA(CUDA)或 AMD(ROCm)显卡,uv 安装。内置 7 个机器人、50+ 任务,**其中有 microduck(14 自由度,任务 `microduck-walk-flat`,README 快速开始就用它)**。RSS 2026 的 GS-Playground(discoverse-dev)用 MotrixSim 做物理后端。
- **能回答什么 / 阶段**:阶段 2 / 4 的一个现成对照实验——**同一只 microduck 换一个物理引擎 + 训练框架训练**,和 mjlab 训出来的比一比(跨引擎差异见五·1);"学习框架"层除了 Isaac Lab、mjlab 还有谁(五·2)。
- **注意**:README 没写 microduck 模型从哪来、执行器怎么建模(是否用 BAM),拿来对比前要先核对资产和执行器是否与上游一致,否则比的不是引擎;没有和 Isaac Lab / mjlab 的公开对比数据;项目还在快速变化(2026-10 仍在重构机器人配置)。

## 七、加新条目的格式

按上面的四项写:**是什么**(类型、作者 / 机构、时间、可信度)、**摘要**(3–5 个具体要点)、**能回答什么 / 阶段**、**注意**(局限、版本、口径)。
"能回答什么"最重要——没有它,这个文件过几个月就退化成一堆记不清为什么存的链接。总览表按需加一行。
