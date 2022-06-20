/*
 * imu.h
 *
 * Created: 26/04/2018 7:13:05 PM
 *  
 */ 

#include "matrix.h"

#ifndef IMU_H_
#define IMU_H_

/*
 * Initiaise the imu 
 */
void imu_init(void);

/*
 * Spin the imu. This will read the last values that have been saved and 
 * compute the new pose. Should be called repeatedly.
 */
void imu_spin(void);

/*
 * Get the current angles of the telescope. Will populate angles
 */
void imu_read_angles(Vector3 angles);

/* 
 * Read the angular rates of the telescope in telescope frame
 */
void imu_read_body_rates(Vector3 rates);

/*
 * Overwrite the current angles and set the current pose to angles
 */
void imu_set_current_angles(Vector3 angles); 

/*
 * Reset the imu
 */
void imu_reset(void);

/*
 * This should be called in an interrupt triggered whenever there is new data to read from a sensor
 */
void imu_new_data_interrupt(void);

/*
 * Overwrite the roll angle
 */
void imu_overwrite_roll(float angle);
#endif /* IMU_H_ */