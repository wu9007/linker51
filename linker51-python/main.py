import cv2
import time
import sys
import config
from core.visualizer import ArmVisualizer
from core.ball_pose_estimator import BallPoseEstimator
from core.communicator import Communicator
from core.servo_controller import ServoController

class RobotTrackingApp:
    def __init__(self):
        self.cap = None
        self.running = False

        # 频率控制参数
        self.last_logic_time = 0
        self.logic_interval = 0.15

        try:
            self.comm = Communicator(config.SERIAL_PORT, config.BAUDRATE)
            self.servo = ServoController(self.comm)

            self.estimator = BallPoseEstimator(
                params_path="calibrate_data/camera_params.npz",
                hand_eye_path="calibrate_data/hand_eye_matrix.npy",
                ball_radius=0.006
            )
        except Exception as e:
            print(f"[Fatal Error] 硬件初始化失败: {e}")
            sys.exit(1)

        # 可视化开关
        self.enable_viz = True
        self.visualizer = None
        # 如果开启可视化，并且机械臂已经初始化，则创建可视化器
        if self.enable_viz and hasattr(self, 'servo'):
            self.visualizer = ArmVisualizer(self.servo.arm_chain)

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

                found, robot_pos, processed_frame = self.estimator.get_robot_coords(frame)

                # 机械臂控制
                self._control_logic(found, robot_pos, processed_frame)

                # 显示
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

    def _control_logic(self, found, robot_pos, processed_frame):
        current_time = time.time()

        if not found:
            cv2.putText(processed_frame, "Searching...", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            return

        # 如果找到了，检查时间间隔
        if current_time - self.last_logic_time > self.logic_interval:
            rx, ry, rz = robot_pos

            # 安全范围检查
            if 0.08 < rx < 0.35 and -0.20 < ry < 0.20:
                print(f"Tracking -> XYZ: [{rx:.3f}, {ry:.3f}, {rz:.3f}]")
                try:
                    for step_angles in self.servo.track_target([rx, ry, rz]):
                        if self.visualizer:
                            self.visualizer.update(step_angles, target_xyz=robot_pos)
                        # 保持 OpenCV 窗口活跃
                        cv2.waitKey(1)
                except Exception as e:
                    print(f"[Servo Error] 指令发送失败: {e}")
            else:
                cv2.putText(processed_frame, "OUT OF RANGE", (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            self.last_logic_time = current_time

    def _cleanup(self):
        """
        资源释放
        """
        print("\n[Exit] 正在停止服务...")
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        if self.visualizer:
            self.visualizer.close()
        print("[Exit] 再见。")

if __name__ == "__main__":
    app = RobotTrackingApp()
    app.run()