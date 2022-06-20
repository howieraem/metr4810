/*
 * mag_lis3mdl.c
 *
 * Created: 26/04/2018 4:21:21 PM
 *  
 */ 

#include <inttypes.h>
#include "mag_mag3110.h"
#include "i2c_common.h"
#include "config.h"

void mag3110_init(void) {
	//configure this to be whatever setup we want
	mag3110_write_register(CTRL_REG1_ADDR_MAG3110, 0x01);
	mag3110_write_register(CTRL_REG2_ADDR_MAG3110, 0x80);
}

void mag3110_read_values (short* values) {
	mag3110_read_block(OUT_X_L_ADDR_MAG3110, 6, (uint8_t*) values);
}

