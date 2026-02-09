import time

import serial

import config


def send_packet(ser, x_val, y_val, z_val):
    packet = bytes([config.PACKET_HEAD, x_val, y_val, z_val])
    ser.write(packet)
    print(f"发送指令: HEX -> {packet.hex().upper()} | X:{x_val} Y:{y_val}")

# 舵机角度校验
def main():
    try:
        ser = serial.Serial(config.SERIAL_PORT, config.BAUDRATE, timeout=1)
        print(f"已连接 {config.SERIAL_PORT}，开始校准...")
        time.sleep(2)  # 等待串口稳定

        send_packet(ser, 10, 10, 10)

        print("等待 2 秒观察动作...")
        time.sleep(2)

        send_packet(ser, 30, 30, 30)

        print("等待 2 秒观察动作...")
        time.sleep(2)

        send_packet(ser, 50, 50, 50)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("串口已关闭。")


if __name__ == "__main__":
    main()
