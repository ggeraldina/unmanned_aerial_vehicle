import datetime
import os

from imutils.video import FPS
import imutils
import cv2

from .tracker_list import TrackerList
from .constants import *
from .utils import is_intersecting_rectangles


class AutoTracker:
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
    _trackers: TrackerList
        Трекеры
    _capture: VideoCapture
        Видео, 
    _current_frame: array([...], dtype=uint8)
        Текущий кадр, 
    _frame_height: int
        Высота кадра, 
    _frame_width: int
        Ширина кадра
    _foreground_mask: array([[0, 0, 0, ..., 0, 0, 0],..., dtype=uint8)
        Маска кадра
    _fps: float
        Счетчик кадров в секунду
    """

    def __init__(self, path_video, tracker_name):
        self._tracker_name = tracker_name
        self._trackers = TrackerList()
        self._capture = cv2.VideoCapture(path_video)
        _, self._current_frame = self._capture.read()
        self._current_frame = imutils.resize(
            self._current_frame, width=WINDOW_WIDTH
        )
        self._frame_height, self._frame_width = self._current_frame.shape[:2]
        self._foreground_mask = None
        self._fps = None

    def run(self):
        """ Выполнить трекинг объектов на видео """
        amount_frame = 1
        background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG(
            history=3, backgroundRatio=0.95
        )

        while True:
            if self._current_frame is None:
                break
            self._current_frame = imutils.resize(
                self._current_frame, width=WINDOW_WIDTH
            )
            self._foreground_mask = background_subtractor.apply(
                self._current_frame
            )
            if self._trackers.get_count_current_boxes() == 0 or amount_frame % 10 == 0:
                boxes = self._detect_framing_boxes()
                self._track_boxes(boxes)
            self._drow_information_text()
            cv2.imshow(DEFAULT_FRAME_WINDOW_NAME, self._current_frame)
            if self._check_commands() == EXIT_SUCCESS:
                break
            _, self._current_frame = self._capture.read()
            amount_frame += 1
        self._capture.release()
        cv2.destroyAllWindows()

    def _detect_framing_boxes(self):
        """ Детектировать области на текущем кадре """
        place_foreground_mask = self._produce_place_foreground_mask()
        place_framing_rectangles = self._produce_place_framing_rectangles(
            place_foreground_mask
        )
        self._process_foreground_mask()
        contours, hierarchy = cv2.findContours(
            self._foreground_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return self._produce_framing_boxes(contours, place_framing_rectangles)

    def _produce_place_foreground_mask(self):
        """ Создать маску для определения места, где находится объект """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        return cv2.morphologyEx(
            self._foreground_mask.copy(), cv2.MORPH_OPEN, kernel
        )

    def _produce_place_framing_rectangles(self, place_foreground_mask):
        """ Вычислить окаймляющие прямоугольники для маски места 
        Parameters
        ----------
        place_foreground_mask:  array([[0, 0, 0, ..., 0, 0, 0],..., dtype=uint8)
            Маска локации
        Returns
        -------
        [(x1, y1, x2, y2), ...] - Координаты углов прямоугольников
        """
        contours, _ = cv2.findContours(
            place_foreground_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        place_framing_rectangles = []
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            place_framing_rectangles.append((x, y, x + w, y + h))
        return place_framing_rectangles

    def _process_foreground_mask(self):
        """ Обработать маску текущего кадра """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self._foreground_mask = cv2.morphologyEx(
            self._foreground_mask.copy(), cv2.MORPH_CLOSE, kernel
        )
        kornel_size = (3, 3)
        sigma = 1
        self._foreground_mask = cv2.GaussianBlur(
            self._foreground_mask.copy(), kornel_size, sigma
        )

    def _produce_framing_boxes(self, contours, place_framing_rectangles):
        """ Нарисовать объемлющие прямоугольники 
        вокруг движущихся объектов и их количество
        Parameters
        ----------
        contours:  [array([[[int, int],...]], dtype=int32)]
            Контуры объектов 
        place_framing_rectangles: [(int, int, int, int), ...]
            Координаты углов прямоугольников (x1, y1, x2, y2)

        Returns
        -------
        [(x, y, w, h)...] - Выбранные области
        """
        boxes = []
        for contour in contours:
            selected = False
            x1, y1, w, h = cv2.boundingRect(contour)
            x2, y2 = x1 + w, y1 + h
            for rec in place_framing_rectangles:
                if is_intersecting_rectangles(rec, (x1, y1, x2, y2)):
                    if not selected:
                        boxes.append((x1, y1, w, h))
                        selected = True
        return boxes

    def _track_boxes(self, boxes):
        """ Отследить области для трекинга

        Parameters
        ----------
        boxes: [(int, int, int, int)...]
            Выбранные области
        """
        # self._clear_boxes()
        for box in boxes:
            tracker = OPENCV_OBJECT_TRACKERS[self._tracker_name]()
            self._trackers.add_with_update(tracker, self._current_frame, box)
        self._fps = FPS().start()

    def _drow_information_text(self):
        """ Отобразить информацию о трекинге """
        if self._trackers.get_count_current_boxes() == 0:
            return
        (success, boxes) = self._trackers.update(self._current_frame)
        color = (0, 0, 255)
        last_box_index = boxes.__len__() - 1
        if success:
            for i, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(
                    self._current_frame, (x, y),
                    (x + w, y + h),
                    color if not i == last_box_index else (0, 225, 0),
                    1
                )
        self._fps.update()
        self._fps.stop()
        info = self._create_information_text(success)
        for (i, (key, value)) in enumerate(info):
            text = "{}: {}".format(key, value)
            cv2.putText(
                self._current_frame, text,
                (10, self._frame_height - ((i * 20) + 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1
            )

    def _create_information_text(self, success):
        """ Создать информацию о трекинге для текущего кадра 
        Parameters
        ----------
        success: bool

        Returns
        -------
        [(str, str), ...] - [(Название характеристики, значение)...]
        """
        return [
            ("Tracker", self._tracker_name),
            ("Count", self._trackers.get_count_current_boxes()),
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
            self._add_box()
        elif key == ord("x"):
            self._update_box()
        elif key == ord("z"):
            self._auto_all_update_box()
        elif key == ord("d"):
            self._delete_box()
        elif key == ord("c"):
            self._clear_boxes()
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

    def _add_box(self):
        """ Выбрать область для трекинга """
        box = cv2.selectROI(
            DEFAULT_FRAME_WINDOW_NAME, self._current_frame,
            fromCenter=False, showCrosshair=True
        )
        tracker = OPENCV_OBJECT_TRACKERS[self._tracker_name]()
        self._trackers.add(tracker, self._current_frame, box)

    def _update_box(self):
        """ Обновить область для трекинга """
        box = cv2.selectROI(
            DEFAULT_FRAME_WINDOW_NAME, self._current_frame,
            fromCenter=False, showCrosshair=True
        )
        tracker = OPENCV_OBJECT_TRACKERS[self._tracker_name]()
        self._trackers.add_with_update(tracker, self._current_frame, box)

    def _auto_all_update_box(self):
        """ Автоматически обновить область для трекинга """
        self._clear_boxes()
        boxes = self._detect_framing_boxes()
        self._track_boxes(boxes)

    def _delete_box(self):
        """ Удалить трекинг для всех объектов из выделенной области """
        box = cv2.selectROI(
            DEFAULT_FRAME_WINDOW_NAME, self._current_frame,
            fromCenter=False, showCrosshair=True
        )
        self._trackers.delete(box)

    def _clear_boxes(self):
        """ Очистить все выбранные прямоугольники """
        self._trackers = TrackerList()
