import datetime
import os

import cv2
import numpy

from .constants import *


class Video:
    """ Поиск и отображение движущихся объектов на видео

    Parameters
    ----------
    path_video: str
        Путь к файлу с видео

    Attributes
    ----------
    _path: str
        Путь к видео,
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
    """

    def __init__(self, path_video):
        self._path = path_video
        self._capture = cv2.VideoCapture(self._path)
        self._init_characteristics()
        self._count_frame = 1
        self._init_out_video()


    def _init_characteristics(self):
        """ Инициализировать характеристики:
                текущий первый кадр, 
                высота и ширина кадра,
                маска,
                результат с видео
        """
        _, self._current_frame = self._capture.read()
        self._frame_height, self._frame_width, _ = self._current_frame.shape
        self._foreground_mask = None

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
        """ Выполнить обработку видео """
        background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG(history=3, backgroundRatio = 0.95)

        while(True):
            if self._current_frame is None:
                break  
            self._foreground_mask = background_subtractor.apply(self._current_frame)
            self._drow_contours()
            self._show_video()
            self._save_video()
            if self._check_commands() == EXIT_SUCCESS:
                break
            _, self._current_frame = self._capture.read()
            self._count_frame += 1
        self._capture.release()
        cv2.destroyAllWindows()
        

    def _drow_contours(self):
        """ Нарисовать окаймляющие контуры на текущем кадре """
        place_foreground_mask = self._produce_place_foreground_mask()
        place_framing_rectangles = self._produce_place_framing_rectangles(place_foreground_mask)
        self._process_foreground_mask()
        contours, _ = cv2.findContours(
            self._foreground_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )        
        self._drow_framing_rectangles(contours, place_framing_rectangles)


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


    def _drow_framing_rectangles(self, contours, place_framing_rectangles):
        """ Нарисовать объемлющие прямоугольники 
        вокруг движущихся объектов и их количество
        Parameters
        ----------
        contours:  [array([[[int, int],...]], dtype=int32)]
            Контуры объектов 
        place_framing_rectangles: [(x1, y1, x2, y2), ...]
            Координаты углов прямоугольников
        """
        amount_drawn_contours = 0
        rectangle_color = (0, 0, 255)
        font_scale = 0.5
        clear_current_frame = self._current_frame.copy()
        for contour in contours:
            flag_drawn = False
            x1, y1, w, h = cv2.boundingRect(contour)
            x2, y2 = x1 + w, y1 + h
            for rec in place_framing_rectangles:
                if(self._is_intersecting_rectangles(rec, (x1, y1, x2, y2))):                    
                    if(not flag_drawn):
                        amount_drawn_contours += 1
                        cv2.rectangle(
                            self._current_frame, (x1, y1), (x2, y2), rectangle_color, thickness=2
                        )                        
                        cv2.putText(
                            self._current_frame, 
                            "num-" + str(self._count_frame) + "_" 
                            + str(x1) + "-" + str(y1) + "_" + str(x2) + "-" + str(y2),
                            (x1, y1 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, rectangle_color, thickness=2
                        )
                        self._save_image(clear_current_frame, x1, y1, x2, y2)
                        flag_drawn = True
                    
        self._drow_count(amount_drawn_contours)


    def _is_intersecting_rectangles(self, first_rectangle, second_rectangle):
        """ Пересекаются ли прямоугольники         
        Returns
        -------
        True / False - пересекаются ли прямоугольники
        """
        r1_x1, r1_y1, r1_x2, r1_y2 = first_rectangle
        r2_x1, r2_y1, r2_x2, r2_y2 = second_rectangle
        if(r1_x1 > r2_x2 or r1_x2 < r2_x1 or r1_y1 > r2_y2 or r1_y2 < r2_y1):
            return False
        return True

    
    def _save_image(self, clear_current_frame, x1, y1, x2, y2):
        cv2.imwrite(
            DIRECTORY_SAVING + "num-" 
            + str(self._count_frame) + "_" 
            + str(x1) + "-" + str(y1) + "_" + str(x2) + "-" + str(y2)
            + ".jpg", 
            cv2.resize(clear_current_frame[y1:y2, x1:x2], (150, 150))
        )       


    def _drow_count(self, amount_drawn_contours):
        """ Нарисовать счетчик с количеством объемлющих прямоугольников
        Parameters
        ----------
        amount_drawn_contours: int
            Количество объемлющих прямоугольников
        """
        coordinate_x_place_text = numpy.int(self._frame_width / 2) - 30
        COORDINATE_Y_PLACE_TEXT = 50
        font_scale = 1
        text_color = (0, 0, 255)
        cv2.putText(
            self._current_frame, str(amount_drawn_contours),
            (coordinate_x_place_text, COORDINATE_Y_PLACE_TEXT),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness=2
        )


    def _show_video(self):
        """ Показать результат """
        cv2.namedWindow(DEFAULT_FRAME_WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.imshow(DEFAULT_FRAME_WINDOW_NAME, self._current_frame)

    def _save_video(self):
        """ Сохранить результат """
        self._out_video.write(self._current_frame)

    def _check_commands(self):
        """ Проверить нет ли команд 
                - окончания просмотра 
                - сохранения текущего кадра
        Returns
        -------
        EXIT_SUCCESS - если, конец просмотра 
        CONTINUE_PROCESSING - если, продолжение просмотра 
        """
        key = cv2.waitKey(30) & 0xff
        # Esc - выход
        if key == 27:
            return EXIT_SUCCESS
        # s - Сохранить кадр и маску
        if key == ord("s"):
            self._save_frame()
        if cv2.getWindowProperty(DEFAULT_FRAME_WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:        
            return EXIT_SUCCESS
        return CONTINUE_PROCESSING


    def _save_frame(self):
        """ Сохранить кадр """
        try:
            os.makedirs(DIRECTORY_SAVING)
        except OSError:
            pass
        now = datetime.datetime.now()
        now = str(now.strftime("%Y-%m-%d_%H-%M-%S_"))
        cv2.imwrite(DIRECTORY_SAVING + now + DEFAULT_IMAGE_NAME, self._current_frame)
