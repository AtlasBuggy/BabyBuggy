import re
import time
import asyncio
import datetime

from atlasbuggy import Message
from atlasbuggy.device import Arduino


class AdafruitGPSMessage(Message):
    message_regex = (
        "lla: \((\d.*)([NESW]), (\d.*)([NESW]), (\d.*)([NESW])\);",
        "lla degrees: \((\d.*), (\d.*)\);",
        "speed: (\d.*), bearing: (\d.*);",
        "fix: (\d*), quality: (\d*), satellites: (\d*);",
        "time: (\d*):(\d*).(\d*) (\d*)/(\d*)/(\d*);",
        "timestamp: (\d.*)",
    )

    def __init__(self, timestamp=None, n=None):
        super(AdafruitGPSMessage, self).__init__(timestamp, n)

        self.hour = 0
        self.minute = 0
        self.seconds = 0
        self.milliseconds = 0

        self.gps_timestamp = 0.0

        self.day = 0
        self.month = 0
        self.year = 0

        self.fix = False
        self.fix_quality = 0

        self.latitude = None
        self.longitude = None
        self.latitude_deg = None
        self.longitude_deg = None

        self.speed = 0.0
        self.bearing = 0.0
        self.altitude = 0.0
        self.satellites = 0

    def __str__(self):
        string = "%s(" % (self.name)
        if self.fix:
            string += "lla: (%4.6f%s, %4.6f%s, %4.6f); " % (self.latitude[0], self.latitude[1],
                                                            self.longitude[0], self.longitude[1], self.altitude)
            string += "lla degrees: (%2.6f, %2.6f); " % (self.latitude_deg, self.longitude_deg)
            string += "speed: %2.6f, bearing: %2.6f; " % (self.speed, self.bearing)

        string += "fix: %s, quality: %i, satellites: %i; " % (self.fix, self.fix_quality, self.satellites)
        string += "time: %s:%s.%s %s/%s/%s; " % (self.hour, self.minute, self.seconds, self.day, self.month, self.year)
        string += "timestamp: %s" % self.timestamp
        return string

    def calculate_timestamp(self):
        current_date = datetime.datetime(
            self.year, self.month, self.day, self.hour, self.minute, self.seconds, self.milliseconds
        )
        self.timestamp = time.mktime(current_date.timetuple()) + current_date.microsecond / 1e3

    @classmethod
    def parse(cls, message):
        return None


class AdafruitGPS(Arduino):
    def __init__(self, enabled=True, enable_limits=True):
        self.update_rate_hz = None

        self.min_lat = 40.4
        self.max_lat = 41
        self.min_lon = -80
        self.max_lon = -79.8
        self.min_alt = 280.0
        self.max_alt = 310.0

        self.enable_limits = enable_limits

        super(AdafruitGPS, self).__init__("Adafruit-GPS", baud=9600, enabled=enabled)

    async def loop(self):
        counter = 0
        while self.device_active():
            while not self.empty():
                packet_time, packets = self.read()

                for packet in packets:
                    message = self.receive(packet_time, packet, counter)
                    self.log_to_buffer(packet_time, message)
                    await self.broadcast(message)
                    counter += 1

            await asyncio.sleep(0.0)

    def receive(self, packet_time, packet, packet_num):
        data = packet.split("\t")
        message = AdafruitGPSMessage(packet_time, packet_num)
        for segment in data:
            if segment[0] == 't':
                subsegments = segment[1:].split(":")
                message.hour = int(subsegments[0])
                message.minute = int(subsegments[1])
                message.seconds = int(subsegments[2])
                message.milliseconds = int(subsegments[3])

            elif segment[0] == 'd':
                subsegments = segment[1:].split("/")
                message.day = int(subsegments[0])
                message.month = int(subsegments[1])
                message.year = int(subsegments[2])

            elif segment[0] == 'f':
                subsegments = segment[1:].split(",")
                message.fix = bool(int(subsegments[0]))
                message.fix_quality = int(subsegments[1])

            elif segment[0] == 'l':
                subsegments = segment[1:].split(",")
                message.latitude = (float(subsegments[0]), subsegments[1])
                message.longitude = (float(subsegments[2]), subsegments[3])

            elif segment[0] == 'g':
                subsegments = segment[1:].split(",")
                message.latitude_deg = float(subsegments[0])
                message.longitude_deg = float(subsegments[1])

            elif segment[0] == 'x':
                subsegments = segment[1:].split(",")
                message.speed = float(subsegments[0])
                message.bearing = float(subsegments[1])
                message.altitude = float(subsegments[2])
                message.satellites = int(subsegments[3])

        message.calculate_timestamp()

        return message

    def receive_first(self, packet):
        data = packet.split("\t")
        self.update_rate_hz = int(data[0])

    def is_position_valid(self, message):
        if not self.enable_limits:
            return True

        if not message.fix or message.latitude_deg is None or message.longitude_deg is None or message.altitude is None:
            return False

        if not (self.min_alt < message.altitude < self.max_alt) or message.altitude == 0.0:
            message.altitude = 300.0

        if (self.min_lon < message.longitude_deg < self.max_lon and
                        self.min_lat < message.latitude_deg < self.max_lat and
                        self.min_alt < message.altitude < self.max_alt):
            return True
        else:
            return False
