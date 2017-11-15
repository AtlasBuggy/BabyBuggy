import os
import asyncio

from atlasbuggy.log.playback import PlaybackNode
from .bno055 import Bno055Message


class BNO055Playback(PlaybackNode):
    def __init__(self, file_name, directory=None, enabled=True):
        directory = os.path.join(directory, "BNO055")
        super(BNO055Playback, self).__init__(file_name, directory=directory, enabled=enabled)

    async def parse(self, line):
        message = Bno055Message.parse(line.message)
        if message is not None:
            # self.logger.info("recovered: %s" % message)
            print(message.euler.get_tuple())
            await self.broadcast(message)
        else:
            # print("Message failed to parse:", line.message)
            self.logger.info(line.full)
            await asyncio.sleep(0.0)
