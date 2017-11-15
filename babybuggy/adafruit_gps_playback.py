import os
import asyncio

from atlasbuggy.log.playback import PlaybackNode
from .adafruit_gps import AdafruitGPSMessage


class AdafruitGpsPlayback(PlaybackNode):
    def __init__(self, file_name, directory=None, enabled=True):
        directory = os.path.join(directory, "AdafruitGPS")
        super(AdafruitGpsPlayback, self).__init__(file_name, directory=directory, enabled=enabled)

    async def parse(self, line):
        message = AdafruitGPSMessage.parse(line.message)
        if message is not None:
            # self.logger.info("recovered: %s" % message)
            # print(message.latitude_deg, message.longitude_deg)
            await self.broadcast(message)
        else:
            print("Message failed to parse:", line.full)
            await asyncio.sleep(0.0)

