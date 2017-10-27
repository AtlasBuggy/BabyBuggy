import os
from babybuggy.adafruit_gps import AdafruitGPS
from babybuggy.bno055 import BNO055

from lms200 import Slam, LMS200
from atlasbuggy import Orchestrator, run
from atlasbuggy.opencv import OpenCVCamera, OpenCVRecorder

map_size_pixels = 1600
map_size_meters = 50

enable_arduinos = False
enable_camera = True
enable_video_recording = True
enable_lidar = False

class BabyBuggy(Orchestrator):
    def __init__(self, event_loop):
        self.set_default(write=True)
        super(BabyBuggy, self).__init__(event_loop)

        video_file_name = self.file_name[:-3] + "avi"
        video_directory = "videos/" + os.path.join(*self.directory.split(os.sep)[1:])  # remove "log" part of directory

        # bno055 = BNO055(enabled=enable_arduinos)
        # adafruit_gps = AdafruitGPS(enabled=enable_arduinos)
        # sicklms = LMS200(
        #     "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0",
        #     # "/dev/cu.usbserial"
        #     enabled=enable_lidar
        # )
        # slam = Slam(map_size_pixels, map_size_meters, write_image=True, enabled=enable_lidar)
        # OpenCVCamera.ignore_capture_numbers(0)
        camera = OpenCVCamera(capture_number=1, enabled=enable_camera)
        recorder = OpenCVRecorder(video_file_name, video_directory, enabled=enable_video_recording)

        # self.add_nodes(bno055, adafruit_gps, sicklms, camera, recorder, slam)
        self.add_nodes(camera, recorder)

        # self.subscribe(sicklms, slam, slam.lms_tag)
        self.subscribe(camera, recorder, recorder.capture_tag)


run(BabyBuggy)
