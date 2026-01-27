import numpy as np
import time
from core.servo_controller import ServoController # 确保路径正确

# 模拟一个简易的通信器，仅用于观察打印输出
class DummyCommunicator:
    def send_packet(self, packet):
        print(f"发送数据包 (Hex): {packet.hex().upper()}")
        return True

def run_test():
    comm = DummyCommunicator()
    servo = ServoController(comm)

    # 初始角度设为 0 (或者根据你的机械臂实际垂直位调整)
    initial_angles = [0, np.pi/2, np.pi/4, np.pi/4, 0]

    print("=== 第一阶段：正向运动学 (FK) ===")
    current_frame = servo.arm_chain.forward_kinematics(initial_angles)
    p_now = current_frame[:3, 3]
    print(f"当前末端物理坐标 (m): X={p_now[0]:.3f}, Y={p_now[1]:.3f}, Z={p_now[2]:.3f}")

    print("\n=== 第二阶段：模拟增量测试 ===")
    offset = np.array([0, 0.02, 0]) # 尝试向前移动 2cm
    p_target = p_now + offset
    print(f"目标末端物理坐标 (m): X={p_target[0]:.3f}, Y={p_target[1]:.3f}, Z={p_target[2]:.3f}")

    print("\n=== 第三阶段：逆向运动学 (IK) ===")
    try:
        # 兼容性修复：不传 active_links_mask
        # ikpy 会默认使用所有活动的 Link
        target_angles = servo.arm_chain.inverse_kinematics(
            p_target,
            initial_position=initial_angles
        )
        print(f"解算出的弧度: {target_angles}")

        # 验证结果是否符合预期
        lvl_x = servo._angle_to_level(target_angles[1])
        lvl_y = servo._angle_to_level(target_angles[2])
        lvl_z = servo._angle_to_level(target_angles[3])
        print(f"最终指令 -> Level X:{lvl_x}, Y:{lvl_y}, Z:{lvl_z}")

    except Exception as e:
        print(f"IK 计算发生错误: {e}")

if __name__ == "__main__":
    run_test()