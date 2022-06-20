/*
 * matrix.h
 *
 * Created: 24/03/2018 12:32:47 PM
 *  
 */ 

#ifndef MATRIX_H_
#define MATRIX_H_

#include <math.h>

#define PI 3.14159265358979
#define DEG_2_RAD 3.14159265358979 / 180.0
#define RAD_2_DEG 180.0 / 3.14159265358979 


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
 * Populate an initialized Matrix with the rotation matrix based on angles phi, theta, psi.
 * Set isDegrees = 1 if the angles are in degrees, if in radians set isDegrees = 0.
 */

void construct_rotation_matrix(Matrix rMatrix, float phi, float theta, float psi, int isDegrees);
void angle_axis_to_rotation_matrix(Matrix rMatrix, Vector3 axis, float angle, int isDegrees);
void gyro_body_to_world_matrix(Matrix m, float phi, float theta, float psi, int isDegrees);

/* 
 * Evaluate result = m * v.
 * Answer will be in result. 
 */
void matrix_vector_multiply(Matrix m, Vector3 v, Vector3 result);
void vector_cross(Vector3 v1, Vector3 v2, Vector3 result);
float vector_dot(Vector3 v1, Vector3 v2);
void gyro_rates_to_world_rates(short* gyroRates, Vector3 worldAngles, Vector3 worldRates);
float calc_magnitude(Vector3 vec);
void vector_to_radians(Vector3 vec);
void matrix_transpose(Matrix in, Matrix out);
#endif /* MATRIX_H_ */