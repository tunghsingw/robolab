# 阶段 1:学会看 —— 工具、面板与「数字 ↔ 行为」映射表

**目标**:对着一个陌生 checkpoint,能说出「它现在的主要问题是 X,对应指标是 Y」。
**素材**:第一次正式训练 `2026-09-15_12-26-40_velocity`(`model_0` → `model_12500`,每 250 一个,51 个存档),
录下了"从不会走到会走"的全过程。挑 `0 / 500 / 1000 / 2000 / 5000 / 12500` 六个看。
(`2026-09-16_09-07-17_velocity` 是从 12500 续训的打磨阶段,课程学习早已走完,存档间差别很细,阶段 1 不用。)

**两个工具的分工**:play 回答「这个存档此刻做什么」(一个样本,实时仿真);TensorBoard 回答「训练过程中各项分数怎么变」(几千只鸭子的平均,一段历史)。阶段 1 就是把两边对上。

---

## 一、启动命令(Windows PowerShell,存档已从 WSL 复制到相同相对路径)

### play 回放查看器(窗口一)

```powershell
$env:WANDB_MODE="offline"
$uv = "$env:USERPROFILE\.local\bin\uv.exe"
cd D:\robot\robolab\src\microduck_rl
$RUN = "logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity"
Test-Path "$RUN\model_0.pt"
& $uv run play Mjlab-Velocity-Flat-MicroDuck --checkpoint-file "$RUN\model_0.pt" --num-envs 2 --viewer viser
```

- `Test-Path` 必须是 `True`,否则存档没复制到位。
- 浏览器开 **`http://localhost:8080`**。看完终端 **Ctrl+C**,别一直占显存。
- 命令结构 = `uv run` + `play` + 任务名 + 选项。`train`、`list-envs` 同一格式,学会一条等于学会一族。
- 只需要记 4 个选项:`--checkpoint-file`(回放哪个存档)、`--num-envs`(几只鸭子)、`--viewer viser`(网页查看器,**才有奖励条和存档切换**)、`--agent zero|random`(不加载存档,做对照)。
- 终端停在转圈的包名(如 `⠧ cycler==0.12.1`)= `uv run` 在同步依赖、网络卡住,**不是 play 在跑**。出现 viser 网址才算启动成功。
- WSL 侧命令见 README「`uv run play`」一节,只是根目录不同。

### TensorBoard 训练曲线(窗口二)

```powershell
$uv = "$env:USERPROFILE\.local\bin\uv.exe"
cd D:\robot\robolab\src\microduck_rl
& $uv run tensorboard --logdir logs\rsl_rl\velocity\2026-09-15_12-26-40_velocity
```

- 浏览器开 **`http://localhost:6006`**。
- `--logdir` 指到单个 run 目录 = 只看这一个;指到 `logs\rsl_rl\velocity` = 所有 run 叠在一起(阶段 2 对比用)。
- 它只读训练时写下的 `events.out.tfevents.*`,不跑仿真、不碰存档。

---

## 二、play 查看器:面板说明

右侧面板分标签页。阶段 1 只用其中 4 个 + Scene 下的 Debug Viz。

| 标签页 | 中文 | 阶段 1 用途 |
|---|---|---|
| **Controls** | 控制 | 时间控制、下指令、开箭头(下面细说) |
| **Checkpoints** | 存档 | 下拉框选存档 = 立刻换策略,不重启。**Sync**(同步)重新扫描目录,训练中存了新档时点它;**Use Latest**(用最新)跳到编号最大的 |
| **Rewards** | 奖励 | 上半:16 项奖励的实时条形图(约 1 秒平均,绿 = 加分、红 = 扣分、越长越大);下半 **Plots**(曲线)看瞬间变化;**Select terms**(选择项)只勾关心的几项 |
| **Metrics** | 指标 | 只有一项(动作加速度),阶段 2 再看 |
| Visualization / Groups / Camera Feeds | 可视化 / 分组 / 相机 | 调仿真模型用,阶段 4 再说 |

### Controls 标签页里的三块

**Simulation(仿真)——控制时间**

| 按钮 | 中文 | 用法 |
|---|---|---|
| Pause / Play | 暂停 / 继续 | 看到怪动作先暂停 |
| Step | 单步 | 暂停状态下每按一次前进 1/50 秒,逐帧看它怎么绊倒 |
| Reset Environment | 重置环境 | 回到初始站姿。**换存档后按一下**,保证每个存档从同一起点比 |
| Speed | 速度 | Slower 慢放 / 1x / Faster |

**Info(信息)**:`Steps` = 查看器启动以来总步数,**只有手动 Reset 才归零,摔倒自动重置不归零**——它不是回合长度。
`Actual RT` 低于 1x 说明电脑跟不上、画面比真实慢。

