# INSTALL.md — 从零搭建

> **这份文档不依赖机器上任何现有文件。** 拿一台干净的 Windows 11 机器,从头照着做就能跑起来。
> 日常使用看 `README.md`;三处环境的分工看 `AGENTS.md`。

## 0. 前提

| 项 | 要求 | 说明 |
|---|---|---|
| 系统 | Windows 11 | WSL2 需要它 |
| 显卡 | NVIDIA,**显存 ≥ 6 GB** | 训练用。只跑推理的话 CPU 也行 |
| 驱动 | 支持 CUDA 12.8 的较新版本 | 本项目 torch 用 `cu128` |
| 磁盘 | ≥ 30 GB 空闲 | 依赖约 8 GB,训练日志能涨到几个 GB |
| 账号 | GitHub | clone 本仓库 |

**只想跑推理、不训练?** 跳过第 3 节,只做第 2 节,不需要 GPU。

## 1. 目录规划

本仓库是一个 **ROS 风格工作区**:仓库根就是工作区根,第三方代码统一进 `src/`(不入库,按清单拉取)。

```
<任选位置>/robolab/          ← clone 本仓库得到
├── *.md  *.ps1              文档与脚本(仓库自带)
├── upstream.repos           上游清单
├── patches/                 对上游的适配补丁
├── policies/                ONNX 策略(自训的仓库自带,官方的要下载)
├── experiments/             实验记录
└── src/                 ←   要你自己拉:microduck / microduck_rl / mjlab
```

**路径可以任选**,脚本用 `$PSScriptRoot` 相对定位,不写死绝对路径。下文用 `D:\robot\robolab` 举例。

---

## 2. Windows 侧

### 2.1 装 git 和 uv

git:从 https://git-scm.com/download/win 下载安装,一路默认。

uv(Python 包管理器,**不需要先装 Python**,它会自己下):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

装完**开一个新的 PowerShell 窗口**(PATH 才生效),验证:

```powershell
uv --version
```

如果提示找不到命令,说明没进 PATH,用全路径 `& "$env:USERPROFILE\.local\bin\uv.exe" --version`。
下文所有 `uv` 都可以换成这个全路径写法。

### 2.2 clone 学习仓库

```powershell
cd D:\robot ; git clone https://github.com/tunghsingw/robolab.git
```

### 2.3 拉上游仓库

`src/` 是空的——这是设计如此,第三方代码不入库。用清单拉:

```powershell
pip install vcs2l
```

```powershell
cd D:\robot\robolab ; vcs import src < upstream.repos
```

`upstream.repos` 里把三个仓库的 commit 写死了,所以任何时候拉到的都是同一份代码,补丁一定打得上。

