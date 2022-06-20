/*
 * matrix.c
 *
 * Created: 11/04/2018 8:46:10 PM
 *  
 */ 

#include <math.h>

#include "matrix.h"
#include "config.h"

/*
 * Populate an initialized Matrix with the rotation matrix based on angles phi, theta, psi.
 * Set isDegrees = 1 if the angles are in degrees, if in radians set isDegrees = 0.
 */

void construct_rotation_matrix(Matrix rMatrix, float phi, float theta, float psi, int isDegrees) {
	if (isDegrees) {
		phi *= DEG_2_RAD;
		theta *= DEG_2_RAD;
		psi *= DEG_2_RAD;
	}
	
	// Could do precomputed trig functions here as well
	//row 0
	rMatrix[0] = cos(psi) * cos (theta);
	rMatrix[1] = cos(theta) * sin(psi);
	rMatrix[2] = -sin(theta);
	//row 1
	rMatrix[3] = cos(psi) * sin(phi) * sin(theta) - cos(phi) * sin(psi);
	rMatrix[4] = cos(phi) * cos(psi) + sin(phi) * sin(psi) * sin(theta);
	rMatrix[5] = cos(theta) * sin(phi);
	//row 2
	rMatrix[6] = sin(phi) * sin(psi) + cos(phi) * cos(psi) * sin(theta);
	rMatrix[7] = cos(phi) * sin(psi) * sin(theta) - cos(psi) * sin(phi);
	rMatrix[8] = cos(phi) * cos(theta);
}

/*
 *https://en.wikipedia.org/wiki/Rotation_matrix#Axis_and_angle
 */
void angle_axis_to_rotation_matrix(Matrix rMatrix, Vector3 axis, float angle, int isDegrees) {
	if (isDegrees) {
		angle *= DEG_2_RAD;
	}
	
	float x = axis[X];
	float y = axis[Y];
	float z = axis[Z];
	float c = cos(angle);
	float s = sin(angle);
	float C = 1 - c;
	
	//row 0
	rMatrix[0] = x*x*C + c;
	rMatrix[1] = x*y*C - z*s;
	rMatrix[2] = x*z*C + y*s;
	//row 1
	rMatrix[3] = y*x*C + z*s;
	rMatrix[4] = y*y*C + c;
	rMatrix[5] = y*z*C - x*s;
	//row 2
	rMatrix[6] = z*x*C - y*s;
	rMatrix[7] = z*y*C + x*s;
	rMatrix[8] = z*z*C + c;
}

/*
 * Convert the current roll, pitch, and yaw to the matrix required to transform
 * the angular rates from body to world frame.
 */
void gyro_body_to_world_matrix(Matrix m, float phi, float theta, float psi, int isDegrees) {
	if (isDegrees) {
		phi *= DEG_2_RAD;
		theta *= DEG_2_RAD;
		psi *= DEG_2_RAD;
	}
	//I think it's slightly faster to precompute the trig functions.
	//Not really sure though
	float sPhi = sin(phi);
	float cPhi = cos(phi);
	float tTheta = tan(theta);
	float cTheta = cos(theta);
	m[0] = 1;
	m[1] = sPhi * tTheta;
	m[2] = cPhi * tTheta;
	
	m[3] = 0;
	m[4] = cPhi;
	m[5] = -sPhi;
	
	m[6] = 0;
	m[7] = sPhi / cTheta;
	m[8] = cPhi / cTheta;	
}

/* 
 * Evaluate result = m * v.
 * Answer will be in result. 
 */
void matrix_vector_multiply(Matrix m, Vector3 v, Vector3 result) {
	result[X] = m[0] * v[X] + m[1] * v[Y] + m[2] * v[Z];
	result[Y] = m[3] * v[X] + m[4] * v[Y] + m[5] * v[Z];
	result[Z] = m[6] * v[X] + m[7] * v[Y] + m[8] * v[Z];
}

/*
 * Evaluate v1 x v2 = result
 */
void vector_cross(Vector3 v1, Vector3 v2, Vector3 result) {
	result[X] = v1[Y] * v2[Z] - v1[Z] * v2[Y];
	result[Y] = -(v1[X] * v2[Z] - v1[Z] * v2[X]);
	result[Z] = v1[X] * v2[Y] - v1[Y] * v2[X];
}

/*
 * Evaluate v1 (dot) v2 and return result
 */
float vector_dot(Vector3 v1, Vector3 v2) {
	return v1[X] * v2[X] + v1[Y] * v2[Y] + v1[Z] * v2[Z];	
}

/*
 * Convert rates in gyroscope rates to angular velocities in world frame. 
 */
void gyro_rates_to_world_rates(short* gyroRates, Vector3 worldAngles, Vector3 worldRates) {
	Matrix D;
	Vector3 gyroRateVector;
	gyroRateVector[X] = gyroRates[X];
	gyroRateVector[Y] = gyroRates[Y];
	gyroRateVector[Z] = gyroRates[Z];
	
	gyro_body_to_world_matrix(D, worldAngles[X], worldAngles[Y], worldAngles[Z], DEGREES);
	matrix_vector_multiply(D, gyroRateVector, worldRates);
	
}

/*
 * Compute and return |vec|
 */
float calc_magnitude(Vector3 vec){
	return sqrtf(vec[X] * vec[X] + vec[Y] * vec[Y] + vec[Z] * vec[Z]);
}

/*
 * Convert a vector from degrees to radians
 */
void vector_to_radians(Vector3 vec) {
	vec[X] *= DEG_2_RAD;
	vec[Y] *= DEG_2_RAD;
	vec[Z] *= DEG_2_RAD;
}

/*
 * Transpose in and copy it into out. 
 */
void matrix_transpose(Matrix in, Matrix out) {
	out[0] = in[0];
	out[1] = in[3];
	out[2] = in[6];
	out[3] = in[1];
	out[4] = in[4];
	out[5] = in[7];
	out[6] = in[2];
	out[7] = in[5];
	out[8] = in[8];
}

	