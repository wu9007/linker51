#include "reg52.h"

typedef unsigned int u16;
typedef unsigned char u8;

sbit DC_Motor = P1^0;

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

void main(){
	DC_Motor = 0;	 
	uart_init(0XFA);
	while(1){
	}
}

void uart() interrupt 4{
	u8 rec_data;
	if(RI){
		RI = 0;	 
		rec_data=SBUF;
		if(rec_data == '1'){
			DC_Motor = 1;
		} else if(rec_data == '0'){
			DC_Motor = 0;
		}
		SBUF = rec_data;
		while(!TI);
		TI=0;
	}
}