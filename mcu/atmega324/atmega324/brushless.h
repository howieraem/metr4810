/*
 * brushless.h
 *
 * Created: 23/03/2018 12:50:39 PM
 *  
 */ 


#ifndef BRUSHLESS_H_
#define BRUSHLESS_H_

#define MOTOR0 0
#define MOTOR1 1

void motors_init(void);
void set_motor_period(int motor, float period);
void set_motor_speed(int motor, float speed);
void stop_motors(void);
float get_motor_speed(int motor);

#endif /* BRUSHLESS_H_ */