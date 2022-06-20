/*
 * sense.h
 *
 * Created: 11/04/2018
 *  
 */

#ifndef SENSE_H_
#define SENSE_H_

#include "matrix.h"

float* sense_complementary_filter(Vector3 magAngles, Vector3 gyroRates, float dt);
float* sense_kalman_filter(Vector3 magAngles, Vector3 gyroRates, float dt);

#endif
