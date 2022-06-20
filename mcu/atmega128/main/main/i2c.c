/*
 * i2c.c
 *
 * Created: 22/03/2018 4:32:54 PM
 *  
 */ 
#include <avr/io.h>
#include <inttypes.h>
#include "i2c.h"

void i2c_init(void) {
	//set SCL to 400 kHz
	TWSR = 0x00;
	TWBR = 0x0C;
	//enable i2c
	TWCR = (1<<TWEN);
}

void i2c_start(void) {
	TWCR = (1<<TWINT)|(1<<TWSTA)|(1<<TWEN);
	while ((TWCR & (1<<TWINT)) == 0);
}

void i2c_stop(void) {
	TWCR = (1<<TWINT)|(1<<TWSTO)|(1<<TWEN);
}

void i2c_write(uint8_t data) {
	TWDR = data;
	TWCR = (1<<TWINT)|(1<<TWEN);
	while ((TWCR & (1<<TWINT)) == 0);
}

uint8_t i2c_read_ack(void) {
	TWCR = (1<<TWINT)|(1<<TWEN)|(1<<TWEA);
	while ((TWCR & (1<<TWINT)) == 0);
	return TWDR;
}

uint8_t i2c_read_nack(void) {
	TWCR = (1<<TWINT)|(1<<TWEN);
	while ((TWCR & (1<<TWINT)) == 0);
	return TWDR;
}

uint8_t i2c_get_status(void) {
	uint8_t status;
	//mask status
	status = TWSR & 0xF8;
	return status;
}