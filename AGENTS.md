# AGENTS.md — 三处环境的分工与同步约定

> 这份文件只管一件事:**哪台机器干什么、文件怎么在它们之间流动**。
> 训练/奖励/sim2real 的经验看 `src/microduck_rl/AGENTS.md`;学习笔记和日常命令看根目录 `README.md`。

## 一、三处 clone,各管一摊

**三处都是 `github.com/tunghsingw/robolab` 的 clone,目录结构完全相同**,只是工作区根不同:

| 环境 | 工作区根 | 负责什么 |
|---|---|---|
| **讨论沙箱**(agent 在这) | agent 的工作目录 | 读代码、改脚本、写文档。**不跑任何真实负载** |
| **Windows 11 原生**(PowerShell) | `D:\robot\robolab\` | 推理:`run_infer*.ps1`,原生 MuJoCo 窗口。也能训练(实测比 WSL 慢 6%) |
| **WSL2 Ubuntu 24.04**(用户 `robot`) | `~/robolab/` | 训练主力、`play` 回放、导出 ONNX、TensorBoard;以后的 duck-sim 只能在这 |

**仓库内的相对路径三处一模一样**,所以 agent 说 `src/microduck_rl/scripts/export.py`,
三处都能直接对号入座,不需要换算——只有写成命令给用户时才要补上对应的根。

Windows ↔ WSL 之间可直接走 `/mnt/d/robot/robolab/...`(WSL 里访问 D 盘)。
⚠️ **WSL 侧仓库必须放在 WSL 自己的文件系统(`~/robolab`),不能放 `/mnt/d`**——跨文件系统 I/O 慢好几倍,训练会被拖垮。

### 目录结构

采用 **ROS 工作区惯例**:根目录是工作区,第三方仓库统一进 `src/`,由清单文件钉住版本。

```
<工作区根>/                   ← 用户的 git 仓库(github.com/tunghsingw/robolab)。三处各是它的一份 clone/副本
├── README.md                         学习笔记(人读)
├── AGENTS.md CLAUDE.md               环境分工与 agent 约定
├── GLOSSARY.md REFERENCES.md         名词表 / 外部资料清单(人和 agent 共用)
├── upstream.repos                    上游清单:URL + 锁定的 commit
├── .gitignore
├── run_infer*.ps1                    自写脚本(推理入口)
├── patches/                          对上游的适配性修改(唯一记录)
├── policies/                         ONNX 策略
├── experiments/                      实验记录(阶段 2 起)
└── src/                          ←   **第三方,整个 git 忽略**,由 upstream.repos 拉取
    ├── microduck/                    上游:Rust 机载运行时 + duck-sim
    ├── microduck_rl/                 上游:训练(logs/ 和 .venv 也在这下面)
    └── mjlab/                        上游:参考源码
