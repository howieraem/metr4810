/*
 * main.c
 *
 * Created: 13/04/2018 2:17:23 PM
 * 
 */ 
#include "config.h"

#include <util/delay.h>
#include <avr/io.h>
#include <stdio.h>
#include <avr/interrupt.h>
#include <avr/eeprom.h>

#include "debug_led.h"
#include "imu.h"
#include "serial.h"
#include "matrix.h"
#include "ocs.h"
#include "brushless.h"
#include "img_tele_power.h"
#include "adc.h"

#include "mag_lis3mdl.h"
#include "gyro_fxas21002.h"

#define ENABLED 1
#define DISABLED 0
#define SPIN_DOWN 2


/*
 * Initialise all of the hardware
 */
void hardware_init(void);

/*
 * Run the message handling. Should be called repeatedly
 */
void message_handling(void);

/*
 * Disable the system except for serial comms
 */
void disable_system(void);

/*
 * Enable the system 
 */
void enable_system(void);

/*
 * Spin down the motors in the system
 */
void spin_down_system(void);

void test_motor_slew_rate(void);

uint8_t systemEnabled; //flag for enabling the system
int pitchSpeed, yawSpeed, pitchDir, yawDir;

/*
 * Power cycle the raspberry pi
 */
void pi_power_cycle(void) {
	img_tele_power_off();
	_delay_ms(2000);
	img_tele_power_on();
}


int main(void) {
	hardware_init();
	
	systemEnabled = DISABLED;
	
	ocs_clear_target();

	uint16_t counter = 0;
	
	while (1) {
		imu_spin();
		counter += 1;
		if (counter == OCS_CONTROL_PERIOD / MAIN_LOOP_TIME_DELAY) {
			counter = 0;
			message_handling();
			if (systemEnabled == ENABLED) {
				if (brushless_check_danger()) {
					serial_printf("DANGER! High speeds detected. Disabling system.");
					disable_system();
				} else {
					ocs_spin_control();
				}
			} else if (systemEnabled == SPIN_DOWN) {
				serial_printf("Speeds: %d, %d", pitchSpeed, yawSpeed);
				if (fabs(pitchSpeed) > 0) {
					pitchSpeed -= pitchDir;
				}
				if (fabs(yawSpeed) > 0) {
					yawSpeed -= yawDir;
				}
				brushless_set_motor_speed(PITCH_MOTOR, pitchSpeed);
				brushless_set_motor_speed(YAW_MOTOR, yawSpeed);
				if (fabs(pitchSpeed) <= SPIN_DOWN_THRESH && fabs(yawSpeed) <= SPIN_DOWN_THRESH) {
					disable_system();
				}
				_delay_ms(100);
			} else {
				debug_led_orange_toggle();
				debug_led_green_toggle();
			}
		}
		_delay_ms(MAIN_LOOP_TIME_DELAY);
    }
}

void disable_system(void) {
	serial_printf("Disabling main system!");
	systemEnabled = DISABLED;
	ocs_disable();
	brushless_stop_motors();
	debug_led_all_off();
}

void enable_system(void) {
	serial_printf("Enabling main system!");
	systemEnabled = ENABLED;
	debug_led_all_off();
	imu_reset();
	brushess_reset();
	ocs_reset();
}

void spin_down_system(void) {
	serial_printf("Spinning down system!");
	systemEnabled = SPIN_DOWN;
	pitchSpeed = brushless_get_motor_speed(PITCH_MOTOR);
	yawSpeed = brushless_get_motor_speed(YAW_MOTOR);
	
	pitchDir = pitchSpeed > 0 ? 1 : -1;
	yawDir = yawSpeed > 0 ? 1 : -1;
}

uint16_t lastTakePictureCounter = 0;
uint16_t lastOrientationSendCounter = 0;
int motorSpeedSendCounter = 0;

