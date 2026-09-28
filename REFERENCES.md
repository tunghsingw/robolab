# REFERENCES.md — 外部信息来源

> **共同的信息来源清单。** 记录哪些资料可以参考、各自能回答什么问题。
>
> **用法**:查外部信息前先看这里有没有现成来源;用了新来源就记进来,并注明"它能回答什么"。
> **规矩**:凡是"领域现状 / 技术分类 / 谁家用什么方法"这类问题,**先查这里,查不到就联网核实,核实完把来源加进来**。
> 不要凭记忆答——本项目 README 里最初那版"两条技术栈"的分类就是凭记忆写的,三处硬伤。
>
> **收录范围:只收具身智能 / 机器人学习相关的资料。** 通用开发话题(git 用法、包管理、工具链选型)查完就用,
> **不进这个文件**——那些结论该写进 `AGENTS.md` 的正文,不该在这里堆链接。
>
> **标记**:`✓` = 已核实/直接读过;`?` = 凭记忆列出,引用前必须先核实。

## 一、项目内部(最优先,不用联网)

| 来源 | 能回答什么 |
|---|---|
| `src/microduck_rl/AGENTS.md` | **上游作者的经验手册,精华。** 奖励设计的硬规则、sim2real 踩过的坑、课程学习怎么排、怎么建一个新任务。每条都是出过事换来的 |
| `src/microduck_rl/README.md` | 任务列表、命令速查、发布流程 |
| `src/microduck/docs/robot/simulation.md` | duck-sim 全栈模拟怎么用 |
| `src/microduck/docs/design/architecture.md` | 真机机载系统架构 |
| **训练日志开头的几张表** | **当前配置的实况**:ObservationManager(观测构成)、RewardManager(16 项奖励及权重)、CurriculumManager(7 项课程)、EventManager(域随机化和扰动)。比读源码快,而且一定是最新的 |
| 本项目 `README.md` / `GLOSSARY.md` | 学习目标、领域地图、实践路线、训练履历 / 名词解释 |

## 二、官方文档

| 来源 | 链接 | 能回答什么 | 核 |
|---|---|---|:-:|
| MuJoCo 文档 | https://mujoco.readthedocs.io/ | 仿真器原理、MJCF 格式、XML 元素参考 | ✓ |
| mjlab | https://github.com/mujocolab/mjlab | 训练框架的 API、CLI 参数、任务注册机制 | ✓ |
| rsl_rl | https://github.com/leggedrobotics/rsl_rl | PPO 实现细节、训练循环、checkpoint 格式 | ✓ |
| MuJoCo XML 参考 | https://mujoco.readthedocs.io/en/stable/XMLreference.html | MJCF 每个属性的精确定义:armature、frictionloss、condim、contype/conaffinity、freejoint、keyframe | ✓ |
| onshape-to-robot 文档 | https://onshape-to-robot.readthedocs.io/ | CAD → URDF/MJCF 怎么导出,`config.json` 各字段(ignore、additional_xml、joint_properties、post_import_commands)的含义 | ✓ |
| BAM 文档 / 代码 | https://bam.readthedocs.io/ · https://github.com/Rhoban/bam | 舵机扩展摩擦模型怎么辨识、有哪些现成舵机模型(XL330 等)、怎么接入 mjlab。**换舵机时照着它搭台架** | ✓ |
| microduck(上游) | https://github.com/pollen-robotics/microduck | 真机运行时(Rust)、策略怎么加载 | ✓ |
| microduck_rl(上游) | https://github.com/pollen-robotics/microduck_rl | 训练环境本体 | ✓ |

## 三、领域综述与关键资料(已核实)

