# 阶段 1 结构图:学会看

复习用:一张图回忆阶段 1 的知识结构。图里的「§五」指课程 [`stage1_observe.md`](stage1_observe.md) 第五节,细节回那里查。

```mermaid
flowchart TB
  ck(["拿到一个存档"])

  subgraph know["§一 看之前要知道的四件事"]
    direction LR
    ep["<b>回合与终止</b><br/>time_out:撑满 20 秒<br/>fell_over:倾斜超 70°<br/>倒了立刻重新放下"]
    cmd["<b>指令</b><br/>速度指令 3–8 秒一换<br/>一部分是全零 = 站着别动<br/>头部指令随机<br/>头自己转不是故障"]
    cur["<b>课程学习</b><br/>前 2000 轮逐步加码<br/>→ 曲线出现拐点"]
    push["<b>推力</b><br/>训练时每 3–6 秒<br/>推一下"]
  end

  diff["<b>回放 ≠ 训练</b><br/>推得更勤(0.5–1 秒)<br/>课程从 0 级算起<br/>只有重启回放才归零<br/>只有几只鸭子<br/>⇒ 两边比趋势,不比数值"]

  subgraph viewer["§二 回放:这个存档此刻在做什么"]
    flow["<b>标准观察流程</b><br/>Reset → 零指令站 10 秒<br/>→ lin_vel_x 0.4 走 20 秒<br/>→ ang_vel_z 0.5 转 10 秒<br/>→ 归零看能否停稳"]
    arrows["<b>速度箭头</b><br/>水平:深蓝指令 vs 青色实际<br/>竖直:绿指令 vs 亮绿实际<br/>看每对是否重合"]
    bars["<b>奖励条 / Steps</b><br/>绿加分、红扣分<br/>两次放下时 Steps 之差<br/>= 一个回合的步数"]
  end

  subgraph board["§三 曲线面板:训练中分数怎么变"]
    groups["<b>只看四组</b><br/>Train 回合长度、总分<br/>Episode_Termination<br/>摔倒占比<br/>Episode_Reward 各项得分<br/>Curriculum 课程级别"]
    rules["<b>五条规矩</b><br/>① 贴着横轴 ≠ 没有值<br/>② 回合短 → 各项都小<br/>③ 主任务项自己要涨<br/>④ 拐点先查 Curriculum<br/>⑤ 回合长度是最近<br/>100 个回合的平均"]
  end

  rew["<b>§四 16 项奖励分六类</b><br/>任务 · 姿态 · 步态<br/>平滑 · 安全 · 关闭<br/>站着时步态项全为 0<br/>单看一项不可信"]

  subgraph ladder["§五 诊断阶梯:前一问没过,后面先不看"]
    q1["<b>① 站得住吗?</b><br/>回放:零指令倒不倒<br/>一个回合多少步<br/>曲线:回合长度接近 1000<br/>time_out 超过 fell_over"]
    q2["<b>② 听指令吗?</b><br/>回放:两对箭头是否重合<br/>曲线:<br/>track_linear_velocity<br/>track_angular_velocity 在涨"]
    q3["<b>③ 步态像样吗?</b><br/>回放:抬脚迈步还是贴地蹭<br/>打不打滑<br/>曲线:air_time 为正且在涨<br/>foot_clearance、foot_slip<br/>扣分变小"]
    q4["<b>④ 细节好吗?</b><br/>回放:抖不抖、归零能否站定<br/>被推后几步稳住<br/>曲线:action_rate_l2 扣分<br/>对照 Curriculum<br/>看是不是刚加码"]
    q1 --> q2 --> q3 --> q4
  end

  out(["<b>诊断结论</b><br/>主要问题是 X(卡在第几问)<br/>对应指标 Y,读数多少"])

  ck --> viewer
  ck --> board
  cur -. 解释看到的现象 .-> diff
  diff -.-> viewer
  viewer --> q1
  board --> q1
  rew -. 任务类 .-> q2
  rew -. 步态类 .-> q3
  rew -. 平滑类 .-> q4
  q4 --> out

  classDef core fill:#e3f2e1,stroke:#4a8a3f,color:#1b3a16
  classDef duck fill:#fdf0dc,stroke:#c98a2b,color:#4a3108
  class q1,q2,q4,diff,rules core
  class rew,q3 duck
```

读法：拿到存档后，回放和曲线面板两边一起看（§二、§三），证据都汇到诊断阶梯（§五），从第 ① 问开始逐问往下，卡住的那一问就是结论。§一 的四件事和「回放 ≠ 训练」用来解释看到的现象；§四 的奖励分类告诉你每一问该看哪几项。

颜色：**绿色**是【换机器人也一样】的判读方法；**橙色**是【microduck 特有】的内容（具体奖励项、腿足步态）；紫色是工具和背景知识。
