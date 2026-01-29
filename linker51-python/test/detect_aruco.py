import cv2
import numpy as np

def main():
    # --- 1. 配置参数 ---
    MARKER_SIZE = 0.04  # 码的实际边长（米）

    # 【新版写法】：初始化字典、参数和检测器对象
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    # --- 2. 加载标定得到的内参 ---
    try:
        data = np.load("camera_params.npz")
        mtx = data['mtx']
        dist = data['dist']
        print("成功加载相机内参！")
    except:
        print("错误：找不到 camera_params.npz，请先运行标定脚本。")
        return

    # --- 3. 启动相机 ---
    # MacBook 建议尝试 0 或 1，加上 cv2.CAP_AVFOUNDATION 更稳定
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    # 定义 3D 坐标参考点 (用于 solvePnP)
    # 这定义了码在它自己局部坐标系里的四个角
    obj_points = np.array([
        [-MARKER_SIZE / 2,  MARKER_SIZE / 2, 0],
        [ MARKER_SIZE / 2,  MARKER_SIZE / 2, 0],
        [ MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
        [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0]
    ], dtype=np.float32)

    while True:
        ret, frame = cap.read()
        if not ret: break

        # 【新版写法】：使用 detector.detectMarkers
        corners, ids, rejected = detector.detectMarkers(frame)

        if ids is not None:
            # 绘制边框
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for i in range(len(ids)):
                # 【新版推荐写法】：使用 solvePnP 替代已弃用的 estimatePoseSingleMarkers
                # 这种方法更精确，且不依赖于具体的 opencv-contrib 版本
                ret_pnp, rvec, tvec = cv2.solvePnP(obj_points, corners[i], mtx, dist)

                if ret_pnp:
                    # 提取坐标 (单位：米)
                    # solvePnP 返回的 tvec 是 (3, 1) 形状
                    x, y, z = tvec.flatten()

                    # 绘制坐标轴 (红:X, 绿:Y, 蓝:Z)
                    cv2.drawFrameAxes(frame, mtx, dist, rvec, tvec, 0.05)

                    # 在屏幕上打印距离信息
                    text = f"X:{x*100:.1f} Y:{y*100:.1f} Z:{z*100:.1f} cm"
                    # 坐标定位到码的左上角
                    pixel_pos = (int(corners[i][0][0][0]), int(corners[i][0][0][1])-10)
                    cv2.putText(frame, text, pixel_pos,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # 控制台输出
                    print(f"ID: {ids[i][0]} | 距离相机: X={x:.3f}m, Y={y:.3f}m, Z={z:.3f}m")

        cv2.imshow('ArUco 3D Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()