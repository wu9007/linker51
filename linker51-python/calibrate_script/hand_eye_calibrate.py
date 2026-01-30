import cv2
import numpy as np

import config
from core.ball_tracker import BallTracker
from core.communicator import Communicator
from core.servo_controller import ServoController


# 手眼标定（手动九点标定法）
def main():
    # 初始化硬件和视觉
    comm = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    servo = ServoController(comm)
    tracker = BallTracker("../calibrate_data/camera_params.npz", ball_radius=0.006)
    cap = cv2.VideoCapture(0)

    # 初始示教位置 (机械臂底座坐标)
    curr_rx, curr_ry, curr_rz = 0.15, 0.0, 0.10
    step = 0.005  # 每次移动 5mm

    camera_data_list = []
    robot_data_list = []

    print("--- 手眼标定采集工具 ---")
    print("方向键/WASD: 水平移动 | R/F: 上下移动 | S: 保存当前点 | Q: 退出并计算")

    while True:
        ret, frame = cap.read()
        if not ret: break

        found, cx, cy, cz, res_frame = tracker.get_ball_coords(frame)

        # 实时更新机械臂位置
        servo.track_target([curr_rx, curr_ry, curr_rz])

        cv2.imshow("Calibration", res_frame)
        key = cv2.waitKey(1) & 0xFF

        # --- 键盘控制逻辑 ---
        if key == ord('w'):
            curr_rx += step
        elif key == ord('s'):
            curr_rx -= step
        elif key == ord('a'):
            curr_ry -= step
        elif key == ord('d'):
            curr_ry += step
        elif key == ord('r'):
            curr_rz += step
        elif key == ord('f'):
            curr_rz -= step

        # --- 保存数据点 ---
        elif key == ord(' '):  # 空格键保存
            if found:
                camera_data_list.append([cx, cy, cz])
                robot_data_list.append([curr_rx, curr_ry, curr_rz])
                print(f"已保存第 {len(camera_data_list)} 组数据:")
                print(f"  相机: {[round(c, 3) for c in [cx, cy, cz]]}")
                print(f"  机械臂: {[round(r, 3) for r in [curr_rx, curr_ry, curr_rz]]}")
            else:
                print("错误：画面中未检测到目标，无法保存！")

        elif key == ord('q'):
            break

    # --- 计算标定矩阵 ---
    if len(camera_data_list) >= 4:
        c_pts = np.array(camera_data_list, dtype=np.float32)
        r_pts = np.array(robot_data_list, dtype=np.float32)
        retval, M, inliers = cv2.estimateAffine3D(c_pts, r_pts)
        if retval:
            np.save("../calibrate_data/hand_eye_matrix.npy", M)
            print("\n标定成功！矩阵已保存为 hand_eye_matrix.npy")
            print(M)
    else:
        print("\n数据不足，至少需要 4 组点。")

    cap.release()
    cv2.destroyAllWindows()
