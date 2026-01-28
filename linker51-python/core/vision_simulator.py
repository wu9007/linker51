import cv2
import os
import numpy as np

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"找不到测试图片: {image_path}")

    def get_target_corners(self):
        frame = cv2.imread(self.image_path)
        if frame is None:
            return None, None

        # 打印新图片的真实规格
        h, w, c = frame.shape
        print(f"--- 图片规格: 宽 {w}px, 高 {h}px, 通道 {c} ---")

        # 中值滤波去噪，防止纹理干扰
        blurred = cv2.medianBlur(frame, 5)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # 定义黄色的 HSV 范围
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # 去除背景杂点，填补球体内的阴影
        kernel = kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 找到面积最大的黄色物体
            c = max(contours, key=cv2.contourArea)

            # 过滤掉过小的杂质区域
            if cv2.contourArea(c) < 100:
                return None, frame

            # 获取最小外接圆
            (x, y), radius = cv2.minEnclosingCircle(c)
            center = (int(x), int(y))
            radius = int(radius)

            # 给 solvePnP 四个点，模拟一个以圆心为中心的“虚拟正方形”
            r = radius
            box = np.array([
                [x - r, y - r],
                [x + r, y - r],
                [x + r, y + r],
                [x - r, y + r]
            ], dtype=np.float32)

            # 在原图上画出绿色边框识别结果
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            # 在原图上画出红色圆心识别结果
            cv2.circle(frame, center, 2, (0, 0, 255), 3)

            return box, frame

        return None, frame