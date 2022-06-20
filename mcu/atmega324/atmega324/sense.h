/*
 * sense.h
 *
 * Created: 11/04/2018
 *  
 */

#ifndef SENSE_H_
#define SENSE_H_

float complementary_filter(Vector3 magAngles, Vector3 gyroRates, float dt);
float kalman_filter(Vector3 accAngle, Vector3 gyroRate, float dt);

#endif
