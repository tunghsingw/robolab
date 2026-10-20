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
| ③ 采数据 | `python record.py` | 存彩色/深度/时间戳到 `data/` | 跑通①②再建这个脚本 |

## 目录约定

- `data/` 是采集输出,**不进 git**(`.gitignore` 已忽略,和 `logs/` 一个规矩)
- `.venv/` 被仓库根 `.gitignore` 的 `.venv/` 规则覆盖,自动不进 git
- 脚本只放这个目录,不进 `src/`(那是第三方上游代码)

## 为什么独立 venv

训练环境被 `uv.lock` 钉死,手动装进去的包下次 `uv sync` 会被卸掉;而且相机采集和训练互不相干,分开出问题好排查。

## 想在 WSL2 里用

WSL2 不原生支持 USB,需 usbipd-win 透传(attach 后 Windows 侧不可用,要 `usbipd detach` 才能切回)。现阶段 Windows 侧就能跑,不必折腾 WSL。
