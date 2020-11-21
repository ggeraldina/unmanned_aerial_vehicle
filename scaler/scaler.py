import datetime
import os
import csv
import cv2

from .constants import *

# Папки для записи должы существовать
class Scaler:
    def __init__(self, path_to_video, path_to_csv, path_to_frames_csv, width, height=None):
        self._path_to_video = path_to_video
        self._path_to_csv = path_to_csv
        self._path_to_frames = path_to_frames_csv     
        self._capture = cv2.VideoCapture(self._path_to_video)
        _, self._current_frame = self._capture.read()
        self._frame_height, self._frame_width = self._current_frame.shape[:2]        
        self._current_frame = self.resize(
            self._current_frame, width=width, height=height
        )
        self._amount_frame = 0
        self._new_height, self._new_width = self._current_frame.shape[:2]

    def run(self):   
        # Чтение кадров, которые нужно сохранить
        name_video = os.path.basename(self._path_to_video).split(".")[0]
        height_ratio = self._new_height / float(self._frame_height)
        width_ratio = self._new_width / float(self._frame_width)
        with open(self._path_to_frames, newline="") as frames_file:
            frames_reader = csv.DictReader(frames_file)            
            frame_row = next(frames_reader, None) 
            # Чтение разметки
            with open(self._path_to_csv, newline="") as csv_file:  
                reader = csv.DictReader(csv_file)            
                row = next(reader, None)
                # Запись csv с характеристиками для tfrecord
                with open(DIRECTORY_SAVING + CSV_RESULT, "w", newline="") as result_csv_file:                    
                    fieldnames = [
                            "video", "frame", "height", "width", 
                            "path", "name", 
                            "xtl", "ytl", "xbr", "ybr", 
                            "w", "h"
                        ]
                    writer = csv.DictWriter(result_csv_file, fieldnames=fieldnames, delimiter=";")
                    writer.writeheader()
                    while(True):
                        self._current_frame = self.resize(
                            self._current_frame, width=self._new_width, height=self._new_height
                        )
                        if self._current_frame is None:
                            break  
                        if row is None:
                            break     
                        if frame_row is None:
                            break
                        print("Current frame " + str(self._amount_frame))
                        save_frame = int(frame_row["frame"])
                        box_frame = int(row["frame"])
                        if box_frame > save_frame:
                            frame_row = next(frames_reader, None)
                            continue
                        if box_frame < save_frame:
                            row = next(reader, None)
                            continue
                        if self._amount_frame < save_frame:
                            _, self._current_frame = self._capture.read()
                            self._amount_frame += 1
                            continue
                        now = datetime.datetime.now()
                        now = str(now.strftime("%Y-%m-%d_%H-%M-%S_%f")) + "_#" + str(save_frame)
                        cv2.imwrite(DIRECTORY_IMAGE_SAVING + now + ".jpg", self._current_frame)
                        new_xtl = int(int(row["x"]) * width_ratio)
                        new_ytl = int(int(row["y"]) * height_ratio)
                        new_w = int(int(row["w"]) * width_ratio)
                        new_h = int(int(row["h"]) * height_ratio)
                        writer.writerow(
                                {
                                    "video": name_video, 
                                    "frame": save_frame, 
                                    "height": self._new_height, 
                                    "width": self._new_width, 
                                    "path": DIRECTORY_IMAGE_SAVING + now + ".jpg", 
                                    "name": now, 
                                    "xtl": new_xtl, 
                                    "ytl": new_ytl, 
                                    "xbr": new_xtl + new_w, 
                                    "ybr": new_ytl + new_h, 
                                    "w": new_w, 
                                    "h": new_h
                                }
                            )
                        cv2.rectangle(
                            self._current_frame, 
                            (
                                new_xtl, 
                                new_ytl
                            ),
                            (
                                new_xtl + new_w, 
                                new_ytl + new_h
                            ),
                            (0, 0, 255),
                            1
                        )
                        cv2.imwrite(DIRECTORY_CHECK_IMAGE_SAVING + "check_" + now + ".jpg", self._current_frame)
                        frame_row = next(frames_reader, None)                          
                        row = next(reader, None)

    def resize(self, image, width=None, height=None):
        dim = (width, height)
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        if height is None:
            r = width / float(w)
            dim = (width, int(h * r))        
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        return resized
    