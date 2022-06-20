/*
 * adc.h
 *
 * Created: 26/04/2018 3:21:12 PM
 *  
 */ 


#ifndef ADC_H_
#define ADC_H_

#define	ADC_0 0
#define	ADC_1 1
#define	ADC_2 2
#define	ADC_3 3
#define	ADC_4 4
#define	ADC_5 5
#define	ADC_6 6
#define	ADC_7 7

// ADC setup
void adc_init(void) {
	ADCSRA = (1<<ADEN | 1<<ADPS2 | 1<<ADPS1 | 1<<ADPS0);
	ADMUX=(1<<REFS0 | ADC_7);
	
	// Start conversions
	ADCSRA |= (1<<ADSC);
	while(ADCSRA & (1<<ADSC)) {
		; /* Wait until conversion finished */
	}
}

uint16_t readADC7(void) {

	ADMUX = (1<<REFS0 | ADC_7);
	// Start the ADC conversion for PINF7
	ADCSRA |= (1<<ADSC);
	while(ADCSRA & (1<<ADSC)) {
		; /* Wait until conversion finished */
	}
	uint16_t reading = ADC;
	return reading;
}

uint16_t readADC6(void) {

	ADMUX = (1<<REFS0 | ADC_6);
	// Start the ADC conversion for PINF6
	ADCSRA |= (1<<ADSC);
	while(ADCSRA & (1<<ADSC)) {
		; /* Wait until conversion finished */
	}
	uint16_t reading = ADC;
	return reading;
}

/*
 * Connected as:
 *
 *		VBatt
 *		18 k
 *		ADC7
 *      10 k
 *		GND
 *
 *	Voltage at ADC7 = VBatt * (10/28)
 *  10 bit max value: 1024
 *	ADC7 Voltage to ADC7 Reading : V = 3.3 / 1024 * count
 */
float battery_get_voltage() {
	uint16_t count = readADC7();
	float voltageAtAdc7 = 3.3 / 1024.0 * count;
	float vBatt = voltageAtAdc7 * 28.0 / 10.0;
	vBatt /= 1.0327;
	return vBatt;	
}



#endif /* ADC_H_ */