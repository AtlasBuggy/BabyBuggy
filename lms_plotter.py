from atlasbuggy import Robot, LogParser
from atlasbuggy.plotters import LivePlotter
from atlasbuggy.subscriptions import *

from lms200 import Slam
from lms200 import LmsSimulator


def key_press_fn(event):
    if event.key == "q":
        plotter.exit()


robot = Robot(write=False, log_level=10)

map_size_pixels = 3200
map_size_meters = 500

file_name = "2017_Sep_30/05;45;57.log.xz"

sicklms = LmsSimulator()
slam = Slam(map_size_pixels, map_size_meters, write_image=True, enabled=True, perform_slam=False, plot_slam=False)
plotter = LivePlotter(2, matplotlib_events=dict(key_press_event=key_press_fn))
log_parser = LogParser(file_name, "logs", update_rate=0.005)

slam.subscribe(Feed(slam.lms_tag, sicklms))
slam.subscribe(Subscription(slam.plotter_tag, plotter))
log_parser.subscribe(Subscription(sicklms.name, sicklms))

robot.run(log_parser, sicklms, plotter, slam)