**Commands → Twist(速度指令)**

| 控件 | 含义 |
|---|---|
| **Enable**(启用) | 勾上滑块才生效。**不勾时指令由环境每几秒随机出**,鸭子乱走不是失控。做对比必须勾 |
| lin_vel_x | 前后速度,m/s,正 = 前。lin = linear,vel = velocity |
| lin_vel_y | 左右横移,m/s,正 = 左(螃蟹步,不是转弯) |
| ang_vel_z | 转向角速度,rad/s,正 = 左转(1 rad ≈ 57°)。ang = angular |
| Max lin_vel_x 等 | 只改滑块上限。默认值 = 训练范围(前后 ±0.4,横移 ±0.3,转向 ±1.0)。**超出 = 超出训练分布,表现无保证** |
| **Zero**(归零) | 三个速度一键归 0 = 让它站住 |

x/y/z 是鸭子自己身体的方向(x 面前、y 左手、z 朝上),不是地图方向。**Enable 只管镜头跟着的那一只**,另一只照样随机指令。

**Scene → Debug Viz(调试可视化)**

- **Enabled**(启用):总开关。**All envs**(所有环境):两只都画。
- **Twist**:在鸭子头顶画 4 根箭头。**读法 = 看两对是否重合**:

| 箭头 | 颜色 | 方向 | 表示 |
|---|---|---|---|
| 指令线速度 | 深蓝 | 水平 | 让它往哪走多快 |
| 实际线速度 | 青色 | 水平 | 实际往哪走多快 |
| 指令转速 | 绿 | 竖直 | 让它转多快(上 = 左转) |
| 实际转速 | 亮绿 | 竖直 | 实际转多快 |

  长度 = 速度大小,速度为 0 的箭头长度为 0(看不见),所以站着时常只剩一根。
  青色比深蓝短 = 追不上指令;青色偏一侧 = 边走边溜;指令 0 青色还乱晃 = 站不稳;被推瞬间青色突变 = 推力,看几步内缩回来。
- **upright**:平地任务里勾了没效果(只在崎岖地形配了地面传感器时画线)。看躯干正不正直接看 Rewards 里的 upright 条。

### 标准观察流程(每个存档都一样做,才有可比性)

1. Checkpoints 选存档
2. 点 Reset Environment
3. Twist 勾 Enable、点 Zero,站 10 s,看 Rewards 条
4. lin_vel_x 拉到 0.4,走 20 s,开着 Debug Viz 看两根水平箭头
5. 摔倒或怪动作 → Pause → Step 逐帧看
6. 记进第五节的表

### play 里的三个陷阱

1. **每 0.5–1 s 被推一次**(训练时 3–6 s 一次,±0.3 m/s)。踉跄多半是刚被推,看被推后几步能不能稳住。【microduck 参数;"回放配置 ≠ 训练配置"这件事换机器人也一样】
2. **play 的课程学习从第 0 级算起**(每次都是新建环境):`action_rate_l2` 权重固定 −0.1(训练 1500 轮后是 −1.0),`head_pose_bias` 恒为 0。所以 **Rewards 条只用来在存档之间横向比**,绝对值以 TensorBoard 为准。
3. **回放是单个样本**。想量回合长度:鸭子刚站起时 Pause 记 Steps,下次站起时再记,相减 = 这一回合的步数(50 步 = 1 s)。多量两三次。

---

## 三、TensorBoard:面板说明

**顶部标签**:SCALARS(标量)和 TIME SERIES(时间序列)是同一批曲线的两种排版,用 SCALARS,分组清楚。

**左侧边栏**

| 控件 | 中文 | 怎么设 |
|---|---|---|
| Smoothing | 平滑 | 看趋势 0.6–0.9;**读某一轮真实值拉到 0** |
| Horizontal Axis | 横轴 | 选 **Step**,一步 = 一轮迭代 |
| Ignore outliers | 忽略离群点 | 勾上,纵轴不被极端值撑大 |
| Tooltip sorting method | 悬停框排序 | 多 run 对比选 descending(分高的排上面);单 run 无所谓 |
| Runs | 运行列表 | 勾选显示哪些 run,一个 run 一种颜色。阶段 2 对比就靠它 |

**主区域**:曲线按「组名/项名」分组。鼠标悬停读值(Value = 原始值,Smoothed = 平滑值,Step = 轮数);框选放大,双击恢复。

**分组一览**(组名来自框架【换机器人也一样】,组内项名 microduck 特有)

