/***************************************************************************/
// File       [node.h]
// Author     [Lumos, Hsinchi]
// Synopsis   [Code for managing car movement when encountering a node]
// Functions  [Stop, TurnRight, TurnLeft, TurnBack, Moveforward]
// Modify     [2026/04/05 Lumos]
/***************************************************************************/
int slow=175;
int extern Tp; // Defined in midterm_project.ino
/*
 * Halts both motors immediately.
 */
void Stop() {
    MotorWriting(0, 0);
}

/*
 * Executes a 90-degree right turn at an intersection.
 */
void TurnRight() {
    int l3, l2, m, r2, r3;
    do {
        MotorWriting(slow, slow);
        l3 = analogRead(L3) > 100;
        l2 = analogRead(L2) > 100;
        m = analogRead(M) > 100;
        r2 = analogRead(R2) > 100;
        r3 = analogRead(R3) > 100;
    } while(l3 * l2 * m * r2 * r3 == 1);
    
    MotorWriting(slow, -slow);
    delay(125);
    
    do {
        MotorWriting(slow-50, -(slow-50));
        l3 = analogRead(L3) > 100;
        l2 = analogRead(L2) > 100;
        m = analogRead(M) > 100;
        r2 = analogRead(R2) > 100;
        r3 = analogRead(R3) > 100;
    } while(!((l3==0) && (l2==0) && (m==0) && (r2==0) && (r3==1)));
    MotorWriting(MAX_POWER, MAX_POWER);
}

/*
 * Executes a 90-degree left turn at an intersection.
 */
void TurnLeft() {
    int l3, l2, m, r2, r3;
    do {
        MotorWriting(slow, slow);
        l3 = analogRead(L3) > 100;
        l2 = analogRead(L2) > 100;
        m = analogRead(M) > 100;
        r2 = analogRead(R2) > 100;
        r3 = analogRead(R3) > 100;
    } while(l3 * l2 * m * r2 * r3 == 1);
    
    MotorWriting(-slow, slow);
    delay(125);
    
    do {
        MotorWriting(-(slow-50), slow-50);
        l3 = analogRead(L3) > 100;
        l2 = analogRead(L2) > 100;
        m = analogRead(M) > 100;
        r2 = analogRead(R2) > 100;
        r3 = analogRead(R3) > 100;
    } while(!((l3==1) && (l2==0) && (m==0) && (r2==0) && (r3==0)));
    MotorWriting(MAX_POWER, MAX_POWER);
}

/*
 * Executes a 180-degree U-turn.
 */
void TurnBack() {
    MotorWriting(-slow, slow);
    delay(400);
    int l3 = analogRead(L3) > 100;
    int l2 = analogRead(L2) > 100;
    int m  = analogRead(M) > 100;
    int r2 = analogRead(R2) > 100;
    int r3 = analogRead(R3) > 100;
    
    do {
        MotorWriting(0, slow-50);
        l3 = analogRead(L3) > 100;
        l2 = analogRead(L2) > 100;
        m = analogRead(M) > 100;
        r2 = analogRead(R2) > 100;
        r3 = analogRead(R3) > 100;
    } while (l3 * l2 * m * r2 * r3 == 1);
    
    
    do {
        MotorWriting(-(slow-50), slow-50);
        l3 = analogRead(L3) > 100;
        l2 = analogRead(L2) > 100;
        m = analogRead(M) > 100;
        r2 = analogRead(R2) > 100;
        r3 = analogRead(R3) > 100;
    } while(!((l3==1) && (l2==0) && (m==0) && (r2==0) && (r3==0)));
    MotorWriting(MAX_POWER, MAX_POWER);
}
/*
 * Moves forward slightly to bypass the current node intersection.
 */
void Moveforward() {
    int l3 = (analogRead(L3) > 100) ? 1 : 0;
    int l2 = (analogRead(L2) > 100) ? 1 : 0;
    int m  = (analogRead(M)  > 100) ? 1 : 0;
    int r2 = (analogRead(R2) > 100) ? 1 : 0;
    int r3 = (analogRead(R3) > 100) ? 1 : 0;

    while (l3 == 1 && l2 == 1 && m == 1 && r2 == 1 && r3 == 1) {
        MotorWriting(MAX_POWER, MAX_POWER);
        l3 = (analogRead(L3) > 100) ? 1 : 0;
        l2 = (analogRead(L2) > 100) ? 1 : 0;
        m  = (analogRead(M)  > 100) ? 1 : 0;
        r2 = (analogRead(R2) > 100) ? 1 : 0;
        r3 = (analogRead(R3) > 100) ? 1 : 0;
    }
}