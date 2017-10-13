from atlasbuggy import Robot
from atlasbuggy.subscriptions import *
from atlasbuggy.camera import CameraViewer, VideoPlayer

from babybuggy.visual_odometry import OdometryPipeline

robot = Robot(write=False)

viewer = CameraViewer(enable_trackbar=False)
video = VideoPlayer(file_name="videos/rolls/2017_Oct_07/07_39_40.mp4", width=800, height=500)
pipeline = OdometryPipeline()

viewer.subscribe(Update(viewer.capture_tag, pipeline))
pipeline.subscribe(Update(pipeline.capture_tag, video))

robot.run(video, viewer, pipeline)
