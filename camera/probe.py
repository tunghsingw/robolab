"""probe.py - 相机验证脚本(第 1 步)

干什么:
    列出连接的 RealSense 设备,启动彩色 + 深度双流,取一帧,
    打印设备信息、画面分辨率、深度内参、镜头正对物体的距离。

判读(看到什么说明什么):
    - 打印出 "Intel RealSense D435" 且距离合理  -> 硬件到软件全通
    - 报错找不到设备 / 设备数为 0              -> 插 USB 3.0 蓝色口、换线,
                                                   或先用 RealSense Viewer 确认系统能识别
    - 中心距离打印 0.000                        -> 镜头正前方没测到东西,
                                                   把手或物体放到正前方再跑
"""
import pyrealsense2 as rs


def main():
    # 1) 列出所有已连接的 RealSense 设备
    ctx = rs.context()
    devices = ctx.query_devices()
    print(f"检测到 {len(devices)} 个 RealSense 设备")
    for dev in devices:
        print(
            f"  - {dev.get_info(rs.camera_info.name)}"
            f"  序列号 {dev.get_info(rs.camera_info.serial_number)}"
        )
    if len(devices) == 0:
        print(
            "\n没有找到设备。排查:"
            "\n  1. 相机插在 USB 3.0 口(蓝色口),不要用 USB 2.0 口或劣质线"
            "\n  2. 打开 RealSense Viewer,确认 Windows 自己能识别到相机"
            "\n  3. 以上都无效,换线(D435 必须 USB 3.0 线材)"
        )
        return

    # 2) 启动双流:深度 640x480@30 + 彩色 640x480@30(D435 常用配置)
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipeline.start(config)

    try:
        # 3) 等一帧到齐,取出其中的深度帧和彩色帧
        #    (等几帧让相机自动曝光稳定下来,第一帧可能偏暗)
        for _ in range(30):
            frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        if not depth or not color:
            print("没取到完整的帧,重跑一次试试")
            return

        # 4) 打印分辨率
        print(f"\n深度画面 {depth.width}x{depth.height},彩色画面 {color.width}x{color.height}")

        # 5) 打印深度内参(焦距 fx/fy、主点 cx/cy)——以后做点云、标定要用
        intr = depth.profile.as_video_stream_profile().get_intrinsics()
        print(
            f"深度内参:焦距 fx={intr.fx:.1f} fy={intr.fy:.1f},"
            f"主点 cx={intr.ppx:.1f} cy={intr.ppy:.1f},单位 毫米"
        )

        # 6) 读画面正中心像素测到的距离(米)
        cx, cy = depth.width // 2, depth.height // 2
        dist = depth.get_distance(cx, cy)
        print(f"\n镜头正对 {dist:.3f} 米处的物体")
        if dist == 0.0 or dist > 60.0:
            print(
                "(距离为 0 或 65.535 米 = 正前方没测到。深度图是 16 位整数,"
                "65535 毫米(≈65.5 米)是'测不到'的满值标记——超出量程、"
                "表面吸光/光滑(玻璃、黑绒)、或被遮挡都会这样。"
                "把手或一个物体放到镜头正前方约 0.5 m,重跑)"
            )
    finally:
        # 7) 无论成败都要停掉流,否则相机被占用,下次跑会报设备忙
        pipeline.stop()


if __name__ == "__main__":
    main()
