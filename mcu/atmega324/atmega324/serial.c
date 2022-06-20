/*
 * serial.c
 *
 * Created: 22/03/2018 8:07:52 PM
 *  
 */ 
#define FOSC 8000000UL 
#define BAUD 9600
#define UBRR FOSC/16/BAUD - 1

#include <avr/io.h>
#include "serial.h"

void serial_init(void) {
	unsigned int ubrr = UBRR;
	//Baud rate
	UBRR0H = (unsigned char) (ubrr >> 8);
	UBRR0L = (unsigned char) ubrr;
	
	// frame format : 8 data, 1 stop bit
	UCSR0B = (1<<RXEN0) | (1<<TXEN0);
	UCSR0C = (3<<UCSZ00);
}

void serial_send_char(unsigned char data) {
	//wait till transmit buffer empty
	while (!(UCSR0A & (1<<UDRE0))) 
		;
	//put data in
	UDR0 = data;
}

unsigned char USART_Receive( void )
{
	/* Wait for data to be received */
	//while ( !(UCSR0A & (1<<RXC)) )
	//;
	/* Get and return received data from buffer */
	return UDR0;
}

void serial_send_gyro_vals(short* vals) {
	uint8_t* sendVals = (uint8_t*) vals;
	serial_send_char('r');
	serial_send_char(sendVals[0]);
	serial_send_char(sendVals[1]);
	serial_send_char(sendVals[2]);
	serial_send_char(sendVals[3]);
	serial_send_char(sendVals[4]);
	serial_send_char(sendVals[5]);
	serial_send_char('\n');
}

void send_float(float value) {
	uint32_t* val = (uint32_t*) &value;
	serial_send_char((*val >> 0));
	serial_send_char((*val >> 8));
	serial_send_char((*val >> 16));
	serial_send_char((*val >> 24));
	
}

void serial_send_float_angles(float* angles) {
	serial_send_char('f');
	for (int i = 0; i < 3; i++) {
		send_float(angles[i]);
	}
	serial_send_char('\n');	
}

void serial_send_both(float* angles, float* vals) {
	serial_send_char('b');
	for (int i = 0; i < 3; i++) {
		send_float(angles[i]);
	}
	for (int i = 0; i < 3; i++) {
		send_float(vals[i]);
	}
	serial_send_char('\n');
}

void serial_send_uint8(int data) {
	serial_send_char('i');
	serial_send_char((unsigned char) data);
	serial_send_char('\n');
}