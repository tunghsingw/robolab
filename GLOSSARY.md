# GLOSSARY.md — 技术名词对照表

> **共同的词汇基线。** 学习过程中出现的每个新技术名词都记在这里:中英对照、简称全称、一句话中文解释。
> 不确定某个词是什么意思,先查这;查不到说明还没记,当场补。
>
> **收录范围:只收具身智能 / 机器人学习相关的词。** 判据一句话——
> **这个词在具身智能之外基本用不到吗?** 用不到才收。
> 通用开发和通用 ML 工具(git、uv、wandb、TensorBoard、Hugging Face、submodule/subtree 之类)**一律不收**,
> 它们换个 Python 项目也会遇到,不属于这门手艺的词汇。
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
| — | Actor-Critic | 演员-评论家 | RL 架构:actor 出动作,critic 评价好坏 | ✓源码 |
| — | Asymmetric Actor-Critic | **非对称**演员-评论家 | critic 比 actor 多看"特权信息",部署时只跑 actor。本项目 critic 76 维 vs actor 61 维 | ✓源码 |
| — | Curriculum Learning | 课程学习 | 从易到难逐步加难度/加约束。本项目有 7 项 | ✓源码 |
| — | Ablation Study | 消融实验 | 一次只改一个部件看结果怎么变,用来定位"哪个部件在起作用" | ✓ |
| — | Privileged Information | 特权信息 | 仿真里拿得到、真机拿不到的量(躯干线速度、触地力)。只给 critic 用 | ✓源码 |
| — | Reward Shaping | 奖励塑形 | 设计奖励函数引导策略学出想要的行为。**这行最大的工作量** | ✓ |
| — | Reward Hacking | 奖励钻空子 | 策略找到"分数高但不是你要的行为"的捷径 | ✓ |
| — | Loco-manipulation | 移动操作 | 边走边操作(搬着东西走路),把运动控制和操作缝起来。当前热点 | ✓ |
| — | Zero-shot Transfer | 零样本迁移 | 仿真训完直接上真机,不做任何真机微调 | ✓ |

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

## 三、本项目专有

| 缩写 | 全称 | 中文 | 一句话解释 | 核 |
|---|---|---|---|:-:|
| BAM | Better Actuator Models | 执行器模型库 | 给 XL330 舵机建模(电压控制 + 摩擦)。包名 `better-actuator-models`,导入名 `bam` | ✓源码 |
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
| ONNX | Open Neural Network Exchange | 跨框架跨平台的模型格式。本身是通用 ML 格式,但**"训练→导出 ONNX→机载运行时加载"是这个领域的标准部署路径**,所以收录 | ✓ |
