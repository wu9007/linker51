import cv2
import time
import numpy as np
import config
from core.ball_tracker import BallTracker
from core.communicator import Communicator
from core.servo_controller import ServoController

def run_service():
    # 1. 初始化硬件连接
    try:
        comm = Communicator(config.SERIAL_PORT, config.BAUDRATE)
        servo = ServoController(comm)
    except Exception as e:
        print(f"无法连接串口: {e}")
        return

    # 2. 初始化视觉追踪器
    # 请确保路径正确，ball_radius 单位为米 (0.006m = 6mm)
    tracker = BallTracker("../calibrate_data/camera_params.npz",
                          "../calibrate_data/hand_eye_matrix.npy",
                          ball_radius=0.006)

    # 3. 初始化摄像头 (针对 Mac 优化)
    # 使用 CAP_AVFOUNDATION 并设置较低的分辨率以减轻 CPU 负担
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("错误: 无法打开摄像头")
        return

    # 变量初始化
    last_logic_time = 0
    logic_interval = 0.15  # 限制机械臂动作频率约为 6-7 Hz，防止串口堵塞

    print("--- 视觉追踪服务已启动 ---")
    print("提示: 请确保小球在摄像头视野内，按 'Q' 键退出程序")

    try:
        while True:
            # A. 跳帧处理：清空缓冲区，只取最新的画面
            # 这一步能有效解决“动作延迟”问题
            for _ in range(2):
                cap.grab()
            ret, frame = cap.retrieve()

            if not ret:
                print("摄像头丢帧...")
                continue

            current_time = time.time()
            display_frame = frame.copy()

            # B. 频率控制逻辑
            # 只有达到时间间隔才进行昂贵的 CV 识别和 IK 计算
            if current_time - last_logic_time > logic_interval:
                found, cx, cy, cz, res_frame = tracker.get_ball_coords(frame)

                if found:
                    display_frame = res_frame # 使用画了圈的画面

                    # 坐标转换：相机 -> 机器人
                    robot_pos = tracker.camera_to_robot(cx, cy, cz)
                    rx, ry, rz = robot_pos

                    # C. 安全边界检查 (根据你的机械臂物理尺寸调整)
                    # 这里的 rx, ry 单位是米
                    if 0.08 < rx < 0.35 and -0.20 < ry < 0.20:
                        print(f"目标捕获 -> Robot XYZ: [{rx:.3f}, {ry:.3f}, {rz:.3f}]")
                        # 执行动作
                        servo.track_target([rx, ry, rz])
                    else:
                        cv2.putText(display_frame, "OUT OF RANGE", (20, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                last_logic_time = current_time

            # E. 给 CPU 留出物理休眠时间，防止 GIL 锁死
            # waitKey 是必须的，否则窗口不会刷新
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n用户手动停止程序")
    except Exception as e:
        print(f"\n程序运行中发生异常: {e}")
    finally:
        # 4. 资源释放
        print("正在关闭硬件并释放资源...")
        cap.release()
        cv2.destroyAllWindows()
        # 可以考虑在此处让机械臂复位到一个安全位置
        # servo.track_target([0.15, 0, 0.15])

if __name__ == "__main__":
    run_service()