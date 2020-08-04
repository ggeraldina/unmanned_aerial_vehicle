import datetime
import time
import os

from imutils.video import FPS
import imutils
import cv2

from .tracker_list import TrackerList
from .constants import *
from .utils import is_intersecting_boxes


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
        Ширина кадра,
    _foreground_mask: array([[0, 0, 0, ..., 0, 0, 0],..., dtype=uint8)
        Маска кадра,
    _fps: float
        Счетчик кадров в секунду,
    _update_manually: bool
        Обновление вручную
    _tracking_area: (int, int, int, int)
        (x, y, w, h) - характеристики прямоугольника,
    _exception_area: [(int, int, int, int), ...]
        (x, y, w, h) - характеристики прямоугольника,
    _saving_videos: bool
        Флаг сохранения результата,

    Если был передан флаг сохранения видео saving_videos:
    _out_video: VideoWriter
        Видео с контурами
    """

    def __init__(self, path_video, tracker_name, saving_videos=False):
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
        self._update_manually = False
        self._tracking_area = (0, 0, self._frame_width, self._frame_height)
        self._exception_area = []  
        self._saving_videos = saving_videos
        if self._saving_videos:
            self._init_out_video()

    def _init_out_video(self):
        """ Инициализировать атрибуты с видео результатом """
        try:
            os.makedirs(DIRECTORY_SAVING)
        except OSError:
            pass
        now = datetime.datetime.now()
        now = str(now.strftime("%Y-%m-%d_%H-%M-%S_"))     
        framerate = 10
        self._out_video = cv2.VideoWriter(
            DIRECTORY_SAVING + now + DEFAULT_VIDEO_NAME, 
            cv2.VideoWriter_fourcc(*"mp4v"),
            framerate, (self._frame_width, self._frame_height)
        )

    def run(self):
        """ Выполнить трекинг объектов на видео """
        amount_frame = 1
        background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG(
            history=3, backgroundRatio=0.95
        )

        while True:
            if self._current_frame is None:
                break            
            self._fps = FPS().start()
            self._fps.update()
            self._current_frame = imutils.resize(
                self._current_frame, width=WINDOW_WIDTH
            )
            self._foreground_mask = background_subtractor.apply(
                self._current_frame
            )
            if self._trackers.get_count_current_boxes() == 0 or amount_frame % 10 == 0 or self._update_manually:
                boxes = self._detect_framing_boxes()
                self._track_boxes(boxes)
                self._update_manually = False
            success = self._drow_rectangles()
            self._save_video()
            if not success is None:
                self._drow_information_text(success)
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
        place_framing_boxes = self._produce_place_framing_boxes(
            place_foreground_mask
        )
        self._process_foreground_mask()
        contours, hierarchy = cv2.findContours(
            self._foreground_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        boxes =  self._produce_framing_boxes(contours, place_framing_boxes)
        result_boxes = []
        for box in boxes:
            if self._is_box_in_area(box):
                result_boxes.append(box)
        return result_boxes

    def _is_box_in_area(self, box):
        """ Входит ли выделеннный объект в область отслеживания
        
        Returns
        -------
        True / False - Входит / Нет
        """
        if not is_intersecting_boxes(box, self._tracking_area):
            return False
        for ex_area in self._exception_area:
            if is_intersecting_boxes(box, ex_area):
                return False
        return True

    def _produce_place_foreground_mask(self):
        """ Создать маску для определения места, где находится объект """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        return cv2.morphologyEx(
            self._foreground_mask.copy(), cv2.MORPH_OPEN, kernel
        )

    def _produce_place_framing_boxes(self, place_foreground_mask):
        """ Вычислить окаймляющие прямоугольники для маски места 
        Parameters
        ----------
        place_foreground_mask:  array([[0, 0, 0, ..., 0, 0, 0],..., dtype=uint8)
            Маска локации
        Returns
        -------
        [(x1, y1, w, h), ...] - Координаты углов прямоугольников
        """
        contours, _ = cv2.findContours(
            place_foreground_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        place_framing_boxes = []
        for contour in contours:
            place_framing_boxes.append(cv2.boundingRect(contour))
        return place_framing_boxes

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

    def _produce_framing_boxes(self, contours, place_framing_boxes):
        """ Нарисовать объемлющие прямоугольники 
        вокруг движущихся объектов и их количество
        Parameters
        ----------
        contours:  [array([[[int, int],...]], dtype=int32)]
            Контуры объектов 
        place_framing_boxes: [(int, int, int, int), ...]
            Координаты углов прямоугольников (x1, y1, w, h)

        Returns
        -------
        [(x, y, w, h)...] - Выбранные области
        """
        boxes = []
        for contour in contours:
            selected = False
            x1, y1, w, h = cv2.boundingRect(contour)
            for box in place_framing_boxes:
                if is_intersecting_boxes(box, (x1, y1, w, h)):
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

    def _drow_rectangles(self):
        """ Отобразить информацию о трекинге 

        Returns
        -------
        success: bool - Нет ли потерянных объектов
        """
        if self._trackers.get_count_current_boxes() == 0:
            return
        (success, boxes) = self._trackers.update(self._current_frame)
        last_box_index = boxes.__len__() - 1
        if success:
            for i, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(
                    self._current_frame, (x, y),
                    (x + w, y + h),
                    (0, 0, 255) if not i == last_box_index else (0, 225, 0),
                    1
                )
        return success

    def _drow_information_text(self, success):
        """ Отобразить информацию о трекинге

        Parameters
        ----------
        success: bool
        """
        info = self._create_information_text(success)
        for (i, (key, value)) in enumerate(info):
            text = "{}: {}".format(key, value)
            cv2.putText(
                self._current_frame, text,
                (10, self._frame_height - ((i * 20) + 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1
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
        self._fps.stop()
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
        if not key == 255:
            print(INFO_KEY[chr(key)])
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
            self._update_manually_boxes()
        elif key == ord("d"):
            self._delete_box()
        elif key == ord("c"):
            self._clear_boxes()
        elif key == ord("f"):
            self._add_tracking_area()
        elif key == ord("g"):
            self._add_exception_area()
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

    def _update_manually_boxes(self):
        """ Автоматически обновить область для трекинга """
        self._update_manually = True

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

    def _add_tracking_area(self):        
        box = cv2.selectROI(
            DEFAULT_FRAME_WINDOW_NAME, self._current_frame,
            fromCenter=False, showCrosshair=True
        )
        if box == (0, 0, 0, 0):
            return
        self._tracking_area = box

    def _add_exception_area(self):       
        box = cv2.selectROI(
            DEFAULT_FRAME_WINDOW_NAME, self._current_frame,
            fromCenter=False, showCrosshair=True
        )
        if box == (0, 0, 0, 0):
            return
        self._exception_area.append(box)
    
    def _save_video(self):
        """ Сохранить результат """
        if self._saving_videos:
            self._out_video.write(self._current_frame)