| 分组 | 记什么 | 阶段 1 |
|---|---|---|
| **Train** | `mean_reward` 平均总奖励;`mean_episode_length` 平均回合长度(满长 20 s = 1000 步);带 `/time` 的是按时间画,不看 | **必看** |
| **Episode_Reward** | 16 项各自得分,和 Rewards 面板同名 | **必看** |
| **Episode_Termination** | 回合为何结束:`fell_over` 摔倒(躯干倾斜 > 70°)、`time_out` 撑满 20 s、`nan_state` 物理数值出错(**应恒为 0**) | **必看** |
| **Metrics** | 不打分的体检数据:`twist/error_vel_xy` 速度误差、`twist/error_vel_yaw` 转向误差、腾空时长、打滑、抬脚高度,物理单位 | 看 |
| **Curriculum** | 课程学习各项当前级别 | 看,解释曲线为什么在 500/750/1000/1250/1500/2000 轮拐弯 |
| Loss / Policy / Perf | PPO 内部量 / 动作噪声 `mean_std`(由大变小正常)/ 速度 | 暂不看 |

**读曲线的三条规矩**

1. `Episode_Reward` 下**所有惩罚项必须 ≤ 0**,出现正值 = 符号写反,策略在钻空子。
2. 总奖励涨不算数,**主任务项 `track_linear_velocity` 自己得涨**,否则可能只是靠站着不动刷正则项。
3. `Episode_Reward` 是**整回合累计再按 20 s 满长折算**,摔得早所有项都偏小 → 看到一片项低,**先查 `fell_over`**。
4. `Episode_Termination/*` 是**这批重置的回合里各原因的个数**,看比例不看绝对值。

---

## 四、16 项奖励速查(权重来自当前配置;正 = 加分、满分 ≈ 权重;负 = 扣分、越接近 0 越好)

| 类 | 项 | 中文 | 权重 | 管什么 | 可迁移 |
|---|---|---|---|---|---|
| 任务 | track_linear_velocity | 线速度跟踪 | +2.0 | 实际前后/左右速度离指令多远。**主任务** | 通用 |
| 任务 | track_angular_velocity | 角速度跟踪 | +2.0 | 实际转速离指令多远 | 通用 |
| 任务 | head_pose_tracking | 头部姿态跟踪 | +2.0 | 头/脖子 4 关节到没到指令角度。**play 里头会自己动**(指令随机,Twist 管不到) | microduck |
| 姿态 | upright | 直立 | +2.0 | 躯干正不正 | 通用 |
| 姿态 | pose | 姿势 | +1.0 | 腿部关节离标准站姿多远;站着严、走路松 | 通用 |
| 步态 | air_time | 腾空时间 | +3.0 | 每步离地 0.125–0.3 s 才给分,逼它真迈步。**指令 0 时不计** | 腿足通用 |
| 步态 | foot_clearance | 抬脚高度 | −2.0 | 摆腿时离地不够 2 cm 扣分,防拖地 | 腿足通用 |
| 步态 | foot_swing_height | 摆动高度 | −0.25 | 落地时检查这一步最高点 | 腿足通用 |
| 步态 | foot_slip | 打滑 | −0.1 | 踩地还在滑。故意弱,鸭子转弯靠拧脚 | 腿足通用 |
| 平滑 | action_rate_l2 | 动作变化率 | −0.1→−1.0(课程) | 这步和上步输出差多少,抖就扣 | 通用 |
| 平滑 | body_ang_vel | 躯干角速度 | −0.05 | 躯干晃多快 | 通用 |
| 平滑 | angular_momentum | 角动量 | −0.02 | 全身甩得多厉害 | 通用 |
| 安全 | dof_pos_limits | 关节极限 | −1.0 | 顶到关节极限附近扣分 | 通用 |
| 安全 | self_collisions | 自碰撞 | −1.0 | 腿撞躯干/电池盒 | 通用 |
| 关闭 | body_pose_tracking | 身体姿态跟踪 | 0 | 此任务不用,留槽位 | — |
| 关闭 | head_pose_bias | 头部偏差 | 0→3(课程),play 恒 0 | 纠正走路时头下耷 | microduck |

站着时步态项全为 0 是设计,不是错。**总奖励涨要看是谁在涨**:任务/姿态项涨是真本事;只有平滑/安全项变好可能是"什么都没做"。

---

## 五、回放记录

| 存档 | 看到的行为 | 主要问题 | 奖励条里最突出的一根 |
|---|---|---|---|
| 0 | 无论给什么指令(含全零)都向前倒;倒后回合结束自动重置,反复倒 | 站都站不住,更谈不上听指令 | (待补) |
| 250 | 站起约 50 步(≈1 s)后向后倒(model_0 是向前倒);倒下过程中 pose 先掉、upright 后掉;倒地时 air_time 为正——脚离地是因为身体翻倒,不是在迈步 | 站不住;跟踪项此时无意义 | pose、upright 掉得最明显 |
| 500 | | | |
| 1000 | | | |
| 2000 | | | |
| 5000 | | | |
| 12500 | | | |