> 没装 pip / 不想装 vcs2l?手动 clone 三个仓库到 `src\` 下,再 `git checkout` 到清单里写的 commit,效果一样。

### 2.4 打补丁

上游代码有两处必须改,否则 Windows 上跑不起来:

```powershell
cd D:\robot\robolab\src\microduck_rl
```

```powershell
git apply ..\..\patches\01-infer_policy-windows-keyboard.patch
```

```powershell
git apply ..\..\patches\02-pyproject-win32-cu128.patch
```

两个补丁分别解决:① 推理脚本用 Linux 专用 `termios` 读键盘,Windows 直接崩;② Windows 上 PyPI 默认给 CPU 版 torch,加 `pytorch-cu128` 索引才拿得到 GPU 版。细节见 `patches/README.md`。

### 2.5 装依赖

```powershell
cd D:\robot\robolab\src\microduck_rl ; $env:UV_HTTP_TIMEOUT="600" ; uv lock ; uv sync
```

`uv lock` 必须在 `uv sync` 之前——补丁 02 改了 `pyproject.toml`,要重新解析依赖。
这一步会下 torch 等约 8 GB,慢,超时时间调到 600 秒是必要的。

验证 GPU 认到了:

```powershell
uv run python -c "import torch, warp; print(torch.__version__, torch.cuda.is_available()); print(warp.__version__)"
```

期望:`2.9.1+cu128 True` 和 warp 版本号。如果 `cuda.is_available()` 是 `False`,补丁 02 没生效,回 2.4 检查。

### 2.6 下载官方策略

仓库自带 4 个自训 ONNX,官方那 9 个要另外下:

```powershell
cd D:\robot\robolab\src\microduck_rl
```

```powershell
$env:HF_ENDPOINT="https://hf-mirror.com"; $env:NO_PROXY="*"; $env:HTTP_PROXY=""; $env:HTTPS_PROXY=""
```

```powershell
uv run python -c "from huggingface_hub import snapshot_download; snapshot_download('pollen-robotics/microduck-policies', local_dir=r'D:\robot\robolab\policies')"
```

直连 Hugging Face 在国内通常不通,所以走 `hf-mirror.com` 并绕过本机代理。

⚠️ **下载完必须做这一步**:

```powershell
cd D:\robot\robolab ; git checkout policies/.gitattributes
```

Hugging Face 的 `.gitattributes` 声明 `*.onnx` 走 Git LFS,会覆盖本仓库的同名文件。不还原的话,你以后提交的自训 ONNX 会被静默存成 130 字节的 LFS 指针,clone 下来是坏的——**这个故障没有任何报错**。`git status` 看到该文件被修改就是这个原因。

### 2.7 验证

```powershell
D:\robot\robolab\run_infer.ps1
```

MuJoCo 窗口弹出、鸭子站稳就成了。按键表见 `README.md`。

---

## 3. WSL2 侧(训练主力)

Windows 原生也能训练(实测和 WSL 速度差 6%),但官方支持的是 Linux,而且以后的 duck-sim 全栈模拟只能在 WSL 跑。

### 3.1 装 WSL2 Ubuntu 24.04

先试商店版:

```powershell
wsl --install -d Ubuntu-24.04
```

**如果报 `0x80071772` 之类的注册失败**(WSL 版本太旧、`wsl --update` 又被网络或权限挡住),改用 rootfs 导入:

1. 从 USTC 镜像站(https://mirrors.ustc.edu.cn/)找 Ubuntu 24.04 的 **WSL rootfs** 压缩包下载到 `D:\wsl\`
2. 导入:

```powershell
wsl --import Ubuntu D:\wsl\Ubuntu D:\wsl\<下载的rootfs文件> --version 2
```

3. 进去:`wsl -d Ubuntu`

### 3.2 建默认用户、换 apt 源

rootfs 导入的默认用户是 root,建一个普通用户(下文用 `robot`):

```bash
useradd -m -s /bin/bash -G sudo robot && passwd robot
```

```bash
echo "robot ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/robot
```

`/etc/wsl.conf` 写入:

```ini
[user]
default=robot

[boot]
systemd=true
```

apt 换 USTC 源(国内必要),然后 `wsl --shutdown` 重启生效。

### 3.3 网络(国内环境必做)

在 Windows 的 `%USERPROFILE%\.wslconfig` 写入:

```ini
[wsl2]
networkingMode=mirrored   # WSL 与 Windows 共享网络栈,能用 Windows 的本机代理
autoProxy=true            # 自动把 Windows 系统代理注入 WSL
dnsTunneling=true
```

`wsl --shutdown` 重启生效。

**镜像模式的两个好处**:① Windows 的本机代理(如 `127.0.0.1:7890`)在 WSL 里直接可用;
② Windows 浏览器能直接开 `localhost:<端口>` 看 WSL 里的 TensorBoard 和 viser 查看器。

代理不在线时的兜底——git 走 gh-proxy:

```bash
git config --global url."https://gh-proxy.com/https://github.com/".insteadOf "https://github.com/"
```

`uv` 调用系统 git,所以这条对 `uv sync` 也生效,且不用改 `uv.lock`。

### 3.4 装 uv 和 vcs2l

⚠️ **不要用 Windows 那次安装**。WSL 是独立的 Linux 系统,有自己的 PATH,Windows 侧的 uv 在里面不存在。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
pip3 install vcs2l
```

