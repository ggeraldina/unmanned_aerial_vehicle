import numpy
import cv2

from constants import *


class Video:
    def __init__(self, path_video, saving_videos=False):
        self._path = path_video
        self.__saving_videos = saving_videos
        self.__capture = cv2.VideoCapture(self._path)
        self.__init_characteristics()

    def __init_characteristics(self):
        # Read the first frame
        _, self.__current_frame = self.__capture.read()
        self._frame_height, self._frame_width, _ = self.__current_frame.shape
        if self.__saving_videos:
            self.__init_out_video()

    def __init_out_video(self):
        # The result is saved in the video
        framerate = 10
        self.__out_video = cv2.VideoWriter(
            DEFAULT_VIDEO_NAME, cv2.VideoWriter_fourcc(*"mp4v"),
            framerate, (self._frame_width, self._frame_height)
        )
        self.__out_video_mask = cv2.VideoWriter(
            DEFAULT_VIDEO_MASK_NAME, cv2.VideoWriter_fourcc(*"mp4v"),
            framerate, (self._frame_width, self._frame_height)
        )

    def run(self):
        # Background subtractor
        background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()

        while(True):
            # Computes a foreground mask
            foreground_mask = background_subtractor.apply(self.__current_frame)
            kornel_size = (5, 5)
            sigma = 1
            foreground_mask = cv2.GaussianBlur(
                foreground_mask, kornel_size, sigma
            )

            self._drow_contours(foreground_mask)

            # Show the foreground mask video and the video
            cv2.imshow("foreground mask", foreground_mask)
            cv2.imshow("frame", self.__current_frame)

            # Save the foreground mask video and the video
            if self.__saving_videos:
                self.__out_video_mask.write(cv2.cvtColor(
                    foreground_mask, cv2.COLOR_GRAY2RGB))
                self.__out_video.write(self.__current_frame)         
            
            if self.__check_commands() == EXIT_SUCCESS:
                break

            # Read a next frame
            _, self.__current_frame = self.__capture.read()

        self.__capture.release()
        cv2.destroyAllWindows()

    def _drow_contours(self, foreground_mask):
        contours, hierarchy = cv2.findContours(
            foreground_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        # Drow contours
        self._drow_framing_contours(contours, hierarchy)
        # OR drow framing rectangles
        self._drow_framing_rectangles(contours)

    def _drow_framing_rectangles(self, contours):
        amount_drawn_contours = 0
        rectangle_color = (0, 0, 255)
        min_size_contour_area = 1000
        for contour in contours:
            if cv2.contourArea(contour) > min_size_contour_area:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(
                    self.__current_frame, (x, y), (x + w, y + h), rectangle_color, thickness=2
                )
                amount_drawn_contours += 1
        # Text on the frame
        self._show_count(amount_drawn_contours)

    def _show_count(self, amount_drawn_contours):
        coordinate_x_place_text = numpy.int(self._frame_width / 2) - 30
        COORDINATE_Y_PLACE_TEXT = 50
        font_scale = 1
        text_color = (0, 0, 255)
        cv2.putText(
            self.__current_frame, str(amount_drawn_contours),
            (coordinate_x_place_text, COORDINATE_Y_PLACE_TEXT),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness=2
        )

    def _drow_framing_contours(self, contours, hierarchy):
        contour_index = -1
        contour_color = (0, 255, 0)
        cv2.drawContours(
            self.__current_frame, contours, contour_index, contour_color,
            thickness=1, lineType=cv2.LINE_AA, hierarchy=hierarchy, maxLevel=1
        )

    def __check_commands(self):
        key = cv2.waitKey(30) & 0xff
        # Exit
        if key == 27:
            return EXIT_SUCCESS
        # Save the frame and the foreground mask
        if key == ord("s"):
            cv2.imwrite(DEFAULT_IMAGE_NAME, self.__current_frame)
            cv2.imwrite(DEFAULT_IMAGE_MASK_NAME, foreground_mask)
        return CONTINUE_PROCESSING
