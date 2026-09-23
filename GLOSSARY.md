# GLOSSARY.md — 技术名词对照表

> **共同的词汇基线。** 学习过程中出现的每个新技术名词都记在这里:中英对照、简称全称、一句话中文解释。
> 不确定某个词是什么意思,先查这;查不到说明还没记,当场补。
>
> **收录范围:只收具身智能 / 机器人学习相关的词。** 判据一句话——
> **这个词在具身智能之外基本用不到吗?** 用不到才收。
> 通用开发和通用 ML 工具(git、uv、wandb、TensorBoard、Hugging Face、submodule/subtree 之类)**一律不收**,
> 它们换个 Python 项目也会遇到,不属于这门手艺的词汇。
>
> 边界怎么划:`vcs2l` 收了、`git submodule` 没收——两者都是多仓库管理,但前者基本只在
> ROS / 机器人生态里出现,后者到处都是。**看的是"实际在哪个圈子里用",不是"理论上能不能用在别处"。**
>
> **给 AI 助手**:对话里出现符合范围的新名词就写进来,别只在当轮解释一次。
> **核实标记**:`✓源码` = 从本项目代码/文档里直接读到的;`✓` = 联网核实过或领域通用共识;`?` = 待核实,引用前先查。

## 一、学习范式与算法

| 缩写 | 全称 | 中文 | 一句话解释 | 核 |
|---|---|---|---|:-:|
| RL | Reinforcement Learning | 强化学习 | 靠"试错 + 奖励"学策略,不需要标注数据 | ✓ |
| PPO | Proximal Policy Optimization | 近端策略优化 | 机器人 RL 最常用的算法,稳定好调。**本项目实际用的就是它** | ✓ |
| IL | Imitation Learning | 模仿学习 | 从示教数据学,绕开奖励设计。操作类任务的主力 | ✓ |
| BC | Behavior Cloning | 行为克隆 | IL 里最直接的一种:把"状态→动作"当监督学习训 | ✓ |
| MPC | Model Predictive Control | 模型预测控制 | 传统控制:建模型、在线滚动求解最优控制。**没被 RL 取代**,常做底层控制、安全兜底、示教数据源 | ✓ |
| WBC | Whole-Body Control | 全身控制 | 同时协调所有关节达成多个目标(平衡 + 动作)的控制框架 | ✓ |
| MDP | Markov Decision Process | 马尔可夫决策过程 | RL 的数学框架:状态、动作、奖励、状态转移。**"定义一个任务"本质就是定义一个 MDP** | ✓ |
| DR | Domain Randomization | 域随机化 | 训练时随机化物理参数(质量、摩擦、质心…),逼策略学会鲁棒。sim2real 的核心手段 | ✓ |
| — | sim2real | 仿真到现实 | 仿真里训好的策略搬到真机还能用。**本项目一半功夫花在这** | ✓ |
| VLA | Vision-Language-Action | 视觉-语言-动作模型 | 输入图像 + 语言指令、输出动作的大模型。操作方向的当前热点 | ✓ |
| LBM | Large Behavior Model | 大行为模型 | 机器人版"大模型"。Atlas 2025 年和 TRI 合作的路线 | ✓ |
| — | Policy | 策略 | 从"当前看到的"映射到"下一步做什么"的函数。本项目里就是一个小 MLP,训练产出 = `policy.onnx` | ✓ |
| — | Observation | 观测 | 策略每一步的输入:它"看到/感觉到"的东西。本项目 61 维(本体感知 + 指令) | ✓源码 |
| — | Action | 动作 | 策略每一步的输出。本项目 = 14 个舵机的目标角度,再由舵机内部的 PD 环去跟上 | ✓源码 |
| — | Episode | 回合 | 一次从重置到结束(摔倒或超时)的完整尝试。训练就是几千只鸭子反复跑回合 | ✓ |
| — | Control Frequency | 控制频率 | 策略每秒做几次决策。本项目 50 Hz;物理仿真步比它更细,一次决策之间要算好几个物理步 | ✓源码 |
| — | Actor-Critic | 演员-评论家 | RL 架构:actor 出动作,critic 评价好坏 | ✓源码 |
| — | Asymmetric Actor-Critic | **非对称**演员-评论家 | critic 比 actor 多看"特权信息",部署时只跑 actor。本项目 critic 76 维 vs actor 61 维 | ✓源码 |
| — | Curriculum Learning | 课程学习 | 从易到难逐步加难度/加约束。本项目有 7 项 | ✓源码 |
| — | Ablation Study | 消融实验 | 一次只改一个部件看结果怎么变,用来定位"哪个部件在起作用" | ✓ |
| — | Privileged Information | 特权信息 | 仿真里拿得到、真机拿不到的量(躯干线速度、触地力)。只给 critic 用 | ✓源码 |
| — | Reward Shaping | 奖励塑形 | 设计奖励函数引导策略学出想要的行为。**这行最大的工作量** | ✓ |
| — | Reward Hacking | 奖励钻空子 | 策略找到"分数高但不是你要的行为"的捷径 | ✓ |
| — | Loco-manipulation | 移动操作 | 边走边操作(搬着东西走路),把运动控制和操作缝起来。当前热点 | ✓ |
| — | Zero-shot Transfer | 零样本迁移 | 仿真训完直接上真机,不做任何真机微调 | ✓ |
| — | Termination | 终止条件 | 回合提前结束的规则,如 `fell_over`(躯干倾斜超 70°)。训练日志里 `Episode_Termination/<名字>` 记的是**这一批重置的回合里有几个是因它结束的**,看比例不看绝对值 | ✓源码 |
| — | External Push / Perturbation | 抗扰推力 | 训练时每隔几秒随机给躯干一个速度冲击,逼策略学会被推不倒。本项目训练时 3–6 s 一次、±0.3 m/s;**play 模式改成 0.5–1 s 一次**,看回放时踉跄多半是刚被推了 | ✓源码 |

