/*
 * timer.c
 *
 * Created: 22/05/2018 11:50:38 AM
 *  
 */ 


#include <avr/io.h>

#include "timer.h"
#include "config.h"

void timer1_init(void) {
	TCCR1B |= (1 << CS12) | (1 << CS10); //prescaler of 1024
	TCNT1 = 0;
}

uint16_t read_timer1(void) {
	return TCNT1;
}