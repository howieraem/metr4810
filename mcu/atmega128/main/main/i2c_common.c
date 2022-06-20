/*
 * i2c_common.c
 *
 * Created: 26/04/2018 2:57:33 PM
 *  
 */ 

#include "i2c_common.h"
#include "i2c.h"

#define READ 1
#define WRITE 0

uint8_t i2c_read_register(uint8_t i2cAddr, uint8_t regAddr) {
	i2c_start();
	i2c_write(i2cAddr | (WRITE << 0)); //Going to write to the i2c device
	i2c_write(regAddr); //tell the device which register we want
	i2c_stop();

	i2c_start();
	i2c_write(i2cAddr | (READ << 0)); //ask device for a response
	uint8_t ret = i2c_read_nack(); //read the register value
	i2c_stop();
	return ret;
}

void i2c_read_block(uint8_t i2cAddr, uint8_t startRegAddr, int length, uint8_t* data) {
	i2c_start();
	i2c_write(i2cAddr | (WRITE << 0));
	i2c_write(startRegAddr);
	i2c_stop();

	i2c_start();
	i2c_write(i2cAddr | (READ << 0));
	int i = 0;
	for (i = 0; i < length - 1; i++) {
		data[i] = i2c_read_ack();
	}
	data[i] = i2c_read_nack();
	i2c_stop();
}

void i2c_write_register(uint8_t i2cAddr, uint8_t regAddr, uint8_t value) {
	i2c_start();
	i2c_write(i2cAddr | (WRITE << 0));
	i2c_write(regAddr);
	i2c_write(value);
	i2c_stop();
}


