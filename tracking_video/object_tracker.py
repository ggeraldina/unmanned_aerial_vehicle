# $ python tracking_video/object_tracker.py --video test_video/uniyar/ch02_20200605114152.mp4 --tracker csrt
# https://www.pyimagesearch.com/2018/07/30/opencv-object-tracking/

from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2

from .constants import *


def run(path, tracker_name):
    tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()

    capture = cv2.VideoCapture(path)

    # Окаймляющий прямоугольник (x, y, w, h)
    rectangle = None

    # Счетчик кадров в секунду
    fps = None

    while True:
        frame = capture.read()
        frame = frame[1]
        if frame is None:
            break
        frame = imutils.resize(frame, width=1000)
        (height, width) = frame.shape[:2]
        if rectangle is not None:
            (success, box) = tracker.update(frame)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            fps.update()
            fps.stop()
            info = [
                ("Tracker", tracker),
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
            old_initBB = rectangle
            rectangle = cv2.selectROI(
                "Frame", frame, fromCenter=False, showCrosshair=True
            )
            if not old_initBB is None:
                tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                    
            tracker.init(frame, rectangle)
            fps = FPS().start()
        elif key == ord("q"):
            break

    capture.release()

    cv2.destroyAllWindows()
