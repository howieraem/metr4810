/*
 * serial.c
 *
 * Created: 26/04/2018 3:44:41 PM
 *  
 */ 

#include "config.h"

#include <stdio.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdarg.h>
#include "serial.h"
#include "matrix.h"
#include "debug_led.h"

#define MAX_MESSAGE_LENGTH 10

#define FOSC F_CPU
#define BAUD 9600
#define UBRR FOSC/16/BAUD - 1

#define RXD0 PINE0
#define TXD0 PINE1



unsigned char serialBuffer[100];
uint8_t currentPos = 0;
uint8_t waitingForStx = 1;
int8_t messageLength = 0;

SerialMessage lastMessage;

uint8_t serialMessageReceivedFlag = 0;

static int serial_putchar(char c, FILE* stream);

static FILE serialStdout = FDEV_SETUP_STREAM(serial_putchar, NULL, _FDEV_SETUP_WRITE);


void serial_init(void) {
	
	//sei(); //enable interrupts
	
	DDRE &= ~(1 << RXD0); // input
	DDRE |= (1 << TXD0); // output
	
	unsigned int ubrr = UBRR;
	//Baud rate
	UBRR0H = (unsigned char) (ubrr >> 8);
	UBRR0L = (unsigned char) ubrr;
	
	// frame format : 8 data, 1 stop bit
	UCSR0B = (1 << RXCIE0) | (1<<RXEN0) | (1<<TXEN0); // enable rx interrupt, enable rx, enable tx
	UCSR0C = (3<<UCSZ00);
	
	stdout = &serialStdout;
	
}


static int serial_putchar(char c, FILE* stream) {
	#ifdef SERIAL_PUTTY 
		if (c == '\n') {
			serial_putchar('\r', stream);
		}
	#endif
	//wait till transmit buffer empty
	while (!(UCSR0A & (1<<UDRE0)))
		;
	//put data in
	UDR0 = c;
	
	return 0;
}

void serial_printf(const char* format, ...) {
	serial_send_byte(SERIAL_STX);
	serial_send_byte(DEBUG_PRINTF_TYPE);
	va_list args;
	va_start(args, format);
	vprintf(format, args);
	serial_send_byte(SERIAL_ETX);
	va_end(args);
}

void serial_send_byte(uint8_t byte) {
	//wait till transmit buffer empty
	while (!(UCSR0A & (1<<UDRE0)))
		;
	//put data in
	UDR0 = byte;
}

unsigned char serial_receive_byte( void ) {
	/* Wait for data to be received */
	while ( !(UCSR0A & (1<<RXC0)) )
		;
	/* Get and return received data from buffer */
	return UDR0;
}


int serial_convert_message_type_to_length (unsigned char type) {
	switch(type) {
		case TELESCOPE_COORD_OVERRIDE_TYPE:
			return sizeof(float) * 3;
		case ORIENTATION_TYPE:
			return sizeof(float) * 2;
		case MANUAL_GYRO_CALIBRATION_OVERRIDE_TYPE:
			return sizeof(float) * 3;
		case POWER_CYCLE_TYPE:
			return sizeof(uint8_t);
		//case SEARCH_MODE_TYPE:
			//return sizeof(uint8_t);
		case DEBUG_LED_TYPE:
			return sizeof(uint8_t);
		case START_STOP_COMMAND_TYPE:
			return sizeof(uint8_t);	
		case ELECTRICAL_TYPE:
			return sizeof(uint8_t);
		case ROLL_ONLY_OVERRIDE_TYPE:
			return sizeof(float) * 1;
		default:
			return -1;
	}
}

int serial_check_message_received(void) {
	return serialMessageReceivedFlag;
}

SerialMessage serial_get_last_message(void) {
	serialMessageReceivedFlag = 0;
	//could also reply here to confirm that it has been acknowledged
	serial_reply_to_command(lastMessage.messageType);
	return lastMessage;
}

void serial_send_picture_request(void) {
	serial_send_byte(SERIAL_STX);
	serial_send_byte(PICTURE_TIME_TYPE);
	serial_send_byte(SERIAL_ETX);
}