## 六、同一迭代的 TensorBoard 读数

| 迭代 | Train/mean_episode_length | Train/mean_reward | Episode_Reward/track_linear_velocity | Episode_Termination/fell_over |
|---|---|---|---|---|
| 0 | | | | |
| 500 | | | | |
| 1000 | | | | |
| 2000 | | | | |
| 5000 | | | | |
| 12500 | | | | |

**参考读数**(同配置、同 seed 的另一次 run:Windows `2026-09-18_18-57-35_velocity`,1024 envs,跑了 1750 轮;从事件文件直接解析,四舍五入):

| 迭代 | mean_episode_length(步) | mean_reward | fell_over(每步平均个数) | time_out(每步平均个数) |
|---|---|---|---|---|
| 0 | 20 | 0.07 | 2.3 | 1.2 |
| 1–11 | 33–43 | 0.2–0.6 | 27–37 | 0 |
| 250 | 199 | 13 | 3.3 | 0 |
| 500 | 825 | 79 | 0.5 | 1.5 |
| 1000 | 837 | 91 | 0.6 | 0.8 |
| 1750 | 927 | 95 | 0.08 | 1.4 |

读法:① 回合长度从第 0 轮就有值(20 步),只是相对满长 1000 步太小,**曲线贴着横轴看起来像没有**——悬停读值、框选放大或切对数轴才看得见;② `time_out` 在 250–500 轮之间超过 `fell_over`,和 play 里"model_250 撑 1 s、model_500 站得住"一致;③ play 里量到的回合长度比这里短(play 每 0.5–1 s 推一次),看趋势不看数值。
`Episode_Termination/*` 的数值 = 每个环境步里因该原因结束的回合数的平均,所以早期 fell_over ≈ 28 是"1024 只鸭子每 37 步摔一次"的意思。

## 七、映射表(最终产出)

| 看到的行为 | 先查哪个指标 | 判读 | 可迁移性 |
|---|---|---|---|
| 一放下就倒、对指令没反应 | `Train/mean_episode_length` 极短、`fell_over` 占绝大多数 | 策略还没学会站,别看别的项 | 通用 |
| 某个加分项(如 air_time)为正,但鸭子明明在倒 | 同时看 upright 和回合长度 | **单项奖励脱离上下文不可信**:air_time 只认"脚离地 0.125–0.3 s",翻倒时脚也离地。先确认站得住,再看步态项 | 通用 |
| 站不住的存档 | `Train/mean_episode_length`、`fell_over`/`time_out` 比例 | 跟踪箭头、track_* 条都不用看,先解决站 | 通用 |
| 曲线前段贴着横轴"没有值" | 悬停读 Value;或框选前几百轮放大;或点图下方按钮切对数纵轴 | 数值小不等于没有。回合长度 20 步 vs 满长 1000 步,在线性轴上就是一条贴地的线 | 通用 |
| | | | |

## 八、结论

(阶段 1 结束时填)

---

## 附:16 项奖励的来源(核对自上游源码)

奖励是**任务定义的一部分**,写在任务配置里,不在网络里。分三层:

| 层 | 在哪 | 包含哪些项 | 可迁移性 |
|---|---|---|---|
| ① 框架的"速度跟踪"通用模板 | `src/mjlab/src/mjlab/tasks/velocity/velocity_env_cfg.py` | track_linear_velocity、track_angular_velocity、upright、pose、body_ang_vel、angular_momentum、dof_pos_limits、action_rate_l2、air_time、foot_clearance、foot_swing_height、foot_slip(另有 soft_landing,microduck 删掉了) | 换机器人也一样:mjlab 里人形 Unitree G1、四足 Unitree Go1 用的是同一个模板 |
| ② 各机器人自己调参数 | microduck:`src/microduck_rl/src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py` | 同一批项,改权重、改容差、改"哪只脚/哪个关节" | 方法通用,数值 microduck 特有 |
| ③ 各机器人自己加的项 | 同上 | self_collisions(用框架现成函数)、head_pose_tracking、body_pose_tracking、head_pose_bias(microduck 自写) | 自碰撞通用;头部三项 microduck 特有(它的头占体重约 38%) |

同一模板在三台机器人上的差异举例:`air_time` 在 microduck 是 +3.0,在 G1 和 Go1 都设为 0;Go1 另加了小腿、躯干头部的碰撞惩罚。
改奖励必须重新训练,已有存档不受影响;惩罚项符号写反是头号坑(上游经验手册硬规则第一条)。
