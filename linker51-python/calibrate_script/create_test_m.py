import numpy as np
import os

# 确保文件夹存在
path = "../calibrate_data"
if not os.path.exists(path):
    os.makedirs(path)

# 构造模拟矩阵 (3x4)
M_test = np.array([
    [1.0, 0.0, 0.0, 0.10],
    [0.0, 1.0, 0.0, 0.05],
    [0.0, 0.0, 1.0, 0.35]
], dtype=np.float32)

# 保存文件
np.save(os.path.join(path, "hand_eye_matrix.npy"), M_test)
print("测试矩阵已生成在: ../calibrate_data/hand_eye_matrix.npy")