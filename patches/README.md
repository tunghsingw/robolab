# patches — 对上游仓库的适配性修改

`src/` 下的上游 clone **不进本仓库**(见 `.gitignore`),所以对它们的修改必须以补丁形式存在这里。
**这个目录是"你到底改过上游什么"的唯一记录。**

## 只装一类修改

| | 适配性修改 → **存这里** | 实验性修改 → **不要存** |
|---|---|---|
| 特征 | 不改就跑不起来 | 改了看效果,看完就扔 |
| 例子 | Windows 键盘补丁、cu128 索引 | 改奖励权重做消融 |
| 处理 | `.patch` 文件 + 本仓库版本管理 | 改 → 跑 → **结论记进 `experiments/`** → `git checkout` 还原 |

判据只有一句:**这个修改是"不改就用不了",还是"想看看会怎样"?**
把实验改动也存成补丁,三个月后你会面对一堆互相冲突、谁也不记得干嘛用的 patch。

## 现有补丁

| 补丁 | 改哪个文件 | 为什么 |
|---|---|---|
| `01-infer_policy-windows-keyboard.patch` | `src/microduck_rl/scripts/infer_policy.py` | ① 原脚本用 Linux 专用 `termios` 读键盘,Windows 崩 → 导入失败时回退 `msvcrt`;② 给 viewer 加 `key_callback`,MuJoCo 窗口内按键也生效 |
| `02-pyproject-win32-cu128.patch` | `src/microduck_rl/pyproject.toml` | 给 `sys_platform == 'win32'` 加 `pytorch-cu128` 索引,否则 Windows 上 PyPI 默认装 CPU 版 torch |

## 应用(拉完上游之后)

```bash
cd src/microduck_rl
git apply ../../patches/01-infer_policy-windows-keyboard.patch
git apply ../../patches/02-pyproject-win32-cu128.patch
uv lock          # 02 改了 pyproject,重新解析依赖
uv sync
```

## 重新生成(改了上游文件之后)

在工作区根目录:

```bash
git -C src/microduck_rl diff --ignore-cr-at-eol scripts/infer_policy.py > patches/01-infer_policy-windows-keyboard.patch
git -C src/microduck_rl diff --ignore-cr-at-eol pyproject.toml       > patches/02-pyproject-win32-cu128.patch
```

`--ignore-cr-at-eol` **不能省**——上游 clone 是 CRLF 检出的,不加这个会把整个文件当成改动。

## 两个注意

- **`uv.lock` 不存补丁**:它是 `pyproject.toml` 的产物,打完 02 跑一次 `uv lock` 即可重新生成。
  存它只会在每次上游更新时制造冲突。
- 补丁会随上游演进失效。`upstream.repos` 里把 commit 写死就是为了防这个;
  真要升级上游,`git apply` 报错就手动改一遍,再用上面的命令重新生成补丁。
