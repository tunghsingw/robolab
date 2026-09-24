# 阶段 1:数字 ↔ 行为 映射表

素材:第一次正式训练 `2026-09-15_12-26-40`(`model_0` → `model_12500`,51 个存档),录下了"从不会走到会走"的全过程。
回放:`uv run play ... --viewer viser`,Checkpoints 标签页切存档,Rewards 标签页看实时奖励条。
曲线:TensorBoard 读同一个 run,横轴 = 迭代数。

**完成标准**:对着一个陌生 checkpoint,能说出「它现在的主要问题是 X,对应指标是 Y」。

⚠️ play 里的奖励条和 TensorBoard 的数不能直接比:play 每次都是新建的环境,课程学习从第 0 阶段算起
(例如 `action_rate_l2` 的权重是 −0.1,而训练到 1500 轮后是 −1.0)。
**play 里的条只用来在不同存档之间横向比**(同一套权重),曲线的绝对值以 TensorBoard 为准。

## 一、回放记录

每个存档同一套指令:① 全零站立 30 s;② `lin_vel_x = 0.4` 前进 30 s;③ 点 Zero 看能否停稳。
行为一栏写具体(倒没倒、多久倒、脚抬多高、被推后几步稳住、停下时是否还在踏步),不写"还行"。

| 存档 | 看到的行为 | 主要问题 | 奖励条里最突出的一根 |
|---|---|---|---|
| 0 | 无论给什么指令(含全零)都向前倒;倒后回合结束自动重置,反复倒 | 站都站不住,更谈不上听指令 | (待补) |
| 500 | | | |
| 1000 | | | |
| 2000 | | | |
| 5000 | | | |
| 12500 | | | |

## 二、同一迭代的 TensorBoard 读数

| 迭代 | Train/mean_episode_length | Train/mean_reward | Episode_Reward/track_linear_velocity | Episode_Termination/fell_over |
|---|---|---|---|---|
| 0 | 无论给什么指令(含全零)都向前倒;倒后回合结束自动重置,反复倒 | 站都站不住,更谈不上听指令 | (待补) | |
| 500 | | | | |
| 1000 | | | | |
| 2000 | | | | |
| 5000 | | | | |
| 12500 | | | | |

## 三、映射表(最终产出)

| 看到的行为 | 先查哪个指标 | 判读 | 可迁移性 |
|---|---|---|---|
| | | | |

## 四、结论

## 附:16 项奖励的来源(核对自上游源码)

奖励是**任务定义的一部分**,写在任务配置里,不在网络里。分三层:

| 层 | 在哪 | 包含哪些项 | 可迁移性 |
|---|---|---|---|
| ① 框架的"速度跟踪"通用模板 | `src/mjlab/src/mjlab/tasks/velocity/velocity_env_cfg.py` | track_linear_velocity、track_angular_velocity、upright、pose、body_ang_vel、angular_momentum、dof_pos_limits、action_rate_l2、air_time、foot_clearance、foot_swing_height、foot_slip(另有 soft_landing,microduck 删掉了) | 换机器人也一样:mjlab 里人形 Unitree G1、四足 Unitree Go1 用的是同一个模板 |
| ② 各机器人自己调参数 | microduck:`src/microduck_rl/src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py` | 同一批项,改权重、改容差、改"哪只脚/哪个关节" | 方法通用,数值 microduck 特有 |
| ③ 各机器人自己加的项 | 同上 | self_collisions(用框架现成函数)、head_pose_tracking、body_pose_tracking、head_pose_bias(microduck 自写) | 自碰撞通用;头部三项 microduck 特有(它的头占体重约 38%) |

同一模板在三台机器人上的差异举例:`air_time` 在 microduck 是 +3.0,在 G1 和 Go1 都设为 0;Go1 另加了小腿、躯干头部的碰撞惩罚。