### 3.5 clone + 拉上游 + 打补丁 + 装依赖

⚠️ **仓库必须放在 WSL 自己的文件系统(`~/...`),不能放 `/mnt/d`**——跨文件系统 I/O 慢好几倍,训练会被拖垮。

```bash
cd ~ && git clone https://github.com/tunghsingw/robolab.git && cd robolab
```

```bash
vcs import src < upstream.repos
```

```bash
git -C src/microduck_rl apply ../../patches/01-infer_policy-windows-keyboard.patch
```

补丁 02 是 Windows 专用(cu128 索引),**Linux 上不要打**——PyPI 的 Linux torch 轮子本来就自带 CUDA。

```bash
cd src/microduck_rl && UV_HTTP_TIMEOUT=600 uv sync
```

验证:

```bash
uv run python -c "import torch, warp; print(torch.__version__, torch.cuda.is_available()); print(warp.__version__)"
```

### 3.6 冒烟测试(仓库铁律,别跳过)

```bash
cd ~/robolab/src/microduck_rl
```

```bash
WANDB_MODE=offline uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 64 --agent.max-iterations 5
```

**开跑后第一眼看 `Learning iteration 0/5` 的分母是不是 5。** 不是 5 说明参数没吃进去,立刻 Ctrl+C。

通过的判据三条:

1. `[INFO] Training with: device=cuda:0` —— 用的是 GPU
2. `Episode_Reward/` 下的惩罚项(`action_rate_l2`、`body_ang_vel` 等)**全部 ≤ 0**
3. `Episode_Termination/nan_state` 恒为 **0**

5 迭代的冒烟测试能抓住约 95% 的配置错误,花不了一分钟。**永远不要不做冒烟就开长训练。**

---

## 4. 故障速查

| 症状 | 原因 | 处理 |
|---|---|---|
| `No module named 'termios'` | 补丁 01 没打 | 回 2.4 |
| `torch.cuda.is_available()` 为 False(Windows) | 补丁 02 没打,或打完没重跑 `uv lock` | 回 2.4 / 2.5 |
| MuJoCo 窗口里按键没反应 | 补丁 01 没打(缺 `key_callback`) | 回 2.4 |
| 训练不停,`Learning iteration N/50000` | `--agent.max-iterations` 没生效 | 注意是**连字符**不是下划线;另见下一行 |
| 参数莫名丢失、命令像被截断 | **PowerShell 粘贴长命令会被截断**(约 160 字符) | 拆成多行、或先把路径存进变量 |
| 自训 ONNX 变成 130 字节文本 | HF 的 `.gitattributes` 覆盖了本仓库的 | `git checkout policies/.gitattributes`,见 2.6 |
| 改了 `.ps1` 后中文乱码、报奇怪的 CommandNotFound | 存成了无 BOM 的 UTF-8 | 含中文的 `.ps1` **必须存 UTF-8 带 BOM** |
| 移动了工作区目录后 venv 失效 | uv 生成的入口 exe 内嵌绝对路径 | 删掉 `.venv` 重新 `uv sync` |
| 训练显存不足(OOM) | 环境数太多 | 6 GB 显存从 `--env.scene.num-envs 1024` 起步,别用 4096 |
| `git apply` 报错打不上补丁 | 上游版本和 `upstream.repos` 里钉的 commit 不一致 | 确认 `git -C src/microduck_rl log -1` 和清单一致 |

## 5. 装完之后

- 日常命令、按键表、训练与导出流程 → `README.md`
- 三处环境分工、同步约定 → `AGENTS.md`
- 名词不懂 → `GLOSSARY.md`
- 找资料 → `REFERENCES.md`
- 奖励设计与 sim2real 的经验 → `src/microduck_rl/AGENTS.md`(上游作者写的,精华)
