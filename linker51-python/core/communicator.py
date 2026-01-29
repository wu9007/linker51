import serial


class Communicator:
    def __init__(self, port, baudrate):
        """
        初始化串口通讯工具
        :param port: 端口
        :param baudrate: 频率
        """
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"--- 成功连接串口 {port} ---")
        except Exception as e:
            print(f"--- 串口连接失败: {e} ---")
            self.ser = None

    def send_level(self, level):
        """
        发送单个命令
        """
        if self.ser and self.ser.is_open:
            level = int(level)
            self.ser.write(bytes([level]))
            return True
        return False

    def send_packet(self, packet):
        """
        发送多个命令
        """
        if self.ser and self.ser.is_open:
            self.ser.write(packet)
            print(f"Sent Packet: {packet.hex().upper()}")
            return True
        return False
