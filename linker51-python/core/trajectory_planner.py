import math

class CriticalDampingFilter:
    """
    临界阻尼滤波器

    用途：将跳跃的视觉坐标转化为平滑的机械臂运动指令。
    核心逻辑：
    1. 启动时：通过“第一帧对齐”避免暴冲。
    2. 运行中：模拟物理弹簧阻尼系统，实现无震荡追踪。
    """
    def __init__(self, f_n=2.0, dt=0.03):
        self.omega_n = 2.0 * math.pi * f_n
        self.dt = dt
        self.cur_pos = None
        self.vel = 0.0

    def update(self, target):
        """
        输入：原始目标位置 (Target)
        输出：平滑后的指令位置 (Output)
        """
        # --- 第一步：初始化对齐 (解决“拨钟”问题) ---
        # 如果是第一次接收数据，直接对齐目标，跳过本帧的平滑计算
        # 这样大范围的“首跳”交给舵机硬件去跑，避免算法计算出恐怖的加速度
        if self.cur_pos is None:
            self.cur_pos = target
            return target

        # 核心公式：计算加速度 (弹簧力 - 阻尼力)
        acc = (self.omega_n**2) * (target - self.cur_pos) - (2.0 * self.omega_n * self.vel)

        # 欧拉积分：更新速度和位置
        self.vel += acc * self.dt
        self.cur_pos += self.vel * self.dt

        return self.cur_pos