| 来源 | 链接 | 能回答什么 | 核 |
|---|---|---|:-:|
| 腿足机器人模仿学习综述(Frontiers) | https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1678567/full | IL 在腿足机器人上的全貌。**"MPC 日志已成为腿足 IL 最常用训练数据源、超过动捕"这个结论出自这里** | ✓ |
| 机器人 RL 分类与趋势 | https://arxiv.org/html/2510.21758v3 | RL 方法分类、与控制论的结合方式 | ✓ |
| 深度 RL 真实世界落地综述 | https://arxiv.org/html/2408.03539v1 | 哪些 RL 成果真上了真机。**"locomotion 比 manipulation 成熟"的论据来源** | ✓ |
| 人形视觉灵巧操作 sim2real | https://arxiv.org/pdf/2502.20396 | **操作方向也能做仿真 RL 的证据**,用来反驳"操作只能靠采数据" | ✓ |
| 控制 + 机器学习融合分类(Actuators) | https://www.mdpi.com/2076-0825/15/5/235 | MPC / RL / IL 三者怎么混着用 | ✓ |
| Atlas + TRI 大行为模型 | https://www.therobotreport.com/boston-dynamics-tri-use-large-behavior-models-train-atlas-humanoid/ | **Atlas 的真实技术栈**:MPC 做底层控制和遥操作底座,上面叠扩散 Transformer 的 LBM | ✓ |
| 操作模仿学习分类综述 | https://arxiv.org/html/2508.17449v1 | IL 在操作方向的方法谱系;行为克隆占比等数据 | ✓ |
| BAM 论文:Duclusaud et al., ICRA 2025 | https://arxiv.org/abs/2410.08650 | **为什么 MuJoCo 默认的"库仑 + 粘性"摩擦不够用**;Stribeck / 负载相关摩擦模型;摆锤台架辨识方法 | ✓ |
| **人形机器人运动智能知识库**(RealXiaoze/humanoid-motion-intelligence,中文) | https://github.com/RealXiaoze/humanoid-motion-intelligence | **运动控制方向的中文索引与地图**:六条技术路线(动作数据、Locomotion、动作跟踪、LocoManip、世界模型/VLA、工程部署)+ 论文逐篇解读 + 训练框架/数据集/公司/求职资料。2026-07 建库、持续更新(600+ star),CC BY-NC-SA。**它是二手索引,不是结论来源**:它自己的 AGENTS.md 就要求"回原始论文/官方仓库核实",所以引用时只用它找入口,结论回原文 | ✓ 读过主页、目录和下列分页 |
| ↳ `技术与研究/02_Locomotion与运动先验.md` | https://github.com/RealXiaoze/humanoid-motion-intelligence/blob/main/技术与研究/02_Locomotion与运动先验.md | **腿足 RL 运动控制的论文清单**(基础行走、地形感知、抗扰、运动先验/AMP)+ **几十个"按机器人配训练环境"的项目**(Unitree RL Mjlab、AMP_mjlab 等基于 mjlab 的,以及各厂商基于 Isaac Lab / legged_gym 的)。阶段 4 换机器人时,看别人怎么给自己的本体写观测/奖励/随机化配置 | ✓ |
| ↳ `技术与研究/06_工程与实机部署.md` | https://github.com/RealXiaoze/humanoid-motion-intelligence/blob/main/技术与研究/06_工程与实机部署.md | **换机器人的工具箱**:URDF/MJCF/USD 模型资源(MuJoCo Menagerie、robot_descriptions.py、在线 URDF 比较器)、系统辨识与 Sim2Real 工具(PACE Sim2Real:固定基座激励 + CMA-ES 拟合惯量/摩擦/延迟;PRIME;ASAP)、策略推理运行框架、评测基准 | ✓ |
| ↳ `强化学习开发者必备开源资料/`(README + 书籍与课程) | https://github.com/RealXiaoze/humanoid-motion-intelligence/tree/main/强化学习开发者必备开源资料 | RL 框架与仿真平台一览(RSL-RL、legged_gym、Isaac Lab、K-Sim 等,每条一句用途);**中文 RL 入门材料**(Easy-RL、动手学强化学习、王树森课程)和机器人学/动力学/足式机器人书单。补 RL 与机器人学基础时从这里挑 | ✓ |
| ↳ `技术与研究/双轮足机器人训练开源方案表.md` | https://github.com/RealXiaoze/humanoid-motion-intelligence/blob/main/技术与研究/双轮足机器人训练开源方案表.md | 6 个双轮足机器人 RL 训练方案对照(框架、动作接口"RL 直接出关节动作 vs RL+VMC"、任务能力)。**以后第三方设备若是轮足形态,从这张表起步** | ✓ |

## 四、经典奠基论文(已核实:标题、作者、日期均查自 arXiv 摘要页)

| 论文 | 链接 | 能回答什么 | 核 |
|---|---|---|:-:|
| Hwangbo et al. 2019, *Learning agile and dynamic motor skills for legged robots*(Science Robotics) | https://arxiv.org/abs/1901.08652 | **执行器网络**(actuator network)——用真机数据训一个小网络当执行器模型,替代解析模型,sim2real 奠基工作之一。本项目的 BAM 是同一思路的解析版 | ✓ |
| Rudin et al. 2021, *Learning to Walk in Minutes Using Massively Parallel Deep RL* | https://arxiv.org/abs/2109.11978 · 代码 https://github.com/leggedrobotics/legged_gym | **几千环境 GPU 并行 + 地形课程**训练四足行走——现在"几千只鸭子并行试错"这一范式的源头;legged_gym 就是它的代码 | ✓ |
| Lee et al. 2020, *Learning Quadrupedal Locomotion over Challenging Terrain*(Science Robotics) | https://arxiv.org/abs/2010.11251 | **只靠本体感知的盲走**:特权信息教师 → 本体历史学生。本项目"非对称 Actor-Critic、actor 观测里没有线速度"的思想来源 | ✓ |
| Tan et al. 2018, *Sim-to-Real: Learning Agile Locomotion For Quadruped Robots* | https://arxiv.org/abs/1804.10332 | **执行器建模 + 延迟仿真 + 系统辨识 + 域随机化**跨越四足 sim2real 差距。回答"为什么小型机器人要在执行器模型上下功夫" | ✓ |
| Peng et al. 2021, *AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control* | https://arxiv.org/abs/2104.02180 | **用对抗判别器从动作数据学"风格奖励"**,替代手写的步态正则项。知识库里大量人形项目(AMP_mjlab、各厂商 *_amp)都基于它;阶段 3 想让步态"自然"时的另一条路 | ✓ |

## 五、加新条目的格式

一行写清三件事:**来源是什么、链接、它能回答什么问题**。
第三项最重要——没有它,这个文件过几个月就退化成一堆记不清为什么存的链接。
