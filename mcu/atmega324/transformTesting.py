from math import cos, sin, tan
DEG_2_RAD = 3.14159265358979 / 180
X,Y,Z = 0,1,2

def construct_rotation_matrix(rMatrix, phi, theta, psi, isDegrees):
	if (isDegrees):
		phi *= DEG_2_RAD;
		theta *= DEG_2_RAD;
		psi *= DEG_2_RAD;
	
	
	# Could do precomputed trig functions here as well
	#row 0
	rMatrix[0] = cos(psi) * cos (theta);
	rMatrix[1] = cos(theta) * sin(psi);
	rMatrix[2] = -sin(theta);
	#row 1
	rMatrix[3] = cos(psi) * sin(phi) * sin(theta) - cos(phi) * sin(psi);
	rMatrix[4] = cos(phi) * cos(psi) + sin(phi) * sin(psi) * sin(theta);
	rMatrix[5] = cos(theta) * sin(phi);
	#row 2
	rMatrix[6] = sin(phi) * sin(psi) + cos(phi) * cos(psi) * sin(theta);
	rMatrix[7] = cos(phi) * sin(psi) * sin(theta) - cos(psi) * sin(phi);
	rMatrix[8] = cos(phi) * cos(theta);

def matrix_vector_multiply(m, v):
	result = [0,0,0]
	result[X] = m[0] * v[X] + m[1] * v[Y] + m[2] * v[Z]
	result[Y] = m[3] * v[X] + m[4] * v[Y] + m[5] * v[Z]
	result[Z] = m[6] * v[X] + m[7] * v[Y] + m[8] * v[Z]
	return result

def print_matrix(m):
	print "Matrix: "
	print "[ %0.2f \t %0.2f \t %0.2f" % (m[0], m[1],m[2]) 
	print "  %0.2f \t %0.2f \t %0.2f" % (m[3], m[4],m[5]) 
	print "  %0.2f \t %0.2f \t %0.2f]" % (m[6], m[7],m[8]) 

if __name__ == "__main__":
	rMatrix =  [1,0,0,
			 	0,1,0,
			 	0,0,1]

	construct_rotation_matrix(rMatrix, 45,0,0,True)
	print_matrix(rMatrix)
	v = [0,1,0]
	print( matrix_vector_multiply(rMatrix, v))