import matplotlib.pyplot as plt
import numpy as np

def plot_arm(servo_controller, target_xyz, angles):
    """
    在3D空间绘制机械臂姿态和目标点
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 绘制机械臂
    servo_controller.arm_chain.plot(angles, ax, target=target_xyz)

    # 设置坐标轴范围 (单位：米)
    # 手臂总长约 0.15m，所以设置到 0.25m 左右比较合适
    limit = 0.25
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-0.05, limit + 0.05)
    ax.set_zlim(0, limit)

    ax.set_xlabel('X (Left/Right)')
    ax.set_ylabel('Y (Forward/Back)')
    ax.set_zlabel('Z (Height)')
    plt.title(f"Arm Sim - Target: {np.around(target_xyz, 3)}")

    print("--- 模拟窗口已弹出，请查看 3D 姿态。关闭窗口后程序继续 ---")
    plt.show()