#include <Encoder.h>
#include <Atlasbuggy.h>

Atlasbuggy robot("Quadrature-Encoder");
Encoder encoder1(3, 4);

long oldPosition = -1;

void setup() {
    robot.begin();
}

void loop() {
    while (robot.available()) {
        robot.readSerial();
        int status = robot.readSerial();
        if (status == 2) {  // start event
            oldPosition = -1;
            encoder1.write(0);
        }
        // else if (status == 1) {  // stop event
        //
        // }
        // else if (status == 0) {  // user command
        //
        // }
    }
    if (!robot.isPaused()) {
        encoder1.read();
        long newPosition = encoder1.read();
        if (newPosition != oldPosition) {
            oldPosition = newPosition;
            Serial.print(newPosition);
            Serial.print('\n');
        }
    }
}
