import time

import cv2
import numpy as np

import config
from core.communicator import Communicator
from core.servo_controller import ServoController


class BallTracker:
    def __init__(self, params_path, hand_eye_path, ball_radius):
        """
        :param params_path: 标定文件路径 (.npz)
        :param ball_radius: 小球的真实半径 (单位: 米)
        """
        # 加载相机内参
        data = np.load(params_path)
        self.mtx = data['mtx']
        self.dist = data['dist']
        self.fx = self.mtx[0, 0]
        self.fy = self.mtx[1, 1]
        self.cx = self.mtx[0, 2]
        self.cy = self.mtx[1, 2]

        self.ball_radius = ball_radius
        self.ball_diameter = ball_radius * 2

        # 加载手眼变换矩阵
        if hand_eye_path is not None:
            self.M = np.load(hand_eye_path)
        else:
            self.M = None
            print("注意：未加载手眼矩阵，camera_to_robot 功能将不可用")

        # 颜色范围配置 (黄色)
        self.color_lower = np.array([20, 100, 100])
        self.color_upper = np.array([40, 255, 255])

    def camera_to_robot(self, x_c, y_c, z_c):
        """
        相机坐标系 -> 机械臂坐标系
        """
        if self.M is None:
            return None
        p_cam = np.array([x_c, y_c, z_c, 1.0])
        p_robot = self.M @ p_cam
        return p_robot[0], p_robot[1], p_robot[2]

    def get_ball_coords(self, frame):
        """
        识别图像中的球并返回 3D 坐标
        :return: (found, x, y, z, processed_frame)
        """
        # 图像预处理
        gs_frame = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)

        # 颜色掩膜
        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # 寻找轮廓
        cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) > 0:
            # 找到面积最大的轮廓
            c = max(cnts, key=cv2.contourArea)
            ((u, v), radius_pixel) = cv2.minEnclosingCircle(c)

            if radius_pixel > 5:  # 过滤噪声
                # --- 计算 3D 坐标 ---
                # 计算深度 Z (利用相似三角形: Z = (D * f) / d)
                # d 是像素直径 (radius_pixel * 2)
                z = (self.ball_diameter * self.fx) / (radius_pixel * 2)

                # 计算 X 和 Y (利用小孔成像逆变换)
                x = (u - self.cx) * z / self.fx
                y = (v - self.cy) * z / self.fy

                # 可视化绘制
                cv2.circle(frame, (int(u), int(v)), int(radius_pixel), (0, 255, 255), 2)
                cv2.putText(frame, f"X:{x:.2f} Y:{y:.2f} Z:{z:.2f}m",
                            (int(u - radius_pixel), int(v - radius_pixel - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                return True, x, y, z, frame

        return False, 0, 0, 0, frame


# --- 使用示例 ---
if __name__ == "__main__":
    tracker = BallTracker("../calibrate_data/camera_params.npz",
                          "../calibrate_data/hand_eye_matrix.npy",
                          ball_radius=0.006)
    img_path = "../assets/1FB70894-64C5-4C27-92D7-9A70BC4055B2.jpeg"
    frame = cv2.imread(img_path)

    communicator = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    servo = ServoController(communicator)

    if frame is not None:
        found, cx, cy, cz, res_frame = tracker.get_ball_coords(frame)
        if found:
            print(f"检测到小球！相机坐标: X={cx:.3f}, Y={cy:.3f}, Z={cz:.3f}")
            robot_pos = tracker.camera_to_robot(cx, cy, cz)
            if robot_pos:
                print(f"目标在机械臂坐标系位置: {robot_pos}")
                servo.track_target(robot_pos)
                cv2.waitKey(0)
        else:
            print("未能从小球图片中提取到黄色目标，请检查HSV阈值。")
    else:
        print(f"找不到图片: {img_path}")
    cv2.destroyAllWindows()
