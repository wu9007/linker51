import matplotlib
try:
    matplotlib.use('TkAgg')
except:
    pass

import matplotlib.pyplot as plt
from ikpy.chain import Chain

class ArmVisualizer:
    def __init__(self, arm_chain: Chain):
        """
        初始化可视化器
        :param arm_chain: 机械臂的 IKPy Chain 对象（用于正运动学计算绘图）
        """
        self.chain = arm_chain

        # 开启交互模式，允许动态刷新
        plt.ion()

        # 创建画布和3D坐标系
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # 窗口标题
        self.fig.canvas.manager.set_window_title("Robot Arm Tracking Visualization")

    def update(self, angles, target_xyz=None):
        """
        刷新一帧画面
        :param angles: 当前各关节角度
        :param target_xyz: 目标点坐标 (x, y, z)，可选
        """
        # 清除上一帧
        self.ax.clear()

        # 调用 ikpy 绘制机械臂姿态
        self.chain.plot(angles, self.ax, target=target_xyz)

        # 每次清除后必须重新设置坐标轴范围，否则画面会随着机械臂移动忽大忽小，看着很晕
        self.ax.set_xlim(-0.3, 0.3)
        self.ax.set_ylim(-0.3, 0.3) # 稍微调整了视野，你可以改回 (-0.1, 0.4)
        self.ax.set_zlim(0, 0.4)

        # 设置标签
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_zlabel("Z (m)")
        self.ax.set_title(f"Target: {target_xyz}" if target_xyz else "Robot Arm")

        # 刷新画布
        plt.draw()
        plt.pause(0.001) # 暂停极短时间让 GUI 线程处理渲染

    def close(self):
        """关闭窗口资源"""
        plt.ioff()
        plt.close(self.fig)