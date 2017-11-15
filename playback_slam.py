from atlasbuggy import Orchestrator, run

from babybuggy.bno055_playback import BNO055Playback
from babybuggy.adafruit_gps_playback import AdafruitGpsPlayback
from babybuggy.quad_encoder_playback import QuadEncoderPlayback
from babybuggy.odometry import Odometry

from lms200.playback import LmsPlayback
from lms200.slam import Slam

map_size_pixels = 1600
map_size_meters = 50


class BabyBuggy(Orchestrator):
    def __init__(self, event_loop):
        # self.set_default(level=30)
        super(BabyBuggy, self).__init__(event_loop)

        file_name = "18_37_23.log"
        directory = "logs/2017_Nov_08"

        bno055 = BNO055Playback(file_name, directory)
        adafruit_gps = AdafruitGpsPlayback(file_name, directory)
        encoder = QuadEncoderPlayback(file_name, directory)
        sicklms = LmsPlayback(file_name, directory)
        odometry = Odometry()
        slam = Slam(map_size_pixels, map_size_meters, write_image=True, enabled=True)

        self.add_nodes(bno055, adafruit_gps, encoder, sicklms, slam, odometry)

        self.subscribe(bno055, odometry, odometry.bno055_tag)
        self.subscribe(encoder, odometry, odometry.encoder_tag)

        self.subscribe(odometry, slam, slam.odometry_tag)
        self.subscribe(sicklms, slam, slam.lms_tag)


run(BabyBuggy)
