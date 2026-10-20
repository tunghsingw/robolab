"""view.py - 实时画面(第 2 步)

前置:probe.py 跑通后,先补装 opencv-python 并加进 requirements.txt:
    uv pip install opencv-python

干什么:
    实时显示两路画面——左边彩色,右边深度(伪彩色:近处偏红/亮,远处偏蓝/暗)。
    按 ESC 键退出。

判读(看到什么说明什么):
    - 手靠近镜头,深度图手的位置变色            -> 深度测量正常
    - 深度图大片黑色                            -> 那些表面没测到:
                                                  光滑/吸光(玻璃、黑绒)、超出 3 m 量程、
                                                  或两个红外相机都看不到的区域
    - 画面卡顿/花屏                            -> USB 供电不足,换主板后置 USB 3.0 口
"""
import cv2
import numpy as np
import pyrealsense2 as rs

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

try:
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # 转成 numpy 数组才能用 OpenCV 处理
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # 深度值是 16 位整数(毫米),乘 0.03 压到 0-255 范围再套伪彩色,方便人眼看
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
        )

        # 左右拼接:左彩色,右深度
        images = np.hstack((color_image, depth_colormap))
        cv2.imshow("color | depth   (ESC to quit)", images)

        # 等 1 毫秒,按 ESC(27)退出
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    # 和 probe.py 一样:退出时一定停流、关窗口,否则相机被占用
    pipeline.stop()
    cv2.destroyAllWindows()
