/*
 * brushless.h
 *
 * Created: 23/03/2018 12:50:39 PM
 *  
 */ 

#include "matrix.h"
#ifndef BRUSHLESS_H_
#define BRUSHLESS_H_



#define MOTOR0 0 
#define MOTOR1 1
#define MOTOR2 2

/*
 * Initialise the brushless motor esc PWM signals
 */
void brushless_motors_init(void);

/*
 * Set a  motor to a given period in ms
 */
void brushless_set_motor_period(int motor, float period);

/*
 * Set a  motor to a speed from -100 to 100
 */
void brushless_set_motor_speed(int motor, float speed); 

/*
 * Set all motor speeds to 0
 */
void brushless_stop_motors(void);

/*
 * Return the current speed of the motor calculated from the PWM register
 */
float brushless_get_motor_speed(int motor);

/*
 * Run the control algorithm for generating torques. The elements in power
 * correspond to the amount of torque required in each axis. 
 */
void brushless_generate_torque(Vector3 power);

/*
 * Reset the brushless motors to 0 speed and clear all the history
 */
void brushess_reset(void);

/*
 * Will return 1 if the motors have been spinning at a high speed.
 * Returns 0 otherwise. 
 */
uint8_t brushless_check_danger(void);

/*
 * Spin the motors down slowly 
 */
void brushless_spin_down(void);
#endif /* BRUSHLESS_H_ */