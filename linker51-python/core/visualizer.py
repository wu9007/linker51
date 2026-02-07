import cv2

class VisionVisualizer:
    def __init__(self):
        # 定义颜色常量
        self.COLOR_BG = (20, 20, 20)      # 深灰色背景
        self.COLOR_TEXT = (255, 255, 255) # 白色文字
        self.COLOR_ACCENT = (0, 255, 255) # 黄色高亮 (Robot系)
        self.COLOR_SERVO = (150, 255, 150)# 浅绿色 (舵机)
        self.COLOR_WARN = (0, 0, 255)     # 红色 (警告)

    def draw_dashboard(self, frame, status_data):
        """
        绘制主仪表盘
        :param frame: 原始图像帧
        :param status_data: 包含所有状态的字典
        """
        # 绘制左侧半透明遮罩面板
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (285, 200), self.COLOR_BG, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # 绘制运行状态 (STATUS)
        found = status_data.get('found', False)
        status_text = "TRACKING" if found else "SEARCHING..."
        status_col = (0, 255, 0) if found else (0, 165, 255)
        cv2.putText(frame, f"STATUS: {status_text}", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_col, 2)

        # 绘制坐标信息
        self._draw_coords(frame, status_data)

        # 绘制舵机信息
        self._draw_servos(frame, status_data.get('servo_angles', [0,0,0]))

        # 绘制安全警报
        if status_data.get('out_of_range', False):
            cv2.putText(frame, "!! OUT OF REACH !!", (15, 185),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_WARN, 2)

        # 绘制目标标记 (在图像中画圆和准心)
        uv_data = status_data.get('uv')
        if found and uv_data is not None:
            u, v, r = status_data['uv']
            cv2.circle(frame, (u, v), r, self.COLOR_ACCENT, 2)
            cv2.drawMarker(frame, (u, v), self.COLOR_ACCENT, cv2.MARKER_CROSS, 10, 1)

    def _draw_coords(self, frame, data):
        cp = data.get('cam_pos')
        if cp is None: cp = (0.0, 0.0, 0.0)

        rp = data.get('robot_pos')
        if rp is None: rp = (0.0, 0.0, 0.0)

        # 相机系显示
        cv2.putText(frame, "CAM Frame (Lens):", (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
        cv2.putText(frame, f"X:{cp[0]:>5.3f} Y:{cp[1]:>5.3f} Z:{cp[2]:>5.3f}m", (15, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_TEXT, 1)

        # 机器人系显示
        cv2.putText(frame, "ROBOT Frame (Base):", (15, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
        cv2.putText(frame, f"X:{rp[0]:>5.3f} Y:{rp[1]:>5.3f} Z:{rp[2]:>5.3f}m", (15, 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_ACCENT, 1)

    def _draw_servos(self, frame, angles):
        cv2.putText(frame, "SERVO Angles (B, S, E):", (15, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
        cv2.putText(frame, f"Degs: {angles[0]}, {angles[1]}, {angles[2]}", (15, 155),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_SERVO, 1)