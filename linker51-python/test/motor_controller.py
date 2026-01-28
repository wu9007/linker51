import config

class MotorController:
    def __init__(self, communicator):
        self.communicator = communicator
        self.x_max = config.SCREEN_WIDTH
        self.min_level = 5
        self.max_level = 25

    def update_by_x(self, x):
        # 根据 X 坐标更新电机转速
        if x is None:
            return False
        # 将坐标转换为 5-25 的等级：Level = 5 + (x / x_max) * 20
        level = self.min_level + int((x / self.x_max) * 20)
        # 安全限位
        level = max(self.min_level, min(self.max_level, level))

        print(f"[Motor] Mapping X:{x} -> Level:{level}")
        return self.communicator.send_level(level)

    def stop(self):
        # 停止电机
        return self.communicator.send_level(0)