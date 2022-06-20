/*
 * img_tele_power.c
 *
 * Created: 29/04/2018 2:52:38 PM
 *  
 */ 

#include <avr/io.h>
#include "config.h"
#include <util/delay.h>
#include "img_tele_power.h"

void img_tele_power_init(void) {
	DDRC |= (1 << IMG_PWR_CTL_PIN) | (1 << IMG_SHT_CTL_PIN) | (1 << IMG_CAM_CTL_PIN);
	img_tele_power_on();
	img_tele_shutdown_on();
	img_tele_camera_on();
}

void img_tele_power_cycle(void) {
	img_tele_power_off();
	_delay_ms(POWER_CYCLE_TIME);
	img_tele_power_on();
}

void img_tele_shutdown_cycle(void) {
	img_tele_shutdown_off();
	_delay_ms(POWER_CYCLE_TIME);
	img_tele_shutdown_on();
}

void img_tele_camera_cycle(void) {
	img_tele_camera_off();
	_delay_ms(POWER_CYCLE_TIME);
	img_tele_camera_on();
}
