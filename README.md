# Linker51 - 视觉反馈电机控制系统
本系统通过 Python (OpenCV) 识别红色目标坐标，经由 串口 (UART) 实时控制 51单片机 输出 PWM 信号，从而调节电机转速或舵机角度。

## 📂 项目结构
- linker51-python/: Python 视觉中心（识别坐标、指令下发）。
- linker51-mcu/: 51单片机程序（串口接收、PWM 驱动）。

## 🛠 硬件环境
- 开发板: 普中 A2 (STC89C52RC)。 
- 电机: 直流电机（接 P1.0 引脚）。 
- 通信: USB 转 TTL (CH340)，识别为 COM4，波特率 9600。

## 🖥 快速开始
### 1. 环境安装
确保安装了 Python 3.x，在 linker51-python 目录下运行：
```shell
pip install -r requirements.txt
```

### 2. 烧录固件
使用 STC-ISP 将 linker51-mcu 编译生成的 .hex 文件下载至单片机。
> 注意：下载完成后务必关闭 STC-ISP，释放串口。

### 3. 启动程序
```shell
python main.py
```

## 🕹 核心逻辑识别: 
1. OpenCV 提取红色物体的 $x$ 像素坐标。
2. 映射: 将坐标线性换算为 PWM 等级（$5 \sim 25$）。
3. 执行: Python 发送单字节指令，单片机实时改变 P1.0 引脚的占空比。