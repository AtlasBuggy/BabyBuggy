import time
from atlasbuggy import ThreadedStream
from atlasbuggy.subscriptions import *

from lms200 import OdometryMessage


class OdometryStream(ThreadedStream):
    def __init__(self, enabled=True, log_level=None):
        super(OdometryStream, self).__init__(enabled, log_level)

        self.kalman_tag = "kalman"
        self.kalman_feed = None
        self.require_subscription(self.kalman_tag, Update)

        self.angular_tag = "angular"
        self.angular_service_tag = "angular_v"
        self.angle_feed = None
        self.require_subscription(self.angular_tag, Update, service_tag=self.angular_service_tag)

        self.adjust_service(message_class=OdometryMessage)

    def take(self, subscriptions):
        self.kalman_feed = self.get_feed(self.kalman_tag)
        self.angle_feed = self.get_feed(self.angular_tag)

    def run(self):
        vx = None
        vy = None
        angular_v = None
        while self.is_running():
            if not self.kalman_feed.empty():
                position, velocity = self.kalman_feed.get()
                vx = velocity[0]
                vy = velocity[1]
                self.logger.debug("kalman data received: (vx=%0.4f, vy%0.4f)" % (vx, vy))
            if not self.angle_feed.empty():
                angular_v = self.angle_feed.get()
                self.logger.debug("angular v data received: %0.6f" % angular_v)

            if vx is not None and vy is not None and angular_v is not None:
                self.logger.debug("posting vx=%0.4f, vy=%0.4f, ang_v=%0.4f" % (vx, vy, angular_v))
                self.post(OdometryMessage(vx, vy, angular_v))
                vx = None
                vy = None
                angular_v = None

            time.sleep(0.001)
