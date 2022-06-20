/*
 * i2c.h
 *
 * Created: 22/03/2018 4:30:13 PM
 *  
 */ 
#include <inttypes.h>

#ifndef I2C_H
#define I2C_H

/*
 * Initialise all of the hardware settings for i2c
 */
void i2c_init(void); 

/*
 * Start an i2c communication
 */
void i2c_start(void);

/*
 * Stop an i2c communication
 */
void i2c_stop(void);

/*
 * Write data to the i2c bus
 */
void i2c_write(uint8_t data);

/*
 * Read and return a byte from the i2c bus with acknowledgment
 */
uint8_t i2c_read_ack(void);

/*
 * Read and return a byte from the i2c bus without acknowledgment
 */
uint8_t i2c_read_nack(void);

/*
 * Return the status of the i2c bus
 */
uint8_t i2c_get_status(void);

#endif