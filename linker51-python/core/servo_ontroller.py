import config

class ServoController:
    def __init__(self, communicator):
        self.communicator = communicator
        self.x_max = config.SCREEN_WIDTH
        self.y_max = config.SCREEN_HEIGHT
        # 这是实际测出的安全区间
        self.min_pos = 5   # 对应舵机约 0 度
        self.max_pos = 22  # 对应舵机约 180 度 (安全上限)
        self.mid_pos = 13  # 对应舵机约 90 度

    def track_xy(self, x, y):
        # 根据 X 坐标更新舵机角度
        if x is None or y is None:
            return False

        # 计算映射比例 (x 轴 0~1536 映射到 5~22)：pos = min + (x / x_max) * (max - min)
        span = self.max_pos - self.min_pos
        pos_x = int(self.min_pos + (x / self.x_max) * span)
        pos_y = int(self.min_pos + (y / self.y_max) * span)

        # 安全限位
        pos_x = max(self.min_pos, min(self.max_pos, pos_x))
        pos_y = max(self.min_pos, min(self.max_pos, pos_y))

        print(f"[Servo] X:{x}->{pos_x}, Y:{y}->{pos_y}")

        # 按照单片机 state 顺序：[帧头, X值, Y值]
        packet = bytes([0xFE, pos_x, pos_y])
        return self.communicator.send_packet(packet)

    def stop(self):
        # 复位
        packet = bytes([0xFE, self.min_pos, self.min_pos])
        return self.communicator.send_packet(packet)