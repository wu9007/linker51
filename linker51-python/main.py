import time

import config
import cv2
import matplotlib.pyplot as plt

import calibrate_data
from core.communicator import Communicator
from core.servo_controller import ServoController


def main():
    communicator = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    servo = ServoController(communicator)

    # 初始位（forward_kinematics：返回正运动学的变换矩阵）
    home_pos = servo.arm_chain.forward_kinematics(servo.home_angles)[:3, 3]
    home_x, home_y, home_z = home_pos
    print(f"--- 初始锚点位置: X={home_x:.3f}, Y={home_y:.3f}, Z={home_z:.3f} ---")

    test_targets = generate_path()
    try:
        for i, rel_xyz in enumerate(test_targets):
            # 相对相机的坐标
            rel_x, rel_y, rel_z = rel_xyz
            print(f"目标相对于相机位置: X={rel_x:.3f}m, Y={rel_y:.3f}m, Z(深度)={rel_z:.3f}m")

            # 在初始位置基础上，叠加相机的观测位移，得到相对机械臂的坐标
            target_x = home_x + rel_x
            target_y = home_y + rel_z
            target_z = home_z - rel_y
            print(f"目标相对于机器人的位置: X={target_x:.3f}m, Y={target_y:.3f}m, Z(深度)={target_z:.3f}m")

            target_xyz = [target_x, target_y, target_z]
            servo.track_target(target_xyz)
            time.sleep(0.2)

        fig = plt.gcf()
        print("\n[提示] 追踪任务结束。请手动关闭 3D 图形窗口以退出程序...")
        # 只要窗口还存在，就保持运行
        while plt.fignum_exists(fig.number):
            plt.pause(0.1)

    except KeyboardInterrupt:
        print("\n Ctr+C 手动停止。")
    finally:
        cv2.destroyAllWindows()


def generate_path():
    # 运动目标点，测试用
    path = [
        [-0.20, 0.00, -0.20],  # 对应目标 [-0.2, 0.0, 0.15]
        [0.20, 0.00, -0.20],  # 对应目标 [0.2, 0.0, 0.15]
        [0.00, -0.20, -0.20],  # 对应目标 [0.0, 0.0, 0.35]
        [0.10, 0.15, -0.15],  # 对应目标 [0.10, 0.05, 0.0]
        [-0.18, 0.05, -0.10],  # 扫向左下方
        [0.18, 0.05, -0.10],  # 扫向右下方
        [0.00, 0.00, 0.00]  # 对应目标 [0.0, 0.2, 0.15]
    ]
    return path


if __name__ == "__main__":
    main()
