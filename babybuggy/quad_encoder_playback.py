import os
import asyncio

from atlasbuggy.log.playback import PlaybackNode
from .quad_encoder import EncoderMessage


class QuadEncoderPlayback(PlaybackNode):
    def __init__(self, file_name, directory=None, enabled=True):
        directory = os.path.join(directory, "QuadEncoder")
        super(QuadEncoderPlayback, self).__init__(file_name, directory=directory, enabled=enabled)

    async def parse(self, line):
        message = EncoderMessage.parse(line.message)
        if message is not None:
            await self.broadcast(message)
        else:
            # print("Message failed to parse:", line.message)
            await asyncio.sleep(0.0)
