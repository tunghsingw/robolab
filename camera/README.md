# camera/ — RealSense D435 数据获取

相机采集程序,和训练环境(`src/microduck_rl/.venv`)完全隔离,各用各的 venv。

## 环境搭建(Windows PowerShell,只做一次)

```powershell
cd D:\robot\robolab\camera
uv venv .venv                        # 建独立环境
uv pip install -r requirements.txt   # 装 pyrealsense2
.\.venv\Scripts\Activate.ps1
```

## 三步走

| 步骤 | 命令 | 干什么 | 看到什么说明什么 |
|---|---|---|---|
| ① 验证 | `python probe.py` | 列设备、启双流、打印中心距离和内参 | 出现 D435 + 距离合理 = 全通;报找不到设备 = 查 USB 3.0 蓝色口/换线 |
| ② 看画面 | `python view.py` | 实时窗口:左彩色、右深度,ESC 退出 | 手靠近镜头深度图变色 = 正常(需先 `uv pip install opencv-python`) |
| ③ 采数据 | `python record.py [--seconds 10] [--name xx]` | 存彩色 PNG/深度 NPY/时间戳/meta 到 `data/run_xxx/` | 有实时预览窗口,ESC 停;深度存 16 位原值不压缩 |

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
