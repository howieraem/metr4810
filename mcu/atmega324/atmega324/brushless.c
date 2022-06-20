/*
 * brushless.c
 *
 * Created: 23/03/2018 12:55:55 PM
 *  
 */ 

#include <avr/io.h>
#include "brushless.h"
#define F_CPU 8000000UL
#include <util/delay.h>

#define MAX_COUNT 20000
#define MOTOR0_SPEED_REG OCR1A
#define MOTOR1_SPEED_REG OCR1B

//Periods in ms
#define PWM_PERIOD 20
#define MAX_SPEED 100
#define MIN_SPEED -100


void motors_init(void) {
	DDRD |= (1 << PORTD5) | (1<< PORTD4);
	TCCR1A = (1 << COM1A1) | (1 << COM1B1) | (1 << WGM11); // clear OC1A on match + WGM mode 14
	TCCR1B = ((1 << WGM12) | (1 << WGM13) | (1 << CS11));	// WGM mode 14 (Fast PWM)
															// and 8x prescaler
	ICR1  = 20000;	//set ICR1 to produce 50Hz frequency
					//(8000000 / 8 / 20000 = 50hz)
	stop_motors();
	_delay_ms(5000); // some time for the esc to acquire signal or whatever
}

void stop_motors(void) {
	set_motor_speed(MOTOR0, 0);
	set_motor_speed(MOTOR1, 0);
}

void set_motor_speed(int motor, float speed) {
	//clamp speed between -100 to 100
	speed = speed > MAX_SPEED ? MAX_SPEED : speed;
	speed = speed < MIN_SPEED ? MIN_SPEED : speed;
	float period = speed * 0.005 + 1.5;
	set_motor_period(motor, period);
}

float get_motor_speed(int motor) {
	uint16_t regValue;
	if (motor = MOTOR0) {
		regValue = MOTOR0_SPEED_REG;
	} else if (motor = MOTOR1) {
		regValue = MOTOR1_SPEED_REG;
	}
	
	float period = regValue*1.0 / MAX_COUNT * PWM_PERIOD;
	return (period - 1.5) / 0.005;
}

void set_motor_period(int motor, float period) {
	uint16_t regValue = (uint16_t) (period*1.0/PWM_PERIOD * MAX_COUNT);
	if (motor == MOTOR0) {
		MOTOR0_SPEED_REG = regValue;
	} else if (motor == MOTOR1) {
		MOTOR1_SPEED_REG = regValue;
	} else {
		//This isn't a valid motor
	}
}
