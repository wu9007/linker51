#include "reg52.h"

typedef unsigned int u16;
typedef unsigned char u8;

sbit Servo_Pin_X = P1^1;
sbit Servo_Pin_Y = P1^2;
sbit Servo_Pin_Z = P1^3;

u16 count = 0;
u16 target_x = 150;
u16 target_y = 150;
u16 target_z = 150;

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
    TH0 = 0xFF; TL0 = 0xF6; // 0.01ms @ 11.0592MHz
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
    TL0 = 0xF6;

    count++;
    if(count >= 2000) {
        count = 0;
    }

    Servo_Pin_X = (count < target_x) ? 1 : 0;
    Servo_Pin_Y = (count < target_y) ? 1 : 0;
    Servo_Pin_Z = (count < target_z) ? 1 : 0;
}

void uart() interrupt 4{
    static u8 state = 0;
    u8 receive_data;
	if(RI){
		RI = 0;
		receive_data = SBUF;

		if(state == 0){
		    if(receive_data == 0xFE){
		        state = 1;
		    }
		} else {
		    // 此时 receive_data 由 Python 发送，范围应在 60-240
            if (receive_data < 60) receive_data = 60;
            if (receive_data > 240) receive_data = 240;
            if(state == 1){
                target_x = receive_data;
                state = 2;
            } else if(state == 2){
                target_y = receive_data;
                state = 3;
            } else if(state == 3){
                target_z = receive_data;
                state = 0;
            }
		}
	}
}