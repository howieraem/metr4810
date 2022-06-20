/*
 * L3GD2Gyro.h
 *
 * Created: 22/03/2018 9:42:14 PM
 *  
 */ 


#ifndef L3GD2GYRO_H_
#define L3GD2GYRO_H_

#include "i2c.h"

#define READ 1
#define WRITE 0

#define X_OFFSET 368.1//367.818
#define Y_OFFSET 140.094
#define Z_OFFSET -201.4 //-199.765
#define RATE_2_DPS  8.75/1000.0 // this is for +/- 250 dps

void enable_gyro(uint8_t addr) {
	i2c_start();
	i2c_write(addr | (WRITE << 0));
	//write to control register 1
	i2c_write(0x20);
	//bring it out of sleep mode
	i2c_write(0x6F); // 0b01101111
	i2c_stop();
	
	i2c_start();
	i2c_write(addr | (WRITE << 0));
	//write to control register 4
	i2c_write(0x23);
	i2c_write(0b00000000);//0x6F); // 0b01101111
	i2c_stop();
}

uint8_t read_WHO_AM_I(uint8_t addr) {
	i2c_start();
	i2c_write(addr | (WRITE << 0));
	//status register
	i2c_write(0x0F);
	i2c_stop();
	
	i2c_start();
	i2c_write(addr | (READ << 0));
	uint8_t ret = i2c_read_nack();
	i2c_stop();
	return ret;
}

void read_gyro(uint8_t addr, short* vals) {
	uint8_t* halfVals = (uint8_t*) vals;
	i2c_start();
	i2c_write(addr | (WRITE << 0));
	i2c_write(0xA8);
	i2c_stop();

	i2c_start();
	i2c_write(addr | (READ << 0));
	halfVals[0] = i2c_read_ack();
	halfVals[1] = i2c_read_ack();
	halfVals[2] = i2c_read_ack();
	halfVals[3] = i2c_read_ack();
	halfVals[4] = i2c_read_ack();
	halfVals[5] = i2c_read_nack();
	i2c_stop();
	
	vals[0] -= X_OFFSET;
	vals[1] -= Y_OFFSET;
	vals[2] -= Z_OFFSET;
}


#endif /* L3GD2GYRO_H_ */