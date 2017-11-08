import asyncio

from babybuggy.adafruit_gps import AdafruitGPS
from babybuggy.bno055 import BNO055
from babybuggy.quad_encoder import QuadEncoder

from atlasbuggy import Orchestrator, run


class ArduinoTester(Orchestrator):
    def __init__(self, event_loop):
        self.set_default(write=False, level=10)
        super(ArduinoTester, self).__init__(event_loop)

        bno055 = BNO055()
        adafruit_gps = AdafruitGPS()
        encoder = QuadEncoder()

        self.add_nodes(bno055, adafruit_gps, encoder)


run(ArduinoTester)
