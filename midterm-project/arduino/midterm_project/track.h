/***************************************************************************/
// File			  [track.h]
// Author		  [Erik Kuo]
// Synopsis		[Code used for tracking]
// Functions  [MotorWriting, MotorInverter, tracking]
// Modify		  [2020/03/27 Erik Kuo]
/***************************************************************************/

/*if you have no idea how to start*/
/*check out what you have learned from week 1 & 6*/
/*feel free to add your own function for convenience*/

/*===========================import variable===========================*/
int extern Tp; //use Tp directly, don't need to implement it, it is defined in midterm_project.ino 
/*===========================import variable===========================*/

// Write the voltage to motor.
void MotorWriting(double vL, double vR) {
  // TODO: use TB6612 to control motor voltage & direction
  // MotorWriting
    if (vR < 0) {
        digitalWrite(MotorR_I3, LOW);
        digitalWrite(MotorR_I4, HIGH);
        vR = -vR;
    } 
    else if (vR > 0) {
        digitalWrite(MotorR_I3, HIGH);
        digitalWrite(MotorR_I4, LOW);
    }
  
    if (vL < 0) {
        digitalWrite(MotorL_I1, LOW);
        digitalWrite(MotorL_I2, HIGH);
        vL = -vL;
    } 
    else if (vL > 0) {
        digitalWrite(MotorL_I1, HIGH);
        digitalWrite(MotorL_I2, LOW);
    }
  
    analogWrite(MotorL_PWM, vL);
    analogWrite(MotorR_PWM, vR);
}


// Handle negative motor_PWMR value.
void MotorInverter(int motor, bool& dir) {
    // Hint: the value of motor_PWMR must between 0~255, cannot write negative value.
}  // MotorInverter

// P/PID control Tracking

void Tracking_P(int l3, int l2, int m, int r2, int r3) {

    double sum = l3 + l2 + m + r2 + r3;

    if (sum == 0) {
        MotorWriting(-150, -150); 
        return;
    }

    double error = 0;
    double w2 = 4, w3 = 8;
    double Kp = 100;  
  
    error = (l3 * (-w3) + l2 * (-w2) + m * (0) + r2 * (w2) + r3 * (w3)) / sum;

    double powerCorrection = Kp * error;
    int vL = (Tp + powerCorrection);
    int vR = (Tp - powerCorrection);

    if (vL > 255) vL = 255; else if (vL < -255) vL = -255;
    if (vR > 255) vR = 255; else if (vR < -255) vR = -255;

    MotorWriting(vL, vR);
}

void Tracking_PD(int l3, int l2, int m, int r2, int r3) {
    // TODO: find your own parameters!
    double sum = l3 + l2 + m + r2 + r3;

    if (sum == 0) {
        MotorWriting(-150, -150);
        return;
    }

    double w2 = 4;  //
    double w3 = 8;  //
    double error = 0;
    static double lastError = 0;
    error = (l3 * (-w3) + l2 * (-w2) + m * (0) + r2 * (w2) + r3 * (w3)) / sum;

    double Kp = 75;  // p term parameter
    double Kd = 25;  // d term parameter (optional)
    
    double dError = error - lastError;
    double powerCorrection = Kp*error + Kd*dError;
    lastError = error;    

    int vL = (Tp + powerCorrection);
    int vR = (Tp - powerCorrection);
    if (vL > 255) vL = 255; else if (vL < -255) vL = -255;
    if (vR > 255) vR = 255; else if (vR < -255) vR = -255;

    MotorWriting(vL, vR);
}  
