/*
 * MAG3110Magnetometer.h
 *
 * Created: 29/03/2018 4:09:38 PM
 *  
 */ 


#ifndef MAG3110MAGNETOMETER_H_
#define MAG3110MAGNETOMETER_H_

#include "i2c.h"

#define READ 1
#define WRITE 0

#define MAG_ADDR 0x0E


#define CTRL_REG1 0x10
#define CTRL_REG2 0x11
#define OUT_X_MSB 0x01

void enable_magnetometer(void) {
	uint8_t addr = (uint8_t) (MAG_ADDR << 1);
	
	i2c_start();
	i2c_write(addr | (WRITE << 0));
	//write to control register 1
	i2c_write(CTRL_REG1);
	i2c_write(0x01);
	i2c_stop();
	
	i2c_start();
	i2c_write(addr | (WRITE << 0));
	i2c_write(CTRL_REG2);
	i2c_write(0x80);
	i2c_stop();
}

void read_magnetometer(short* vals) {
	uint8_t addr = (uint8_t) (MAG_ADDR << 1);
	uint8_t* halfVals = (uint8_t*) vals;
	i2c_start();
	i2c_write(addr | (WRITE << 0));
	i2c_write(OUT_X_MSB);
	i2c_stop();

	i2c_start();
	i2c_write(addr | (READ << 0));
	halfVals[1] = i2c_read_ack();
	halfVals[0] = i2c_read_ack();
	halfVals[3] = i2c_read_ack();
	halfVals[2] = i2c_read_ack();
	halfVals[5] = i2c_read_ack();
	halfVals[4] = i2c_read_nack();
	i2c_stop();
}



#endif /* MAG3110MAGNETOMETER_H_ */