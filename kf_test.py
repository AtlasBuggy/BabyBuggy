from atlasbuggy import Robot
from atlasbuggy.subscriptions import *
from atlasbuggy.logparser import LogParser
from atlasbuggy.plotters import LivePlotter

from babybuggy import BabyBuggySerial
from babybuggy.kalman.kalman_filter import KalmanFilterStream


def key_press_fn(event):
    if event.key == "q":
        plotter.exit()


robot = Robot(write=False, log_level=10)

serial = BabyBuggySerial(enabled=True)
log_parser = LogParser("logs/2017_Oct_07/07;39;40.log.xz", update_rate=0.001)
kalman = KalmanFilterStream(0.0, 0.0, 0.0)
plotter = LivePlotter(2, matplotlib_events=dict(key_press_event=key_press_fn), enabled=True, skip_count=50)

serial.subscribe(Subscription(serial.plotter_tag, plotter))
log_parser.subscribe(Subscription(serial.name, serial))
kalman.subscribe(Feed(kalman.imu_tag, serial, kalman.imu_service_tag))
kalman.subscribe(Feed(kalman.gps_tag, serial, kalman.gps_service_tag))
kalman.subscribe(Subscription(kalman.plotter_tag, plotter))


robot.run(log_parser, plotter, kalman)
