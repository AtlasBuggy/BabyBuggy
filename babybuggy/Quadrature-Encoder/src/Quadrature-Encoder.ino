#include <Encoder.h>
#include <Atlasbuggy.h>

Atlasbuggy robot("Quadrature-Encoder");
Encoder encoder1(3, 4);

void setup() {
    robot.begin();
}

void loop() {
    while (robot.available()) {
        robot.readSerial();
        int status = robot.readSerial();
        if (status == 2) {  // start event
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
        Serial.print(encoder1.read());
        delay(25);
    }
}
