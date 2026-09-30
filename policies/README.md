# policies — 策略文件清单

本目录放 ONNX 策略。官方策略从 Hugging Face 下载、不进 git;自训策略和基准文件进 git。

## 官方策略(不进 git,下载方法见 `INSTALL.md` 2.6;许可 Apache-2.0)

`alpha_walking` / `alpha_stand` / `alpha_sitstand` / `alpha_ground_pick` / `ball_kick_left` / `ball_kick_right` / `roller` / `roller_crouch` / `roulade`(均为 `.onnx`)+ `manifest.json`。`run_infer.ps1` 用的就是这一组。

## 自训策略与基准(进 git)

| 文件 | 来源 | 用在哪 |
|---|---|---|
| `2026-09-16_09-07-17_velocity.onnx` | run `2026-09-16_09-07-17` 的 `model_62499`(文件内嵌存档标记,已确认) | `run_infer2.ps1` |
| `my_walking.onnx` | **来源存疑**:文件里没有存档标记;推测出自 `2026-09-15_12-26-40`(12500 轮),未证实 | `run_infer1.ps1` |
| `untrained_random.onnx` | 用正常导出路径导 `model_0.pt`(训练的真实起点,随机初始网络) | `run_infer0.ps1` 默认模式 |
| `untrained_zero.onnx` | 把 `untrained_random.onnx` 的输出层权重清零制成(onnx 库改图,已验证输出恒 0) | `run_infer0.ps1 zero` |

两个基准文件不用 `export.py --agent random/zero` 直接导,是因为上游那条导出路径有 bug(`runner` 未定义)。

## 规矩

- **新导出的文件名带轮数**(如 `my_walking_12500.onnx`),导出方法见 `experiments/stage0_commands.md` 第十节。`my_walking.onnx` 就是没带轮数、事后查不清来源的反例。
- **下载官方策略会覆盖本目录的 `.gitattributes` 和本 README**。`git status` 看到它们被修改就执行 `git checkout policies/.gitattributes policies/README.md` 还原。不还原 `.gitattributes`,之后提交的自训 ONNX 会被静默存成 130 字节的 LFS 指针,clone 下来是坏的且没有报错。
- 训练存档(`.pt`)的清单在 `experiments/runs.md`,本目录只管 ONNX。
