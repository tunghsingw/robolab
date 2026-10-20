"""record.py - 数据采集(第 3 步)

前置:probe.py、view.py 都跑通后再用这个脚本。

干什么:
    实时录制彩色 + 深度双流,每一帧存三样东西到 data/run_<时间戳>/:
      color/    彩色图 PNG(8 位 BGR,和 OpenCV 习惯一致)
      depth/    深度图 NPY(16 位原始毫米值,不压缩——保留物理信息)
      preview/  彩色+深度伪彩色并排的 JPEG(给人眼快速翻看用的)
    外加两份记录:
      timestamps.csv  每帧的系统时间、设备时间戳、中心像素距离
      meta.json       序列号、两路内参、深度单位、帧数

用法:
    python record.py                    # 录到按 ESC 或 q 为止,带实时预览窗口
    python record.py --seconds 10       # 录 10 秒自动停
    python record.py --name sit_test    # 给这次 run 起个名字(默认用时间戳)

判读(录完怎么知道录好了):
    - 窗口不卡、帧数在涨                              -> 采集正常
    - preview 里手/物体移动,深度伪彩色跟着变           -> 数据是活的
    - timestamps.csv 的 center_distance_m 有合理变化   -> 距离信息有效
    - 预览里某些区域发黑                              -> 那是没测到的区域
                                                       (65535 哨兵值,见 meta.json 说明)

已知简化(以后需要再升级):
    - 每帧同步写三个文件,帧率可能低于 30fps;要满帧采集需加异步队列
    - 彩色和深度未做像素级对齐(rs.align);需要时在 start() 后加
"""
import argparse
import csv
import json
import time
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs


def intr_to_dict(intr):
    """把 SDK 的内参对象转成可 JSON 序列化的字典(以后做点云/标定要用)。"""
    return {
        "width": intr.width,
        "height": intr.height,
        "fx": intr.fx,
        "fy": intr.fy,
        "ppx": intr.ppx,
        "ppy": intr.ppy,
        "model": str(intr.model),
        "coeffs": list(intr.coeffs),
    }


def main():
    parser = argparse.ArgumentParser(description="录制 D435 彩色+深度数据")
    parser.add_argument("--seconds", type=float, default=0,
                        help="录制秒数;0(默认)= 手动按 ESC/q 停止")
    parser.add_argument("--name", default="",
                        help="run 名字,默认用时间戳")
    args = parser.parse_args()

    # 输出目录:camera/data/run_<名字或时间戳>/
    run_name = args.name or f"run_{time.strftime('%Y%m%d_%H%M%S')}"
    out_dir = Path(__file__).parent / "data" / run_name
    (out_dir / "color").mkdir(parents=True, exist_ok=True)
    (out_dir / "depth").mkdir(parents=True, exist_ok=True)
    (out_dir / "preview").mkdir(parents=True, exist_ok=True)
    print(f"输出目录:{out_dir}")

    # 启动双流(和 probe.py 相同配置)
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipeline.start(config)

    # 录制前先拿设备信息和内参,写进 meta.json
    dev = profile.get_device()
    depth_scale = dev.first_depth_sensor().get_depth_scale()  # 米/单位,通常 0.001

    frame_idx = 0
    t_start = time.time()
    csv_path = out_dir / "timestamps.csv"
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["frame", "system_time_s", "device_time_ms", "center_distance_m"])

    print("录制中……按 ESC 或 q 停止" if not args.seconds else f"录制 {args.seconds} 秒……")
    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth = frames.get_depth_frame()
            color = frames.get_color_frame()
            if not depth or not color:
                continue

            # 转 numpy:深度保持 16 位原值,彩色就是 8 位 BGR
            depth_np = np.asanyarray(depth.get_data())
            color_np = np.asanyarray(color.get_data())

            # 存三样
            cv2.imwrite(str(out_dir / "color" / f"{frame_idx:06d}.png"), color_np)
            np.save(out_dir / "depth" / f"{frame_idx:06d}.npy", depth_np)
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_np, alpha=0.03), cv2.COLORMAP_JET
            )
            preview = np.hstack((color_np, depth_colormap))
            cv2.imwrite(str(out_dir / "preview" / f"{frame_idx:06d}.jpg"), preview,
                        [cv2.IMWRITE_JPEG_QUALITY, 80])

            # 记一行:系统时间 + 设备时间戳(多传感器同步用) + 中心距离(米)
            center_dist = depth.get_distance(depth.width // 2, depth.height // 2)
            csv_writer.writerow([
                frame_idx,
                f"{time.time():.3f}",
                f"{depth.get_timestamp():.1f}",
                f"{center_dist:.4f}",
            ])

            # 实时预览窗口,录的时候能盯着
            cv2.imshow("recording  (ESC/q to stop)", preview)
            key = cv2.waitKey(1) & 0xFF

            frame_idx += 1
            elapsed = time.time() - t_start
            print(f"\r已录 {frame_idx} 帧,{elapsed:.1f} 秒,中心距离 {center_dist:.2f} m",
                  end="", flush=True)

            if key in (27, ord("q")):
                break
            if args.seconds and elapsed >= args.seconds:
                break
    finally:
        # 无论怎么停,都要收尾:停流、关窗口、关 csv
        pipeline.stop()
        cv2.destroyAllWindows()
        csv_file.close()

        # 写 meta.json:设备信息 + 内参 + 深度单位 + 帧数 + 哨兵值说明
        depth_intr = intr_to_dict(
            depth.profile.as_video_stream_profile().get_intrinsics()
        ) if depth else None
        color_intr = intr_to_dict(
            color.profile.as_video_stream_profile().get_intrinsics()
        ) if color else None
        meta = {
            "run_name": run_name,
            "recorded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": {
                "name": dev.get_info(rs.camera_info.name),
                "serial": dev.get_info(rs.camera_info.serial_number),
            },
            "streams": {"depth": "640x480 z16 @30fps", "color": "640x480 bgr8 @30fps"},
            "depth_scale_m_per_unit": depth_scale,
            "depth_intrinsics": depth_intr,
            "color_intrinsics": color_intr,
            "frame_count": frame_idx,
            "sentinel_note": (
                "depth/*.npy 是 16 位原始值,单位由 depth_scale 换算成米。"
                "值 65535 表示'没测到'(超出量程/表面吸光/被遮挡),"
                "用之前要先 mask 掉,不能当真距离。"
            ),
        }
        with open(out_dir / "meta.json", "w") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        print(f"\n录了 {frame_idx} 帧 → {out_dir}")
        print("meta.json 已写入(内参/序列号/深度单位都在里面)")


if __name__ == "__main__":
    main()
