import cv2
import numpy as np

class BallPoseEstimator:
    def __init__(self, params_path, hand_eye_path, ball_radius):
        """
        :param params_path: 标定文件路径 (.npz)
        :param ball_radius: 小球的真实半径 (单位: 米)
        """
        # 加载相机内参
        data = np.load(params_path)
        self._mtx = data['mtx']
        self._dist = data['dist']
        self._fx = self._mtx[0, 0]
        self._fy = self._mtx[1, 1]
        self._cx = self._mtx[0, 2]
        self._cy = self._mtx[1, 2]

        self._ball_radius = ball_radius
        self._ball_diameter = ball_radius * 2

        # 加载手眼变换矩阵
        if hand_eye_path is not None:
            self.M = np.load(hand_eye_path)
        else:
            self.M = None
            print("注意：未加载手眼矩阵，camera_to_robot 功能将不可用")

        # 颜色范围配置 (黄色)
        self._color_lower = np.array([20, 100, 100])
        self._color_upper = np.array([40, 255, 255])

    def get_robot_coords(self, frame):
        """
        输入图像，直接返回小球相对于机械臂的坐标 (x, y, z)
        :return:
            如果找到: (True, (x_rob, y_rob, z_rob), processed_frame)
            如果没找: (False, None, processed_frame)
        """
        # 获取目标在相机坐标系下的坐标
        found, p_cam, processed_frame = self._process_image(frame)

        if not found:
            return False, None, None, processed_frame

        # 转换为机械臂坐标系下的坐标
        p_robot = self._camera_to_robot(p_cam)

        # 如果转换失败则返回空
        if p_robot is None:
            return False, None, None, processed_frame

        # 返回最终结果
        return True, p_cam, p_robot, processed_frame

    def _camera_to_robot(self, p_cam):
        """
        相机坐标系 -> 机械臂坐标系
        """
        if self.M is None:
            return None
        p_robot = self.M @ np.append(p_cam, 1.0)
        return p_robot[0], p_robot[1], p_robot[2]

    def _process_image(self, frame):
        """
        识别图像中的球并返回其在相机坐标系下的3D 坐标
        :return: (found, x, y, z, processed_frame)
        """
        # 图像预处理
        gs_frame = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)

        # 颜色掩膜
        mask = cv2.inRange(hsv, self._color_lower, self._color_upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # 寻找轮廓
        cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((u, v), radius_pixel) = cv2.minEnclosingCircle(c)
            if radius_pixel > 5:
                z = (self._ball_diameter * self._fx) / (radius_pixel * 2)
                x = (u - self._cx) * z / self._fx
                y = (v - self._cy) * z / self._fy
                self.last_uv = (int(u), int(v), int(radius_pixel))
                return True, np.array([x, y, z]), frame
        return False, None, frame
