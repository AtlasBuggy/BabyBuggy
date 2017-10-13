from atlasbuggy import Robot
from atlasbuggy.subscriptions import *
from atlasbuggy.camera import CameraViewer, VideoPlayer
from atlasbuggy.plotters import LivePlotter
from atlasbuggy.logparser import LogParser

from lms200 import LmsSimulator, Slam
from babybuggy import BabyBuggySerial
from babybuggy.kalman.kalman_filter import KalmanFilterStream
from babybuggy.odometry_stream import OdometryStream


def key_press_fn(event):
    if event.key == "q":
        plotter.exit()


map_size_pixels = 3200
map_size_meters = 500

# map_size_pixels = 1600
# map_size_meters = 50

enable_camera = False

robot = Robot(write=False, log_level=10)

video = VideoPlayer(enabled=enable_camera, file_name="videos/rolls/2017_Oct_07/07_39_40.mp4")
viewer = CameraViewer(enable_trackbar=False, enabled=enable_camera)

serial = BabyBuggySerial(enabled=True)
log_parser = LogParser("logs/2017_Oct_07/07;39;40-cut.log.xz", update_rate=0.001)
kalman = KalmanFilterStream(0.0, 0.0, 0.0)
sicklms = LmsSimulator()
slam = Slam(map_size_pixels, map_size_meters, write_image=False, enabled=True, perform_slam=True, plot_slam=True)
odometry_converter = OdometryStream()
plotter = LivePlotter(2, matplotlib_events=dict(key_press_event=key_press_fn), enabled=True, skip_count=100)

viewer.subscribe(Update(viewer.capture_tag, video))

slam.subscribe(Feed(slam.lms_tag, sicklms))
slam.subscribe(Update(slam.odometry_tag, odometry_converter))
slam.subscribe(Subscription(slam.plotter_tag, plotter))

log_parser.subscribe(Subscription(serial.name, serial))
log_parser.subscribe(Subscription(sicklms.name, sicklms))

kalman.subscribe(Feed(kalman.imu_tag, serial, kalman.imu_service_tag))
kalman.subscribe(Feed(kalman.gps_tag, serial, kalman.gps_service_tag))
kalman.subscribe(Subscription(kalman.plotter_tag, plotter))

serial.subscribe(Subscription(serial.plotter_tag, plotter))

odometry_converter.subscribe(Update(odometry_converter.angular_tag, serial, odometry_converter.angular_service_tag))
odometry_converter.subscribe(Update(odometry_converter.kalman_tag, kalman))

robot.run(log_parser, viewer, video, plotter, sicklms, slam, kalman, odometry_converter)