void message_handling(void) {
	SerialMessage msg;
	Vector3 targetAngles, worldAngles;
	targetAngles[X] = 0;
	targetAngles[Y] = 0;
	targetAngles[Z] = 0;
	float vBatt;
	Vector3 newAngles, rawRatesVector;
	short rawRates[3];
	float angle;
	int yawSpeedSend, pitchSpeedSend;
	if (SEND_ANGLES) {
		if (lastOrientationSendCounter == 0) {
			imu_read_angles(worldAngles);
			gyro_read_raw_rates(rawRates);
			rawRatesVector[X] = (float) rawRates[X];
			rawRatesVector[Y] = (float) rawRates[Y];
			rawRatesVector[Z] = (float) rawRates[Z];
			
			serial_send_angles(worldAngles);
			serial_send_raw_rates(rawRatesVector);
			motorSpeedSendCounter++;
			if (motorSpeedSendCounter == 5) {
				pitchSpeedSend =  brushless_get_motor_speed(PITCH_MOTOR);
				yawSpeedSend = brushless_get_motor_speed(YAW_MOTOR);
				serial_printf("Motor Speeds: %d, %d", pitchSpeedSend, yawSpeedSend);
				motorSpeedSendCounter = 0;
			}
		}

		lastOrientationSendCounter++;
		if (lastOrientationSendCounter >= TELEM_SEND_PERIOD / LOOP_TIME_DELAY) {
			lastOrientationSendCounter = 0;
		}
	}
	
	if (lastTakePictureCounter > 0) {
		lastTakePictureCounter += 1;
	}
	
	if (lastTakePictureCounter >= PICTURE_REQUEST_PERIOD / LOOP_TIME_DELAY ) {
		lastTakePictureCounter = 0;
	}
	
	if (ocs_check_if_on_target()) {
		// we are stable on the target
		// need to notify the telescope to take a photo
		if (lastTakePictureCounter == 0) {
			serial_send_picture_request();
			lastTakePictureCounter += 1;
		}
	}
	
	if (serial_check_message_received()) {
		msg = serial_get_last_message();
		
		switch (msg.messageType) {
			case ORIENTATION_TYPE:
				targetAngles[Y] = msg.data.angles[0];
				targetAngles[Z] = msg.data.angles[1];
				ocs_set_target(targetAngles);
				break;
			case POWER_CYCLE_TYPE:
				if (msg.data.value == 0) {
					cli();
					imu_read_angles(worldAngles); //store the current angles
					brushless_stop_motors();
					ocs_power_cycle();
					imu_init();
					sei();
					_delay_ms(1000); // not sure why this is needed. Seems required
					imu_set_current_angles(worldAngles); //reset the orientation
				} else if (msg.data.value == 1) {
					pi_power_cycle();
				}
				break;
			case TELESCOPE_COORD_OVERRIDE_TYPE:
				newAngles[X] = msg.data.angles[0];
				newAngles[Y] = msg.data.angles[1];
				newAngles[Z] = msg.data.angles[2];
				ocs_disable(); //shouldn't be necessary but do it anyway
				ocs_set_target(newAngles);
				imu_set_current_angles(newAngles);
				ocs_enable();
				break;
			case ELECTRICAL_TYPE:
				vBatt = battery_get_voltage();
				serial_send_electrical_info(0.0, vBatt);
				break;
			case START_STOP_COMMAND_TYPE:
				if (msg.data.value == 0) {
					//SUSPEND EVERYTHING EXCEPT SERIAL
					disable_system();
				} else if (msg.data.value == 1) {
					//RESTART CLEANLY
					enable_system();
				} else if (msg.data.value == 50) {
					//SPIN THE MOTORS DOWN
					spin_down_system();
				} else if (msg.data.value == 100) {
					//force gyro calibration
					gyro_force_calibration();
					
				}
				break;
				
			case MANUAL_GYRO_CALIBRATION_OVERRIDE_TYPE:
				cli();
				gyro_set_offsets((short) (msg.data.angles[X]), (short) (msg.data.angles[Y]), (short) (msg.data.angles[Z]));
				newAngles[X] = 0;
				newAngles[Y] = 0;
				newAngles[Z] = 0;
				ocs_disable(); //shouldn't be necessary but do it anyway
				ocs_set_target(newAngles);
				imu_set_current_angles(newAngles);
				ocs_enable();
				sei();
				break;
				
			case ROLL_ONLY_OVERRIDE_TYPE:
				angle = msg.data.angles[0];
				imu_overwrite_roll(angle);
				break;
		}
	}
}

void hardware_init(void) {
	ocs_power_init();
	ocs_power_off();
	
	debug_led_init();
	debug_led_all_off();
	
	adc_init();
	
	serial_init();
	float vBatt = battery_get_voltage();
	if ( vBatt <= BATTERY_MIN_VOLTAGE) {
		debug_led_all_off();
		ocs_power_off();
		while(1) {
			debug_led_red_toggle();
			serial_printf("Low Voltage (x1000): %5d\n", (int) (vBatt*1000));
			_delay_ms(100);
		}
	}
		
	ocs_power_on();
		
	img_tele_power_init();
	
	ocs_init();
	debug_led_orange_on();
	_delay_ms(MOTOR_ARMING_TIME); // wait for the motors to prime
	debug_led_green_on();
	serial_init();
	imu_init();
	sei();
	_delay_ms(1000); // not sure why this is needed. Seems required
	debug_led_all_off();
	
	
	
}

void test_motor_slew_rate(void) {
	int speed = 0;
	//int changeMag = 1;
	//int max_speed = 20;
	//int min_speed = -20;
	int motor = YAW_MOTOR;
	//int motor1 = PITCH_MOTOR;
	while (1) {
		speed = 20  ;
		brushless_set_motor_speed(motor, (float) (speed));

		debug_led_orange_toggle();
		_delay_ms(100);
	}
}
