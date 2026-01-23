import config
import cv2
from core.communicator import Communicator
from core.vision_simulator import ImageProcessor

def main():
    communicator = Communicator(config.BACKEND_SERVER_URL)
    # 指定测试图片
    img_path = "assets/mid.png"
    processor = ImageProcessor(img_path)
    print(f"--- 正在分析测试图片: {img_path} ---")
    try:
        # 从图片获取“模拟”坐标
        x, y, frame = processor.get_target_center()
        if x is not None:
            print(f"\n[发送] 原始坐标: x={x}, y={y}")
            success = communicator.send_coordinates(x, y)
            if success:
                # 可视化反馈（画个圈）
                cv2.circle(frame, (x, y), 20, (0, 255, 0), 2)
                cv2.imshow("Debug View", frame)
            else:
                print(" -> 发送失败。")
        cv2.waitKey(0)

        communicator.send_coordinates(0, 0)
    except KeyboardInterrupt:
        print("\n Ctr+C 手动停止。")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()