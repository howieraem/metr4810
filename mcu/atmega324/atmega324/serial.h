/*
 * serial.h
 *
 * Created: 22/03/2018 8:07:12 PM
 *  
 */ 


#ifndef SERIAL_H_
#define SERIAL_H_

void serial_init(void);
void serial_send_char(unsigned char data);
void serial_send_gyro_vals(short* vals);
void serial_send_float_angles(float* angles);
void serial_send_both(float* angles, float* vals);
void serial_send_int8(uint8_t data);
#endif /* SERIAL_H_ */