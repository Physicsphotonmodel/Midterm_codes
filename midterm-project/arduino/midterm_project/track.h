/***************************************************************************/
// File       [track.h]
// Author     [Lumos, Hsinchi]
// Synopsis   [Code used for line tracking]
// Functions  [MotorWriting, Tracking_P, Tracking_PD]
// Modify     [2026/04/05 Lumos]
/***************************************************************************/

int extern Tp; // Defined in midterm_project.ino

/*
 * Translates desired Left/Right speeds into hardware-specific PWM 
 * and directional pin logic for the TB6612 motor driver.
 */
void MotorWriting(double vL, double vR) {
    if (vR < 0) {
        digitalWrite(MotorR_I3, LOW);
        digitalWrite(MotorR_I4, HIGH);
        vR = -vR;
    } else if (vR > 0) {
        digitalWrite(MotorR_I3, HIGH);
        digitalWrite(MotorR_I4, LOW);
    }

    if (vL < 0) {
        digitalWrite(MotorL_I1, LOW);
        digitalWrite(MotorL_I2, HIGH);
        vL = -vL;
    } else if (vL > 0) {
        digitalWrite(MotorL_I1, HIGH);
        digitalWrite(MotorL_I2, LOW);
    }

    analogWrite(MotorL_PWM, vL);
    analogWrite(MotorR_PWM, vR);
}

/*
 * Proportional (P) control line tracking algorithm.
 * Features line-loss recovery to smoothly return the vehicle to the track.
 */
void Tracking_P(int l3, int l2, int m, int r2, int r3) {
    double sum = l3 + l2 + m + r2 + r3;
    static double last_error = 0; 

    // Line-loss recovery mechanism
    if (sum == 0) {
        if (last_error > 0) {
            MotorWriting(150, 0); 
        } else if (last_error < 0) {
            MotorWriting(0, 150); 
        } else {
            MotorWriting(100, 100); 
        }
        return;
    }

    double error = 0;
    double w2 = 8, w3 = 12;
    double Kp = 25;

    error = (l3 * (-w3) + l2 * (-w2) + m * (0) + r2 * (w2) + r3 * (w3)) / sum;
    last_error = error; 

    double powerCorrection = Kp * error;
    int vL = (Tp + powerCorrection);
    int vR = (Tp - powerCorrection);

    // Limit power bounds (prevent reverse rotation during high-speed tracking)
    if (vL > 255) vL = 255; else if (vL < 0) vL = 0;
    if (vR > 255) vR = 255; else if (vR < 0) vR = 0;

#if DEBUG
    Serial3.print("vL/vR: ");
    Serial3.print(vL);
    Serial3.print(" ");
    Serial3.println(vR);
#endif

    MotorWriting(vL, vR);
}

/*
 * Proportional-Derivative (PD) control line tracking algorithm.
 */
void Tracking_PD(int l3, int l2, int m, int r2, int r3) {
    double sum = l3 + l2 + m + r2 + r3;
    
    double w2 = 4;
    double w3 = 8;
    double error = 0;
    static double lastError = 0;
    if (sum == 0) {
        if (lastError > 0) {
            MotorWriting(150, 0); 
        } else if (lastError < 0) {
            MotorWriting(0, 150); 
        } else {
            MotorWriting(100, 100); 
        }
        return;
    }

    
    error = (l3 * (-w3) + l2 * (-w2) + m * (0) + r2 * (w2) + r3 * (w3)) / sum;

    double Kp = 10; 
    double Kd = 5; 

    double dError = error - lastError;
    double powerCorrection = Kp * error + Kd * dError;
    lastError = error;

    int vL = (Tp + powerCorrection);
    int vR = (Tp - powerCorrection);
    
    if (vL > 255) vL = 255; else if (vL < 0) vL = 0;
    if (vR > 255) vR = 255; else if (vR < 0) vR = 0;
#if DEBUG
    Serial3.print("vL/vR: ");
    Serial3.print(vL);
    Serial3.print(" ");
    Serial3.println(vR);
#endif
    MotorWriting(vL, vR);
}