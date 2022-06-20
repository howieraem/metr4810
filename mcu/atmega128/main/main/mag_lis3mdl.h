/*
 * mag_lis3mdl.h
 *
 * Created: 26/04/2018 4:15:51 PM
 *  
 */ 


#ifndef MAG_LIS3MDL_H_
#define MAG_LIS3MDL_H_

#include <inttypes.h>
#include "i2c_common.h"

#define I2C_ADDR_MAG (0x3C << 0) //i2c address value

//Register addresses
#define WHO_AM_I_ADDR_MAG		0x0F	// Default Value: 0b00111101, 0x3D
#define CTRL_REG1_ADDR_MAG		0x20
#define CTRL_REG2_ADDR_MAG		0x21
#define CTRL_REG3_ADDR_MAG		0x22
#define CTRL_REG4_ADDR_MAG		0x23
#define CTRL_REG5_ADDR_MAG		0x24
#define STATUS_REG_ADDR_MAG		0x27
#define OUT_X_L_ADDR_MAG		0x28
#define OUT_X_H_ADDR_MAG		0x29
#define OUT_Y_L_ADDR_MAG		0x2A
#define OUT_Y_H_ADDR_MAG		0x2B
#define OUT_Z_L_ADDR_MAG		0x2C
#define OUT_Z_H_ADDR_MAG		0x2D
#define TEMP_OUT_L_ADDR_MAG		0x2E
#define TEMP_OUT_H_ADDR_MAG		0x2F
#define INT_CFG_ADDR_MAG		0x30
#define INT_SRC_ADDR_MAG		0x31
#define INT_THS_L_ADDR_MAG		0x32
#define INT_THS_H_ADDR_MAG		0x33




/*
 * Read a specified register from the magnetometer
 */
#define mag_read_register(regAddr)						i2c_read_register(I2C_ADDR_MAG, regAddr)
/*
 * Read a block of registers from the magnetometer
 */
#define mag_read_block(startRegAddr, length, data)		i2c_read_block(I2C_ADDR_MAG, startRegAddr, length, data)
/*
 * Write to a magnetometer register
 */
#define mag_write_register(regAddr, value)				i2c_write_register(I2C_ADDR_MAG, regAddr, value)

/************************ EXTERNAL FUNCTIONS *******************************/
/*
 * Initialise the magnetometer
 */
void mag_init(void);

/*
 * Read the values from the magnetometer and copy into values
 */
void mag_read_values (short* values);



#endif /* MAG_LIS3MDL_H_ */