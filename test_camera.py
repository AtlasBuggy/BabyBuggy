from atlasbuggy.opencv import OpenCVCamera

from atlasbuggy import Orchestrator, run


class CameraTester(Orchestrator):
    def __init__(self, event_loop):
        super(CameraTester, self).__init__(event_loop)

        OpenCVCamera.ignore_capture_numbers(0)
        camera = OpenCVCamera(capture_number=1)

        self.add_nodes(camera)


run(CameraTester)
