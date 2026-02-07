import numpy as np
import config
from core.robot_config import RobotArmConfig
from core.trajectory_planner import CriticalDampingFilter


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
        # 为 X, Y, Z 三个轴分别创建滤波器
        # f_n = 2.0 (响应速度), dt = 0.03 (假设循环是 30fps)
        self.filter_x = CriticalDampingFilter(f_n=2.0, dt=0.03)
        self.filter_y = CriticalDampingFilter(f_n=2.0, dt=0.03)
        self.filter_z = CriticalDampingFilter(f_n=2.0, dt=0.03)

    def track_target(self, target_xyz):
        """
        让机械臂转动到指定坐标（坐标换->角度->单片机命令包）
        :param target_xyz: 坐标
        :return: 角度
        """
        # 通过滤波器，将跳跃的原始坐标转化为平滑的当前指令坐标
        smooth_x = self.filter_x.update(target_xyz[0])
        smooth_y = self.filter_y.update(target_xyz[1])
        smooth_z = self.filter_z.update(target_xyz[2])
        smooth_target = [smooth_x, smooth_y, smooth_z]

        # 直接对平滑后的坐标进行逆解计算
        target_angles = self.arm_chain.inverse_kinematics(
            smooth_target,
            initial_position=self.current_angles)
        # 发送给硬件
        self._send_angles_to_servo(target_angles)
        # 更新状态
        self.current_angles = target_angles
        return target_angles

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
        将角度转换成单片机指令包之后发送给单片机，以驱动舵机旋转
        :param rad: 角度数组
        :return: 是否发送成功

        """
        # 弧度转角度
        angle = np.degrees(rad)

        # 映射公式：(当前角度 / 总角度180) * 总刻度跨度200 + 起始偏移50
        level = config.PWM_MIN_BASE + (angle / 180.0) * config.PWM_SPAN

        # 严格执行安全限位 (SERVO_MIN_VAL=60, SERVO_MAX_VAL=240)
        final_level = int(max(config.SERVO_MIN_VAL, min(config.SERVO_MAX_VAL, round(level))))

        return final_level
