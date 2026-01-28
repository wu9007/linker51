import matplotlib.pyplot as plt
import numpy as np

def plot_arm(servo_controller, target_xyz, angles):
    plt.ioff()

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 绘制机械臂
    servo_controller.arm_chain.plot(angles, ax, target=target_xyz)

    # 设置坐标轴范围 (单位：米)
    limit = max(0.3, np.max(np.abs(target_xyz)) + 0.05)
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-0.05, limit)
    ax.set_zlim(0, limit)

    ax.set_xlabel('X (Left/Right)')
    ax.set_ylabel('Y (Forward/Back)')
    ax.set_zlabel('Z (Height)')
    plt.title(f"Arm Sim - Target: {np.around(target_xyz, 3)}")

    print("--- 模拟窗口已弹出，请查看 3D 姿态。关闭窗口后程序继续 ---")
    plt.show()