# 阶段 2:学会改 —— 奖励消融

**目标**:改一个奖励权重之前,能**预测**行为会往哪个方向变;训练完能**判断**看到的变化是真的由这次改动造成,还是随机波动。

**完成标准**:① 至少 4 个单变量实验,每个都是"先写预测 → 训练 → 回放 + 曲线验证 → 写结论";② 对最后一个实验,预测方向说对;③ 能说出对照组的"噪声带"有多宽。

**前置**:阶段 1 的判读能力(看回放说出问题、找到对应指标)。阶段 1 目前**未完成**(第 5–10 步待做),阶段 2 做到哪一步用到哪个判读,就回去补对应的存档。

---

## 大纲

### 第 1 步:建立对照组(baseline)

- 实验组和对照组**只差一个变量**:代码版本、环境数量、随机种子、训练轮数全部相同。【换机器人也一样】
- 候选:现成的 `2026-09-15_12-26-40_velocity`,前提是它的 `params\env.yaml` 里 `num_envs: 1024`,且 `git\microduck_rl.diff` 的 commit 与 `upstream.repos` 锁定的一致。对不上就新训一个 baseline。
- 每个实验跑 **1000 轮**(Windows 约 40 分钟)。依据:回合长度在 250–500 轮之间跳升,步态质量相关的课程在 1500 轮前加码;1000 轮能看清"站 → 走"阶段的差别。

### 第 2 步:量噪声带

- 同一配置换一个种子(`--agent.seed 43`)再跑一次 baseline,两条曲线的差距就是"什么都没改也会有的差别"。
- **之后任何实验的差别,小于这个差距就不算数。**【换机器人也一样】这是阶段 2 最容易被跳过、也最重要的一步。

### 第 3 步:学会改权重的方法

- **用的就是上游自带的训练配置**:任务 `Mjlab-Velocity-Flat-MicroDuck` 的奖励、课程、域随机化全部照旧,算法是 rsl_rl 的 PPO。阶段 2 只动其中一个数字。
- 参数在哪:`src/microduck_rl/src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py`(奖励权重在"=== REWARDS ==="一段,约 270–350 行);其中 12 项的默认值来自 mjlab 的通用模板 `src/mjlab/src/mjlab/tasks/velocity/velocity_env_cfg.py`,microduck 在自己文件里覆盖。
- **方法一(推荐):命令行覆盖,不改文件。** 格式 `--env.rewards.<项名>.weight <值>`,项名里的下划线写成连字符或下划线都行(已用锁定版本 tyro 1.0.5 验证)。例:

  ```powershell
  & $uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 1024 --agent.max-iterations 1000 --agent.run-name e1_airtime0 --env.rewards.air-time.weight 0.0
  ```

  **验证是否生效**:训练开头打印的 `Active Reward Terms` 表里,该项的 Weight 一栏应显示新值。不对立刻 Ctrl+C。命令太长会被 PowerShell 截断,见 README。
- **方法二(兜底):临时改上面那个配置文件**,训完 `git -C src/microduck_rl checkout .` 还原,**不提交、不存补丁**(AGENTS.md 同步约定)。
- 陷阱:`action_rate_l2` 和 `head_pose_bias` 的权重由课程学习按轮数覆盖,改它们的初始权重在 500 轮后就被盖掉。改这两项要改课程,不是改权重。
- `Episode_Reward/*` 记的是**乘过权重**的值。权重改成 0,曲线就是 0,不代表行为没了——要看回放和 Metrics 组。

### 第 4 步:单变量实验(每个都先写预测)

| # | 改什么 | 为什么选它 | 预测方向(实验前填) |
|---|---|---|---|
| E1 | `air_time` +3.0 → 0 | 最直观:去掉"迈步奖励"会怎样 | |
| E2 | `upright` +2.0 → 0.5 | 上游注释说弱了会前倾、被推时向前摔 —— 验证作者的说法 | |
| E3 | `foot_slip` −0.1 → −1.0 | 上游注释说太强会妨碍转弯 —— 验证作者的说法 | |
| E4 | 故意把一个惩罚项符号写反(如 `foot_clearance` −2.0 → +2.0) | 亲眼看"奖励钻空子":惩罚项在 TensorBoard 里变成正值、策略专门去刷它 | |

每个实验看的东西:回放(同一套标准观察流程)+ TensorBoard 叠在 baseline 上(左侧 Runs 两个都勾,Tooltip sorting 选 descending)。

### 第 5 步:归纳

- 哪些项是"阻碍动作"的(body_ang_vel 这类,动态任务要调低),哪些是"只管平滑"的(action_rate 这类,可以加重但要在技能学会之后)。——上游经验手册"Regularizers come in two kinds"一条,用自己的实验印证。
- **比较奖励时比"奖励总量",不比权重**:同一个惩罚权重,在正奖励总量大 4 倍的任务里等于弱了 4 倍。【换机器人也一样】

---

## 实验记录

| # | 改动 | 预测 | 回放看到的 | 关键指标(vs baseline) | 超出噪声带? | 结论 |
|---|---|---|---|---|---|---|
| baseline(seed 42) | — | — | | | — | |
| baseline(seed 43) | 换种子 | — | | | — | 噪声带 = |
| E1 | | | | | | |
| E2 | | | | | | |
| E3 | | | | | | |
| E4 | | | | | | |
