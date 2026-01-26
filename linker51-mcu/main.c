#include "reg52.h"

typedef unsigned int u16;
typedef unsigned char u8;

sbit Servo_Pin = P1^1;

u8 count = 0;
u8 target = 5;
unsigned int i, j;

void timer0_init(){
	TMOD &=0xF0;
	TMOD |=0x01;
    TH0 = 0xFF; TL0 = 0xA4; // 0.1ms @ 11.0592MHz
    ET0 = 1; EA = 1; TR0 = 1;
}

void delay_ms(unsigned int ms) {
    for(i=0; i<ms; i++)
        for(j=0; j<120; j++);
}

void main() {
    timer0_init();

    while(1) {
        target = 5;  // 0
        delay_ms(1000);

        target = 13; // 90
        delay_ms(1000);

        target = 22; // 180
        delay_ms(1000);		
    }
}

void timer0_isr() interrupt 1 {
    TH0 = 0xFF;
    TL0 = 0xA4;

    if(count >= 200) {
        count = 0;
    }
    if(count < target){
        Servo_Pin = 1;
    }else {
        Servo_Pin = 0;
    }
}