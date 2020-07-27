# $ python tracking_video/object_tracker.py --video test_video/uniyar/ch02_20200605114152.mp4 --tracker csrt
# https://www.pyimagesearch.com/2018/07/30/opencv-object-tracking/

from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2

from constants import *

app = argparse.ArgumentParser()
app.add_argument(
    "-v", "--video", type=str,
    help="path to input video file"
)
app.add_argument(
    "-t", "--tracker", type=str, default="kcf",
    help="OpenCV object tracker type"
)
args = vars(app.parse_args())

tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

initBB = None

if not args.get("video", False):
    print("Нужно указать путь к видео. Параметр -v или --video.")
else:
    vs = cv2.VideoCapture(args["video"])

# Счетчик кадров в секунду
fps = None

while True:
    frame = vs.read()
    frame = frame[1]
    if frame is None:
        break
    frame = imutils.resize(frame, width=1000)
    (height, width) = frame.shape[:2]
    if initBB is not None:
        (success, box) = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        fps.update()
        fps.stop()
        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps())),
        ]
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(
                frame, text, (10, height - ((i * 20) + 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
            )
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("s"):
        old_initBB = initBB
        initBB = cv2.selectROI(
            "Frame", frame, fromCenter=False, showCrosshair=True
        )
        if not old_initBB is None:
            tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
                   
        tracker.init(frame, initBB)
        fps = FPS().start()
    elif key == ord("q"):
        break

vs.release()

cv2.destroyAllWindows()