## 二、机器人学与硬件

| 缩写 | 全称 | 中文 | 一句话解释 | 核 |
|---|---|---|---|:-:|
| DoF | Degrees of Freedom | 自由度 | 能独立运动的维度数。microduck 14 个舵机 = 14 DoF | ✓ |
| IMU | Inertial Measurement Unit | 惯性测量单元 | 测角速度和加速度的传感器。**测不准线速度**(积分会漂)——这就是本项目 actor 观测里没有线速度的原因 | ✓ |
| PD | Proportional-Derivative | 比例-微分控制 | 最常见的底层位置控制律。策略输出关节目标位置,PD 环负责跟上 | ✓ |
| URDF | Unified Robot Description Format | 统一机器人描述格式 | ROS 生态的机器人模型格式(XML) | ✓ |
| MJCF | MuJoCo Modeling XML File | MuJoCo 模型格式 | MuJoCo 原生模型格式(XML),URDF 的替代。本项目机器人模型用它。官方文档不展开这个缩写,展开法出自 NVIDIA Isaac Sim 文档 | ✓ |
| ZMP | Zero Moment Point | 零力矩点 | 传统双足步态规划的核心判据。学习方法出现前的主流路线 | ✓ |
| — | Proprioception | 本体感知 | 机器人"感觉到自己":关节角度、角速度、姿态。不含外部视觉 | ✓ |
| — | Motion Capture (mocap) | 动作捕捉 | 采人的动作数据,人形机器人常用作参考动作 | ✓ |
| — | Retargeting | (动作)重定向 | 把人的动作映射到机器人身上,解决身材比例和关节结构不同的问题 | ✓ |
| — | Backlash | 齿隙 / 回差 | 齿轮传动的空程间隙。本项目专门为它建了模型和对照任务 | ✓源码 |
| — | Actuator | 执行器 | 舵机/电机。**建准它是小型机器人 sim2real 的生死线** | ✓ |
| — | Kinematic Tree | 运动学树 | 机器人模型的骨架:刚体(body)一节套一节,相邻两节之间用关节连接。microduck 以躯干为根,分出左腿、脖子/头、右腿三条支链 | ✓源码 |
| — | Free Joint | 自由关节 | 6 自由度"关节",让根刚体在空间里任意平移和转动。**浮动基座机器人(会走的)必须有它**,机械臂则没有(固定在桌上)。在 qpos 里占 7 个数(3 个位置 + 4 个四元数) | ✓ |
| — | Floating Base | 浮动基座 | 根部不固定在世界上的机器人(腿足、人形)。和"固定基座"的机械臂相对 | ✓ |
| — | Inertial (mass / CoM / inertia tensor) | 惯性参数(质量 / 质心 / 惯量张量) | 每个刚体的质量分布,决定它被推动时怎么动。由 CAD 按材料密度算出,**是仿真准不准的第一道关** | ✓ |
| — | Collision Geom / Visual Geom | 碰撞几何体 / 视觉几何体 | 同一个零件两套外形:视觉用精细网格只负责好看,碰撞用简化形状参与物理计算。碰撞体越少仿真越快 | ✓ |
| — | Armature | 电枢惯量 / 转子惯量 | MuJoCo 关节参数。电机转子的惯量折算到关节上,只影响动力学(转起来多"沉"),不影响几何 | ✓ |
| — | Frictionloss | 摩擦损耗(库仑摩擦) | MuJoCo 关节参数:大小恒定、方向与运动相反的摩擦力矩 | ✓ |
| — | Damping (viscous) | 粘性阻尼 | MuJoCo 关节参数:与速度成正比的阻力 | ✓ |
| — | Stribeck Effect | 斯特里贝克效应 | 摩擦力随速度变化的非线性:静止时的静摩擦大,开始动之后反而下降。BAM 模型里包含它 | ✓ |
| — | condim | 接触维度 | MuJoCo 碰撞体参数:1 = 无摩擦,3 = 有滑动摩擦,4/6 = 再加上扭转和滚动摩擦 | ✓ |
| — | contype / conaffinity | 碰撞位掩码 | MuJoCo 的碰撞过滤规则:两个碰撞体的位掩码按位与后非零才碰撞。用它实现"只和自己碰、不和地面碰"之类的分组 | ✓ |
| — | Keyframe | 关键帧 | MJCF 里预存的一组关节姿态(qpos),如 STAND / SIT。用作初始姿态或参考姿态 | ✓ |
| — | System Identification (SysID) | 系统辨识 | 在真机上采数据、反推模型参数(摩擦、增益、惯量)。**换机器人时最费工的一步** | ✓ |
| — | Swing / Stance Phase | 摆动相 / 支撑相 | 步态的两个阶段:脚在空中往前摆 = 摆动相,脚踩地撑住身体 = 支撑相。`air_time` 奖励量的就是摆动相时长 | ✓ |
| — | Foot Clearance | 足端离地高度 | 摆动相里脚抬多高。太低会拖地、绊倒;`foot_clearance` / `foot_swing_height` 两项惩罚都在管它 | ✓源码 |
| — | Foot Slip | 足端打滑 | 脚踩地时还在水平滑动。仿真里打滑的步态到真机上更容易摔;`foot_slip` 惩罚项对应它 | ✓源码 |

