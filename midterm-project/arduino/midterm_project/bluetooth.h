/***************************************************************************/
// File			  [bluetooth.h]
// Author		  [Erik Kuo]
// Synopsis		[Code for bluetooth communication]
// Functions  [ask_BT, send_msg, send_byte]
// Modify		  [2020/03/27 Erik Kuo]
/***************************************************************************/

/*if you have no idea how to start*/
/*check out what you have learned from week 2*/


enum BT_CMD{   // add movements
    NOTHING,
    START,
    HALT,
    LEFT_TURN,
    MOVE_FORWARD,
    RIGHT_TURN,
    BACKWARD
};

BT_CMD ask_BT() {   //link interface.send() to Serial3.read()
    BT_CMD message = NOTHING;
    char cmd;
    if (Serial3.available()) {  //transform messages and return it

        cmd = Serial3.read();
        switch(cmd){ 
            case 's': 
                message = START;
                break;
            case 'h':
                message = HALT;
                break;
            case 'l': 
                message = LEFT_TURN;
                break;
            case 'f': 
                message = MOVE_FORWARD;
                break;
            case 'r': 
                message = RIGHT_TURN;
                break;
            case 'b': 
                message = BACKWARD;
                break;
            default:
                message = NOTHING;
        }

    #ifdef DEBUG
        Serial.print("cmd : ");
        Serial.println(cmd);
    #endif
    }
    
    return message;
}

// send msg back through Serial1(bluetooth serial)
// can use send_byte alternatively to send msg back
// (but need to convert to byte type)
void send_msg(const char& msg) {

    Serial3.print(msg);

    #ifdef DEBUG   //print on the screen as well
        Serial.print("Sent msg to BT: ");
        Serial.println(msg);
    #endif   
}  

// send UID back through Serial3(bluetooth serial)
void send_byte(byte* id, byte& idSize) {
    for (byte i = 0; i < idSize; i++) {  // Send UID consequently.
        Serial3.print(id[i]);
    }
    
#ifdef DEBUG
    Serial.print("Sent id: ");
    for (byte i = 0; i < idSize; i++) {  // Show UID consequently.
        Serial.print(id[i], HEX);
    }
    Serial.println();
#endif
}  // send_byte