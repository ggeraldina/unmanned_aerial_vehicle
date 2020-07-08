import numpy
import cv2

from constants import *


def run(path_video):
    capture = cv2.VideoCapture(path_video)

    # Read the first frame
    _, frame = capture.read()
    height, width, _ = frame.shape

    # The result is saved in the video
    # framerate = 10
    # out_video = cv2.VideoWriter(DEFAULT_VIDEO_NAME, cv2.VideoWriter_fourcc(*"mp4v"), framerate, (width, height))
    # out_video_mask = cv2.VideoWriter(DEFAULT_VIDEO_MASK_NAME, cv2.VideoWriter_fourcc(*"mp4v"), framerate, (width, height))

    # Background subtractor
    background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()

    while(True):
        # Computes a foreground mask
        foreground_mask = background_subtractor.apply(frame)
        kornel_size = (5, 5)
        sigma = 1
        foreground_mask = cv2.GaussianBlur(foreground_mask, kornel_size, sigma)

        drow_contours(frame, foreground_mask)

        # Show and save the foreground mask video
        # cv2.imshow("foreground mask", foreground_mask)
        # out_video_mask.write(cv2.cvtColor(foreground_mask, cv2.COLOR_GRAY2RGB))

        # Show and save the video
        cv2.imshow("frame", frame)
        # out_video.write(frame)

        key = cv2.waitKey(30) & 0xff
        # Exit
        if key == 27:
            break
        # Save the frame and the foreground mask
        if key == ord("s"):
            cv2.imwrite(DEFAULT_IMAGE_NAME, frame)
            cv2.imwrite(DEFAULT_IMAGE_MASK_NAME, foreground_mask)

        # Read a next frame
        _, frame = capture.read()

    capture.release()
    cv2.destroyAllWindows()


def drow_contours(frame, foreground_mask):
    contours, hierarchy = cv2.findContours(
        foreground_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    # Drow contours
    drow_framing_contours(frame, contours, hierarchy)
    # OR drow framing rectangles
    drow_framing_rectangles(frame, contours)


def drow_framing_rectangles(frame, contours):
    amount_drawn_contours = 0
    rectangle_color = (0, 0, 255)
    min_size_contour_area = 1000
    for contour in contours:
        if cv2.contourArea(contour) > min_size_contour_area:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(
                frame, (x, y), (x + w, y + h), rectangle_color, thickness=2
            )
            amount_drawn_contours += 1
    # Text on the frame
    show_count(frame, amount_drawn_contours)


def show_count(frame, amount_drawn_contours):
    _, width, _ = frame.shape
    coordinate_x_place_text = numpy.int(width / 2) - 30
    COORDINATE_Y_PLACE_TEXT = 50
    font_scale = 1
    text_color = (0, 0, 255)
    cv2.putText(
        frame, str(amount_drawn_contours),
        (coordinate_x_place_text, COORDINATE_Y_PLACE_TEXT),
        cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness=2
    )


def drow_framing_contours(frame, contours, hierarchy):
    contour_index = -1
    contour_color = (0, 255, 0)
    cv2.drawContours(frame, contours, contour_index, contour_color,
                     thickness=1, lineType=cv2.LINE_AA, hierarchy=hierarchy, maxLevel=1)
