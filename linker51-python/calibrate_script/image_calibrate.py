import glob
import os

import cv2
import numpy as np

# 相机标定（10x7棋盘格）
# ----------------- 配置区 -----------------
# 棋盘格内角点数量 (横向点数, 纵向点数)
# 注意：是“内角点”，即格子交叉的地方。如果格子是 10x7，角点就是 9x6
CHECKERBOARD = (9, 6)
# 方格边长（单位：米。例如 25mm 填 0.025）
SQUARE_SIZE = 0.024
# 存放照片的文件夹路径
IMAGE_FOLDER = '../assets/calib_images'
# ------------------------------------------

# 准备 3D 目标点 (0,0,0), (1,0,0), (2,0,0) ... (7,4,0)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # 真实世界的 3D 点
imgpoints = []  # 图像平面的 2D 点

# 获取文件夹下所有图片
images = glob.glob(os.path.join(IMAGE_FOLDER, '*.jpeg'))

print(f"找到 {len(images)} 张图片，开始检测角点...")

found_count = 0
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 寻找角点
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)
        # 亚像素精确化，提高精度
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        found_count += 1
        # 可视化进度
        cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        cv2.imshow('Calibration Progress', cv2.resize(img, (800, 600)))
        cv2.waitKey(100)
    else:
        print(f"警告: 图片 {fname} 未能检测到角点，请检查是否模糊或光照不足。")

cv2.destroyAllWindows()

if found_count < 10:
    print(f"\n错误: 有效图片仅 {found_count} 张，建议至少准备 15 张有效图片再进行标定。")
else:
    print(f"\n正在计算内参... (有效图片数: {found_count})")
    # 核心计算
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    if ret:
        # 保存结果
        np.savez("../calibrate_data/camera_params.npz", mtx=mtx, dist=dist)
        print("\n" + "=" * 30)
        print("【标定成功！】")
        print("内参矩阵 (Camera Matrix):\n", mtx)
        print("\n畸变系数 (Dist Coefficients):\n", dist.flatten())
        print("=" * 30)
        print("\n结果已保存至 camera_params.npz")

        # 计算重投影误差（越小越准，通常应 < 0.5 像素）
        mean_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.norm_L2) / len(imgpoints2)
            mean_error += error
        print(f"平均重投影误差: {mean_error / len(objpoints):.4f} 像素")
