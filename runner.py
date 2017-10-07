import os
from atlasbuggy import Robot
from atlasbuggy.subscriptions import *
from atlasbuggy.camera import CameraViewer, CameraStream, VideoRecorder
from atlasbuggy.plotters import LivePlotter

from lms200 import LMS200, Slam
from babybuggy import BabyBuggySerial


def key_press_fn(event):
    if event.key == "q":
        plotter.exit()


robot = Robot(write=True)

enable_camera = True
enable_lidar = True

todays_folder = os.path.split(robot.log_info["directory"])[-1]
recorder = VideoRecorder(enabled=enable_camera, directory=os.path.join("videos", todays_folder))
camera = CameraStream(capture_number=1, width=800, height=500, enabled=enable_camera)
viewer = CameraViewer(enable_trackbar=False, enabled=enable_camera)
serial = BabyBuggySerial(enabled=True)

map_size_pixels = 3200
map_size_meters = 500

sicklms = LMS200("/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0",
                 enabled=enable_lidar, log_level=10)
slam = Slam(map_size_pixels, map_size_meters, write_image=False, enabled=False, perform_slam=False, plot_slam=False)
plotter = LivePlotter(2, matplotlib_events=dict(key_press_event=key_press_fn), enabled=False)

recorder.subscribe(Feed(recorder.capture_tag, camera))
viewer.subscribe(Update(viewer.capture_tag, camera))

slam.subscribe(Feed(slam.lms_tag, sicklms))
slam.subscribe(Subscription(slam.plotter_tag, plotter))

robot.run(serial, viewer, recorder, camera, plotter, sicklms, slam)