void serial_construct_message(void) {
	unsigned char type = serialBuffer[1];
	lastMessage.messageType = type;
	
	switch(type) {
		case ORIENTATION_TYPE:
			//Orientation command
			//this should be followed by 2 floats;
			for (int i = 0; i < 2; i++) {
				unsigned char bytes[] = { serialBuffer[4 * i + 2],
					serialBuffer[4 * i + 3],
					serialBuffer[4 * i + 4],
				serialBuffer[4 * i + 5] };
				memcpy(&lastMessage.data.angles[i], bytes, sizeof(float));
			}
			break;
		case TELESCOPE_COORD_OVERRIDE_TYPE:
			//Telescope override
			//this should be followed by 3 floats;
			for (int i = 0; i < 3; i++) {
				unsigned char bytes[] = { serialBuffer[4 * i + 2],
					serialBuffer[4 * i + 3],
					serialBuffer[4 * i + 4],
				serialBuffer[4 * i + 5] };
				memcpy(&lastMessage.data.angles[i], bytes, sizeof(float));
			}
			break;
			
		case MANUAL_GYRO_CALIBRATION_OVERRIDE_TYPE:
			//this should be followed by 3 floats;
			for (int i = 0; i < 3; i++) {
				unsigned char bytes[] = { serialBuffer[4 * i + 2],
					serialBuffer[4 * i + 3],
					serialBuffer[4 * i + 4],
				serialBuffer[4 * i + 5] };
				memcpy(&lastMessage.data.angles[i], bytes, sizeof(float));
			}
			break;
		case ROLL_ONLY_OVERRIDE_TYPE:
			for (int i = 0; i < 1; i++) {
				unsigned char bytes[] = { serialBuffer[4 * i + 2],
					serialBuffer[4 * i + 3],
					serialBuffer[4 * i + 4],
				serialBuffer[4 * i + 5] };
				memcpy(&lastMessage.data.angles[i], bytes, sizeof(float));
			}
			break;
		case POWER_CYCLE_TYPE:
			lastMessage.data.value = serialBuffer[2];
			break;
		case START_STOP_COMMAND_TYPE:
			lastMessage.data.value = serialBuffer[2];
			break;
		//case SEARCH_MODE_TYPE:
			//lastMessage.data.value = serialBuffer[2];
			//break;
		//case CALIBRATE_TYPE:
			//lastMessage.data.value = serialBuffer[2];
			//break;
		case DEBUG_LED_TYPE:
			lastMessage.data.value = serialBuffer[2];
			break;
		case ELECTRICAL_TYPE:
			lastMessage.data.value = serialBuffer[2];
			break;	
		default:	
			break;	  
	}
	
	serialMessageReceivedFlag = 1; //possibly raise a software interrupt to handle this??
}

/*
 * Interrupt vector for receiving a character
 */
ISR(USART0_RX_vect) {
	//Put the character into the buffer
	serialBuffer[currentPos] = UDR0;
	#if ECHO_SERIAL
		serial_send_byte(serialBuffer[currentPos]);
	#endif
	 
	if (waitingForStx && serialBuffer[currentPos] == SERIAL_STX) {
		waitingForStx = 0; //received the stx
		currentPos++;
		//debug_led_green_toggle();
		
	} else if (currentPos == 1) {
		//this is the first character which signifies type of message
		messageLength = serial_convert_message_type_to_length(serialBuffer[currentPos]);
		if (messageLength == -1) {
			//this message type was not valid
			//reset everything
			currentPos = 0;
			waitingForStx = 1;
		} else {
			currentPos++;
		}
	} else if (!waitingForStx) {
		//we are in the midst of receiving a message 
		if (currentPos == messageLength + 2) { //+2 because STX and messageType
			//this should be the end of the message
			if (serialBuffer[currentPos] == SERIAL_ETX) {
				//the ETX came through as expected
				serial_construct_message();
				
			} 
			//got enough data but this should have been an ETX, reset everything
			currentPos = 0;
			waitingForStx = 1;
		} else {
			currentPos++;
		}
	} else {
		//we're waiting for an stx but haven't received one.
		//Probably missed the start of the message
		//just continue and wait for the next stx
		;
	}
}


void serial_send_float(float value) {
	uint32_t* val = (uint32_t*) &value;
	serial_send_byte((*val >> 0));
	serial_send_byte((*val >> 8));
	serial_send_byte((*val >> 16));
	serial_send_byte((*val >> 24));
}

void serial_send_vector(Vector3 data) {
	serial_send_float(data[X]);
	serial_send_float(data[Y]);
	serial_send_float(data[Z]);
}

void serial_send_electrical_info(float iReading, float vReading) {
	serial_send_byte(SERIAL_STX);
	serial_send_byte(ELECTRICAL_TYPE);
	serial_send_float(iReading);
	serial_send_float(vReading);
	serial_send_byte(SERIAL_ETX);
}

void serial_send_orientation_info(char key, Vector3 data) {
	if (key == RAW_RATES_TYPE || key == GYROSCOPE_TYPE) {
		serial_send_byte(SERIAL_STX);
		serial_send_byte(key);
		serial_send_vector(data);
		serial_send_byte(SERIAL_ETX);
	}
}

void serial_reply_to_command(char key) {
	serial_send_byte(SERIAL_STX);
	serial_send_byte(key);
	serial_send_byte('o');
	serial_send_byte('k');
	serial_send_byte(SERIAL_ETX);
}