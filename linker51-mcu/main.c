#include "reg52.h"

typedef unsigned char u8;

sbit Servo_Pin = P1^1; // 舵机信号线接 P1.1

u8 timer_count = 0;    // 0.1ms 计数器 (数到 200 就是 20ms)
u8 compare_value = 15; // PWM 比较值 (5=0.5ms, 15=1.5ms, 25=2.5ms)

/**
 * 串口初始化 (9600波特率 @ 11.0592MHz)
 */
void uart_init() {
    SCON = 0x50;  // 8位数据, 可接收
    TMOD |= 0x20; // 定时器1：方式2 (8位自动重装)用于波特率
    TH1 = 0xFA;   // 9600 波特率
    TL1 = 0xFA;
    PCON = 0x80;  // 波特率倍增
    ES = 1;       // 开启串口中断
    TR1 = 1;      // 启动定时器1
}

/**
 * 定时器0初始化 (产生高精度 PWM)
 */
void timer0_init() {
    TMOD &= 0xF0; // 设置定时器0：方式1 (16位)
    TMOD |= 0x01;
    TH0 = 0xFF;   // 0.1ms 初始值 (11.0592MHz 晶振)
    TL0 = 0xA4;
    ET0 = 1;      // 开启定时器0中断
    EA = 1;       // 开启总中断
    TR0 = 1;      // 启动定时器0
}

void main() {
    Servo_Pin = 0;
    uart_init();
    timer0_init();

    while(1) {
        // 主循环什么都不用写，全靠中断办事
    }
}

/**
 * 定时器0中断：每 0.1ms 进来一次
 * 负责挥动 P1.1 引脚，产生 50Hz 的舵机信号
 */
void timer0_isr() interrupt 1 {
    TH0 = 0xFF; // 重新装载 0.1ms 初始值
    TL0 = 0xA4;

    timer_count++;

    // 一个周期是 20ms (200 * 0.1ms)
    if (timer_count >= 200) {
        timer_count = 0;
    }

    // 产生舵机脉宽 (0.5ms ~ 2.5ms)
    if (timer_count < compare_value) {
        Servo_Pin = 1;
    } else {
        Servo_Pin = 0;
    }
}

/**
 * 串口中断：Python 发个数字过来，舵机就动一下
 */
void uart_isr() interrupt 4 {
    if (RI) {
        RI = 0;
        compare_value = SBUF; // 接收指令

        // --- 舵机保护：只允许 5 到 25 之间的数值 ---
        if (compare_value < 5)  compare_value = 5;  // 0度
        if (compare_value > 25) compare_value = 25; // 180度

        // 回传给电脑，方便在 Python 终端看到当前数值
        SBUF = compare_value;
        while (!TI);
        TI = 0;
    }
}