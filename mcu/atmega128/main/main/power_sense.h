/*
 * power_sense.h
 *
 * Created: 30/04/2018 5:20:55 PM
 *  
 */ 


#ifndef POWER_SENSE_H_
#define POWER_SENSE_H_

//******************************************************* UNTESTED *********************************************************************************************

/*
 * Initiliase the power sensing hardware
 */
void power_sense_init(void);

/*
 * Read the battery voltage
 */
uint16_t power_sense_read_battery_voltage(void); 

/*
 * Read the current from the battery
 */
uint16_t power_sense_read_battery_current(void); 


#endif /* POWER_SENSE_H_ */