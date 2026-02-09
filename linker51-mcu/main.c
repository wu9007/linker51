#include "reg52.h"

typedef unsigned int u16;
typedef unsigned char u8;

sbit Servo_Pin_X = P1^1;
sbit Servo_Pin_Y = P1^2;
sbit Servo_Pin_Z = P1^3;

u16 count = 0;
u16 target_x = 30;
u16 target_y = 30;
u16 target_z = 30;

void uart_init(u8 baud) {
    SCON = 0x50;
    TMOD |= 0x20;
    PCON=0x80;
    TH1 = baud; TL1 = baud;
    TR1 = 1; ES = 1; EA = 1;
}

void timer0_init(){
	TMOD &=0xF0;
	TMOD |=0x01;
	// 50us @ 11.0592MHz 初值 = 65536 - (50 * 11.0592 / 12) = 65490 (0xFFD2)
    TH0 = 0xFF; TL0 = 0xD2;
    ET0 = 1; EA = 1; TR0 = 1;
}

void main() {
	uart_init(0XFA);
    timer0_init();
    IP = 0x02;
    while(1) {
    }
}

void timer0_isr() interrupt 1 {
    TH0 = 0xFF;
    TL0 = 0xD2;

    count++;
    // 400 * 50us = 20ms 周期
    if(count >= 400) {
        count = 0;
    }

    Servo_Pin_X = (count < target_x);
    Servo_Pin_Y = (count < target_y);
    Servo_Pin_Z = (count < target_z);
}

void uart() interrupt 4 {
    static u8 state = 0;
    u8 dat;
    if(RI) {
        RI = 0;
        dat = SBUF;
        // 帧头检测
        if(dat == 0xFE) {
            state = 1;
            return;
        }
        if(dat < 10) dat = 10; if(dat > 50) dat = 50;
        if(state == 1) {
            target_x = dat; state = 2;
        } else if(state == 2) {
            target_y = dat; state = 3;
        } else if(state == 3) {
            target_z = dat; state = 0;
        }
    }
}