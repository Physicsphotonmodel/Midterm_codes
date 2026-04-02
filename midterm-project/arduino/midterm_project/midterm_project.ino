/***************************************************************************/
// File       [final_project.ino]
// Author     [Erik Kuo]
// Synopsis   [Code for managing main process]
// Functions  [setup, loop, Search_Mode, Hault_Mode, SetState]
// Modify     [2020/03/27 Erik Kuo]
/***************************************************************************/

#define DEBUG  // debug flag

// for RFID
#include <MFRC522.h>
#include <SPI.h>

/*===========================define pin & create module object================================*/
// BlueTooth
// BT connect to Serial1 (Hardware Serial)
// Mega               HC05
// Pin  (Function)    Pin
// 18    TX       ->  RX
// 19    RX       <-  TX
// TB6612, 請按照自己車上的接線寫入腳位(左右不一定要跟註解寫的一樣)
// TODO: 請將腳位寫入下方
#define MotorL_PWM = 10;
#define MotorR_PWM = 11;  
#define MotorL_I1 = 7;
#define MotorL_I2 = 6;
#define MotorR_I3 = 9;
#define MotorR_I4 = 8;
// 循線模組, 請按照自己車上的接線寫入腳位
#define R3 A3 
#define R2 A4 
#define M A5 
#define L2 A6 
#define L3 A7 
// RFID, 請按照自己車上的接線寫入腳位
#define RST_PIN 3                 // 讀卡機的重置腳位
#define SS_PIN 2                  // 晶片選擇腳位
MFRC522 mfrc522(SS_PIN, RST_PIN);  // 建立MFRC522物件
// BT
#define CUSTOM_NAME "HM10_7" // Max length is 12 characters [1]

/*===========================define pin & create module object===========================*/

/*============setup============*/
void setup() {
    // bluetooth initialization
    Serial3.begin(9600);  
    // Serial window
    Serial.begin(9600);
    // RFID initial
    SPI.begin();
    mfrc522.PCD_Init();
    // TB6612 pin
    pinMode(MotorR_I3, OUTPUT);
    pinMode(MotorR_I4, OUTPUT);
    pinMode(MotorL_I1, OUTPUT);
    pinMode(MotorL_I2, OUTPUT);
    pinMode(MotorL_PWM, OUTPUT);
    pinMode(MotorR_PWM, OUTPUT);
    // tracking pin
    pinMode(R3, INPUT);
    pinMode(R2, INPUT);
    pinMode(M, INPUT);
    pinMode(L2, INPUT);
    pinMode(L3, INPUT);
#ifdef DEBUG
    Serial.println("Start!");
#endif
}
/*============setup============*/

/*=====Import header files=====*/
#include "RFID.h"
#include "bluetooth.h"
#include "node.h"
#include "track.h"
/*=====Import header files=====*/

/*===========================initialize variables===========================*/
int l3 = 0, l2 = 0, m = 0, r2 = 0, r3 = 0;  // 紅外線模組的讀值(0->white,1->black)
int Tp = 200;                                // set your own value for motor power
bool state = false;     // set state to false to halt the car, set state to true to activate the car
BT_CMD _cmd = NOTHING;  // enum for bluetooth message, reference in bluetooth.h line 2
/*===========================initialize variables===========================*/

/*===========================declare function prototypes===========================*/
void Search();    // search graph
void SetState();  // switch the state
/*===========================declare function prototypes===========================*/

/*===========================define function===========================*/

char data[100];

void loop() {
    if (!state)
        MotorWriting(0, 0);
    else
        Search();
    SetState();
}

void SetState() {
    BT_CMD incoming_cmd = ask_BT();
    if (incoming_cmd == NOTHING) return; 

    if (incoming_cmd == START) {state = true;}
    else if (incoming_cmd == HALT) {state = false;}
    else {_cmd = incoming_cmd;}
}

void Search() {   //這裡只是大概寫一下之後還會再改

    int l3 = analogRead(L3) > 100;
    int l2 = analogRead(L2) > 100;
    int m = analogRead(M) > 100;
    int r2 = analogRead(R2) > 100;
    int r3 = analogRead(R3) > 100;

    if(_cmd == MOVE_FORWARD){
        //moveforward()
    }

    if (l2 && r2) { // arrive at a node
        MotorWriting(0, 0);
        send_msg('K'); 
        
        if (_cmd == LEFT_TURN) {
            // turnLeft();
        }
        else if (_cmd == RIGHT_TURN) {
            // turnRight();
        }
        else if (_cmd == BACKWARD) {
            // turnBack();
        }

        send_msg('L');  // if it leaves a node
        _cmd = NOTHING; // clear the command

    }

    else {
        // tracking(); 
    }
}


/*===========================define function===========================*/
