import time
import config
from core.communicator import Communicator

def main():
    communicator = Communicator(config.BACKEND_SERVER_URL)
    test_coordinates = [
        (160, 240),  # 左侧
        (320, 240),  # 中间
        (480, 240),  # 右侧
        (640, 240),  # 极右
        (-1, -1),
    ]
    try:
        for x, y in test_coordinates:
            print(f"\n[发送] 原始坐标: x={x}, y={y}")
            success = communicator.send_coordinates(x, y)
            if success:
                print(" -> Java 端接收成功！")
            else:
                print(" -> 发送失败，请检查 Java 后端是否开启。")
            time.sleep(2)

        print("\n--- 测试序列执行完毕 ---")
    except KeyboardInterrupt:
        print("\n用户手动停止。")

if __name__ == "__main__":
    main()