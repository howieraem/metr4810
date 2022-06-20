/*
 * ocs.h
 *
 * Created: 30/04/2018 12:55:31 PM
 *  
 */ 

#include "matrix.h"

#ifndef OCS_H_
#define OCS_H_

/*
 * Initilise the power to the ocs module
 */
void ocs_power_init(void);

/*
 * Power cycle the ocs module
 */
void ocs_power_cycle(void);

/*
 * Cut power to ocs module
 */
void ocs_power_off(void);

/*
 * Enable power to ocs module
 */
void ocs_power_on(void);

/*
 * Initialise the control algorithms for orientation control
 */
void ocs_init(void);

/*
 * Step the ocs algorithm. Should be called repeatedly
 */
void ocs_spin_control(void);

/*
 * Do the control algorithm based on the current and desired poses
 */
void ocs_run_control(Vector3 currentWorld, Vector3 desiredWorld);

/*
 * Compute the torque vector required to get from current to desired angles. 
 * Returns the angle that must be rotated. 
 */
float ocs_compute_torque_vector(Vector3 currentAngles, Vector3 desiredAngles, int isDegrees, Vector3 torqueVectorTelescope);

/*
 * Set the current target for the control system
 */
void ocs_set_target(Vector3 target);

/*
 * Get the current target for the control system
 */
void ocs_get_target(Vector3 target);

/*
 * Enable the ocs system
 */
void ocs_enable(void);

/*
 * Disable the ocs system
 */
void ocs_disable(void);

/*
 * Returns 1 if stable around the setpoint
 */
uint8_t ocs_check_if_on_target(void);

/*
 * Reset the control algorithms
 */
void ocs_reset(void);

/*
 * Set the target to 0,0
 */
void ocs_clear_target(void);

#endif /* OCS_H_ */