```

三处的 `src/` 内容由 `upstream.repos` + `patches/` 唯一确定,**所以不需要在沙箱里再存一份别处的镜像**。
唯一的合法差异:补丁 02(win32 的 cu128 索引)只在 Windows 打,Linux 侧不打。

### 上游仓库怎么管

**不用 submodule,也不用 subtree。** 用"目录 + gitignore + 声明式清单 + 补丁":

| 环节 | 怎么做 |
|---|---|
| 获取 | `vcs import src < upstream.repos`(工具:`pip install vcs2l`,vcstool 的继任者,命令名仍是 `vcs`) |
| 版本锁定 | `upstream.repos` 里写死 commit,三处环境拿到的代码完全一致,补丁一定打得上 |
| 本地修改 | 存成 `patches/*.patch`,**只存适配性修改**,实验性改动不存(见 `patches/README.md`) |
| 升级上游 | 改清单里的 commit → 重新 import → 补丁打不上就手动改再重新生成 |

为什么不用 submodule:用户**没有上游写权限**,改了没地方 push,要用就得先 fork 三个仓库。
为什么不用 subtree:三个仓库几十 MB 且含大量 CAD 资产,并进学习笔记仓库不划算;上游都是公开活跃仓库,随时能拉。
**以后阶段 3 建自己的任务包时,mjlab 会真正变成依赖,那时改用 `[tool.uv.sources]` 才是正解——路线会演进。**

`src/` 下每个上游 clone 的 `.git/` 要保留——它是判断"哪些文件相对上游被改过"的唯一依据。

## 二、给 AI agent 的硬性约定

1. **沙箱里的 Bash 不是用户的机器。** 在沙箱里跑不了 `run_infer.ps1`、调不到 `wsl.exe`、看不到 `logs/` 和 GPU。
   需要真机验证的事,**给用户可直接复制的命令并标明在哪一侧敲**,不要声称自己执行过。
2. **命令按目标环境写路径**:PowerShell 用 `D:\robot\robolab\...`;WSL 用 `~/robolab/src/microduck_rl`。
   **绝不把 `/srv/workspace/...` 写进交付物**(脚本、文档、README)。
3. **沙箱的 `src/` 就是三处应有的上游状态**(由 `upstream.repos` + `patches/` 唯一确定)。
   要知道相对上游改了什么:`git -C src/microduck_rl status`。
   真机上如果出现这之外的改动,那是临时实验,**让用户把现状发过来再看,不要假设**。
4. ⚠️ **换行不统一**:三个 clone 里 git 跟踪的文件是 **CRLF**(Windows 侧 `core.autocrlf` 检出的),
   根目录自写的 `.ps1`/`.md` 是 LF,训练日志是 CRLF。沙箱的三个 clone 已设 `core.autocrlf=input`,
   git 不再把换行差异当改动;但**手动比对两份文件时必须先 `tr -d '\r'`**,否则整个文件都显示不同。
5. **改文档和脚本一律在沙箱改,改完 commit + push**,用户在真机 `git pull`。
   不要让用户在三处各改一遍,也不要再列 XFTP 清单——那是建仓库之前的做法。
6. 会话收尾时,若这轮有提交,**说清楚推了什么、用户该在哪台机器 `git pull`**。
7. ⚠️ **领域常识不许凭记忆回答**——技术分类、领域现状、谁家用什么方法、缩写全称、论文结论,
   这类问题先查 `REFERENCES.md`,查不到就**联网核实**,核实完把来源加进 `REFERENCES.md`(注明它能回答什么)。
   这条是踩坑立的:README 最初那版"两条技术栈"的分类凭记忆写,三处硬伤,核实后才改对。
8. **对话里出现新技术名词,当场写进 `GLOSSARY.md`**(中英对照、简称全称、一句话中文解释、核实标记),
   不要只在当轮解释一次就过去。用户的学习基础靠这个文件累积。
9. **提交不带 AI 痕迹。** commit 消息**不要**加 `Co-Authored-By` 之类的 AI 署名,也不要在消息里提工具名。
   作者身份由 `git config --local` 设为 `tunghsingw <tunghsingw@163.com>`,三处 clone 都一样。
10. ⚠️ **不要往 `src/` 里写任何自己的东西。** 整个 `src/` 是第三方、不进用户的仓库,写进去的东西重装即失。
   自写脚本、导出的 onnx、实验记录一律放**工作区根目录**;对上游源码的修改存成 `patches/*.patch`。
   给用户的命令里凡有重定向/导出路径,都要**显式指到根目录**
   (例:在 `src/microduck_rl` 下跑训练时写 `... | tee ../../experiments/xxx.log`,不是 `tee xxx.log`)。

## 三、同步约定

**三处都是同一个仓库的 clone,同步走 git,不要再手工拷贝。**

| 内容 | 怎么同步 |
|---|---|
| 文档、脚本、`upstream.repos`、`.gitignore`、`patches/`、自训 ONNX、`experiments/` | **git**。沙箱改完 push,真机 `git pull` |
| `src/` 下的上游代码 | **各自 `vcs import` + `git apply`**。清单钉死 commit,所以三处必然一致 |
| `.venv/` | **各自 `uv sync`**。平台相关,且 uv 入口内嵌绝对路径,搬过去必失效 |
| `logs/`(训练输出) | **不同步**。上 G,留在训练的那台机器上 |

**XFTP 只剩一个用途**:把真机上未纳入 git 的临时东西(训练日志片段、临时改过的文件)拉给 agent 看。
需要时再拉,不必常备镜像。

谁改谁负责:

- **文档、脚本、配置** —— 一律在沙箱改,agent commit + push,用户 `git pull`。
- **实验记录** —— 谁做的实验谁写进 `experiments/`,commit + push。
- **训练产出的 ONNX** —— 在哪台机器导出就在哪台 `git add`,push 之后另外两处 pull 即可。
- **临时的上游代码改动**(比如改奖励权重做消融) —— 做完 `git checkout` 还原,**不要 commit,也不要存成补丁**;
  要保留的是结论,写进 `experiments/`。

⚠️ 一个反复踩过的坑:从 Hugging Face 下载官方策略会带来它自己的 `policies/.gitattributes`
(声明 `*.onnx` 走 Git LFS),覆盖本仓库的同名文件。不还原的话,以后提交的自训 ONNX 会被静默存成
130 字节的 LFS 指针,clone 下来是坏的且**没有任何报错**。`git status` 显示该文件被改就执行
`git checkout policies/.gitattributes`。

## 四、文档分工(这几个 md 谁管什么)

根目录这几个文件,**各有唯一职责,不要互相抄**:

| 文件 | 读者 | 内容 | 谁是权威 |
|---|---|---|---|
| `INSTALL.md` | 人 | **从零搭建步骤**,不依赖现有文件 | 安装流程 |
| `README.md` | 人 | 学习笔记:目标、领域地图、实践路线、日常命令、按键表、进度 | 学习与操作内容 |
| `AGENTS.md`(本文件) | AI agent | 环境分工、路径换算、同步约定、行为约束 | **三处环境与同步规则** |
| `GLOSSARY.md` | **人 + agent 共用** | 技术名词:中英对照、简称全称、一句话中文解释 | **名词定义** |
| `REFERENCES.md` | **人 + agent 共用** | 外部资料清单,每条注明"它能回答什么" | **外部信息出处** |
| `CLAUDE.md` | Claude Code | 只有一行 `@AGENTS.md` | 无(纯指针) |

`GLOSSARY.md` 和 `REFERENCES.md` 是**双方共同查看的认知基线**——统一词汇、统一信息来源,
也是用户的学习基础。两个文件都只增不删(条目错了就改正并更新核实标记,不要删掉)。

**为什么正文放 `AGENTS.md` 而不是 `CLAUDE.md`**:`AGENTS.md` 是跨工具的通用约定(别的 agent 也认),`CLAUDE.md` 只有 Claude Code 认。
内容写一份在 `AGENTS.md`,用一行 `@AGENTS.md` 的 `CLAUDE.md` 把 Claude Code 引过来,既通用又保证加载,且**永远不会两份说法打架**。
`src/microduck_rl/` 里就是这个写法(其 `CLAUDE.md` 内容就是 `@AGENTS.md`),根目录跟它保持一致。

⚠️ 本文件放在**根目录**(非 git 目录),不要把这些内容写进 `src/microduck_rl/AGENTS.md` 或 `src/mjlab/AGENTS.md`——那两个是上游 git 跟踪的文件,`git pull` 会冲掉。

⚠️ 本项目是学习项目,**文档只记"现在是什么样",不留变更记录和日期戳**。环境变了就直接改正文,不要另起变更日志。
