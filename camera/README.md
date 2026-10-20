# camera/ — RealSense D435 数据获取

相机采集程序,和训练环境(`src/microduck_rl/.venv`)完全隔离,各用各的 venv。

## 环境搭建(Windows PowerShell,只做一次)

```powershell
cd D:\robot\robolab\camera
uv venv .venv --python "D:\Programs\Python\Python312\python.exe"   # 必须用系统 Python,原因见下
uv pip install -r requirements.txt
.\.venv\Scripts\Activate.ps1
```

⚠️ 为什么指定 Python:uv 自带的 managed Python(3.13)**不带 tkinter**,而 `console.py`
的界面依赖 tkinter。系统 Python 3.12(训练环境同一个)带 tkinter,所以用它建环境。
`probe.py` / `view.py` / `record.py` 三个脚本不挑解释器,只有 console.py 挑。

## 三步走

**共同前提**(每条命令都一样,开新终端就先跑这两行):

```powershell
cd D:\robot\robolab\camera
.\.venv\Scripts\Activate.ps1
```

提示符前面出现 `(.venv)` 才算激活。没有它,下面所有 `python xxx.py` 都会报
`ModuleNotFoundError`——那不是相机的问题,是环境没切过来。

| 步骤 | 命令 | 干什么 | 看到什么说明什么 |
|---|---|---|---|
| ① 验证 | `python probe.py` | 列设备、启双流、打印中心距离和内参 | 出现 D435 + 距离合理 = 全通;报找不到设备 = 查 USB 3.0 蓝色口/换线 |
| ② 看画面 | `python view.py` | 实时窗口:左彩色、右深度,ESC 退出 | 手靠近镜头深度图变色 = 正常(需先 `uv pip install opencv-python`) |
| ③ 采数据 | `python record.py --seconds 10 --name xx` | 存彩色 PNG/深度 NPY/时间戳/meta 到 `data/run_xxx/` | 有实时预览窗口,ESC 停;深度存 16 位原值不压缩 |

③ 的 `--seconds` / `--name` 可省:不打就是手动停 + 时间戳默认名。

## 常见报错对照表

照抄命令直接运行报错时,拿报错原文和左列对照:

| 报错 | 原因 | 怎么办 |
|---|---|---|
| `can't open file '...\probe.py'` | 目录不对,脚本都在 `camera\` 目录下 | `cd D:\robot\robolab\camera` 再跑 |
| `ModuleNotFoundError: No module named 'pyrealsense2'` | 没激活 venv,python 用的是系统解释器 | `.\.venv\Scripts\Activate.ps1`,提示符出现 `(.venv)` 再跑 |
| `ModuleNotFoundError: No module named 'cv2'` | 环境里没装 opencv(view/record/console 都要) | `uv pip install opencv-python`,或重跑 `uv pip install -r requirements.txt` |
| `record.py: error: unrecognized arguments: [--seconds 10]` | 方括号是文档里表示“可选”的写法,照抄会被当成真参数 | 去掉方括号再跑:`--seconds 10 --name xx` |
| `无法加载文件 ...Activate.ps1,因为在此系统上禁止运行脚本` | PowerShell 执行策略不让运行脚本 | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`(本机只需一次) |
| `Device or resource busy` | 相机被别的进程占着(另一个 console.py 窗口,或 RealSense Viewer 没关) | 关掉占相机的程序再跑 |
| `uv : 无法将"uv"识别为 cmdlet` | 装 uv 之前开的终端,PATH 没刷新 | 关掉终端重开;还不行 `pip install uv` |
| console.py 窗口起不来、报 tkinter 相关错 | venv 建在了不带 tkinter 的 Python 3.13 上 | 按本文档指定系统 Python 3.12 重建 `.venv`(见环境搭建一节) |

## 控制台 console.py(三步合一)

三个脚本的功能合成一个窗口:`python console.py`。

- 设备卡:连接状态、型号、序列号、内参摘要 + 重新验证
- 画面区:左彩色、右深度实时显示,伪彩色可关;**录制中画面左上角变红色 `REC` + 读秒**(设了定时附总时长,如 `REC 6.3s/10s`)
- 录制卡:run 名字、时长(0 = 手动停),开始/停止;按钮下方常驻**"已录 xx.x s"**,停止后保留最终时长
- 状态栏:帧数、fps、中心距离、画面最近距离;录制时切换为 `REC 6.3s/10s | 录 189 帧 | ...`
- 日志区:连接、开录、停录、错误全部落痕,出问题有据可查

排障:`python console.py --selftest` 不开窗口自检(连接→取帧→录 2 秒→落盘),
GUI 出问题时先跑它,分辨是相机/录制的错还是界面的错。

## 数据结构(record.py 产出)

```
data/run_<时间戳>/
├── color/000000.png ...     彩色图,8 位 BGR
├── depth/000000.npy ...     深度图,16 位原始值(毫米),保留物理信息
├── preview/000000.jpg ...   彩色+深度伪彩色并排,人眼快速翻看用
├── timestamps.csv           每帧时间戳 + 中心距离(米)
└── meta.json                序列号、两路内参、深度单位、帧数
```

注意:
- depth 里的 65535 = "没测到"(哨兵值),喂网络或算距离前先 mask 掉
- 彩色和深度内参不同(两个物理相机),meta.json 分别记录;像素级对齐(`rs.align`)以后需要再加
- 每帧同步写盘,实测约 24fps;要满 30fps 需加异步队列,需要时再升级

## 目录约定

- `data/` 是采集输出,**不进 git**(`.gitignore` 已忽略,和 `logs/` 一个规矩)
- `.venv/` 被仓库根 `.gitignore` 的 `.venv/` 规则覆盖,自动不进 git
- 脚本只放这个目录,不进 `src/`(那是第三方上游代码)

## 为什么独立 venv

训练环境被 `uv.lock` 钉死,手动装进去的包下次 `uv sync` 会被卸掉;而且相机采集和训练互不相干,分开出问题好排查。

## 想在 WSL2 里用

WSL2 不原生支持 USB,需 usbipd-win 透传(attach 后 Windows 侧不可用,要 `usbipd detach` 才能切回)。现阶段 Windows 侧就能跑,不必折腾 WSL。
