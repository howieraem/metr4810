/*
 * serial.h
 *
 * Created: 26/04/2018 3:43:49 PM
 *  
 */ 

#include "matrix.h"

#ifndef SERIAL_H_
#define SERIAL_H_

#define SERIAL_PUTTY

//chars for message line
#define SERIAL_STX '$'
#define SERIAL_ETX '\n'

//chars for command types
#define ORIENTATION_TYPE 'o'
#define POWER_CYCLE_TYPE 'p'
//#define SEARCH_MODE_TYPE 'm'
//#define CALIBRATE_TYPE 'c'
#define DEBUG_LED_TYPE 'l'
#define TELESCOPE_COORD_OVERRIDE_TYPE 'c'

//chars for measurement types
#define RAW_RATES_TYPE 'f'
#define GYROSCOPE_TYPE 'r'
#define ELECTRICAL_TYPE 'v'

#define START_STOP_COMMAND_TYPE 's'
#define PICTURE_TIME_TYPE 'y'
#define MANUAL_GYRO_CALIBRATION_OVERRIDE_TYPE 'm'
#define ROLL_ONLY_OVERRIDE_TYPE 'r'

#define DEBUG_PRINTF_TYPE 'w'

/*
 * Data that could be in a message
 */
typedef union MessageData {
	float angles[3];
	uint8_t value;
} MessageData;

/*
 * A struct for storing different message types and there data
 */
typedef struct SerialMessage {
	char messageType;
	MessageData data;
} SerialMessage;

/*
 * Send the current pose angles
 */
#define serial_send_angles(angles) serial_send_orientation_info(GYROSCOPE_TYPE, angles)

/*
 * Send the raw gyroscope velocities
 */
#define serial_send_raw_rates(rates) serial_send_orientation_info(RAW_RATES_TYPE, rates)

/*
 * Initialise the serial hardware
 */
void serial_init(void);

/*
 * Send a byte
 */
void serial_send_byte(uint8_t byte);

/*
 * Send the bytes of a float
 */
void serial_send_float(float value);

/*
 * Send a full vector
 */
void serial_send_vector(Vector3 data);

/*
 * Receive a byte from serial
 */
unsigned char serial_receive_byte( void );

/*
 * Get the last message received over serial
 */
SerialMessage serial_get_last_message(void);	

/*
 * Send the electrical info over serial
 */
void serial_send_electrical_info(float iReading, float vReading);

/*
 * Send info about orientation
 */
void serial_send_orientation_info(char key, Vector3 data);

/*
 * Reply to a command to confirm
 */
void serial_reply_to_command(char key);

/*
 * Send a request for a picture
 */
void serial_send_picture_request(void);

/*
 * Will return 1 if a message has been received, 0 otherwise
 */
int serial_check_message_received(void);

/*
 * Print a general string to the serial bus
 */
void serial_printf(const char* format, ...);

#endif /* SERIAL_H_ */