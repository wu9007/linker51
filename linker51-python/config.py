# --- 基础设施配置 ---
# SERIAL_PORT = "COM4"
SERIAL_PORT = "/dev/tty.usbserial-1130"
BAUDRATE=9600

SCREEN_WIDTH=1536
SCREEN_HEIGHT=860

PACKET_HEAD=0xFE

# --- 机械臂物理尺寸 (单位: 米) ---
ARM_BASE_HEIGHT = 0.045
ARM_SHOULDER_OFFSET_Z = 0.12
ARM_UPPER_ARM_LEN = 0.055
ARM_FOREARM_LEN = 0.12

# --- 舵机底层映射基准 (由单片机定时器频率决定) ---
# 对应 0.5ms - 2.5ms 的 10us 计数值
PWM_MIN_BASE = 5   # 理论 0度
PWM_MAX_BASE = 25  # 理论 180度
PWM_SPAN = PWM_MAX_BASE - PWM_MIN_BASE

# --- 舵机安全限制 ---
SERVO_MIN_VAL = 6
SERVO_MAX_VAL = 24