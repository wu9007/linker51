import config
import cv2
import numpy as np
from core.communicator import Communicator
from core.vision_simulator import ImageProcessor
from core.servo_controller import ServoController

def main():
    # 初始化串口通信
    communicator = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    # 初始化舵机控制器
    servo = ServoController(communicator)

    # 假设图片中的红块是一个 4cm x 4cm 的正方形
    obj_points = np.array([
        [-0.02, -0.02, 0],
        [ 0.02, -0.02, 0],
        [ 0.02,  0.02, 0],
        [-0.02,  0.02, 0]
    ], dtype=np.float32)
    # 摄像头内参 (根据你的分辨率 1536x860 估算)
    f = 1000
    cx, cy = 1536/2, 860/2
    camera_matrix = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float32)
    dist_coeffs = np.zeros((4, 1)) # 假设没有镜头畸变

    # 指定测试图片
    img_path = "assets/mid.png"
    processor = ImageProcessor(img_path)
    print(f"--- 正在分析测试图片: {img_path} ---")
    try:
        # 从图片获取“模拟”坐标
        corners_2d, frame = processor.get_target_corners()
        if corners_2d is not None:
            # 解算 PnP，tvec 就是物体相对于相机的 [x, y, z] 偏移 (单位: 米)
            _, rvec, tvec = cv2.solvePnP(obj_points, corners_2d, camera_matrix, dist_coeffs)

            rel_x, rel_y, rel_z = tvec.flatten()
            print(f"目标相对于相机位置: X={rel_x:.3f}m, Y={rel_y:.3f}m, Z(深度)={rel_z:.3f}m")

            # 转换到机器人坐标系并移动，先通过当前关节角度算出相机（末端）现在的绝对位置（假设当前关节角度是 servo.current_angles）
            current_pos = servo.arm_chain.forward_kinematics(servo.current_angles)[:3, 3]
            curr_x, curr_y, curr_z = current_pos
            # 在当前位置基础上，叠加相机的观测位移
            target_x = curr_x + rel_x
            target_y = curr_y + rel_z
            target_z = curr_z - rel_y
            print(f"目标相对于机器人的位置: X={target_x:.3f}m, Y={target_y:.3f}m, Z(深度)={target_z:.3f}m")

            # target_xyz = [target_x, target_y, target_z]
            target_xyz = [0.0, 0.15, 0.15]
            success = servo.track_target(target_xyz)
            if success:
                print(" -> 发送成功。")
            else:
                print(" -> 发送失败。")
        cv2.waitKey(0)

        servo.stop()
    except KeyboardInterrupt:
        print("\n Ctr+C 手动停止。")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()