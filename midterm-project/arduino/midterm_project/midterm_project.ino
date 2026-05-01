/***************************************************************************/
// File       [midterm_project.ino]
// Author     [Lumos, Hsinchi]
// Synopsis   [Code for managing main process]
// Functions  [setup, loop, Search, SetState]
// Modify     [2026/04/05 Lumos]
/***************************************************************************/

#define DEBUG 0 // Debug flag

#include <MFRC522.h>
#include <SPI.h>

/*=========================== Define Pin & Modules ===========================*/
// TB6612 Motor Driver Pins
#define MotorL_PWM 10
#define MotorR_PWM 11
#define MotorL_I1 7
#define MotorL_I2 6
#define MotorR_I3 9
#define MotorR_I4 8

// IR Tracking Sensor Pins
#define R3 A3
#define R2 A4
#define M  A5
#define L2 A6
#define L3 A7

// MFRC522 RFID Pins
#define RST_PIN 3                 
#define SS_PIN 2                  
MFRC522 mfrc522(SS_PIN, RST_PIN); 

// Bluetooth Configuration
#define CUSTOM_NAME "HM10_7" 
#define MAX_POWER 255
/*=========================== Define Pin & Modules ===========================*/

void setup() {
    // Serial communication initialization
    Serial3.begin(9600); // HM-10 Bluetooth
    Serial.begin(9600);  // PC Serial Monitor

    // RFID initialization
    SPI.begin();
    mfrc522.PCD_Init();

    // Motor pin initialization
    pinMode(MotorR_I3, OUTPUT);
    pinMode(MotorR_I4, OUTPUT);
    pinMode(MotorL_I1, OUTPUT);
    pinMode(MotorL_I2, OUTPUT);
    pinMode(MotorL_PWM, OUTPUT);
    pinMode(MotorR_PWM, OUTPUT);

    // IR sensor pin initialization
    pinMode(R3, INPUT);
    pinMode(R2, INPUT);
    pinMode(M, INPUT);
    pinMode(L2, INPUT);
    pinMode(L3, INPUT);

#ifdef DEBUG
    Serial.println("Start!");
#endif
}

/*===== Import header files =====*/
#include "RFID.h"
#include "bluetooth.h"
#include "track.h"
#include "node.h"
/*===== Import header files =====*/

/*=========================== Initialize Variables ===========================*/
// IR sensor readings (0 -> white, 1 -> black)
int l3 = 0, l2 = 0, m = 0, r2 = 0, r3 = 0;
int Tp = 255; // Base motor power
String cards="";
bool state = false; // true = active, false = halt
BT_CMD _cmd = NOTHING; 
/*=========================== Initialize Variables ===========================*/

/*=========================== Function Prototypes ===========================*/
void Search();    // Graph searching and routing logic
void SetState();  // State machine updater
/*=========================== Function Prototypes ===========================*/

void loop() {
    static unsigned long last_ping = 0;

    if (!state) {
        MotorWriting(0, 0);
        // Send "READY" to Bluetooth every 1 second to indicate alive status
        if (millis() - last_ping > 1000) {
            Serial3.println("READY");
            last_ping = millis();
        }
    } else {
        // Start searching once 's' is received
        Search();
    }
    SetState();
    //TESTER
    // MotorWriting(255,255);
    // delay(920);
    // Stop();
    // delay(5000);
    // MotorWriting(-255,255);
    // delay(340);
    // Stop();
    // delay(5000);
    // MotorWriting(255,-255);
    // delay(340);
    // Stop();
    // delay(5000);
}

/*
 * Updates the system state based on incoming Bluetooth commands.
 */
void SetState() {
    BT_CMD incoming_cmd = ask_BT();
    if (incoming_cmd == NOTHING) return;

    if (incoming_cmd == START) {
        state = true;
    // } else if (incoming_cmd == HALT) {
    //     state = false;
    } else {
        _cmd = incoming_cmd;
    }
}

/*
 * Main logic for reading RFID, detecting nodes, requesting commands,
 * executing actions, and performing line tracking.
 */
void Search() {
    byte idSize;
    byte* id = rfid(idSize);
    
    if (id != 0) {
        String uidStr = "ID";
        for (byte i = 0; i < idSize; i++) {
            if (id[i] < 0x10) uidStr += "0";
            uidStr += String(id[i], HEX);
        }
        uidStr.toUpperCase();
        Serial3.println(uidStr); 
    }

    l3 = analogRead(L3) > 100;
    l2 = analogRead(L2) > 100;
    m  = analogRead(M) > 100;
    r2 = analogRead(R2) > 100;
    r3 = analogRead(R3) > 100;

    if (l3 && r3) { 
        MotorWriting(100, 100); // Brake immediately at node
        Serial3.println("K"); // Report node arrival to Python
        
        // Wait in loop until the next movement command is received
        while(_cmd == NOTHING) {
            SetState();
        }

        // Execute the corresponding action based on the received command
        if (_cmd == LEFT_TURN) {
            TurnLeft();
            Serial3.println("L");
        }
        else if (_cmd == RIGHT_TURN) {
            TurnRight();
            Serial3.println("R");
        }
        else if (_cmd == BACKWARD) {
            TurnBack();
            Serial3.println("B");
        }
        else if (_cmd == MOVE_FORWARD) {
            Moveforward();
            Serial3.println("F");
        }
        else if (_cmd == HALT) {
            Stop();
            Serial3.println("S");
            state = false; // Halt main process
        }

        _cmd = NOTHING; // Clear command queue for the next node
    } else {
        // Continue line tracking if not at a node
        Tracking_PD(l3, l2, m, r2, r3);
    }
}