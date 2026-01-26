#include "reg52.h"

typedef unsigned int u16;
typedef unsigned char u8;

sbit Servo_Pin = P1^1;

u8 count = 0;
u8 target_pos = 5;

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
    TH0 = 0xFF; TL0 = 0xA4; // 0.1ms @ 11.0592MHz
    ET0 = 1; EA = 1; TR0 = 1;
}

void main() {
	uart_init(0XFA);
    timer0_init();

    while(1) {		
    }
}

void timer0_isr() interrupt 1 {
    TH0 = 0xFF;
    TL0 = 0xA4;

    count++;
    if(count >= 200) {
        count = 0;
    }
    if(count < target_pos){
        Servo_Pin = 1;
    }else {
        Servo_Pin = 0;
    }
}

void uart() interrupt 4{
	if(RI){
		RI = 0;
		target_pos = SBUF;

        if (target_pos < 5) target_pos = 5;
        if (target_pos > 22) target_pos = 22;

		SBUF = target_pos;
		while(!TI);
		TI=0;
	}
}