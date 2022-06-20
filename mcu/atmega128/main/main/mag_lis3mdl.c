/*
 * mag_lis3mdl.c
 *
 * Created: 26/04/2018 4:21:21 PM
 *  
 */ 

#include <inttypes.h>
#include "mag_lis3mdl.h"
#include "i2c_common.h"
#include "config.h"

void mag_init(void) {
	//configure this to be whatever setup we want
	mag_write_register(CTRL_REG3_ADDR_MAG, 0b00000000);
}

void mag_read_values (short* values) {
	mag_read_block(OUT_X_L_ADDR_MAG, 6, (uint8_t*) values);
}

