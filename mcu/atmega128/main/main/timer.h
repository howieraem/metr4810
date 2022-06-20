/*
 * timer.h
 *
 * Created: 26/04/2018 6:46:21 PM
 *  
 */ 

#include <avr/io.h>

#ifndef TIMER_H_
#define TIMER_H_
#include "config.h"

#define PRESCALER 1024
#define CLOCK_PERIOD  1.0 / (F_CPU * 1.0 / PRESCALER)
#define TIMER1_TICK_TO_MS CLOCK_PERIOD * 1000.0

/*
 * Initilase the timer hardware
 */
void timer1_init(void);

/*
 * Return the current value of the timer
 */
uint16_t read_timer1(void);



#endif /* TIMER_H_ */