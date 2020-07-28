from imutils.video import FPS
import imutils
import cv2

from .constants import *

class Tracker:

    def __init__(self):
        self._tracker = None
        self._current_frame = None
        # Окаймляющий прямоугольник (x, y, w, h)
        self._rectangle = None
        # Счетчик кадров в секунду
        self._fps = None

    def run(self, path, tracker_name):
        self._tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()

        capture = cv2.VideoCapture(path)

        while True:
            _, self._current_frame = capture.read()
            if self._current_frame is None:
                break
            self._current_frame = imutils.resize(self._current_frame, width=1000)
            (height, width) = self._current_frame.shape[:2]
            if self._rectangle is not None:
                (success, box) = self._tracker.update(self._current_frame)
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(self._current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self._fps.update()
                self._fps.stop()
                info = [
                    ("Tracker", self._tracker),
                    ("Success", "Yes" if success else "No"),
                    ("FPS", "{:.2f}".format(self._fps.fps())),
                ]
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(
                        self._current_frame, text, (10, height - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
                    )
            cv2.imshow(DEFAULT_FRAME_WINDOW_NAME, self._current_frame)

            
            if self._check_commands() == EXIT_SUCCESS:
                break            

        capture.release()
        cv2.destroyAllWindows()

    def _check_commands(self):
        key = cv2.waitKey(30) & 0xFF
        # Esc - выход
        if key == 27:
            return EXIT_SUCCESS
        if cv2.getWindowProperty(DEFAULT_FRAME_WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:        
            return EXIT_SUCCESS
        elif key == ord("a"):
            old_rectangle = self._rectangle
            self._rectangle = cv2.selectROI(
                "Frame", self._current_frame, fromCenter=False, showCrosshair=True
            )
            if not old_rectangle is None:
                self._tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                    
            self._tracker.init(self._current_frame, self._rectangle)
            self._fps = FPS().start()
        return CONTINUE_PROCESSING