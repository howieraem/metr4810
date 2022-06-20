/*
 * timer.h
 *
 * Created: 23/03/2018 9:24:09 AM
 *  
 */ 


#ifndef TIMER_H_
#define TIMER_H_

#define PRESCALER 1024
#define CLOCK_PERIOD  1.0 / (F_CPU * 1.0 / PRESCALER)

void timer0_init(void) {
	// set up timer with  prescaling
	TCCR0B |= (1 << CS02) | (1 << CS00);
	
	// initialize counter
	TCNT0 = 0;
}

uint8_t read_timer0(void) {
	return TCNT0;
}



#endif /* TIMER_H_ */