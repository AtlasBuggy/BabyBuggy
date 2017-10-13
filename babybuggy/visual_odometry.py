import cv2
import numpy as np

from atlasbuggy.camera import Pipeline
from atlasbuggy.subscriptions import Update

STAGE_FIRST_FRAME = 0
STAGE_SECOND_FRAME = 1
STAGE_DEFAULT_FRAME = 2
kMinNumFeature = 1500

lk_params = dict(winSize=(21, 21),
                 # maxLevel = 3,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))


def feature_tracking(image_ref, image_cur, px_ref):
    kp2, st, err = cv2.calcOpticalFlowPyrLK(image_ref, image_cur, px_ref, None, **lk_params)  # shape: [k,2] [k,1] [k,1]

    st = st.reshape(st.shape[0])
    kp1 = px_ref[st == 1]
    kp2 = kp2[st == 1]

    return kp1, kp2


class Vector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise ValueError("Invalid index: %s. Only values 0...2 are allowed" % item)

    def __str__(self):
        return "(%0.4f, %0.4f, %0.4f)" % (self.x, self.y, self.z)


class OdometryPipeline(Pipeline):
    def __init__(self, enabled=True, log_level=None):
        super(OdometryPipeline, self).__init__(enabled, log_level)

        self.capture = None
        self.capture_feed = None
        self.capture_tag = "capture"
        self.rpi_cam = None
        self.visual_odometry = None

        self.require_subscription(self.capture_tag, Update, required_attributes=("width", "height"))

        self.odometry_service_tag = "odometry"
        self.add_service(self.odometry_service_tag, message_class=Vector)

    def take(self, subscriptions):
        self.capture = self.get_stream(self.capture_tag)
        self.capture_feed = self.get_feed(self.capture_tag)

        # focal_length = 753.89072627, 746.98092088
        # principle_point = 268.01003591, 131.86922614
        # # rms = 0.34601143374607224
        # distortion_coefficients = [-0.20154387, 2.59173859, -0.03040153, -0.02874057, -6.8478438]

        focal_length = 1241.0, 376.0
        principle_point = 718.8560, 718.8560
        distortion_coefficients = [607.1928, 185.2157]

        self.rpi_cam = PinholeCamera(self.capture.width, self.capture.height,
                                     focal_length[0], focal_length[1], principle_point[0], principle_point[1],
                                     *distortion_coefficients)
        self.visual_odometry = VisualOdometry(self.rpi_cam)

    def pipeline(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.visual_odometry.update(gray)

        if self.visual_odometry.cur_t is not None:
            output = Vector(*self.visual_odometry.cur_t)
            self.post(output, self.odometry_service_tag)
            print(output)

        return frame


class PinholeCamera:
    def __init__(self, width, height, fx, fy, cx, cy,
                 k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0):
        self.width = width
        self.height = height
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy
        self.distortion = (abs(k1) > 0.0000001)
        self.d = [k1, k2, p1, p2, k3]


class VisualOdometry:
    def __init__(self, cam):
        self.frame_stage = 0
        self.cam = cam
        self.new_frame = None
        self.last_frame = None
        self.cur_R = None
        self.cur_t = None
        self.px_ref = None
        self.px_cur = None
        self.focal = cam.fx
        self.pp = (cam.cx, cam.cy)
        self.trueX, self.trueY, self.trueZ = 0, 0, 0
        self.detector = cv2.FastFeatureDetector_create(threshold=25, nonmaxSuppression=True)
        # with open(annotations) as f:
        #     self.annotations = f.readlines()

    def process_first_frame(self):
        self.px_ref = self.detector.detect(self.new_frame)
        self.px_ref = np.array([x.pt for x in self.px_ref], dtype=np.float32)
        self.frame_stage = STAGE_SECOND_FRAME

    def process_second_frame(self):
        self.px_ref, self.px_cur = feature_tracking(self.last_frame, self.new_frame, self.px_ref)
        E, mask = cv2.findEssentialMat(self.px_cur, self.px_ref, focal=self.focal, pp=self.pp, method=cv2.RANSAC,
                                       prob=0.999, threshold=1.0)
        _, self.cur_R, self.cur_t, mask = cv2.recoverPose(E, self.px_cur, self.px_ref, focal=self.focal, pp=self.pp)
        self.frame_stage = STAGE_DEFAULT_FRAME
        self.px_ref = self.px_cur

    def process_frame(self):
        self.px_ref, self.px_cur = feature_tracking(self.last_frame, self.new_frame, self.px_ref)
        E, mask = cv2.findEssentialMat(self.px_cur, self.px_ref, focal=self.focal, pp=self.pp, method=cv2.RANSAC,
                                       prob=0.999, threshold=1.0)
        _, R, t, mask = cv2.recoverPose(E, self.px_cur, self.px_ref, focal=self.focal, pp=self.pp)
        # if absolute_scale > 0.1:
        #     self.cur_t = self.cur_t + absolute_scale * self.cur_R.dot(t)
        #     self.cur_R = R.dot(self.cur_R)
        self.cur_t = self.cur_t + 0.1 * self.cur_R.dot(t)
        self.cur_R = R.dot(self.cur_R)

        if self.px_ref.shape[0] < kMinNumFeature:
            self.px_cur = self.detector.detect(self.new_frame)
            self.px_cur = np.array([x.pt for x in self.px_cur], dtype=np.float32)
        self.px_ref = self.px_cur

    def update(self, img):
        assert (img.ndim == 2 and img.shape[0] == self.cam.height and img.shape[1] == self.cam.width), \
            "Frame: provided image has not the same size as the camera model or image is not grayscale"
        self.new_frame = img
        if self.frame_stage == STAGE_DEFAULT_FRAME:
            self.process_frame()
        elif self.frame_stage == STAGE_SECOND_FRAME:
            self.process_second_frame()
        elif self.frame_stage == STAGE_FIRST_FRAME:
            self.process_first_frame()
        self.last_frame = self.new_frame
