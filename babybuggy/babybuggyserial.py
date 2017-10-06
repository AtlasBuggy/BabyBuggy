from atlasbuggy.microcontrollers import SerialStream
from .imu import IMU
from .gps import GPS


class BabyBuggySerial(SerialStream):
    def __init__(self):
        self.imu = IMU()
        self.gps = GPS()
        super(BabyBuggySerial, self).__init__(self.imu, self.gps)

        self.link_callback(self.imu, self.received_imu)
        self.link_callback(self.gps, self.received_gps)

    def received_imu(self, timestamp, packet):
        print("%0.4f, %0.4f, %0.4f" % self.imu.euler.get_tuple())

    def received_gps(self, timestamp, packet):
        print(self.gps)
