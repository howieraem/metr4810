/*
 * sense.c
 *
 * Created: 11/04/2018
 * 
 */ 
#include "config.h"
#include "matrix.h"
#include "sense.h"

// Complementary filter parameters
#define CF_GAIN 0.97 // Best value to be determined
Vector3 cf_angles;
//cf_angles[X] = 0;
//cf_angles[Y] = 0;
//cf_angles[Z] = 0;

// Kalman Filter parameters
float Q_angle  =  0.01; // Process noise variance
float Q_gyro   =  0.0003; // Process noise variance
float R_angle  =  0.01; // Sensor noise variance
Vector3 bias; // Estimated bias (e.g. drift?)
//bias[X] = 0;
//bias[Y] = 0;
//bias[Z] = 0;

float Px[4], Py[4], Pz[4]; // Covariance matrices

Vector3 kf_angles; // Estimated angles
//kf_angles[X] = 0;
//kf_angles[Y] = 0;
//kf_angles[Z] = 0;


float* sense_complementary_filter(Vector3 magAngles, Vector3 gyroRates, float dt) {

    cf_angles[X] = CF_GAIN * (cf_angles[X] + gyroRates[X] * dt)
                   + (1 - CF_GAIN) * magAngles[X];
    cf_angles[Y] = CF_GAIN * (cf_angles[Y] + gyroRates[Y] * dt) 
                   + (1 - CF_GAIN) * magAngles[Y];
    cf_angles[Z] = CF_GAIN * (cf_angles[Z] + gyroRates[Z] * dt) 
                   + (1 - CF_GAIN) * magAngles[Z];

    return cf_angles;
}

float* sense_kalman_filter(Vector3 magAngles, Vector3 gyroRates, float dt) {
    // We should generalise here to avoid 3x repeat code

    Vector3  y, S;
    Vector3 K_0, K_1;

    // X
    // Prediction step
    kf_angles[X] += dt * (gyroRates[X] - bias[X]);

    Px[0] +=  - dt * (Px[2] + Px[1]) + Q_angle * dt;
    Px[1] +=  - dt * Px[3];
    Px[2] +=  - dt * Px[3];
    Px[3] +=    Q_gyro * dt;

    // Update step
    y[X] = magAngles[X] - kf_angles[X];
    S[X] = Px[0] + R_angle;
    K_0[X] = Px[0] / S[X];
    K_1[X] = Px[2] / S[X];

    kf_angles[X] +=  K_0[X] * y[X];
    bias[X]  +=  K_1[X] * y[X];
    Px[0] -= K_0[X] * Px[0];
    Px[1] -= K_0[X] * Px[1];
    Px[2] -= K_1[X] * Px[0];
    Px[3] -= K_1[X] * Px[1];

    // Y
    // Prediction step
    kf_angles[Y] += dt * (gyroRates[Y] - bias[Y]);

    Py[0] +=  - dt * (Py[2] + Py[1]) + Q_angle * dt;
    Py[1] +=  - dt * Py[3];
    Py[2] +=  - dt * Py[3];
    Py[3] +=    Q_gyro * dt;

    // Update step
    y[Y] = magAngles[Y] - kf_angles[Y];
    S[Y] = Py[0] + R_angle;
    K_0[Y] = Py[0] / S[Y];
    K_1[Y] = Py[2] / S[Y];

    kf_angles[Y] +=  K_0[Y] * y[Y];
    bias[Y]  +=  K_1[Y] * y[Y];
    Py[0] -= K_0[Y] * Py[0];
    Py[1] -= K_0[Y] * Py[1];
    Py[2] -= K_1[Y] * Py[0];
    Py[3] -= K_1[Y] * Py[1];

    // Z
    // Prediction step
    kf_angles[Z] += dt * (gyroRates[Z] - bias[Z]);

    Pz[0] +=  - dt * (Pz[2] + Pz[1]) + Q_angle * dt;
    Pz[1] +=  - dt * Pz[3];
    Pz[2] +=  - dt * Pz[3];
    Pz[3] +=    Q_gyro * dt;

    // Update step
    y[Z] = magAngles[Z] - kf_angles[Z];
    S[Z] = Pz[0] + R_angle;
    K_0[Z] = Pz[0] / S[Z];
    K_1[Z] = Pz[2] / S[Z];

    kf_angles[Z] +=  K_0[Z] * y[Z];
    bias[Z]  +=  K_1[Z] * y[Z];
    Pz[0] -= K_0[Z] * Pz[0];
    Pz[1] -= K_0[Z] * Pz[1];
    Pz[2] -= K_1[Z] * Pz[0];
    Pz[3] -= K_1[Z] * Pz[1];

    return kf_angles;
}

