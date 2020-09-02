import csv

import cv2

from .constants import *


class Reader:
    def __init__(self, path_video, path_csv, saving_video=False):
        self._path_csv = path_csv
        self._capture = cv2.VideoCapture(path_video)
        _, self._current_frame = self._capture.read()
        self._amount_frame = 0
        self._frame_height, self._frame_width = self._current_frame.shape[:2]
        self._box = None

    def run(self):
        with open(self._path_csv, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if self._current_frame is None:
                    break
                while int(row["frame"]) > self._amount_frame:
                    if self._current_frame is None:
                        break
                    self._drow_count()
                    cv2.namedWindow(DEFAULT_FRAME_WINDOW_NAME, cv2.WINDOW_NORMAL)
                    cv2.imshow(DEFAULT_FRAME_WINDOW_NAME, self._current_frame)
                    if self._check_commands() == EXIT_SUCCESS:
                        break                        
                    _, self._current_frame = self._capture.read()
                    self._amount_frame += 1

                if not row["logs"] == "":
                    continue
                cv2.rectangle(
                    self._current_frame, (int(row["x"]), int(row["y"])),
                    (int(row["x"]) + int(row["w"]), int(row["y"]) + int(row["h"])),
                    (0, 0, 255),
                    2
                )                
                if self._check_commands() == EXIT_SUCCESS:
                    break                        

    def _drow_count(self):
        """ Нарисовать счетчик
        Parameters
        ----------
        amount_drawn_contours: int
            Количество объемлющих прямоугольников
        """
        coordinate_x_place_text = int(self._frame_width / 2) - 150
        COORDINATE_Y_PLACE_TEXT = 50
        font_scale = 1
        text_color = (0, 0, 255)
        cv2.putText(
            self._current_frame, "Number frame: " + str(self._amount_frame),
            (coordinate_x_place_text, COORDINATE_Y_PLACE_TEXT),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness=2
        )

    def _check_commands(self):
        """ Проверить нет ли команд 
                - окончания просмотра
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
        return CONTINUE_PROCESSING