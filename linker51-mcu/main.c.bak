#include "reg52.h"

typedef unsigned int u16;
typedef unsigned char u8;

sbit DC_Motor = P1^0;

u8 timer_count = 0;
u8 compare_value = 0;

void uart_init(u8 baud){
	TMOD|=0x20;
	SCON=0x50;
	PCON=0x80;
	TH1=baud;
	TL1=baud;
	ES=1;
	EA=1;
	TR1=1;
}

void timer0_init(){
	TMOD &=0xF0;
	TMOD |=0x01;
	TH0 = 0xFC;   
    TL0 = 0x66;
	ET0 = 1;
    EA = 1;
    TR0 = 1;
}

void main(){
	DC_Motor = 0;	 
	uart_init(0XFA);
	timer0_init();
	while(1){
	}
}

void timer0_isr() interrupt 1{
	TH0 = 0xFC;
    TL0 = 0x66;
	timer_count++; 
    if(timer_count >= 20) {
        timer_count = 0;
    }
    // PWM
	if(timer_count < compare_value){
		DC_Motor = 1;
	}else {
        DC_Motor = 0;
    }
}

void uart() interrupt 4{
	if(RI){
		RI = 0;	 
		compare_value = SBUF;

        if(compare_value > 20){
			compare_value = 20;
		}

		SBUF = compare_value;
		while(!TI);
		TI=0;
	}
}