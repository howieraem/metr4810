/*
 * atmega324.c
 *
 * Created: 22/03/2018 4:11:23 PM
 * 
 */ 

#include <avr/io.h>
#define F_CPU 8000000UL
#include <util/delay.h>
#include "i2c.h"
#include "serial.h"
#include "L3GD2Gyro.h"
#include "timer.h"
#include "brushless.h"
#include "matrix.h"
#include "MAG3110Magnetometer.h"

#define X 0
#define Y 1
#define Z 2

#define DEG_2_RAD 3.14159265358979 / 180.0


/*
 * I2C Connections.
 * PC0 is SCL, PC1 is SDA 
 */

int main(void)
{
	DDRA = 0xFF; //set port A as output for LEDs
	PORTA = 0x00;
	//initialize the i2c, serial, and timer
	i2c_init();
	//serial_init();
	//timer0_init();
	////motors_init();
//
	//uint8_t gyroAddress = 0b11010110; //address of the gyro in i2c
	//
	////enable the gyro (bring out of sleep mode)
	//enable_gyro(gyroAddress);
	
	enable_magnetometer();
	
	//short gyroRates[3]; //Values for the gyro speeds. Unsure of the units
	//Vector3 gyroRatesWorld;
	//Vector3 angles;
	//angles[X] = 0;
	//angles[Y] = 0;
	//angles[Z] = 0;
	//uint8_t currentTime; 
	//// currently set up to time up to 32.768 ms with accuracy 0.128 ms
	//uint8_t nextTime= read_timer0(); 
	//int dtCount; //measured in multiples of CLOCK_PERIOD
	//float dt; 
	//uint16_t counter = 0;
	//
	//short magnetVals[3];
	//float magValNorm[3];
    while (1) {
		//PORTA = 0x00;

		//_delay_ms(100);
		//PORTA = 0xFF;
		//_delay_ms(100);
		
		//counter++;
		//read_gyro(gyroAddress, gyroRates); //read the current speeds into gyroVals, takes 194us
		//currentTime = nextTime;
		//nextTime = read_timer0();
		//dtCount = nextTime > currentTime ? nextTime - currentTime : nextTime - currentTime + 256;
		//dt = CLOCK_PERIOD * dtCount; // delta time in seconds
		//
		//gyro_rates_to_world_rates(gyroRates, angles, gyroRatesWorld);
		//
		//angles[X] += gyroRatesWorld[X] * dt * RATE_2_DPS;
		//angles[Y] += gyroRatesWorld[Y] * dt * RATE_2_DPS;
		//angles[Z] += gyroRatesWorld[Z] * dt * RATE_2_DPS;
		//
		////set_motor_speed(MOTOR0, 5*angles[Y]);
		//
		//if (counter > 10) {
			//counter = 0;
			//read_magnetometer(magnetVals);
			////float magnitude = sqrtf(1.0*(magnetVals[0] * magnetVals[0] + magnetVals[1] * magnetVals[1] + magnetVals[2] * magnetVals[2]));
			//magValNorm[0] = magnetVals[0];
			//magValNorm[1] = magnetVals[1];
			//magValNorm[2] = magnetVals[2];
			//
			////serial_send_float_angles((float*) angles);
			//serial_send_both(angles, magValNorm);
		//}
		
    }
}

		/*
		 * Needs to be some functions in here that can take the angular rates in 
		 * gyroVals and estimate the angles based on the rates. 
		 *
		 * Will also need to know the dt of the loop. Need to set up a timer to measure this. 
		 * 
		 */
		
		//serial_send_gyro_vals( gyroVals); //optionally send the raw vals over serial
		