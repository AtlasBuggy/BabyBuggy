from atlasbuggy import Robot
from atlasbuggy.subscriptions import *
from atlasbuggy.camera import CameraViewer, CameraStream, VideoRecorder
from atlasbuggy.plotters import LivePlotter

from lms200 import LMS200, Slam


def key_press_fn(event):
    if event.key == "q":
        plotter.exit()


robot = Robot(write=True)

recorder = VideoRecorder(enabled=True, directory="videos/2017_Oct_01")
camera = CameraStream(capture_number=1, width=800, height=500, enabled=True)
viewer = CameraViewer(enable_trackbar=False, enabled=True)

map_size_pixels = 3200
map_size_meters = 500

sicklms = LMS200("/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0",
                 enabled=True)
slam = Slam(map_size_pixels, map_size_meters, write_image=True, enabled=True, perform_slam=True, plot_slam=False)
plotter = LivePlotter(2, matplotlib_events=dict(key_press_event=key_press_fn), enabled=True)

recorder.subscribe(Feed(recorder.capture_tag, camera))
viewer.subscribe(Update(viewer.capture_tag, camera))

slam.subscribe(Feed(slam.lms_tag, sicklms))
slam.subscribe(Subscription(slam.plotter_tag, plotter))

robot.run(viewer, recorder, camera, sicklms, plotter, slam)
