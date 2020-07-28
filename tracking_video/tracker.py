from imutils.video import FPS
import imutils
import cv2

from .constants import *

class Tracker:

    def __init__(self, path, tracker_name):
        self._tracker_name = tracker_name
        self._tracker = OPENCV_OBJECT_TRACKERS[self._tracker_name]()
        self._capture = cv2.VideoCapture(path)
        _, self._current_frame = self._capture.read()
        self._current_frame = imutils.resize(self._current_frame, width=WINDOW_WIDTH)
        self._frame_height, self._frame_width = self._current_frame.shape[:2]
        # Окаймляющий прямоугольник (x, y, w, h)
        self._rectangle = None
        # Счетчик кадров в секунду
        self._fps = None

    def run(self):
        while True:
            if self._current_frame is None:
                break
            self._current_frame = imutils.resize(self._current_frame, width=WINDOW_WIDTH)
            self._drow_information_text()
            cv2.imshow(DEFAULT_FRAME_WINDOW_NAME, self._current_frame)            
            if self._check_commands() == EXIT_SUCCESS:
                break
            _, self._current_frame = self._capture.read()            
        self._capture.release()
        cv2.destroyAllWindows()

    def _drow_information_text(self):
        if self._rectangle is not None:
            (success, box) = self._tracker.update(self._current_frame)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(self._current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            self._fps.update()
            self._fps.stop()
            info = self._create_information_text(success)
            for (i, (key, value)) in enumerate(info):
                text = "{}: {}".format(key, value)
                cv2.putText(
                    self._current_frame, text, (10, self._frame_height - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
                )

    def _create_information_text(self, success):        
        return [
            ("Tracker", self._tracker),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(self._fps.fps())),
        ]

    def _check_commands(self):
        key = cv2.waitKey(30) & 0xFF
        # Esc - выход
        if key == 27:
            return EXIT_SUCCESS
        if cv2.getWindowProperty(DEFAULT_FRAME_WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:        
            return EXIT_SUCCESS
        elif key == ord("a"):
            self._select_rectangle()
        return CONTINUE_PROCESSING


    def _select_rectangle(self):
        old_rectangle = self._rectangle
        self._rectangle = cv2.selectROI(
            "Frame", self._current_frame, fromCenter=False, showCrosshair=True
        )
        if not old_rectangle is None:
            self._tracker = OPENCV_OBJECT_TRACKERS[self._tracker_name]()                
        self._tracker.init(self._current_frame, self._rectangle)
        self._fps = FPS().start()
