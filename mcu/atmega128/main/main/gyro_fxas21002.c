/*
 * gyro_fxas21002.c
 *
 * Created: 26/04/2018 3:11:55 PM
 *  
 */ 
#include <stdlib.h>
#include <inttypes.h>
#include <avr/interrupt.h>
#include <avr/eeprom.h>
#include <stdio.h>
#include "i2c_common.h"
#include "gyro_fxas21002.h"
#include "matrix.h"
#include "debug_led.h"
#include "config.h"

short xOffset = 0;
short yOffset = 0;
short zOffset = 0;
short lastRates[3];

void (*gyro_new_data)(void);

/*
 * Interrupt vector triggered by new data from gyro
 */
ISR(INT2_vect) {
	gyro_new_data();
}
	
void gyro_init(void) {	
		
	DDRD &= ~(1 << PIND2);
	PORTD |= (0 << PIND2);
	
	EICRA |= (1 << ISC21) | (1 << ISC20); //rising edge mode
	EIMSK |= (1 << INT2); //enable external interrupt 2
	//sei();
	
	
	//configure this to be whatever setup we want
	// NOTE : THIS SEEMS TO NEED TO BE CONSISTENTLY REWRITTEN IN gyro_read_values(). This is what fixed the issue when OCS board stopped working
	gyro_write_register(CTRL_REG0_ADDR_GYRO, (1 << 1)); // set to 500 dps 
	gyro_write_register(CTRL_REG1_ADDR_GYRO, 0b00010010);  
	gyro_write_register(CTRL_REG2_ADDR_GYRO,  (1 << 3) | (1 << 2) | (1 << 1));
	
	//gyro_new_data = NULL;
	//gyro_read_register(WHO_AM_I_ADDR_GYRO);
	
	short vals[3];
	gyro_read_values(vals);
}

void gyro_attach_callback(void (*func)(void)) {
	gyro_new_data = func;
}

void gyro_read_values (short* values) {
	gyro_write_register(CTRL_REG1_ADDR_GYRO, 0b00010010);
	uint8_t tempValues[6];
	uint8_t* halfVals = (uint8_t*) values;
	gyro_read_block(OUT_X_MSB_ADDR_GYRO, 6, tempValues);
	
	//reverse the endianness
	halfVals[0] = tempValues[1];
	halfVals[1] = tempValues[0];
	halfVals[2] = tempValues[3];
	halfVals[3] = tempValues[2];
	halfVals[4] = tempValues[5];
	halfVals[5] = tempValues[4];
	
	
	//printf("Values[X]: %d\n", values[X]);
	//Deal with the coordinates system differences between gyro and telescope
	short temp[3];
	temp[X] = -values[X];
	temp[Y] = values[Y];
	temp[Z] = -values[Z];
	
	values[X] = temp[X];
	values[Y] = temp[Y];
	values[Z] = temp[Z];
		
	lastRates[X] = values[X];
	lastRates[Y] = values[Y];
	lastRates[Z] = values[Z];
	
	values[X] -= xOffset;
	values[Y] -= yOffset;
	values[Z] -= zOffset;
	
	
}

void gyro_read_raw_rates(short* rates) {
	rates[X] = lastRates[X];
	rates[Y] = lastRates[Y];
	rates[Z] = lastRates[Z];
}

void gyro_run_calibration(void) {
	
	#if ENABLE_GYRO_CALIBRATION
		int32_t sumX = 0, sumY = 0, sumZ = 0;
		short gyroRates[3];
		int nValues = 10000;
		for (int i = 0; i < nValues; i++) {
			gyro_read_values(gyroRates);
			
			sumX += gyroRates[X];
			sumY += gyroRates[Y];
			sumZ += gyroRates[Z];
		}
		//printf("Rates: %d, %d, %d\n", gyroRates[X], gyroRates[Y], gyroRates[Z]);
		xOffset = sumX / nValues;
		yOffset = sumY / nValues;
		zOffset = sumZ / nValues;
		//printf("Offsets: %d, %d, %d\n", xOffset, yOffset, zOffset);
		eeprom_busy_wait();
		eeprom_write_word((uint16_t*) 0, (uint16_t) xOffset);
		eeprom_busy_wait();
		eeprom_write_word((uint16_t*) 2, (uint16_t) yOffset);
		eeprom_busy_wait();
		eeprom_write_word((uint16_t*) 4, (uint16_t) zOffset);
		eeprom_busy_wait();
	#else
		eeprom_busy_wait();
		xOffset = eeprom_read_word((uint16_t*) 0);
		eeprom_busy_wait();
		yOffset = eeprom_read_word((uint16_t*) 2);
		eeprom_busy_wait();
		zOffset = eeprom_read_word((uint16_t*) 4);
		eeprom_busy_wait();
	#endif
	
}

void gyro_set_offsets(short x, short y, short z) {
	xOffset = x;
	yOffset = y;
	zOffset = z;
	
	eeprom_busy_wait();
	eeprom_write_word((uint16_t*) 0, (uint16_t) xOffset);
	eeprom_busy_wait();
	eeprom_write_word((uint16_t*) 2, (uint16_t) yOffset);
	eeprom_busy_wait();
	eeprom_write_word((uint16_t*) 4, (uint16_t) zOffset);
	eeprom_busy_wait();
	
}

void gyro_force_calibration(void) {
	cli();
	int32_t sumX = 0, sumY = 0, sumZ = 0;
	short gyroRates[3];
	int nValues = 10000;
	for (int i = 0; i < nValues; i++) {
		gyro_read_values(gyroRates);
		sumX += gyroRates[X];
		sumY += gyroRates[Y];
		sumZ += gyroRates[Z];
	}
	
	xOffset = sumX / nValues;
	yOffset = sumY / nValues;
	zOffset = sumZ / nValues;
	eeprom_busy_wait();
	eeprom_write_word((uint16_t*) 0, (uint16_t) xOffset);
	eeprom_busy_wait();
	eeprom_write_word((uint16_t*) 2, (uint16_t) yOffset);
	eeprom_busy_wait();
	eeprom_write_word((uint16_t*) 4, (uint16_t) zOffset);
	eeprom_busy_wait();
	sei();
}