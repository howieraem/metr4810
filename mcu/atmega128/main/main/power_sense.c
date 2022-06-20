/*
 * power_sense.c
 *
 * Created: 30/04/2018 5:21:17 PM
 *  
 */ 
#include <avr/io.h>


//******************************************************* UNTESTED *********************************************************************************************
#define	ADC_0 0
#define	ADC_1 1
#define	ADC_2 2
#define	ADC_3 3
#define	ADC_4 4
#define	ADC_5 5
#define	ADC_6 6
#define	ADC_7 7

void power_sense_init(void) {
	ADCSRA = (1<<ADEN | 1<<ADPS2 | 1<<ADPS1 | 1<<ADPS0);
	ADMUX=(1<<REFS0 | ADC_7);
	
	// Start conversions
	ADCSRA |= (1<<ADSC);
	while(ADCSRA & (1<<ADSC)) {
		; /* Wait until conversion finished */
	}
}


uint16_t power_sense_read_battery_voltage(void) {

	ADMUX = (1<<REFS0 | ADC_7);
	// Start the ADC conversion for PINF7
	ADCSRA |= (1<<ADSC);
	while(ADCSRA & (1<<ADSC)) {
		; /* Wait until conversion finished */
	}
	uint16_t reading = ADC;
	return reading;
}

uint16_t power_sense_read_battery_current(void) {

	ADMUX = (1<<REFS0 | ADC_6);
	// Start the ADC conversion for PINF6
	ADCSRA |= (1<<ADSC);
	while(ADCSRA & (1<<ADSC)) {
		; /* Wait until conversion finished */
	}
	uint16_t reading = ADC;
	return reading;
}


