import time

import numpy as np
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink

import config
from core.visualizer import plot_arm_animated


class ServoController:
    def __init__(self, communicator):
        self.communicator = communicator
        self.arm_chain = Chain(name='bottle_arm', links=[
            OriginLink(),
            URDFLink(
                name="base",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, 0.05]),
                origin_orientation=np.array([0, 0, -np.pi / 2]),
                rotation=np.array([0, 0, 1])
            ),
            URDFLink(
                name="shoulder",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, 0.1]),
                origin_orientation=np.array([-np.pi / 2, 0, 0]),
                rotation=np.array([1, 0, 0])
            ),
            URDFLink(
                name="elbow",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0.1, 0]),
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
        self.current_angles = [0, np.pi / 2, np.pi / 2, np.pi / 2, 0]

        self.active_mask = [False, True, True, True, False]
        self.min_pos = 5
        self.max_pos = 22

    def _angle_to_level(self, rad):
        angle = np.degrees(rad)
        span = self.max_pos - self.min_pos
        level = self.min_pos + (angle / 180.0) * span
        return int(max(self.min_pos, min(self.max_pos, round(level))))

    def track_target(self, target_xyz):
        # plot_arm(self, target_xyz, self.current_angles)
        # 解算角度
        target_angles = self.arm_chain.inverse_kinematics(
            target_xyz,
            initial_position=self.current_angles)

        # 生成角度插值路径（让动画变丝滑的关键）
        path = np.linspace(self.current_angles, target_angles, num=10)
        for step_angles in path:
            # 更新动画
            plot_arm_animated(self, target_xyz, step_angles)
            # 在这里实时发送指令给舵机，实物也会跟着丝滑移动
            self._send_angles_to_servo(step_angles)
            # 稍微控制一下频率，避免单片机处理不过来 (单位: 秒)
            time.sleep(0.02)

        # 更新记录当前角度
        self.current_angles = target_angles
        return True

    def _send_angles_to_servo(self, angles):
        lvl_base = self._angle_to_level(angles[1])
        lvl_shoulder = self._angle_to_level(angles[2])
        lvl_elbow = self._angle_to_level(angles[3])

        # 发送符合单片机新状态机的数据包
        packet = bytes([config.PACKET_HEAD, lvl_base, lvl_shoulder, lvl_elbow])
        print(f"[IK] Angles: {np.degrees(angles[1:4])} -> Levels: {lvl_base, lvl_shoulder, lvl_elbow}")
        return self.communicator.send_packet(packet)

    def stop(self):
        mid_level = self._angle_to_level(np.pi / 2)
        packet = bytes([0xFE, mid_level, mid_level, mid_level])
        return self.communicator.send_packet(packet)
