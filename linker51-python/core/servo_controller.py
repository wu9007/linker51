import time

import numpy as np
import config
from core.robot_config import RobotArmConfig


class ServoController:
    def __init__(self, communicator, robot_config: RobotArmConfig = None):
        """
        初始化舵机控制器
        :param communicator: 串口通讯实例
        """
        self.communicator = communicator
        # 构建机械臂模型
        if robot_config is None:
            self.config = RobotArmConfig()
        else:
            self.config = robot_config
        self.arm_chain = self.config.build_chain()
        # 设置初始角度
        self.home_angles = list(self.config.home_angles)
        self.current_angles = list(self.home_angles)
        # 舵机映射范围
        self.min_pos = self.config.servo_min_level
        self.max_pos = self.config.servo_max_level

    def track_target(self, target_xyz):
        """
        让机械臂转动到指定坐标（坐标换->角度->单片机命令包）
        :param target_xyz: 坐标
        :return: 角度
        """
        # 解算角度（inverse_kinematics：返回逆运动学的变换矩阵）
        target_angles = self.arm_chain.inverse_kinematics(
            target_xyz,
            initial_position=self.home_angles)

        # 生成角度插值路径（让动画变丝滑）
        path = np.linspace(self.current_angles, target_angles, num=10)
        for step_angles in path:
            # 发送硬件指令
            self._send_angles_to_servo(step_angles)
            # 把控制权交还给调用者，并带出当前状态
            yield step_angles
            # 控制频率，避免单片机处理不过来 (单位: 秒)
            time.sleep(0.02)
        self.current_angles = target_angles

    def _send_angles_to_servo(self, angles):
        """
        将角度转换成单片机指令包之后发送给单片机，以驱动舵机旋转
        :param angles: 角度数组
        :return: 是否发送成功
        """
        lvl_base = self._angle_to_level(angles[1])
        lvl_shoulder = self._angle_to_level(angles[2])
        lvl_elbow = self._angle_to_level(angles[3])

        packet = bytes([config.PACKET_HEAD, lvl_base, lvl_shoulder, lvl_elbow])
        print(f"[IK] Angles: {np.degrees(angles[1:4])} -> Levels: {lvl_base, lvl_shoulder, lvl_elbow}")
        return self.communicator.send_packet(packet)

    def _angle_to_level(self, rad):
        """
        将角度转换成发送给舵机的指令
        :param rad: 角度
        :return: 舵机指令
        """
        angle = np.degrees(rad)
        span = self.max_pos - self.min_pos
        level = self.min_pos + (angle / 180.0) * span
        return int(max(self.min_pos-1, min(self.max_pos-1, round(level))))
