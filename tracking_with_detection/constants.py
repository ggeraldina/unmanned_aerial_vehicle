import cv2

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

INFO_KEY = {
    "s": "Press key: s. Сохранить кадр",
    "a": "Press key: a. Добавить область с объектом",
    "x": "Press key: x. Изменить рамку объекта",
    "z": "Press key: z. Детектировать движение и обновить рамки",
    "d": "Press key: d. Удалить рамку",
    "c": "Press key: c. Удалить все рамки",
    "f": "Press key: f. Изменить зону детекции",
    "g": "Press key: g. Добавить зону исключения детекции",
    " ": "Press key: Пробел"
}

DIRECTORY_SAVING = "saving/"
DEFAULT_IMAGE_NAME = "Tracker_frame_video.png"
DEFAULT_VIDEO_NAME = "Video.mp4"

DEFAULT_FRAME_WINDOW_NAME = "Frame"
WINDOW_WIDTH = 1000

EXIT_SUCCESS = 0
# EXIT_FAILURE = 1
CONTINUE_PROCESSING = 2
