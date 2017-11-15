import re
import math
import time
import asyncio

from atlasbuggy import Message
from atlasbuggy.device import Arduino


class EncoderMessage(Message):
    message_regex = r"EncoderMessage\(t=(\d.*), n=(\d*), pt=(\d.*), tick=(-\d*), dist=(-\d.*), ptick=(-\d*), pdist=(-\d.*)\)"

    def __init__(self, tick, dist_mm, prev_message=None, timestamp=None, n=None):
        super(EncoderMessage, self).__init__(timestamp, n)

        self.tick = tick
        self.dist_mm = dist_mm

        if prev_message is None:
            self.prev_tick = self.tick
            self.prev_dist_mm = self.dist_mm
            self.prev_timestamp = self.timestamp
        else:
            self.prev_tick = prev_message.tick
            self.prev_dist_mm = prev_message.dist_mm
            self.prev_timestamp = prev_message.timestamp

        self.dt = self.timestamp - self.prev_timestamp
        self.delta_arc = self.dist_mm - self.prev_dist_mm

    def __str__(self):
        return "%s(t=%s, n=%s, pt=%s, tick=%s, dist=%s, ptick=%s, pdist=%s)" % (
            self.name, self.timestamp, self.n, self.prev_timestamp, self.tick, self.dist_mm, self.prev_tick,
            self.prev_dist_mm
        )

    @classmethod
    def parse(cls, message):
        match = re.match(cls.message_regex, message)
        if match is not None:
            timestamp = float(match.group(1))
            n = int(match.group(2))
            prev_time = float(match.group(3))
            tick = float(match.group(4))
            dist = float(match.group(5))
            prev_tick = float(match.group(6))
            prev_dist = float(match.group(7))
            prev_message = cls(prev_tick, prev_dist, timestamp=prev_time, n=n - 1)
            message = cls(tick, dist, prev_message, timestamp, n)

            return message
        else:
            return None


class QuadEncoder(Arduino):
    wheel_radius = 30.825
    ticks_per_rotation = 1024
    ticks_to_mm = wheel_radius * 2 * math.pi / ticks_per_rotation

    def __init__(self, enabled=True):
        self.message = None
        self.start_tick = None
        super(QuadEncoder, self).__init__("Quadrature-Encoder", enabled=enabled)

    async def loop(self):
        counter = 0
        self.start()
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
        tick = int(packet)
        dist_mm = tick * QuadEncoder.ticks_to_mm

        if self.start_tick is None:
            self.start_tick = tick
            self.logger.info("start tick value: %s" % self.start_tick)

        tick -= self.start_tick

        self.message = EncoderMessage(tick, dist_mm, self.message, packet_time, packet_num)
        return self.message

    async def teardown(self):
        await super(QuadEncoder, self).teardown()
        self.logger.info("Last measured distance: %smm (%s ticks)" % (self.message.dist_mm, self.message.tick))
