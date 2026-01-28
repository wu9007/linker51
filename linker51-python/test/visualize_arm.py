import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from core.servo_controller import ServoController

def visualize():
    # 模拟一个不发指令的控制器
    servo = ServoController(None)

    # 定义你想观察的角度 (Base, Shoulder, Elbow)
    # 比如：全部中位 (90度)
    test_angles = [0, np.pi/2, np.pi/2, np.pi/2, 0]

    # 创建 3D 图形
    fig, ax = plt.subplots(subplot_kw={'projection': '3d'})

    # 绘制机械臂
    # target 参数会在空间中画一个红点，方便对比末端是否指到了那里
    target_pos = [0, 0.1, 0.1]
    servo.arm_chain.plot(test_angles, ax, target=target_pos)

    # 设置坐标轴显示范围 (米)
    ax.set_xlim(-0.2, 0.2)
    ax.set_ylim(-0.2, 0.2)
    ax.set_zlim(0, 0.2)
    ax.set_xlabel('X (Side)')
    ax.set_ylabel('Y (Front)')
    ax.set_zlabel('Z (Height)')

    print("--- 3D 模拟窗口已开启，请检查机械臂姿态 ---")
    plt.show()

if __name__ == "__main__":
    visualize()