/*
 * ocs.c
 *
 * Created: 30/04/2018 12:58:56 PM
 *  
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>
#include <inttypes.h>
#include "matrix.h"
#include "config.h"
#include <math.h>
#include <stdio.h>
#include "imu.h"
#include "brushless.h"
#include "debug_led.h"
#include "ocs.h"
#include <util/delay.h>


//#include "timer.h"
//Vector3 lastAngleError;
//Vector3 angleErrorIntegral;
Vector3 desiredWorld;
//uint16_t lastTime;
uint8_t enabled;
uint8_t targetReceived;

uint8_t missionAccomplished;
uint16_t stabilityCounter;

void ocs_angles_to_xyz(Vector3 angles, Vector3 vec, int isDegrees);

void ocs_power_init() {
	DDRB |= (1 << PINB0);
	ocs_power_off();
}

void ocs_power_cycle(void) {
	brushless_stop_motors();
	_delay_ms(1000); //give a second for motors to stop
	ocs_power_off();
	_delay_ms(POWER_CYCLE_TIME); // off time
	ocs_power_on();
	_delay_ms(MOTOR_ARMING_TIME); // wait for motors to arm
}

void ocs_power_off() {
	PORTB &= ~(1 << PINB0);
}

void ocs_power_on() {
	PORTB |= (1 << PINB0);
}

void ocs_init(void) {
	DDRB |= (1 << PINB0);
	#ifdef MOTORS_CONNECTED
		brushless_motors_init();
	#endif
	desiredWorld[X] = 0;
	desiredWorld[Y] = 0;
	desiredWorld[Z] = 0;
	enabled = 1;
	missionAccomplished = 0;
	stabilityCounter = 0;
	targetReceived = 0;
}

void ocs_reset(void) {
	desiredWorld[X] = 0;
	desiredWorld[Y] = 0;
	desiredWorld[Z] = 0;
	enabled = 1;
	missionAccomplished = 0;
	stabilityCounter = 0;
	targetReceived = 0;
}

void ocs_set_target(Vector3 target) {
	missionAccomplished = 0;
	targetReceived = 1;
	desiredWorld[X] = target[X];
	desiredWorld[Y] = target[Y];
	desiredWorld[Z] = target[Z];
}

void ocs_clear_target(void) {
	missionAccomplished = 0;
	targetReceived = 0;
	desiredWorld[X] = 0;
	desiredWorld[Y] = 0;
	desiredWorld[Z] = 0;
}

void ocs_get_target(Vector3 target) {
	target[X] = desiredWorld[X];
	target[Y] = desiredWorld[Y];
	target[Z] = desiredWorld[Z];
}

void ocs_enable(void) {
	enabled = 1;
}

void ocs_disable(void) {
	enabled = 0;
}

uint8_t ocs_check_if_on_target(void) {
	return missionAccomplished;
}

void ocs_spin_control(void) {
	if (!enabled) {
		
		return;
	}
	
	Vector3 currentWorld;
	imu_read_angles(currentWorld);
	if (targetReceived) {
		if (fabs(currentWorld[Y] - desiredWorld[Y]) <= TARGET_ANGLE_THRESHOLD &&
		fabs(currentWorld[Z] - desiredWorld[Z]) <= TARGET_ANGLE_THRESHOLD ) {
			
			stabilityCounter += 1;
			
			if (stabilityCounter >= STABILITY_TIME_THRESHOLD / LOOP_TIME_DELAY) {
				missionAccomplished = 1;
			}  else {
				missionAccomplished = 0;
				stabilityCounter = 0;
			}
		}
	}
	
	
	
	if (fabs(currentWorld[Z] - desiredWorld[Z]) <= 2) {
		debug_led_green_on();
	} else {
		debug_led_green_off();
	}	
	
	if (fabs(currentWorld[Y] - desiredWorld[Y]) <= 2) {
		debug_led_red_on();
		} else {
		debug_led_red_off();
	}
	
	Vector3 currentBodyRates;
	imu_read_body_rates(currentBodyRates);
	ocs_run_control(currentWorld, currentBodyRates);
}

void ocs_run_control(Vector3 currentWorld, Vector3 currentBodyRates) {
	Vector3 torqueVector; //The torque vector around which the craft needs to spin. In telescope frame

	float angle = ocs_compute_torque_vector(currentWorld, desiredWorld, DEGREES, torqueVector);
	
	Vector3 axisPowers;
	
	//torqueVector[X] is always 0, but the derivative control should keep the craft from spinning about the roll axis
	// could use:
	// float rollAngle = currentWorld[X];
	// axisPowers[X] = -KpX * rollAngle + KdX * currentBodyRates[X];
	axisPowers[X] = -torqueVector[X] * KpX * angle + KdX * currentBodyRates[X];
	axisPowers[Y] = -torqueVector[Y] * KpY * angle + KdY * currentBodyRates[Y];
	axisPowers[Z] = -torqueVector[Z] * KpZ * angle + KdZ * currentBodyRates[Z];
	
	

	
	//printf("\nAxis powers (x1000): %5d, %5d, %5d\n", (int) (currentBodyRates[X]), (int) (currentBodyRates[Y]), (int) (currentBodyRates[Z]));
	#ifdef MOTORS_CONNECTED
		brushless_generate_torque(axisPowers);
	#endif
}

void ocs_angles_to_xyz(Vector3 angles, Vector3 vec, int isDegrees) {
	Vector3 anglesRads;
	if (isDegrees) {
		anglesRads[X] = angles[X] * DEG_2_RAD;
		anglesRads[Y] = angles[Y] * DEG_2_RAD;
		anglesRads[Z] = angles[Z] * DEG_2_RAD;
	} else {
		anglesRads[X] = angles[X];
		anglesRads[Y] = angles[Y];
		anglesRads[Z] = angles[Z];
	}
	
	vec[X] = cosf(anglesRads[Y]) * cosf(anglesRads[Z]);
	vec[Y] = cosf(anglesRads[Y]) * sinf(anglesRads[Z]);
	vec[Z] = -sinf(anglesRads[Y]);
}

float ocs_compute_torque_vector(Vector3 currentAngles, Vector3 desiredAngles, int isDegrees, Vector3 torqueVectorTelescope) {
	Vector3 currentPoseVector;
	Vector3 desiredPoseVector;
	
	ocs_angles_to_xyz(currentAngles, currentPoseVector, isDegrees);
	
	ocs_angles_to_xyz(desiredAngles, desiredPoseVector, isDegrees);

	Vector3 torqueVectorWorld;
	vector_cross(currentPoseVector, desiredPoseVector, torqueVectorWorld);
	
	Matrix R;
	construct_rotation_matrix(R, currentAngles[X], currentAngles[Y], currentAngles[Z], isDegrees);
	
	//Matrix Rinv;
	//matrix_transpose(R, Rinv);
	
	matrix_vector_multiply(R, torqueVectorWorld, torqueVectorTelescope);
	
	float mag = calc_magnitude(torqueVectorTelescope);
	
	float angle = asinf(mag) * RAD_2_DEG;
	torqueVectorTelescope[X] /= mag;
	torqueVectorTelescope[Y] /= mag;
	torqueVectorTelescope[Z] /= mag;

	return angle;
	
	
}