/*
 * i2c.h
 *
 * Created: 22/03/2018 4:30:13 PM
 *  
 */ 


#ifndef I2C_H
#define I2C_H

void i2c_init(void); 
void i2c_start(void);
void i2c_stop(void);
void i2c_write(uint8_t data);
uint8_t i2c_read_ack(void);
uint8_t i2c_read_nack(void);
uint8_t i2c_get_status(void);

#endif