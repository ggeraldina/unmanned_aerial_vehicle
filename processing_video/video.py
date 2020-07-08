import cv2
import numpy

from .constants import *


class Video:
    """ Поиск и отображение движущихся объектов на видео

    Parameters
    ----------
    path_video: str
        Путь к файлу с видео, 
    saving_videos: bool
        Флаг сохранения видео с результатом и его маски в mp4 файлы, 
    showing_mask: bool
        Флаг отображения маски

    Attributes
    ----------
    _path: str
        Путь к видео, 
    _saving_videos: bool
        Флаг сохранения результата, 
    _showing_mask: bool
        Флаг отображения маски, 
    _capture: VideoCapture
        Видео, 
    _current_frame: array([...], dtype=uint8)
        Текущий кадр, 
    _frame_height: int
        Высота кадра, 
    _frame_width: int
        Ширина кадра
    """

    def __init__(self, path_video, saving_videos=False, showing_mask=False):
        self._path = path_video
        self._saving_videos = saving_videos
        self._showing_mask = showing_mask
        self._capture = cv2.VideoCapture(self._path)
        self._init_characteristics()

    def _init_characteristics(self):
        """ Инициализировать характеристики:
                текущий первый кадр, 
                высота и ширина кадра, 
                результат с видео
        """
        _, self._current_frame = self._capture.read()
        self._frame_height, self._frame_width, _ = self._current_frame.shape
        if self._saving_videos:
            self._init_out_video()

    def _init_out_video(self):
        """ Инициализировать атрибуты с видео результатом """
        framerate = 10
        self._out_video = cv2.VideoWriter(
            DEFAULT_VIDEO_NAME, cv2.VideoWriter_fourcc(*"mp4v"),
            framerate, (self._frame_width, self._frame_height)
        )
        self._out_video_mask = cv2.VideoWriter(
            DEFAULT_VIDEO_MASK_NAME, cv2.VideoWriter_fourcc(*"mp4v"),
            framerate, (self._frame_width, self._frame_height)
        )

    def run(self):
        """ Выполнить обработку видео """
        background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()

        while(True):
            self._update_foreground_mask(background_subtractor)
            self._drow_contours()
            self._show_video()
            self._save_video()
            if self._check_commands() == EXIT_SUCCESS:
                break
            _, self._current_frame = self._capture.read()
        self._capture.release()
        cv2.destroyAllWindows()

    def _update_foreground_mask(self, background_subtractor):
        """ Обновить маску для текущего кадра 
        Parameters
        ----------
        background_subtractor : BackgroundSubtractor
            Вычитание фона
        """
        self._foreground_mask = background_subtractor.apply(
            self._current_frame)
        kornel_size = (5, 5)
        sigma = 1
        self._foreground_mask = cv2.GaussianBlur(
            self._foreground_mask, kornel_size, sigma
        )

    def _drow_contours(self):
        """ Нарисовать окаймляющие контуры на текущем кадре """
        contours, hierarchy = cv2.findContours(
            self._foreground_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        self._drow_framing_contours(contours, hierarchy)
        self._drow_framing_rectangles(contours)

    def _drow_framing_rectangles(self, contours):
        """ Нарисовать объемлющие прямоугольники 
        вокруг движущихся объектов и их количество
        Parameters
        ----------
        contours:  [array([[[int, int],...]], dtype=int32)]
            Контуры объектов
        """
        amount_drawn_contours = 0
        rectangle_color = (0, 0, 255)
        min_size_contour_area = 1000
        for contour in contours:
            if cv2.contourArea(contour) > min_size_contour_area:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(
                    self._current_frame, (x, y), (x + w, y + h), rectangle_color, thickness=2
                )
                amount_drawn_contours += 1
        self._drow_count(amount_drawn_contours)

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

    def _drow_framing_contours(self, contours, hierarchy):
        """ Нарисовать контур вокруг движущихся объектов
        Parameters
        ----------
        contours: [array([[[int, int],...]], dtype=int32)]
            Контуры объектов, 
        hierarchy: array([[[ int, int, int, int],...]], dtype=int32)
            Иерархия, информация о вложенности контуров
        """
        contour_index = -1
        contour_color = (0, 255, 0)
        cv2.drawContours(
            self._current_frame, contours, contour_index, contour_color,
            thickness=1, lineType=cv2.LINE_AA, hierarchy=hierarchy, maxLevel=1
        )

    def _show_video(self):
        """ Показать результат """
        if self._showing_mask:
            cv2.imshow("foreground mask", self._foreground_mask)
        cv2.imshow("frame", self._current_frame)

    def _save_video(self):
        """ Сохранить результат """
        if self._saving_videos:
            self._out_video_mask.write(
                cv2.cvtColor(self._foreground_mask, cv2.COLOR_GRAY2RGB)
            )
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
            cv2.imwrite(DEFAULT_IMAGE_NAME, self._current_frame)
            cv2.imwrite(DEFAULT_IMAGE_MASK_NAME, self._foreground_mask)
        return CONTINUE_PROCESSING
