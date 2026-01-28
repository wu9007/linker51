import config
import cv2
import time
import matplotlib.pyplot as plt
from core.communicator import Communicator
from core.servo_controller import ServoController

def main():
    # 初始化串口通信
    communicator = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    # 初始化舵机控制器
    servo = ServoController(communicator)

    # 初始位
    home_pos = servo.arm_chain.forward_kinematics(servo.current_angles)[:3, 3]
    home_x, home_y, home_z = home_pos
    print(f"--- 初始锚点位置: X={home_x:.3f}, Y={home_y:.3f}, Z={home_z:.3f} ---")

    # 运动目标点，测试用
    test_targets = [
        [-0.20,  0.00, -0.20],  # 对应目标 [-0.2, 0.0, 0.15]
        [ 0.00,  0.00,  0.00],  # 对应目标 [0.0, 0.2, 0.15]
        [ 0.20,  0.00, -0.20],  # 对应目标 [0.2, 0.0, 0.15]
        [ 0.00, -0.20, -0.20],  # 对应目标 [0.0, 0.0, 0.35]
        [ 0.10,  0.15, -0.15]   # 对应目标 [0.10, 0.05, 0.0]
    ]

    try:
        for i, rel_xyz in enumerate(test_targets):
            print(f"\n[点位 {i+1}] 正在移向目标: {rel_xyz}")
            # 解算 PnP，tvec 就是物体相对于相机的 [x, y, z] 偏移 (单位: 米)
            rel_x, rel_y, rel_z = rel_xyz
            print(f"目标相对于相机位置: X={rel_x:.3f}m, Y={rel_y:.3f}m, Z(深度)={rel_z:.3f}m")

            # 在初始位置基础上，叠加相机的观测位移
            target_x = home_x + rel_x
            target_y = home_y + rel_z
            target_z = home_z - rel_y
            print(f"目标相对于机器人的位置: X={target_x:.3f}m, Y={target_y:.3f}m, Z(深度)={target_z:.3f}m")

            # target_xyz = [0.10, 0.05, 0.0]
            # target_xyz = [-0.2, 0.0, 0.15]
            # target_xyz = [0.0, 0.2, 0.15]
            # target_xyz = [0.2, 0.0, 0.15]
            # target_xyz = [0.0, 0.0, 0.35]
            target_xyz = [target_x, target_y, target_z]
            success = servo.track_target(target_xyz)
            if success:
                print(" -> 发送成功。")
            else:
                print(" -> 发送失败。")
            time.sleep(0.5)

        fig = plt.gcf()
        print("\n[提示] 追踪任务结束。请手动关闭 3D 图形窗口以退出程序...")
        # 只要窗口还存在，就保持运行
        while plt.fignum_exists(fig.number):
            plt.pause(0.1)

        servo.stop()
    except KeyboardInterrupt:
        print("\n Ctr+C 手动停止。")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()