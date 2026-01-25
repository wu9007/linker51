import config
import cv2
from core.communicator import Communicator
from core.vision_simulator import ImageProcessor
from core.motor_controller import MotorController

def main():
    # 初始化串口通信
    communicator = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    # 初始化电机逻辑控制器
    motor = MotorController(communicator)
    # 指定测试图片
    img_path = "assets/mid.png"
    processor = ImageProcessor(img_path)
    print(f"--- 正在分析测试图片: {img_path} ---")
    try:
        # 从图片获取“模拟”坐标
        x, y, frame = processor.get_target_center()
        # 可视化反馈（画个圈）
        cv2.circle(frame, (x, y), 20, (0, 255, 0), 2)
        cv2.imshow("Debug View", frame)
        if x is not None:
            success = motor.update_by_x(x)
            if success:
                print(" -> 发送成功。")
            else:
                print(" -> 发送失败。")
        cv2.waitKey(0)

        communicator.send_level(0)
    except KeyboardInterrupt:
        print("\n Ctr+C 手动停止。")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()