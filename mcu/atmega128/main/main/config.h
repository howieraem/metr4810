/*
 * config.h
 *
 * Created: 29/04/2018 4:24:31 PM
 *  
 */ 


#ifndef CONFIG_H_
#define CONFIG_H_

#define F_CPU 8000000UL//7820000UL// 

#define ECHO_SERIAL 0

#define MOTORS_CONNECTED 1
#define DISABLE_ROLL 0
#define ENABLE_GYRO_CALIBRATION 0

#define SEND_ANGLES 1

#define BATTERY_MIN_VOLTAGE 0.0
#define COUNT_BEFORE_KILL 20
#define POWER_CYCLE_TIME 2000 // time between off and on in ms
#define MOTOR_ARMING_TIME 3000 // time for motors to arm in ms


#define TARGET_ANGLE_THRESHOLD 2 // plus or minus this much is on target
#define STABILITY_TIME_THRESHOLD 1000 // ms for which it must be stable before considered on target

#define MAIN_LOOP_TIME_DELAY 1 // main loop runs every this many ms
#define LOOP_TIME_DELAY 50 // main loop runs every this many ms
#define PICTURE_REQUEST_PERIOD 4000 // picture requests will be sent at most every this many ms
#define TELEM_SEND_PERIOD 200 // period for sending the telemetry information if enabled
#define OCS_CONTROL_PERIOD 50

#define SPIN_DOWN_THRESH 0 // motors will turn off when they get below this speed

//PID Constants for the OCS module
#define KpX 0.1			//ROLL Proportional
#define KpY 1.5//0.1	//PITCH Proportional
#define KpZ 1.5//1.5	//YAW Proportional

#define KdX 0.0			//ROLL Derivative
#define KdY 1.5//2.0	//PITCH Derivative
#define KdZ 1.5			//YAW Derivative

//brushless motor PID constants
#define Kp 0.5
#define Kd 0.005
#define Ki 0.03
#define Kbias 0//0.001 

//Used for vector indexing
#define X 0
#define Y 1
#define Z 2
#define ROLL X
#define PITCH Y
#define YAW Z

#define ROLL_MOTOR MOTOR0 //IF MOTORS ARE WIRED INCORRECTLY CHANGE THIS
#define PITCH_MOTOR MOTOR2 //MOTOR2 
#define YAW_MOTOR MOTOR1 //MOTOR1

#define ROLL_MOTOR_DIR -1
#define PITCH_MOTOR_DIR -1
#define YAW_MOTOR_DIR 1

#define ABSOLUTE_MAX_SPEED 50
#define MAX_SPEED ABSOLUTE_MAX_SPEED
#define MIN_SPEED -ABSOLUTE_MAX_SPEED


#endif /* CONFIG_H_ */