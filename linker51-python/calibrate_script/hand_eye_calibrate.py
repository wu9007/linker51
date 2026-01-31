import cv2
import numpy as np
import time
import config
from core.ball_tracker import BallTracker
from core.communicator import Communicator
from core.servo_controller import ServoController

def main():
    # 1. 初始化硬件和视觉
    comm = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    servo = ServoController(comm)
    # 注意：BallTracker 还没生成 M 矩阵时，hand_eye_path 传 None
    tracker = BallTracker("../calibrate_data/camera_params.npz",
                          hand_eye_path=None,
                          ball_radius=0.006)

    cap = cv2.VideoCapture(0)
    # 稍微降低分辨率，减轻 macOS 扩展坞带宽压力
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # 初始位置
    curr_rx, curr_ry, curr_rz = 0.15, 0.0, 0.10
    step = 0.005

    camera_data_list = []
    robot_data_list = []

    print("--- 手眼标定采集工具 ---")
    print("操作说明:")
    print("  W/S/A/D: 前/后/左/右 移动")
    print("  R/F: 上/下 移动")
    print("  Space(空格): 确认并记录当前点")
    print("  Q: 完成并计算矩阵")

    # 初始移动一次到预设位
    servo.track_target([curr_rx, curr_ry, curr_rz])

    while True:
        ret, frame = cap.read()
        if not ret: break

        # 视觉识别
        found, cx, cy, cz, res_frame = tracker.get_ball_coords(frame)

        # 实时显示（仅显示，不在此处频繁调用 servo）
        cv2.imshow("Calibration Mode", res_frame)

        key = cv2.waitKey(20) & 0xFF # 增加一点点等待时间，给 macOS UI 喘息

        # --- 键盘控制逻辑 ---
        moved = False
        if key == ord('w'):
            curr_rx += step; moved = True
        elif key == ord('s'):
            curr_rx -= step; moved = True
        elif key == ord('a'):
            curr_ry -= step; moved = True
        elif key == ord('d'):
            curr_ry += step; moved = True
        elif key == ord('r'):
            curr_rz += step; moved = True
        elif key == ord('f'):
            curr_rz -= step; moved = True

        # 只有位置变化时才下发指令，避免串口堵塞
        if moved:
            servo.track_target([curr_rx, curr_ry, curr_rz])
            print(f"机械臂移动至: X={curr_rx:.3f}, Y={curr_ry:.3f}, Z={curr_rz:.3f}")
            time.sleep(0.2)

        # --- 保存数据点 ---
        elif key == ord(' '):
            if found:
                camera_data_list.append([cx, cy, cz])
                robot_data_list.append([curr_rx, curr_ry, curr_rz])
                print(f"\n[SAVE] 已保存第 {len(camera_data_list)} 组点:")
                print(f"  相机坐标系 (x,y,z): {[round(c, 4) for c in [cx, cy, cz]]}")
                print(f"  机械臂坐标系 (x,y,z): {[round(r, 4) for r in [curr_rx, curr_ry, curr_rz]]}")
            else:
                print("\a警告：当前画面未检测到球，请调整后再保存！")

        elif key == ord('q'):
            break

    # --- 计算标定矩阵 ---
    if len(camera_data_list) >= 4:
        print("\n正在解算变换矩阵...")
        c_pts = np.array(camera_data_list, dtype=np.float32)
        r_pts = np.array(robot_data_list, dtype=np.float32)

        # 使用 estimateAffine3D 求解 3x4 映射矩阵
        retval, M, inliers = cv2.estimateAffine3D(c_pts, r_pts)

        if retval:
            import os
            save_path = "../calibrate_data/hand_eye_matrix.npy"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            np.save(save_path, M)
            print("="*30)
            print("标定成功！")
            print(f"变换矩阵 M:\n{M}")
            print(f"矩阵已保存至: {save_path}")
            print("="*30)
    else:
        print("\n[Error] 数据点不足（当前仅有 {} 组），至少需要 4 组。".format(len(camera_data_list)))

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()