## 三、本项目专有

| 缩写 | 全称 | 中文 | 一句话解释 | 核 |
|---|---|---|---|:-:|
| BAM | Better Actuator Models | 执行器模型库 | Rhoban 的开源库(ICRA 2025 论文):用摆锤台架辨识舵机的扩展摩擦模型(Stribeck、负载相关),替代 MuJoCo 默认的"库仑 + 粘性"摩擦。本项目用它的 XL330 **M6** 模型,按电压驱动。包名 `better-actuator-models`,导入名 `bam` | ✓ |
| — | Dynamixel XL330 | — | microduck 用的舵机型号,14 个 | ✓源码 |
| — | twist | 速度指令 | 观测里的 3 维指令块:前进 / 横移 / 转向速度 | ✓源码 |
| — | `passive_*` | 被动关节 | 不受驱动的关节(轮子、齿隙铰链)的命名前缀约定 | ✓源码 |
| — | obs normalizer | 观测归一化器 | 把观测缩放到合适范围。**必须烤进 ONNX**,漏了部署即废 | ✓源码 |
| — | checkpoint | 存档 | `model_XXXX.pt`,训练中途的权重快照,每 250 迭代存一个 | ✓源码 |
| — | episodic / perpetual | 一次性 / 持续型策略 | 一次性 = 做完一个动作就结束(翻滚、踢球);持续型 = 一直跑(走路、站立) | ✓源码 |

## 四、这个领域专用的工具

(通用工具不收,见开头的收录范围)

| 名字 | 全称 | 是什么 | 核 |
|---|---|---|:-:|
| MuJoCo | — | Google DeepMind 的机器人物理仿真引擎。**这个领域的事实标准之一** | ✓ |
| MuJoCo Warp | — | GPU 加速版 MuJoCo,让几千个环境并行跑在显卡上(底座是 NVIDIA Warp,一个写 GPU kernel 的 Python 库) | ✓ |
| mjlab | — | 建在 MuJoCo Warp 上的 RL 训练框架,本项目的直接依赖 | ✓源码 |
| rsl_rl | Robotic Systems Lab – RL | 苏黎世联邦理工(ETH)机器人系统实验室的 RL 库,提供 PPO 实现。腿足机器人 RL 的常用底座 | ✓ |
| onshape-to-robot | — | Rhoban 的工具:通过 Onshape API 把 CAD 装配体导出成 URDF / SDF / MJCF。本项目每个 `config_mjcf_*.json` 就是它的配置 | ✓ |
| vcs / vcstool | version control system tool | ROS 工作区的多仓库管理工具:从一个 `.repos` 清单文件(YAML)一次 clone / 更新多个上游仓库到指定目录,命令形如 `vcs import src < file.repos`。**本项目用它在 `src/` 下按 `upstream.repos` 拉 microduck / microduck_rl / mjlab 三个上游** | ✓ |
| vcs2l | — | vcstool 停止维护后的继任 fork,由 ROS 官方组织 ros-infrastructure 维护(官方未给出停更的具体时间点)。命令名仍是 `vcs`,可无缝替换。**本项目 INSTALL.md 装的是它**(`pip install vcs2l`) | ✓ |
| ONNX | Open Neural Network Exchange | 跨框架跨平台的模型格式。本身是通用 ML 格式,但**"训练→导出 ONNX→机载运行时加载"是这个领域的标准部署路径**,所以收录 | ✓ |
