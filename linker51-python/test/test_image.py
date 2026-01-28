import cv2
import numpy as np
from core.vision_simulator import ImageProcessor

def test_single_image():
    img_path = "../assets/1.jpg"

    try:
        processor = ImageProcessor(img_path)
        box, frame = processor.get_target_corners()

        if box is not None:
            center_x = int(np.mean(box[:, 0]))
            center_y = int(np.mean(box[:, 1]))
            print(f"成功识别！中心坐标: ({center_x}, {center_y})")
            cv2.imshow("Detection Result", frame)
        else:
            print("未能在图中识别到黄球，请检查 HSV 阈值。")
            cv2.imshow("Failed Frame", frame)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    test_single_image()