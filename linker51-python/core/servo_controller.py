import time

import numpy as np
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink

import config
from core.visualizer import plot_arm_animated


class ServoController:
    def __init__(self, communicator):
        """
        初始化舵机控制器
        :param communicator: 串口通讯实例
        """
        self.communicator = communicator
        self.arm_chain = Chain(name='bottle_arm', links=[
            OriginLink(),
            URDFLink(
                name="base",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, 0.045]),
                origin_orientation=np.array([0, 0, -np.pi / 2]),
                rotation=np.array([0, 0, 1])
            ),
            URDFLink(
                name="shoulder",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, 0.14]),
                origin_orientation=np.array([-np.pi / 2, 0, 0]),
                rotation=np.array([1, 0, 0])
            ),
            URDFLink(
                name="elbow",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0.55, 0]),
                origin_orientation=np.array([-np.pi / 2, 0, 0]),
                rotation=np.array([1, 0, 0])
            ),
            URDFLink(
                name="tip",
                bounds=(0, 0.001),
                origin_translation=np.array([0, 0.1, 0]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 0, 0])
            ),
        ])

        # 设置初始角度
        self.home_angles = [0, np.pi / 2, np.pi / 2, np.pi / 2, 0]

        self.active_mask = [False, True, True, True, False]
        self.min_pos = 5
        self.max_pos = 22

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
        path = np.linspace(self.home_angles, target_angles, num=10)
        for step_angles in path:
            plot_arm_animated(self, target_xyz, step_angles)
            self._send_angles_to_servo(step_angles)
            # 控制频率，避免单片机处理不过来 (单位: 秒)
            time.sleep(0.02)

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
        return int(max(self.min_pos, min(self.max_pos, round(level))))
