import datetime
import os

from imutils.video import FPS
import imutils
import cv2

from .constants import *


class Tracker:
    """ Поиск и отображение движущихся объектов на видео

    Parameters
    ----------
    path_video: str
        Путь к файлу с видео, 
    tracker_name: str
        Название трекера:
            "csrt",
            "kcf", 
            "boosting", 
            "mil", 
            "tld", 
            "medianflow",
            "mosse"

    Attributes
    ----------
    _tracker_name: str
        Название трекера
    _tracker: TrackerXXX
        Трекер
    _capture: VideoCapture
        Видео, 
    _current_frame: array([...], dtype=uint8)
        Текущий кадр, 
    _frame_height: int
        Высота кадра, 
    _frame_width: int
        Ширина кадра
    _rectangle: (int, int, int, int)
        Окаймляющий прямоугольник (x, y, w, h)
    _fps: float
        Счетчик кадров в секунду
    """

    def __init__(self, path_video, tracker_name):
        self._tracker_name = tracker_name
        self._tracker = OPENCV_OBJECT_TRACKERS[self._tracker_name]()
        self._capture = cv2.VideoCapture(path_video)
        _, self._current_frame = self._capture.read()
        self._current_frame = imutils.resize(
            self._current_frame, width=WINDOW_WIDTH
        )
        self._frame_height, self._frame_width = self._current_frame.shape[:2]
        self._rectangle = None
        self._fps = None

    def run(self):
        """ Выполнить трекинг объектов на видео """
        while True:
            if self._current_frame is None:
                break
            self._current_frame = imutils.resize(
                self._current_frame, width=WINDOW_WIDTH
            )
            self._drow_information_text()
            cv2.imshow(DEFAULT_FRAME_WINDOW_NAME, self._current_frame)
            if self._check_commands() == EXIT_SUCCESS:
                break
            _, self._current_frame = self._capture.read()
        self._capture.release()
        cv2.destroyAllWindows()

    def _drow_information_text(self):
        """ Отобразить информацию о трекинге """
        if self._rectangle is not None:
            (success, box) = self._tracker.update(self._current_frame)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(
                    self._current_frame, (x, y),
                    (x + w, y + h), (0, 0, 255), 2
                )
            self._fps.update()
            self._fps.stop()
            info = self._create_information_text(success)
            for (i, (key, value)) in enumerate(info):
                text = "{}: {}".format(key, value)
                cv2.putText(
                    self._current_frame, text,
                    (10, self._frame_height - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
                )

    def _create_information_text(self, success):
        """ Создать информацию о трекинге для текущего кадра 
        Returns
        -------
        [(str, str), ...] - [(Название характеристики, значение)...]
        """
        return [
            ("Tracker", self._tracker),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(self._fps.fps())),
        ]

    def _check_commands(self):
        """ Проверить нет ли команд 
                - окончания просмотра 
                - сохранения кадра 
                - выбора области
                - очищения области
        Returns
        -------
        EXIT_SUCCESS - если конец просмотра 
        CONTINUE_PROCESSING - если продолжение просмотра 
        """
        key = cv2.waitKey(30) & 0xFF
        # Esc - выход
        if key == 27:
            return EXIT_SUCCESS
        if cv2.getWindowProperty(DEFAULT_FRAME_WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            return EXIT_SUCCESS
        if key == ord("s"):
            self._save_frame()
        elif key == ord("a"):
            self._select_rectangle()
        return CONTINUE_PROCESSING

    def _save_frame(self):
        """ Сохранить кадр """
        try:
            os.makedirs(DIRECTORY_SAVING)
        except OSError:
            pass
        now = datetime.datetime.now()
        now = str(now.strftime("%Y-%m-%d_%H-%M-%S_"))
        cv2.imwrite(
            DIRECTORY_SAVING + now +
            DEFAULT_IMAGE_NAME, self._current_frame
        )

    def _select_rectangle(self):
        """ Выбрать область для трекинга """
        old_rectangle = self._rectangle
        self._rectangle = cv2.selectROI(
            DEFAULT_FRAME_WINDOW_NAME, self._current_frame,
            fromCenter=False, showCrosshair=True
        )
        if not old_rectangle is None:
            self._tracker = OPENCV_OBJECT_TRACKERS[self._tracker_name]()
        self._tracker.init(self._current_frame, self._rectangle)
        self._fps = FPS().start()
