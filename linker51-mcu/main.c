#include "reg52.h"

typedef unsigned int u16;
typedef unsigned char u8;

sbit Servo_Pin_X = P1^1;
sbit Servo_Pin_Y = P1^2;

u8 count = 0;
u8 target_x = 5;
u8 target_y = 5;

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

    if(count < target_x){
        Servo_Pin_X = 1;
    }else {
        Servo_Pin_X = 0;
    }

    if(count < target_y){
        Servo_Pin_Y = 1;
    }else {
        Servo_Pin_Y = 0;
    }
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
		} else if(state == 1){
		    if (receive_data < 5) receive_data = 5;
            if (receive_data > 22) receive_data = 22;
		    target_x = receive_data;
		    state = 2;
		} else if(state == 2){
		    if (receive_data < 5) receive_data = 5;
            if (receive_data > 22) receive_data = 22;
		    target_y = receive_data;
		    state = 0;
		}

		SBUF = receive_data;
		while(!TI);
		TI=0;
	}
}