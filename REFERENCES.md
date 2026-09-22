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

## 四、经典奠基论文(⚠️ 凭记忆列出,待核实)

下面几篇是 AI 助手凭记忆列的,**引用前必须先核实作者、年份、结论**:

| 论文 | 大致内容 | 核 |
|---|---|:-:|
| Hwangbo et al., Science Robotics 2019 | actuator network——用神经网络建执行器模型,sim2real 的奠基工作之一。本项目的 BAM 是同一思路 | ? |
| Rudin et al., CoRL 2021 | 大规模并行 RL("几分钟学会走路"),现在几千环境并行训练的范式源头 | ? |
| Lee et al., Science Robotics 2020 | 复杂地形上的盲走(只靠本体感知,不用视觉) | ? |

## 五、加新条目的格式

一行写清三件事:**来源是什么、链接、它能回答什么问题**。
第三项最重要——没有它,这个文件过几个月就退化成一堆记不清为什么存的链接。
