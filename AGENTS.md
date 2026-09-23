# AGENTS.md — 三处环境的分工与同步约定

> 这份文件只管一件事:**哪台机器干什么、文件怎么在它们之间流动**。
> 训练/奖励/sim2real 的经验看 `src/microduck_rl/AGENTS.md`;学习笔记和日常命令看根目录 `README.md`。

## 一、两个运行环境,沙箱里两份镜像

开发机上有两个环境,沙箱里各存一份镜像:

| 环境 | 真机路径 | 沙箱里对应 | 负责什么 |
|---|---|---|---|
| **Windows 11 原生**(PowerShell) | `D:\robot\robolab\` | **根目录** | CPU 推理:`run_infer*.ps1`,弹原生 MuJoCo 窗口 |
| **WSL2 Ubuntu 24.04**(用户 `robot`) | `~/robot/microduck/` | **`wsl/`** | GPU 训练、`play` 回放、导出 ONNX、TensorBoard |

讨论沙箱(一台独立 Ubuntu 上的工作目录,agent 就在那儿)本身**不跑任何真实负载**,
它只是这两份镜像的编辑处:读代码、改脚本、写文档。

路径换算,前缀一换即可:

| 沙箱 | 真机 |
|---|---|
| `<X>` | `D:\robot\robolab\<X>` |
| `wsl/<X>` | `~/robot/microduck/<X>` |

例:沙箱 `wsl/src/microduck_rl/scripts/export.py` = WSL 的 `~/robot/microduck/src/microduck_rl/scripts/export.py`。

Windows ↔ WSL 之间可直接走 `/mnt/d/robot/microduck/...`(WSL 里访问 D 盘),不经过 XFTP。
WSL 侧仓库必须放在 WSL 自己的文件系统(`~/robot/...`),不能放 `/mnt/d`——跨文件系统 I/O 慢好几倍。

### 目录结构

采用 **ROS 工作区惯例**:根目录是工作区,第三方仓库统一进 `src/`,由清单文件钉住版本。

```
<工作区根>/                   ← 用户的 git 仓库(github.com/tunghsingw/robolab)。三处各是它的一份 clone/副本
├── README.md                         学习笔记(人读)
├── AGENTS.md CLAUDE.md               环境分工与 agent 约定
├── GLOSSARY.md REFERENCES.md         名词表 / 外部资料清单(人和 agent 共用)
├── upstream.repos                    上游清单:URL + 锁定的 commit
├── .gitignore
├── run_infer*.ps1 setup*.ps1         自写脚本
├── patches/                          对上游的适配性修改(唯一记录)
├── policies/                         ONNX 策略
├── experiments/                      实验记录(阶段 2 起)
├── src/                          ←   **第三方,整个 git 忽略**
│   ├── microduck/                    上游:Rust 机载运行时 + duck-sim
│   ├── microduck_rl/                 上游:训练(Windows 那份)
│   └── mjlab/                        上游:参考源码
└── wsl/                          ←   = WSL ~/robot/microduck/(只存在于沙箱)
    └── src/microduck_rl/             训练(WSL 那份,真正跑训练的)
