/*
 * debug_led.h
 *
 * Created: 26/04/2018 3:22:37 PM
 *  
 */ 


#ifndef DEBUG_LED_H_
#define DEBUG_LED_H_

#define RED_LED		PIND6
#define ORANGE_LED	PIND4
#define GREEN_LED	PIND5
#define LED_PORT	PORTD
#define LED_DDR		DDRD

#define ON 1
#define OFF 0

/*
 * Initialise all the DDR settings for the LEDs
 */
#define debug_led_init()			LED_DDR |= (1 << RED_LED) | (1 << ORANGE_LED) | (1 << GREEN_LED)

/*
 * Functions for controlling the LEDs
 */
#define debug_led_all_off()			LED_PORT &= ~((1 << RED_LED) | (1 << ORANGE_LED) | (1 << GREEN_LED))
#define debug_led_all_on()			LED_PORT |= (ON << RED_LED) | (ON << ORANGE_LED) | (ON << GREEN_LED)
#define debug_led_all_toggle()		LED_PORT ^= (ON << RED_LED) | (ON << ORANGE_LED) | (ON << GREEN_LED)

#define debug_led_red_on()			LED_PORT |= (ON << RED_LED)
#define debug_led_red_off()			LED_PORT &= ~(ON << RED_LED)
#define debug_led_red_toggle()		LED_PORT ^= (ON << RED_LED)

#define debug_led_orange_on()		LED_PORT |= (ON << ORANGE_LED)
#define debug_led_orange_off()		LED_PORT &= ~(ON << ORANGE_LED)
#define debug_led_orange_toggle()	LED_PORT ^= (ON << ORANGE_LED)

#define debug_led_green_on()		LED_PORT |= (ON << GREEN_LED)
#define debug_led_green_off()		LED_PORT &= ~(ON << GREEN_LED)
#define debug_led_green_toggle()	LED_PORT ^= (ON << GREEN_LED)



#endif /* DEBUG_LED_H_ */