import cv2
import time
import sys
import config
import numpy as np
from core.visualizer import VisionVisualizer
from core.ball_pose_estimator import BallPoseEstimator
from core.communicator import Communicator
from core.servo_controller import ServoController

class RobotTrackingApp:
    def __init__(self):
        self.cap = None
        self.running = False

        # 频率控制参数
        self.last_logic_time = 0
        self.logic_interval = 0.03

        try:
            self.comm = Communicator(config.SERIAL_PORT, config.BAUDRATE)
            self.servo = ServoController(self.comm)
            self.visualizer = VisionVisualizer()

            self.estimator = BallPoseEstimator(
                params_path="calibrate_data/camera_params.npz",
                hand_eye_path="calibrate_data/hand_eye_matrix.npy",
                ball_radius=0.006
            )
        except Exception as e:
            print(f"[Fatal Error] 硬件初始化失败: {e}")
            sys.exit(1)

    def _setup_camera(self):
        # Mac 使用 CAP_AVFOUNDATION，其他系统可移除该参数
        self.cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

        if not self.cap.isOpened():
            raise IOError("无法打开摄像头设备")

        # 设置参数
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        for _ in range(10):
            self.cap.read()

    def run(self):
        try:
            self._setup_camera()
            print("--- 视觉追踪服务已启动 (按 'Q' 退出) ---")

            self.running = True
            while self.running:
                # 抓取最新帧 (防止缓冲区积压延迟)
                self._grab_latest_frame()
                ret, frame = self.cap.retrieve()

                if not ret:
                    print("[Warn] 摄像头丢帧")
                    continue

                found, p_cam, p_robot, processed_frame = self.estimator.get_robot_coords(frame)

                # 机械臂控制
                self._control_logic(found, p_robot)

                status_snapshot = {
                    'found': found,
                    'cam_pos': p_cam,
                    'robot_pos': p_robot,
                    'servo_angles': np.degrees(self.servo.current_angles[1:4]).astype(int),
                    'out_of_range': found and not (0.08 < p_robot[0] < 0.35), # 示例逻辑
                    'uv': getattr(self.estimator, 'last_uv', None)
                }
                self.visualizer.draw_dashboard(processed_frame, status_snapshot)

                cv2.imshow("Robot Vision", processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False

        except Exception as e:
            print(f"\n[Runtime Error] 运行中发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()

    def _grab_latest_frame(self):
        """清空缓冲区，只取最新"""
        for _ in range(2):
            if self.cap.isOpened():
                self.cap.grab()

    def _control_logic(self, found, p_robot):
        """
        负责判断是否发送指令给机械臂
        """
        current_time = time.time()
        # 频率控制 + 状态判断
        if found and (current_time - self.last_logic_time > self.logic_interval):
            rx, ry, rz = p_robot
            # 安全范围检查 (米)
            if 0.08 < rx < 0.35 and -0.20 < ry < 0.20:
                try:
                    self.servo.track_target([rx, ry, rz])
                except Exception as e:
                    print(f"[Servo Error] 指令发送失败: {e}")
            self.last_logic_time = current_time

    def _cleanup(self):
        """
        资源释放
        """
        print("\n[Exit] 正在停止服务...")
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        print("[Exit] 再见。")

if __name__ == "__main__":
    app = RobotTrackingApp()
    app.run()