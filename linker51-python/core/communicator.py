import serial

class Communicator:
    def __init__(self, port, baudrate):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"--- 成功连接串口 {port} ---")
        except Exception as e:
            print(f"--- 串口连接失败: {e} ---")
            self.ser = None

    def send_level(self, level):
        if self.ser and self.ser.is_open:
            level = int(level)
            self.ser.write(bytes([level]))
            return True
        return False