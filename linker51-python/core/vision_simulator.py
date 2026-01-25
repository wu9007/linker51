import cv2
import os

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"找不到测试图片: {image_path}")

    def get_target_center(self):
        frame = cv2.imread(self.image_path)
        if frame is None:
            return None, None, None

        print(f"图片维度: {frame.shape} | 数据类型: {frame.dtype}")

        h, w, _ = frame.shape

        # 转换颜色空间到 HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 把图像中所有符合红色的区域变白，不符合的变黑
        lower_red = (170, 70, 70)
        upper_red = (180, 255, 255)
        mask = cv2.inRange(hsv, lower_red, upper_red)
        cv2.imshow("Mask View", mask)

        # 它在刚才的黑白图中“描边”
        # RETR_EXTERNAL：只找最外层的轮廓，不管物体里面的孔洞。
        # CHAIN_APPROX_SIMPLE：把弯曲的边压缩成几个点，节省内存。
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            # 给目标物体外面套上一个矩形（x, y 是盒子的左上角坐标，w_box, h_box 是盒子的宽和高）
            (x, y, w_box, h_box) = cv2.boundingRect(c)
            # 左上角加上一半的宽度，就是物体的中心点 x。这个 x 就是最后传给 Java 用来算 level 的那个值。
            center_x = x + (w_box // 2)
            center_y = y + (h_box // 2)
            return center_x, center_y, frame

        # 如果没找到，返回画面中心点作为保底
        return w // 2, h // 2, frame