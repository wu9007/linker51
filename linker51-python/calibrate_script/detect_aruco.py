import cv2
import numpy as np


# ArUco码 3D 坐标检测测试
def main():
    # 码实际边长（米）：这是计算绝对距离的“一把尺子”，必须准确
    MARKER_SIZE = 0.04

    # 1. 初始化检测器
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    # 2. 加载相机内参 (决定了如何将像素点映射到 3D 空间)
    try:
        data = np.load("camera_params.npz")
        mtx = data['mtx']  # 内参矩阵：包含焦距 fx, fy 和中心点 cx, cy
        dist = data['dist']  # 畸变参数：修正镜头边缘的弯曲
        print("成功加载相机内参！")
    except:
        print("错误：找不到 camera_params.npz，请先运行标定脚本。")
        return

    # 3. 定义 ArUco 码在“码坐标系”下的四个角点坐标
    # 坐标系原点位于码中心，Z轴垂直于码向上
    obj_points = np.array([
        [-MARKER_SIZE / 2, MARKER_SIZE / 2, 0],  # 左上
        [MARKER_SIZE / 2, MARKER_SIZE / 2, 0],  # 右上
        [MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],  # 右下
        [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0]  # 左下
    ], dtype=np.float32)

    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    while True:
        ret, frame = cap.read()
        if not ret: break

        # 4. 检测图像中的码，返回角点的像素坐标 corners
        corners, ids, rejected = detector.detectMarkers(frame)

        if ids is not None:
            # 视觉反馈：在画面中画出检测到的绿色边框
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for i in range(len(ids)):
                # 5. PnP 算法核心 (Perspective-n-Point)
                # 作用：已知 3D 点 (obj_points) 和对应的像素点 (corners)，反推物体在相机前的位姿
                # rvec: 旋转向量（表示物体的姿态）
                # tvec: 平移向量（表示物体中心相对于相机光心的 X, Y, Z 距离）
                ret_pnp, rvec, tvec = cv2.solvePnP(obj_points, corners[i], mtx, dist)

                if ret_pnp:
                    # tvec 展平后得到 (x, y, z)，单位是米
                    x, y, z = tvec.flatten()

                    # 在码中心画出 3D 坐标轴 (红色X, 绿色Y, 蓝色Z)
                    cv2.drawFrameAxes(frame, mtx, dist, rvec, tvec, 0.05)

                    # 可视化距离信息：转化为厘米显示
                    text = f"X:{x * 100:.1f} Y:{y * 100:.1f} Z:{z * 100:.1f} cm"
                    pixel_pos = (int(corners[i][0][0][0]), int(corners[i][0][0][1]) - 10)
                    cv2.putText(frame, text, pixel_pos,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # 打印结果：用于下一步手眼标定的 Camera Point 数据
                    print(f"ID: {ids[i][0]} | 距离相机: X={x:.3f}m, Y={y:.3f}m, Z={z:.3f}m")

        cv2.imshow('ArUco 3D Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
