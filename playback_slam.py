import cv2

from atlasbuggy import Orchestrator, run
from atlasbuggy.plotters import LivePlotter, PlotMessage
from atlasbuggy.opencv import OpenCVViewer, ImageMessage

from babybuggy.bno055_playback import BNO055Playback
from babybuggy.adafruit_gps_playback import AdafruitGpsPlayback
from babybuggy.quad_encoder_playback import QuadEncoderPlayback
from babybuggy.odometry import Odometry

from lms200.playback import LmsPlayback
from lms200.slam import Slam

map_size_pixels = 3200
map_size_meters = 100


class BabyBuggy(Orchestrator):
    def __init__(self, event_loop):
        # self.set_default(level=30)
        super(BabyBuggy, self).__init__(event_loop)

        self.image_counter = 0

        file_name = "18_04_53.log"
        directory = "logs/2017_Nov_15"

        bno055 = BNO055Playback(file_name, directory)
        adafruit_gps = AdafruitGpsPlayback(file_name, directory)
        encoder = QuadEncoderPlayback(file_name, directory)
        sicklms = LmsPlayback(file_name, directory)
        odometry = Odometry(enabled=True)
        self.slam = Slam(map_size_pixels, map_size_meters, write_image=False, enabled=True, produce_images=True, force_rmhc_slam=True)
        map_viewer = OpenCVViewer(enabled=True, producer_service=self.slam.slam_image_service)
        plotter = LivePlotter(enabled=False)
        odometry_plot_tag = plotter.add_plot("Odometry", service=odometry.odom_position_service)

        self.add_nodes(bno055, adafruit_gps, encoder, sicklms, self.slam, odometry, plotter, map_viewer)

        self.subscribe(bno055, odometry, odometry.bno055_tag)
        self.subscribe(encoder, odometry, odometry.encoder_tag)

        self.subscribe(odometry, self.slam, self.slam.odometry_tag)
        self.subscribe(sicklms, self.slam, self.slam.lms_tag)

        self.subscribe(odometry, plotter, odometry_plot_tag, self.plot_odometry)

        self.subscribe(self.slam, map_viewer, map_viewer.capture_tag, self.numpy_to_viewer)

    def numpy_to_viewer(self, slam_image):
        for coords in self.slam.trajectory:
            x_mm, y_mm = coords

            x_pix = self.slam.mm2pix(x_mm)
            y_pix = self.slam.mm2pix(y_mm)

            # slam_image[x_pix, y_pix] = 0
            cv2.circle(slam_image, (x_pix, y_pix), 5, (0, 0, 0), 3)

        slam_image = cv2.resize(slam_image, (900, 900))
        message = ImageMessage(slam_image, self.image_counter)
        self.image_counter += 1
        return message

    def plot_odometry(self, data):
        x, y, th = data
        return PlotMessage(x, y)


run(BabyBuggy)
