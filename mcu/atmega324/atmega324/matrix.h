/*
 * matrix.h
 *
 * Created: 24/03/2018 12:32:47 PM
 *  
 */ 

#ifndef MATRIX_H_
#define MATRIX_H_

#define DEG_2_RAD 3.14159265358979 / 180.0

//Used for indexing Vectors
#define X 0
#define Y 1
#define Z 2

#define DEGREES 1
#define RADIANS 0

/*
Matrix supports a 3x3 matrix (usually rotation matrix). 
Will be stored in a float array as follows:
[ 0 1 2;
  3 4 5;
  6 7 8]
  
  Constructors are based on coordinate system here: http://www.chrobotics.com/library/understanding-euler-angles
  
  
 */

typedef float Matrix[9];
typedef float Vector3[3];


/*
 * Populate an initialised Matrix with the rotation matrix based on angles phi, theta, psi.
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

void gyro_rates_to_world_rates(short* gyroRates, Vector3 worldAngles, Vector3 worldRates) {
	Matrix D;
	Vector3 gyroRateVector;
	gyroRateVector[X] = gyroRates[X];
	gyroRateVector[Y] = gyroRates[Y];
	gyroRateVector[Z] = gyroRates[Z];
	
	gyro_body_to_world_matrix(D, worldAngles[X], worldAngles[Y], worldAngles[Z], DEGREES);
	matrix_vector_multiply(D, gyroRateVector, worldRates);
	
}

#endif /* MATRIX_H_ */