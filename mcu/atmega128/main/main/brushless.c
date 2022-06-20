/*
 * brushless.c
 *
 * Created: 23/03/2018 12:55:55 PM
 *  
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>
#include "brushless.h"
#include "config.h"
#include "debug_led.h"
#include "timer.h"
#include "serial.h"
#include <stdio.h>
#include <util/delay.h>
#include <math.h>

#define MAX_COUNT F_CPU / (8*50)
#define MOTOR0_SPEED_REG OCR3A
#define MOTOR1_SPEED_REG OCR3B
#define MOTOR2_SPEED_REG OCR3C

//Periods in ms
#define PWM_PERIOD 20

int counter = 0;
Vector3 currentSpeeds;
uint16_t lastUpdateTime = 0;
int firstRunThrough = 1;

Vector3 integral;
Vector3 lastPowers;

uint8_t dangerDetected = 0;


void brushless_generate_torque(Vector3 power) {
	uint16_t currentTime = read_timer1();
	
	int16_t dtInt = currentTime - lastUpdateTime;
	
	if (dtInt < 0) {
		dtInt += 65536;
	}
	lastUpdateTime = currentTime;
	
	if (firstRunThrough) {
		//this makes sure the first dt value is not something crazy
		firstRunThrough = 0;
		return;
	} 
	
	//float dt = dtInt * TIMER1_TICK_TO_MS / 1000;
		
	integral[X] += power[X];
	integral[Y] += power[Y];
	integral[Z] += power[Z];
	
	if (integral[X] > 2000) {
		integral[X] = 2000;
	} else if (integral[X] < -2000) {
		integral[X] = -2000;
	}
	
	if (integral[Y] > 2000) {
		integral[Y] = 2000;
	} else if (integral[Y] < -2000) {
		integral[Y] = -2000;
	}
	
	if (integral[Z] > 2000) {
		integral[Z] = 2000;
	} else if (integral[Z] < -2000) {
		integral[Z] = -2000;
	}
	

	//THIS SHOULD PROBABLY INVOLVE SOME SORT OF DT OR OTHER TIME MEASURE  ******************************** FIX ************************************************************
	currentSpeeds[X] =	Kp * power[X] +	Ki * integral[X] +	Kd * (power[X] - lastPowers[X]) - Kbias * currentSpeeds[X];
	currentSpeeds[Y] =	Kp * power[Y] +	Ki * integral[Y] +	Kd * (power[Y] - lastPowers[Y]) - Kbias * currentSpeeds[Y];
	currentSpeeds[Z] =	Kp * power[Z] +	Ki * integral[Z] +	Kd * (power[Z] - lastPowers[Z]) - Kbias * currentSpeeds[Z];

	lastPowers[X] = power[X];
	lastPowers[Y] = power[Y];
	lastPowers[Z] = power[Z];
	
	currentSpeeds[X] = currentSpeeds[X] > MAX_SPEED ? MAX_SPEED : currentSpeeds[X];
	currentSpeeds[X] = currentSpeeds[X] < MIN_SPEED ? MIN_SPEED : currentSpeeds[X];
	
	currentSpeeds[Y] = currentSpeeds[Y] > MAX_SPEED ? MAX_SPEED : currentSpeeds[Y];
	currentSpeeds[Y] = currentSpeeds[Y] < MIN_SPEED ? MIN_SPEED : currentSpeeds[Y];
	
	currentSpeeds[Z] = currentSpeeds[Z] > MAX_SPEED ? MAX_SPEED : currentSpeeds[Z];
	currentSpeeds[Z] = currentSpeeds[Z] < MIN_SPEED ? MIN_SPEED : currentSpeeds[Z];
	
	#if MOTORS_CONNECTED
		;
	#else
		return;
	#endif

	brushless_set_motor_speed(ROLL_MOTOR, (int) currentSpeeds[X]); 
	brushless_set_motor_speed(PITCH_MOTOR, (int) currentSpeeds[Y]);
	brushless_set_motor_speed(YAW_MOTOR, (int) currentSpeeds[Z]);
	
	if (fabs(brushless_get_motor_speed(ROLL_MOTOR)) >= MAX_SPEED - 1 || 
			fabs(brushless_get_motor_speed(YAW_MOTOR)) >= MAX_SPEED - 1 || 
			fabs(brushless_get_motor_speed(PITCH_MOTOR)) >= MAX_SPEED - 1) {
		counter++;
		debug_led_orange_on();
	} else {
		debug_led_orange_toggle();
		counter = 0;
	}
	if (counter > COUNT_BEFORE_KILL) {
		dangerDetected = 1;
		counter = 0;
	}
}

void brushless_spin_down(void) {
	serial_printf("Spinning down motors!");
	int speedY = (int) currentSpeeds[Y];
	int dY = speedY > 0 ? 1 : -1;
	int speedZ = (int) currentSpeeds[Z];
	int dZ = speedZ > 0 ? 1 : -1;
	while (1) {
		if (fabs(speedY) > 2) {
			speedY -= dY;
		}
		if (fabs(speedZ) > 2) {
			speedZ -= dZ;
		}
		brushless_set_motor_speed(PITCH_MOTOR, speedY);
		brushless_set_motor_speed(YAW_MOTOR, speedZ);
		if (fabs(currentSpeeds[Y]) < SPIN_DOWN_THRESH && fabs(currentSpeeds[Z]) < SPIN_DOWN_THRESH) {
			break;
		}
		_delay_ms(50);
	}
	brushless_stop_motors();
}

void brushless_motors_init(void) {
	DDRE |= (1 << DDE3) | (1 << DDE4) | (1 << DDE5);
	TCCR3A = (1 << COM3A1) | (1 << COM3B1) | (1 << COM3C1) | (1 << WGM31); // WGM mode 14
	TCCR3B = ((1 << WGM32) | (1 << WGM33) | (1 << CS31));	// WGM mode 14 (Fast PWM)
	ICR3  = MAX_COUNT;	//set ICR3 to produce 50Hz frequency
	brushless_stop_motors();
	currentSpeeds[ROLL] = 0.0;
	currentSpeeds[PITCH] = 0.0;
	currentSpeeds[YAW] = 0.0;
	
	integral[X] = 0;
	integral[Y] = 0;
	integral[Z] = 0;
	lastPowers[X] = 0;
	lastPowers[Y] = 0;
	lastPowers[Z] = 0;
	
}

void brushess_reset(void) {
	brushless_stop_motors();
	firstRunThrough = 1;
}

uint8_t brushless_check_danger(void) {
	return dangerDetected;
}

void brushless_stop_motors(void) {
	dangerDetected = 0;
	brushless_set_motor_speed(MOTOR0, 0);
	brushless_set_motor_speed(MOTOR1, 0);
	brushless_set_motor_speed(MOTOR2, 0);
	currentSpeeds[ROLL] = 0.0;
	currentSpeeds[PITCH] = 0.0;
	currentSpeeds[YAW] = 0.0;
	integral[X] = 0;
	integral[Y] = 0;
	integral[Z] = 0;
	lastPowers[X] = 0;
	lastPowers[Y] = 0;
	lastPowers[Z] = 0;
}

void brushless_set_motor_speed(int motor, float speed) {
	//correct for motor directions
	if (motor == ROLL_MOTOR) {
		speed *= ROLL_MOTOR_DIR;
	} else if (motor == PITCH_MOTOR) {
		speed *= PITCH_MOTOR_DIR;
	} else if (motor == YAW_MOTOR) {
		speed *= YAW_MOTOR_DIR;
	} else {
		//invalid motor
		;
	}
	//clamp speed between MAX_SPEED and MIN_SPEED
	speed = speed > MAX_SPEED ? MAX_SPEED : speed;
	speed = speed < MIN_SPEED ? MIN_SPEED : speed;
	float period = speed * 0.005 + 1.5;
	brushless_set_motor_period(motor, period);
}

float brushless_get_motor_speed(int motor) {
	uint16_t regValue = 0;
	if (motor == MOTOR0) {
		regValue = MOTOR0_SPEED_REG;
	} else if (motor == MOTOR1) {
		regValue = MOTOR1_SPEED_REG;
	} else if (motor == MOTOR2) {
		regValue = MOTOR2_SPEED_REG;
	} else {
		//invalid motor
		;
	}
	
	float period = ((float) regValue) / (1.0 * MAX_COUNT) * PWM_PERIOD;
	float speed = (period - 1.5) / 0.005;

	if (motor == ROLL_MOTOR) {
		return speed * ROLL_MOTOR_DIR;
	} else if (motor == PITCH_MOTOR) {
		return speed * PITCH_MOTOR_DIR;
	} else if (motor == YAW_MOTOR) {
		return speed * YAW_MOTOR_DIR;
	} else {
		return 0;
	}
}

void brushless_set_motor_period(int motor, float period) {
	uint16_t regValue = (uint16_t) (period*1.0/PWM_PERIOD * MAX_COUNT);
	if (motor == MOTOR0) {
		MOTOR0_SPEED_REG = regValue;
	} else if (motor == MOTOR1) {
		MOTOR1_SPEED_REG = regValue;
	} else if (motor == MOTOR2) {
		MOTOR2_SPEED_REG = regValue;
	} else {
		//This isn't a valid motor
		;
	}
}