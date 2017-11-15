import time
import math
import asyncio

from atlasbuggy import Node

from lms200.messages import OdometryMessage
from babybuggy.quad_encoder import EncoderMessage
from babybuggy.bno055 import Bno055Message


class Odometry(Node):
    def __init__(self, enabled=True):
        super(Odometry, self).__init__(enabled)

        self.encoder_tag = "encoder"
        self.encoder_sub = self.define_subscription(self.encoder_tag, message_type=EncoderMessage)
        self.encoder_queue = None

        self.bno055_tag = "bno055"
        self.bno055_sub = self.define_subscription(self.bno055_tag, message_type=Bno055Message)
        self.bno055_queue = None

        self.prev_angle = 0.0

    def take(self):
        self.encoder_queue = self.encoder_sub.get_queue()
        self.bno055_queue = self.bno055_sub.get_queue()

    async def loop(self):
        message_num = 0
        odometry_message = OdometryMessage()
        enc_updated = False
        bno_updated = False
        prev_t = time.time()


        while True:
            enc_updated = not self.encoder_queue.empty()
            if enc_updated:
                encoder_message = await self.encoder_queue.get()
                odometry_message.delta_t = encoder_message.dt
                odometry_message.delta_xy_mm = encoder_message.delta_arc
            else:
                odometry_message.delta_t = 0.0
                odometry_message.delta_xy_mm = 0.0

            bno_updated = not self.bno055_queue.empty()
            if bno_updated:
                bno055_message = await self.bno055_queue.get()
                odometry_message.delta_theta_degrees = math.degrees(bno055_message.euler.z - self.prev_angle)
                self.prev_angle = bno055_message.euler.z

                if not enc_updated:
                    odometry_message.delta_t = bno055_message.timestamp - prev_t
                prev_t = bno055_message.timestamp

            else:
                odometry_message.delta_theta_degrees = 0.0

            if enc_updated or bno_updated:
                odometry_message.timestamp = time.time()
                odometry_message.n = message_num

                message_num += 1

                await self.broadcast(odometry_message)
            else:
                await asyncio.sleep(0.01)
