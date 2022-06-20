/*
 * gyro_fxas21002.h
 *
 * Created: 26/04/2018 3:02:38 PM
 *  
 * 
 * Interrupt connected to PD2 (RXD1 / INT2)
 */ 

#include <avr/interrupt.h>
#include "i2c_common.h"

#ifndef GYRO_FXAS21002_H_
#define GYRO_FXAS21002_H_

#define GYRO_COUNT_TO_DPS 15.625/1000
//62.5/1000

#define GYRO_NEW_DATA_INT_VECT INT2_vect

#define I2C_ADDR_GYRO (0x40 << 0) //i2c address value 

//Register addresses
#define STATUS_ADDR_GYRO		0x00
#define OUT_X_MSB_ADDR_GYRO		0x01
#define OUT_X_LSB_ADDR_GYRO		0x02
#define OUT_Y_MSB_ADDR_GYRO		0x03
#define OUT_Y_LSB_ADDR_GYRO		0x04
#define OUT_Z_MSB_ADDR_GYRO		0x05
#define OUT_Z_LSB_ADDR_GYRO		0x06
#define DR_STATUS_ADDR_GYRO		0x07
#define F_STATUS_ADDR_GYRO		0x08
#define F_SETUP_ADDR_GYRO		0x09
#define F_EVENT_ADDR_GYRO		0x0A
#define INT_SRC_FLAG_ADDR_GYRO	0x0B
#define WHO_AM_I_ADDR_GYRO		0x0C	// Default value: 0xD7
#define CTRL_REG0_ADDR_GYRO		0x0D
#define RT_CFG_ADDR_GYRO		0x0E
#define RT_SRC_ADDR_GYRO		0x0F
#define RT_THS_ADDR_GYRO		0x10
#define RT_COUNT_ADDR_GYRO		0x11
#define TEMP_ADDR_GYRO			0x12
#define CTRL_REG1_ADDR_GYRO		0x13
#define CTRL_REG2_ADDR_GYRO		0x14
#define CTRL_REG3_ADDR_GYRO		0x15

/*
 * Read a specified register from the gyroscope
 */
#define gyro_read_register(regAddr)						i2c_read_register(I2C_ADDR_GYRO, regAddr)

/*
 * Read a block of registers from the gyroscope
 */
#define gyro_read_block(startRegAddr, length, data)		i2c_read_block(I2C_ADDR_GYRO, startRegAddr, length, data)

/*
 * Write to a gyroscope register
 */
#define gyro_write_register(regAddr, value)				i2c_write_register(I2C_ADDR_GYRO, regAddr, value)

/************************ EXTERNAL FUNCTIONS *******************************/
/*
 * Initialise the gyroscope
 */
void gyro_init(void);

/*
 * Copy the values from the gyroscope into the values vector. 
 * values should have a length of 3
 */
void gyro_read_values (short* values);

/* 
 * Run the calibration routine or read the values from EEPROM
 */
void gyro_run_calibration(void);

/*
 * Attach a callback to the gyroscope new data interrupt
 */
void gyro_attach_callback(void (*func)(void));

/*
 * Force a new calibration
 */
void gyro_force_calibration(void);

/*
 * Manually overwrite the offsets for the gyroscope readings. Used to manually
 * reduce drift. 
 */
void gyro_set_offsets(short x, short y, short z);

/*
 * Copys the last measured raw rates into rates. rates should be of length 3
 */
void gyro_read_raw_rates(short* rates);
#endif /* GYRO_FXAS21002_H_ */