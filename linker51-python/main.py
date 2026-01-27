import config
import cv2
from core.communicator import Communicator
from core.vision_simulator import ImageProcessor
from core.servo_ontroller import ServoController

def main():
    # 初始化串口通信
    communicator = Communicator(config.SERIAL_PORT, config.BAUDRATE)
    # 初始化专门的舵机控制器
    servo = ServoController(communicator)
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
            success = servo.track_xy(x, y)
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