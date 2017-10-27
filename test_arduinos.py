from babybuggy.adafruit_gps import AdafruitGPS
from babybuggy.bno055 import BNO055

from atlasbuggy import Orchestrator, run


class ArduinoTester(Orchestrator):
    def __init__(self, event_loop):
        super(ArduinoTester, self).__init__(event_loop)

        bno055 = BNO055()
        adafruit_gps = AdafruitGPS()

        self.add_nodes(bno055, adafruit_gps)


run(ArduinoTester)
