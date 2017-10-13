import math

from atlasbuggy.microcontrollers import SerialStream
from atlasbuggy.plotters import RobotPlot
from atlasbuggy.subscriptions import *

from .imu import IMU
from .gps import GPS


class BabyBuggySerial(SerialStream):
    def __init__(self, enabled=True, log_level=None, enable_plotting=True):
        self.imu = IMU()
        self.gps = GPS()
        super(BabyBuggySerial, self).__init__(self.imu, self.gps, enabled=enabled)

        self.link_callback(self.imu, self.received_imu)
        self.link_callback(self.gps, self.received_gps)

        self.angular_service = "angular_v"
        self.add_service(self.angular_service, message_class=float)

        self.kalman_imu_service = "kalman-imu"
        self.add_service(self.kalman_imu_service, message_class=dict)

        self.kalman_gps_service = "kalman-gps"
        self.add_service(self.kalman_gps_service, message_class=dict)

        self.prev_angle = 0.0
        self.prev_imu_t = None
        self.prev_gps_t = None

        self.plotter_tag = "plotter"
        self.plotter = None
        self.require_subscription(self.plotter_tag, Subscription, is_suggestion=True)

        self.gps_plot = RobotPlot("gps plot", enable_plotting)

    def take(self, subscriptions):
        if self.is_subscribed(self.plotter_tag):
            self.plotter = self.get_stream(self.plotter_tag)
            self.plotter.add_plots(self.gps_plot)

    def received_imu(self, timestamp, packet):
        # print("%0.4f, %0.4f, %0.4f" % self.imu.euler.get_tuple())

        # ----- form angle message -----

        if self.prev_imu_t is None:
            self.prev_imu_t = timestamp
            delta_t = self.dt()
        else:
            delta_t = timestamp - self.prev_imu_t

        if delta_t == 0.0:
            return

        angle = -self.imu.euler.z
        delta_angle = angle - self.prev_angle
        self.prev_angle = angle
        if delta_angle > math.pi:
            delta_angle -= math.pi / 2
        angular_v = delta_angle / delta_t


        self.sync_post(angular_v, self.angular_service)

        # ----- form kalman filter imu message -----
        self.sync_post(dict(
            imu_dt=delta_t,
            ax=self.imu.accel.x, ay=self.imu.accel.y, az=self.imu.accel.z,
            gx=self.imu.gyro.x, gy=self.imu.gyro.y, gz=self.imu.gyro.z,
        ), self.kalman_imu_service)

        self.prev_imu_t = timestamp

    def received_gps(self, timestamp, packet):
        if self.prev_gps_t is None:
            self.prev_gps_t = timestamp
            delta_t = self.dt()
        else:
            delta_t = timestamp - self.prev_gps_t

        if delta_t == 0.0:
            return

        if self.gps.is_position_valid():
            self.sync_post(dict(
                gps_dt=delta_t,
                lat=self.gps.latitude_deg, long=self.gps.longitude_deg, altitude=self.gps.altitude
            ), self.kalman_gps_service)

            self.gps_plot.append(self.gps.latitude_deg, self.gps.longitude_deg)

            self.prev_gps_t = timestamp

        self.logger.debug("gps position (%s, %s, %s) is %s" % (
            self.gps.latitude_deg, self.gps.longitude_deg, self.gps.altitude,
            "valid" if self.gps.is_position_valid() else "invalid"))
