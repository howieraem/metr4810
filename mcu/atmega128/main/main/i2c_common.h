/*
 * i2c_common.h
 *
 * Created: 26/04/2018 2:56:06 PM
 *  
 */ 
#include <inttypes.h>

#ifndef I2C_COMMON_H_
#define I2C_COMMON_H_

/*
 * Read and return the register address regAddr from the device at address i2cAddr 
 */
uint8_t i2c_read_register(uint8_t i2cAddr, uint8_t regAddr);

/*
 * Read a block of data starting from startRegAddr from the device at address
 * i2cAddr. Will read length registers and copy into data. 
 */
void i2c_read_block(uint8_t i2cAddr, uint8_t startRegAddr, int length, uint8_t* data);

/*
 * Write value to the regAddr register of the device with address i2cAddr
 */
void i2c_write_register(uint8_t i2cAddr, uint8_t regAddr, uint8_t value);


#endif /* I2C_COMMON_H_ */