```

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

**不传进沙箱**:`.venv/`(平台相关,各自 `uv sync` 生成)、`logs/`(训练输出,上 G)。
**`.git/` 要传**——它是判断"哪些文件相对上游被改过"的唯一依据,值这几十 MB。

## 二、给 AI agent 的硬性约定

1. **沙箱里的 Bash 不是用户的机器。** 在沙箱里跑不了 `run_infer.ps1`、调不到 `wsl.exe`、看不到 `logs/` 和 GPU。
   需要真机验证的事,**给用户可直接复制的命令并标明在哪一侧敲**,不要声称自己执行过。
2. **命令按目标环境写路径**:PowerShell 用 `D:\robot\robolab\...`;WSL 用 `~/robot/microduck/src/microduck_rl`。
   **绝不把 `/srv/workspace/...` 写进交付物**(脚本、文档、README)。
3. **沙箱两份镜像就是真机现状**(含本地补丁)。要知道相对上游改了什么,一条命令:
   `git -C src/microduck_rl status`(Windows 侧)、`git -C wsl/src/microduck_rl status`(WSL 侧)。
4. ⚠️ **换行不统一**:三个 clone 里 git 跟踪的文件是 **CRLF**(Windows 侧 `core.autocrlf` 检出的),
   根目录自写的 `.ps1`/`.md` 是 LF,训练日志是 CRLF。沙箱的三个 clone 已设 `core.autocrlf=input`,
   git 不再把换行差异当改动;但**手动比对两份文件时必须先 `tr -d '\r'`**,否则整个文件都显示不同。
5. **改代码优先在沙箱改**,改完告诉用户要同步哪几个文件过去;不要让用户在两边各改一遍。
   改的是哪台机器的文件,就去对应目录改:Windows 的在根目录,WSL 的在 `wsl/` 下。
6. 会话收尾时,若这轮改了需要同步的文件,**列一份"待 XFTP 同步清单"**(文件 → 目标环境)。
7. ⚠️ **领域常识不许凭记忆回答**——技术分类、领域现状、谁家用什么方法、缩写全称、论文结论,
   这类问题先查 `REFERENCES.md`,查不到就**联网核实**,核实完把来源加进 `REFERENCES.md`(注明它能回答什么)。
   这条是踩坑立的:README 最初那版"两条技术栈"的分类凭记忆写,三处硬伤,核实后才改对。
8. **对话里出现新技术名词,当场写进 `GLOSSARY.md`**(中英对照、简称全称、一句话中文解释、核实标记),
   不要只在当轮解释一次就过去。用户的学习基础靠这个文件累积。
9. ⚠️ **不要往 `src/` 里写任何自己的东西。** 整个 `src/` 是第三方、不进用户的仓库,写进去的东西重装即失。
   自写脚本、导出的 onnx、实验记录一律放**工作区根目录**;对上游源码的修改存成 `patches/*.patch`。
   给用户的命令里凡有重定向/导出路径,都要**显式指到根目录**
   (例:在 `src/microduck_rl` 下跑训练时写 `... | tee ../../experiments/xxx.log`,不是 `tee xxx.log`)。

## 三、同步约定

**文档、脚本、配置走 git,不要再手工拷。** 工作区本身是 `github.com/tunghsingw/robolab`,
沙箱和 Windows 都是它的 clone:沙箱改完 `git push`,真机 `git pull` 即可。

**XFTP 只剩两个用途**:① 把真机现状(被改过的上游源码、训练日志)拉给 agent 看;
② WSL 侧接入 git 之前的临时手段。

下面这张表是 XFTP 时代的约定,**凡是 git 已跟踪的文件一律走 git**,表里只有未跟踪的部分还适用。
方向按"谁是源头"定:

| 内容 | 源头 | 同步到 | 说明 |
|---|---|---|---|
| `README.md`、`AGENTS.md`、`GLOSSARY.md`、`REFERENCES.md` | 沙箱 | Windows + WSL | 文档一律在沙箱写,写完推过去 |
| `upstream.repos`、`.gitignore`、`patches/` | 沙箱 | Windows + WSL | 工作区配置,三处一致 |
| `experiments/` 实验记录 | 谁做的实验谁先写 | 另外两处 | 阶段 2 起 |
| 自写脚本 `run_infer*.ps1` 等 | 沙箱 | Windows | 含中文的 `.ps1` 必须存 **UTF-8 带 BOM**(PowerShell 5.1 会把无 BOM 当 ANSI 读,中文乱码) |
| 对仓库源码的本地补丁(如 `infer_policy.py`) | 沙箱 | 打补丁的那一侧 | 先把真机现状拉回沙箱,改完再推回去 |
| 训练产出 `*.onnx` | WSL | 沙箱(备查) / Windows(`policies\` 供推理) | 单个几百 KB,同步无压力 |
| 真机现状(被改过的源码、目录清单) | Windows / WSL | 沙箱 | 需要我读真机现状时按需拉 |

**不要同步**:

- `.venv/` —— 平台相关且入口 exe 内嵌绝对路径,三处各自 `uv sync`
- `logs/` —— 训练输出巨大,只留在 WSL
- `__pycache__/`、`*.pyc`
- `.git/` —— **只在"沙箱 → 真机"这个方向上不要推**,两台机器各自的 git 状态别互相覆盖

### 真机 → 沙箱:怎么传

按机器对号入座,同一相对路径直接覆盖:

| 真机 | 传到沙箱 |
|---|---|
| `D:\robot\robolab\<X>` | 根目录 `<X>` |
| `~/robot/microduck/<X>` | `wsl/<X>` |

XFTP 里排除 `.venv/`、`logs/`、`__pycache__/`;**`.git/` 要传**(见第一节末)。

Windows 和 WSL 都有 `src/microduck_rl/`,同名文件后传的覆盖先传的,不必分类——
哪些文件被改过,agent 用 `git -C src/microduck_rl diff` 一看便知。

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
