import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# 在全局初始化交互模式
plt.ion()
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')


def plot_arm_animated(controller, target, angles, title="Robot Arm Tracking"):
    """标准动画刷新模式"""
    ax.clear()  # 清除上一帧内容

    # 使用 ikpy 自带的绘图功能或你自定义的逻辑
    controller.arm_chain.plot(angles, ax, target=target)

    # 设置固定的坐标轴范围，防止窗口晃动
    ax.set_xlim(-0.3, 0.3)
    ax.set_ylim(-0.1, 0.4)
    ax.set_zlim(0, 0.4)
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    plt.draw()  # 重新渲染画布
    plt.pause(0.001)  # 暂停极短时间让 GUI 线程处理渲染
