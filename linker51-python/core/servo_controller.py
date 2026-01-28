import config
import numpy as np
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
from core.visualizer import plot_arm

class ServoController:
    def __init__(self, communicator):
        self.communicator = communicator
        # 机械臂应该是一条沿 Y 轴平躺在 $Z=0.05$ 平面上的直线
        self.arm_chain = Chain(name='arm_3dof', links=[
            OriginLink(),
            URDFLink(
                name="base",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, 0.05]), # 底座高度 5cm
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 0, 1])               # 绕 Z 轴左右转
            ),
            URDFLink(
                name="shoulder",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, 0]),     # 肩部舵机在底座顶部
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 1, 0])               # 绕 Y 轴俯仰
            ),
            URDFLink(
                name="elbow",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, 0.1]), # 大臂长度 5cm，向上延伸
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 1, 0])               # 绕 Y 轴俯仰
            ),
            URDFLink(
                name="tip",
                bounds=(0, 0.001),
                origin_translation=np.array([0, 0.1, 0]), # 小臂长度 5cm，向前延伸
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 0, 0])
            ),
        ])
        # 2. 设置初始弧度 (90度 = pi/2)
        init_rad = np.pi / 2
        # 对应链接: [Origin, Base, Shoulder, Elbow, Tip]
        self.current_angles = [0, init_rad, init_rad, init_rad, 0]

        # 记录当前活动的 mask，避免每次调用传参报错
        self.active_mask = [False, True, True, True, False]
        self.min_pos = 5   # 对应舵机约 0 度
        self.max_pos = 22  # 对应舵机约 180 度 (安全上限)

    def _angle_to_level(self, rad):
        """将 ikpy 的弧度转为 5-22 的 level"""
        angle = np.degrees(rad)
        span = self.max_pos - self.min_pos
        level = self.min_pos + (angle / 180.0) * span
        return int(max(self.min_pos, min(self.max_pos, round(level))))

    def track_target(self, target_xyz):
        """target_xyz: [x, y, z] 的列表，例如 [0.1, 0.05, 0.1]"""
        # 解算角度
        angles = self.arm_chain.inverse_kinematics(
            target_xyz,
            initial_position=self.current_angles)

        plot_arm(self, target_xyz, angles)

        # 更新记录当前角度
        self.current_angles = angles

        # 映射到 Level
        lvl_x = self._angle_to_level(angles[1])
        lvl_y = self._angle_to_level(angles[2])
        lvl_z = self._angle_to_level(angles[3])

        # 发送符合单片机新状态机的数据包
        packet = bytes([config.PACKET_HEAD, lvl_x, lvl_y, lvl_z]) #
        print(f"[IK] Angles: {np.degrees(angles[1:4])} -> Levels: {lvl_x, lvl_y, lvl_z}")
        return self.communicator.send_packet(packet)

    def stop(self):
        # 复位到 90 度位 (Level 13 左右)
        mid_level = self._angle_to_level(np.pi/2)
        packet = bytes([0xFE, mid_level, mid_level, mid_level])
        return self.communicator.send_packet(packet)