/*
 * imu.c
 *
 * Created: 26/04/2018 7:13:36 PM
 *  
 */ 

#include "imu.h"
#include "gyro_fxas21002.h"
#include "mag_lis3mdl.h"
#include "i2c.h"
#include "timer.h"
#include "matrix.h"
#include "sense.h"
#include "debug_led.h"
#include "config.h"
#include <stdio.h>

#define EXP_FILTER_VAL 0.5

Vector3 worldAngles;
Vector3 magAngles;
Vector3 worldRates;

Vector3 smoothedBodyRates;
uint16_t lastTime = 0;

uint8_t newDataFlag = 0;
int16_t dtInt;
short rawGyroRates[3];


void imu_init(void) {
	i2c_init();
	timer1_init();
	
	//mag_init();
	
	smoothedBodyRates[X] = 0;
	smoothedBodyRates[Y] = 0;
	smoothedBodyRates[Z] = 0;
	
	worldAngles[X] = 0;
	worldAngles[Y] = 0;
	worldAngles[Z] = 0;
	
	gyro_attach_callback(&imu_new_data_interrupt);
	gyro_init();
	
	gyro_run_calibration();

	//sei();
	lastTime = read_timer1(); //Possibly necessary. Need to think about this
}

void imu_reset(void) {
	smoothedBodyRates[X] = 0;
	smoothedBodyRates[Y] = 0;
	smoothedBodyRates[Z] = 0;
	
	//worldAngles[X] = 0; // want to maintain the roll angle so don't reset this
	worldAngles[Y] = 0;
	worldAngles[Z] = 0;

}

void imu_set_current_angles(Vector3 angles) {
	worldAngles[X] = angles[X];
	worldAngles[Y] = angles[Y];
	worldAngles[Z] = angles[Z];
}

void imu_overwrite_roll(float angle) {
	worldAngles[X] = angle;	
}

void imu_spin(void) {
	if (newDataFlag) {
		newDataFlag = 0;
	} else {
		return;
	}
	
	if (dtInt < 0) {
		dtInt += 65536;
	}
	
	float dt = dtInt * TIMER1_TICK_TO_MS / 1000;
	
	gyro_rates_to_world_rates(rawGyroRates, worldAngles, worldRates);
	worldRates[X] *= GYRO_COUNT_TO_DPS;
	worldRates[Y] *= GYRO_COUNT_TO_DPS;
	worldRates[Z] *= GYRO_COUNT_TO_DPS;
	
	worldAngles[X] += worldRates[X] * dt;
	worldAngles[Y] += worldRates[Y] * dt;
	worldAngles[Z] += worldRates[Z] * dt;
	
	smoothedBodyRates[X] = smoothedBodyRates[X] * EXP_FILTER_VAL + ((float) (rawGyroRates[X])) * (1 - EXP_FILTER_VAL) * GYRO_COUNT_TO_DPS;
	smoothedBodyRates[Y] = smoothedBodyRates[Y] * EXP_FILTER_VAL + ((float) (rawGyroRates[Y])) * (1 - EXP_FILTER_VAL) * GYRO_COUNT_TO_DPS;
	smoothedBodyRates[Z] = smoothedBodyRates[Z] * EXP_FILTER_VAL + ((float) (rawGyroRates[Z])) * (1 - EXP_FILTER_VAL) * GYRO_COUNT_TO_DPS;
}

void imu_new_data_interrupt(void) {
	
	gyro_read_values(rawGyroRates);
	#if DISABLE_ROLL
		rawGyroRates[X] = 0;  ////TODO: TAKE ME OUT ************************************************************************************************************
	#endif
	
	uint16_t currentTime = read_timer1();
	
	dtInt = currentTime - lastTime;
	lastTime = currentTime;	
	
	newDataFlag = 1;
}

void imu_read_body_rates(Vector3 rates) {
	rates[X] = smoothedBodyRates[X];
	rates[Y] = smoothedBodyRates[Y];
	rates[Z] = smoothedBodyRates[Z];
	//printf("World rates (x1000): %6d, %6d, %6d\n", (int) (rates[X]), (int) (rates[Y]), (int) (rates[Z]));
}

void imu_read_angles(Vector3 angles) {
	angles[X] = worldAngles[X];
	angles[Y] = worldAngles[Y];
	angles[Z] = worldAngles[Z];
	
}