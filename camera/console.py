"""console.py - D435 控制台(GUI,三步合一)

把 probe / view / record 三个脚本合成一个窗口:
    设备卡   = probe 的功能(列设备、序列号、内参)
    画面区   = view 的功能(实时彩色+深度,可开关伪彩色)
    录制卡   = record 的功能(写 color/depth/timestamps/meta,带实时指标)

用法:
    python console.py              打开控制台
    python console.py --selftest   不开窗口:验证设备、取帧、录 2 秒(排障用)

依赖:pyrealsense2、opencv-python、numpy、Pillow(tkinter 随 Python 自带)

设计要点:
    1. 相机逻辑(D435Console)和界面(D435App)分开——逻辑不依赖 tkinter,
       所以能在命令行自检,以后想换界面(网页/Qt)也只需重写界面层。
    2. 取帧不用 while 死循环,也不用多线程——用 tkinter 的 after(15ms)
       定时回调在界面主循环里拉一帧。死循环会卡死窗口,多线程和 tkinter
       共享数据会崩。【换机器人也一样】GUI + 硬件阻塞设备的标准解法。
    3. 状态机:idle / preview / recording。按钮可用性跟着状态走,
       录制中不让改 run 名字——防止用户录到一半改参数,数据错乱。
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs

DATA_DIR = Path(__file__).parent / "data"
CENTER_U, CENTER_V = 320, 240          # 画面正中心像素(640x480 的一半)
SENTINEL = 60000                       # 大于这个值视为"没测到"(哨兵值 65535 附近)


def intr_to_dict(intr):
    """SDK 内参对象 → 可 JSON 序列化的字典。"""
    return {
        "width": intr.width, "height": intr.height,
        "fx": intr.fx, "fy": intr.fy,
        "ppx": intr.ppx, "ppy": intr.ppy,
        "model": str(intr.model),
        "coeffs": list(intr.coeffs),
    }


class D435Console:
    """相机逻辑:连接、取帧、设备信息、录制。完全不碰 GUI。"""

    def __init__(self):
        self.pipeline = None
        self.device_info = {}
        # 录制状态
        self.recording = False
        self.run_dir = None
        self._csv_file = None
        self._csv_writer = None
        self.frame_idx = 0
        self.record_frames = 0
        self.record_deadline = None    # 定时录制的截止时间(秒,None=手动)

    # ---------- 设备 ----------

    def open_camera(self):
        """启动双流并读设备信息。失败会抛异常,由调用方决定怎么提示。"""
        ctx = rs.context()
        devices = ctx.query_devices()
        if not devices:
            raise RuntimeError(
                "没找到 RealSense 设备。检查:①USB 3.0 蓝色口 ②换线 ③RealSense Viewer 能否识别"
            )
        dev = devices[0]

        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = self.pipeline.start(config)

        # 设备信息(probe 的功能:序列号 + 两路内参 + 深度单位)
        depth_profile = profile.get_stream(rs.stream.depth).as_video_stream_profile()
        color_profile = profile.get_stream(rs.stream.color).as_video_stream_profile()
        self.device_info = {
            "name": dev.get_info(rs.camera_info.name),
            "serial": dev.get_info(rs.camera_info.serial_number),
            "firmware": dev.get_info(rs.camera_info.firmware_version),
            "depth_scale": dev.first_depth_sensor().get_depth_scale(),
            "depth_intr": intr_to_dict(depth_profile.get_intrinsics()),
            "color_intr": intr_to_dict(color_profile.get_intrinsics()),
        }
        return self.device_info

    def close_camera(self):
        """停流并收尾(录制中先停录制,否则 meta.json 写不完整)。"""
        if self.recording:
            self.stop_recording()
        if self.pipeline is not None:
            try:
                self.pipeline.stop()
            finally:
                self.pipeline = None

    @property
    def is_open(self):
        return self.pipeline is not None

    # ---------- 取帧 ----------

    def grab(self):
        """等一组配对帧,返回 (depth_np, color_np, depth_frame, color_frame)。"""
        frames = self.pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        if not depth or not color:
            raise RuntimeError("帧不完整(缺深度或缺彩色),重试一次")
        depth_np = np.asanyarray(depth.get_data())
        color_np = np.asanyarray(color.get_data())
        return depth_np, color_np, depth, color

    # ---------- 统计 ----------

    @staticmethod
    def center_distance(depth_frame):
        """正中心像素距离(米)。0 = 没测到。"""
        return depth_frame.get_distance(CENTER_U, CENTER_V)

    @staticmethod
    def min_distance(depth_np):
        """整幅画面最近的有效距离(米);没有有效像素返回 None。"""
        valid = (depth_np > 0) & (depth_np < SENTINEL)
        if not valid.any():
            return None
        return int(depth_np[valid].min()) / 1000.0

    # ---------- 录制 ----------

    def start_recording(self, name="", seconds=0):
        """建 run 目录、开 csv。name 空 = 时间戳;seconds=0 = 手动停。"""
        if self.recording:
            raise RuntimeError("已在录制中")
        run_name = name or f"run_{time.strftime('%Y%m%d_%H%M%S')}"
        self.run_dir = DATA_DIR / run_name
        (self.run_dir / "color").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "depth").mkdir(parents=True, exist_ok=True)
        self._csv_file = open(self.run_dir / "timestamps.csv", "w", newline="")
        self._csv_writer = csv.writer(self._csv_file)
        self._csv_writer.writerow(
            ["frame", "system_time_s", "device_time_ms", "center_distance_m"]
        )
        self.frame_idx = 0
        self.record_frames = 0
        self.record_deadline = time.time() + seconds if seconds > 0 else None
        self.recording = True
        return self.run_dir

    def write_frame(self, depth_np, color_np, depth_frame):
        """把当前帧落盘。调用方负责在每帧 grab 之后调用。"""
        idx = self.frame_idx
        cv2.imwrite(str(self.run_dir / "color" / f"{idx:06d}.png"), color_np)
        np.save(self.run_dir / "depth" / f"{idx:06d}.npy", depth_np)
        self._csv_writer.writerow([
            idx,
            f"{time.time():.3f}",
            f"{depth_frame.get_timestamp():.1f}",
            f"{depth_frame.get_distance(CENTER_U, CENTER_V):.4f}",
        ])
        self.frame_idx += 1
        self.record_frames = self.frame_idx

    def stop_recording(self):
        """停录制,写 meta.json,返回摘要 dict。"""
        if not self.recording:
            return None
        self.recording = False
        if self._csv_file is not None:
            self._csv_file.close()
            self._csv_file = None
        meta = {
            "run_name": self.run_dir.name,
            "recorded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": {
                "name": self.device_info.get("name"),
                "serial": self.device_info.get("serial"),
            },
            "depth_scale_m_per_unit": self.device_info.get("depth_scale"),
            "depth_intrinsics": self.device_info.get("depth_intr"),
            "color_intrinsics": self.device_info.get("color_intr"),
            "frame_count": self.record_frames,
            "sentinel_note": (
                "depth/*.npy 是 16 位原始值,单位由 depth_scale 换算成米。"
                "值 65535 表示'没测到'(超出量程/表面吸光/被遮挡),"
                "用之前要先 mask 掉,不能当真距离。"
            ),
        }
        with open(self.run_dir / "meta.json", "w") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        summary = {"run_dir": str(self.run_dir), "frames": self.record_frames}
        return summary


def selftest(seconds=2):
    """命令行自检:不开窗口,验证 连接→取帧→录制→落盘 整条链路。"""
    console = D435Console()
    print("== 1/3 打开相机 ==")
    info = console.open_camera()
    print(f"   {info['name']} / 序列号 {info['serial']} / 固件 {info['firmware']}")

    print(f"== 2/3 取帧 {seconds} 秒 ==")
    t0 = time.time()
    n = 0
    mind_all = []
    while time.time() - t0 < seconds:
        depth_np, color_np, depth_frame, _ = console.grab()
        n += 1
        d = console.min_distance(depth_np)
        if d is not None:
            mind_all.append(d)
    print(f"   取了 {n} 帧(约 {n / seconds:.0f} fps)")
    if mind_all:
        print(f"   画面最近距离 {min(mind_all):.2f} m ~ {max(mind_all):.2f} m")

    print(f"== 3/3 录制 {seconds} 秒 ==")
    run_dir = console.start_recording(name="selftest", seconds=seconds)
    t0 = time.time()
    while time.time() - t0 < seconds:
        depth_np, color_np, depth_frame, _ = console.grab()
        console.write_frame(depth_np, color_np, depth_frame)
    summary = console.stop_recording()
    n_color = len(list((run_dir / "color").glob("*.png")))
    n_depth = len(list((run_dir / "depth").glob("*.npy")))
    meta_ok = (run_dir / "meta.json").exists() and (run_dir / "timestamps.csv").exists()
    console.close_camera()
    print(f"   落盘:color {n_color} / depth {n_depth} / meta+csv {'OK' if meta_ok else '缺失'}")
    if n_color != n_depth or not meta_ok or n_color == 0:
        print("自检失败:文件数不匹配或 meta 缺失")
        sys.exit(1)
    print(f"自检通过 → {summary['run_dir']}(共 {summary['frames']} 帧,已自动清理可删)")


def run_gui():
    """GUI 部分:所有 tkinter 相关都在这里 import,自检模式不需要它们。"""
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
    from PIL import Image, ImageTk

    FONT = ("Microsoft YaHei UI", 10)
    FONT_SMALL = ("Microsoft YaHei UI", 9)

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("D435 控制台")
            self.geometry("1400x760")
            self.minsize(1100, 640)

            self.console = D435Console()
            self.frame_count = 0
            self.fps = 0.0
            self._last_t = None
            self._photo = None            # 必须持有引用,否则图片被垃圾回收

            self._build_ui()
            self.protocol("WM_DELETE_WINDOW", self._on_close)

            # 启动即连接相机并开始定时取帧
            self.after(100, self._auto_connect)
            self.after(500, self._tick)

        # ---------- 界面搭建 ----------

        def _build_ui(self):
            self.configure(bg="#f0efec")
            left = tk.Frame(self, bg="#f0efec", width=250)
            left.pack(side="left", fill="y", padx=10, pady=10)
            left.pack_propagate(False)
            right = tk.Frame(self, bg="#f0efec")
            right.pack(side="right", expand=True, fill="both", padx=10, pady=10)

            # 设备卡(probe 功能)
            frm_dev = tk.LabelFrame(left, text="设备", font=FONT, bg="#ffffff",
                                    padx=10, pady=8)
            frm_dev.pack(fill="x", pady=(0, 10))
            self.var_status = tk.StringVar(value="● 未连接")
            self.lbl_status = tk.Label(frm_dev, textvariable=self.var_status,
                                       font=FONT, fg="#c0392b", bg="#ffffff")
            self.lbl_status.pack(anchor="w")
            self.var_dev = tk.StringVar(value="—")
            tk.Label(frm_dev, textvariable=self.var_dev, font=FONT_SMALL,
                     fg="#555555", bg="#ffffff", justify="left").pack(anchor="w", pady=4)
            tk.Button(frm_dev, text="重新验证", font=FONT_SMALL,
                      command=self._on_reprobe).pack(fill="x")

            # 录制卡(record 功能)
            frm_rec = tk.LabelFrame(left, text="录制", font=FONT, bg="#ffffff",
                                    padx=10, pady=8)
            frm_rec.pack(fill="x")
            tk.Label(frm_rec, text="run 名字(空 = 时间戳)", font=FONT_SMALL,
                     bg="#ffffff").pack(anchor="w")
            self.ent_name = tk.Entry(frm_rec, font=FONT)
            self.ent_name.pack(fill="x")
            tk.Label(frm_rec, text="时长(秒,0 = 手动停)", font=FONT_SMALL,
                     bg="#ffffff").pack(anchor="w", pady=(6, 0))
            self.ent_dur = tk.Entry(frm_rec, font=FONT, width=8)
            self.ent_dur.insert(0, "0")
            self.ent_dur.pack(anchor="w")
            self.btn_start = tk.Button(frm_rec, text="开始录制", font=FONT,
                                       command=self._on_start_rec)
            self.btn_start.pack(fill="x", pady=(8, 4))
            self.btn_stop = tk.Button(frm_rec, text="停止", font=FONT,
                                      command=self._on_stop_rec, state="disabled")
            self.btn_stop.pack(fill="x")
            tk.Button(frm_rec, text="打开数据目录", font=FONT_SMALL,
                      command=self._on_open_data).pack(fill="x", pady=(6, 0))

            # 画面卡(view 功能)
            frm_view = tk.LabelFrame(left, text="画面", font=FONT, bg="#ffffff",
                                     padx=10, pady=8)
            frm_view.pack(fill="x", pady=10)
            self.var_colorize = tk.BooleanVar(value=True)
            tk.Checkbutton(frm_view, text="深度伪彩色(近红远蓝)", font=FONT_SMALL,
                           variable=self.var_colorize, bg="#ffffff").pack(anchor="w")
            tk.Label(frm_view, text="关掉可看原始灰度深度", font=FONT_SMALL,
                     fg="#888888", bg="#ffffff").pack(anchor="w")

            # 画面区
            self.lbl_video = tk.Label(right, text="相机未启动", bg="#ffffff",
                                      font=FONT, fg="#888888")
            self.lbl_video.pack(expand=True, fill="both")

            # 实时指标(状态栏)
            frm_stat = tk.Frame(right, bg="#f0efec")
            frm_stat.pack(fill="x", pady=(8, 0))
            self.var_stats = tk.StringVar(value="帧 0 | 0.0 fps | 中心 — | 最近 —")
            tk.Label(frm_stat, textvariable=self.var_stats, font=FONT,
                     bg="#f0efec", fg="#333333").pack(side="left")

            # 日志
            self.txt_log = scrolledtext.ScrolledText(right, height=5, font=FONT_SMALL,
                                                     state="disabled", bg="#ffffff")
            self.txt_log.pack(fill="x", pady=(6, 0))

        def _log(self, msg):
            t = time.strftime("%H:%M:%S")
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", f"[{t}] {msg}\n")
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")

        # ---------- 事件 ----------

        def _auto_connect(self):
            try:
                info = self.console.open_camera()
            except Exception as e:
                self.var_status.set("● 连接失败")
                self._log(f"连接失败:{e}")
                messagebox.showerror("连不上相机", str(e))
                return
            self._set_connected(info)

        def _set_connected(self, info):
            self.var_status.set("● 运行中")
            self.lbl_status.configure(fg="#2e7d32")
            self.var_dev.set(
                f"{info['name']}\n序列号 {info['serial']}\n"
                f"内参 fx=fy={info['depth_intr']['fx']:.1f}"
            )
            self._log(f"相机已连接:{info['name']} / {info['serial']}")

        def _on_reprobe(self):
            if self.console.is_open:
                self._log("设备运行中,无需重验")
                return
            self._auto_connect()

        def _on_start_rec(self):
            if not self.console.is_open:
                messagebox.showwarning("还没连上", "相机未连接,先解决设备问题")
                return
            name = self.ent_name.get().strip()
            try:
                seconds = float(self.ent_dur.get() or 0)
            except ValueError:
                messagebox.showerror("输入错误", "时长必须是数字(0 = 手动停)")
                return
            try:
                run_dir = self.console.start_recording(name=name, seconds=seconds)
            except Exception as e:
                messagebox.showerror("启动录制失败", str(e))
                return
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.ent_name.configure(state="disabled")
            self._log(f"开始录制 → {run_dir}")

        def _on_stop_rec(self):
            summary = self.console.stop_recording()
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.ent_name.configure(state="normal")
            if summary:
                self._log(f"停止,共 {summary['frames']} 帧 → {summary['run_dir']}")

        def _on_open_data(self):
            if not DATA_DIR.exists():
                DATA_DIR.mkdir(parents=True)
            try:
                os.startfile(str(DATA_DIR))      # Windows
            except AttributeError:
                import subprocess
                subprocess.run(["xdg-open", str(DATA_DIR)])   # Linux/macOS

        def _on_close(self):
            self.console.close_camera()
            self.destroy()

        # ---------- 帧循环 ----------

        def _tick(self):
            if self.console.is_open:
                try:
                    depth_np, color_np, depth_frame, _ = self.console.grab()
                except Exception as e:
                    self._log(f"取帧失败:{e}")
                    self.after(500, self._tick)
                    return

                # 帧率(滑动估计)+ 统计
                now = time.time()
                if self._last_t is not None:
                    dt = now - self._last_t
                    if dt > 0:
                        inst = 1.0 / dt
                        self.fps = self.fps * 0.9 + inst * 0.1 if self.fps else inst
                self._last_t = now
                self.frame_count += 1
                center = self.console.center_distance(depth_frame)
                mind = self.console.min_distance(depth_np)

                # 录制中:落盘(写盘会拖慢帧率,状态栏能看到)
                if self.console.recording:
                    self.console.write_frame(depth_np, color_np, depth_frame)
                    if self.console.record_deadline and now >= self.console.record_deadline:
                        self._on_stop_rec()
                        self._log("到达设定时长,自动停止")

                # 画面:左彩色,右深度(伪彩色可关)
                if self.var_colorize.get():
                    dep_show = cv2.applyColorMap(
                        cv2.convertScaleAbs(depth_np, alpha=0.03), cv2.COLORMAP_JET)
                else:
                    dep_show = cv2.cvtColor(
                        cv2.convertScaleAbs(depth_np, alpha=0.03), cv2.COLOR_GRAY2BGR)
                min_txt = f"{mind:.2f}m" if mind is not None else "--"
                hud = (f"#{self.frame_count}  {self.fps:.1f}fps  "
                       f"ctr {center:.2f}m  min {min_txt}")
                disp = np.hstack((color_np, dep_show))
                cv2.putText(disp, hud, (10, 28), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255, 255, 255), 2)
                img = Image.fromarray(cv2.cvtColor(disp, cv2.COLOR_BGR2RGB))
                self._photo = ImageTk.PhotoImage(image=img)
                self.lbl_video.configure(image=self._photo)

                self.var_stats.set(
                    f"帧 {self.frame_count} | {self.fps:.1f} fps | "
                    f"中心 {center:.2f} m | 画面最近 {min_txt}"
                )
            self.after(15, self._tick)

    app = App()
    app.mainloop()


def main():
    parser = argparse.ArgumentParser(description="D435 控制台(probe/view/record 三合一)")
    parser.add_argument("--selftest", action="store_true",
                        help="不开窗口,命令行自检(连接→取帧→录制→落盘)")
    args = parser.parse_args()
    if args.selftest:
        selftest()
    else:
        run_gui()


if __name__ == "__main__":
    main()
