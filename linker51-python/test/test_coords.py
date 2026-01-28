import cv2
import numpy as np
import os

class VisionTester:
    def __init__(self, camera_matrix, dist_coeffs, obj_points):
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.obj_points = obj_points

    def debug_image(self, image_path):
        frame = cv2.imread(image_path)
        if frame is None:
            print("图片加载失败")
            return

        # 这里的逻辑复用你之前的 ImageProcessor 识别部分
        # 假设我们已经拿到了 corners_2d
        from core.vision_simulator import ImageProcessor
        processor = ImageProcessor(image_path)
        corners_2d, _ = processor.get_target_corners()

        h, w = frame.shape[:2]
        # 在画面中心画一个十字，代表相机坐标系的 (0,0)
        cv2.line(frame, (int(w/2), 0), (int(w/2), h), (255, 0, 0), 1) # 蓝色垂直线
        cv2.line(frame, (0, int(h/2)), (w, int(h/2)), (255, 0, 0), 1) # 蓝色水平线

        if corners_2d is not None:
            # 1. PnP 计算
            _, rvec, tvec = cv2.solvePnP(self.obj_points, corners_2d, self.camera_matrix, self.dist_coeffs)
            rel_x, rel_y, rel_z = tvec.flatten()

            # 2. 在图片上显示坐标数值
            text = f"Cam Rel: X:{rel_x:.3f} Y:{rel_y:.3f} Z:{rel_z:.3f}"
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # 3. 绘制 3D 轴（非常重要：显示相机认为的 XYZ 方向）
            # 蓝色=Z(深), 绿色=Y(下), 红色=X(右)
            axis_points = np.float32([[0.05,0,0], [0,0.05,0], [0,0,0.05], [0,0,0]]).reshape(-1, 3)
            imgpts, _ = cv2.projectPoints(axis_points, rvec, tvec, self.camera_matrix, self.dist_coeffs)
            imgpts = imgpts.astype(int)

            origin = tuple(imgpts[3].ravel())
            frame = cv2.line(frame, origin, tuple(imgpts[0].ravel()), (0,0,255), 5) # X
            frame = cv2.line(frame, origin, tuple(imgpts[1].ravel()), (0,255,0), 5) # Y
            frame = cv2.line(frame, origin, tuple(imgpts[2].ravel()), (255,0,0), 5) # Z

            print(f"--- 坐标分析 ({os.path.basename(image_path)}) ---")
            print(f"1. 如果球在画面中心右侧，rel_x 应为正: {rel_x:.3f}")
            print(f"2. 如果球在画面中心下方，rel_y 应为正: {rel_y:.3f}")
            print(f"3. rel_z 是相机到球的直线距离: {rel_z:.3f}")

        cv2.imshow("Coordinate Test", frame)
        cv2.waitKey(0)

# --- 运行测试 ---
if __name__ == "__main__":
    # 使用你代码里的参数
    w, h = 1280, 1707
    f = 1080
    c_matrix = np.array([[f, 0, w/2], [0, f, h/2], [0, 0, 1]], dtype=np.float32)
    d_coeffs = np.zeros((4, 1))
    # 设定一个准确的半径，比如 1.5cm
    r = 0.015
    o_points = np.array([[-r,-r,0], [r,-r,0], [r,r,0], [-r,r,0]], dtype=np.float32)

    tester = VisionTester(c_matrix, d_coeffs, o_points)
    tester.debug_image("../assets/1.png")