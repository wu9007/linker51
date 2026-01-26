import config

class ServoController:
    def __init__(self, communicator):
        self.communicator = communicator
        self.x_max = config.SCREEN_WIDTH
        # 这是实际测出的安全区间
        self.min_pos = 5   # 对应舵机约 0 度
        self.max_pos = 22  # 对应舵机约 180 度 (安全上限)
        self.mid_pos = 13  # 对应舵机约 90 度

    def track_x(self, x):
        # 根据 X 坐标更新舵机角度
        if x is None:
            return False

        # 计算映射比例 (x 轴 0~1536 映射到 5~22)：pos = min + (x / x_max) * (max - min)
        span = self.max_pos - self.min_pos
        pos = self.min_pos + (x / self.x_max) * span

        # 安全限位
        pos_cmd = int(round(pos))
        pos_cmd = max(self.min_pos, min(self.max_pos, pos_cmd))

        print(f"[Servo] Mapping X:{x} -> POS:{pos_cmd}")

        return self.communicator.send_level(pos_cmd)

    def stop(self):
        # 复位
        return self.communicator.send_level(self.min_pos)