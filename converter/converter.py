import datetime
import os
import csv

from .constants import *


class Converter:
    def __init__(self, path_in_file):
        self._path_in_file = path_in_file

    def convert_my_csv_to_my_xml(self):
        now = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_"))        
        name_video = os.path.basename(self._path_in_file).split(".")[0]
        xml_file_name = DIRECTORY_SAVING + now + name_video + ".txt"
        tracker_number = 0
        frame_start = 0
        with open(xml_file_name, "w") as xml_file:
            with open(self._path_in_file, newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                row = next(reader, None)
                while(True):
                    if not row is None:
                        if not row["logs"] == "" or int(row["frame"]) < frame_start:
                            row = next(reader, None)
                            continue                    
                        start_tag = f'  <track id="{tracker_number}" label="drone" source="manual">\n'
                        line = f'    <box frame="{row["frame"]}" outside="0" occluded="0" keyframe="1" xtl="{int(row["x"])}" ytl="{int(row["y"])}" xbr="{int(row["x"]) + int(row["w"])}" ybr="{int(row["y"]) + int(row["h"])}">\n    </box>\n'
                        end_tag = f'    <box frame="{int(row["frame"]) + 1}" outside="1" occluded="0" keyframe="1" xtl="{int(row["x"])}" ytl="{int(row["y"])}" xbr="{int(row["x"]) + int(row["w"])}" ybr="{int(row["y"]) + int(row["h"])}">\n    </box>\n  </track>\n'
                        xml_file.write(start_tag + line + end_tag)
                        tracker_number += 1
                        row = next(reader, None)
                    else:
                        break


    def convert_txt_drone_vs_bird_to_my_xml(self):
        now = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_"))        
        name_video = os.path.basename(self._path_in_file).split(".")[0]
        xml_file_name = DIRECTORY_SAVING + now + name_video + ".txt"
        tracker_number = 0
        frame_start = 0
        shift = 5
        with open(xml_file_name, "w") as xml_file:
            with open(self._path_in_file, "r") as txt_file:
                try:
                    row = txt_file.__next__()
                    while(True):
                        if not row is None:
                            arr_row = row.split(" ", 2)
                            number_frame = int(arr_row[0])
                            amount_drone_in_frame = int(arr_row[1])
                            if amount_drone_in_frame == 0 or number_frame < frame_start:
                                row = txt_file.__next__()
                                continue
                            arr_drone = arr_row[2].split(" ")
                            for i in range(amount_drone_in_frame):
                                start_tag = f'  <track id="{tracker_number}" label="drone" source="manual">\n'
                                line = f'    <box frame="{number_frame}" outside="0" occluded="0" keyframe="1" xtl="{int(arr_drone[0 + shift * i])}" ytl="{int(arr_drone[1 + shift * i])}" xbr="{int(arr_drone[0 + shift * i]) + int(arr_drone[2 + shift * i])}" ybr="{int(arr_drone[1 + shift * i]) + int(arr_drone[3 + shift * i])}">\n    </box>\n'
                                end_tag = f'    <box frame="{number_frame + 1}" outside="1" occluded="0" keyframe="1" xtl="{int(arr_drone[0 + shift * i])}" ytl="{int(arr_drone[1 + shift * i])}" xbr="{int(arr_drone[0 + shift * i]) + int(arr_drone[2 + shift * i])}" ybr="{int(arr_drone[1 + shift * i]) + int(arr_drone[3 + shift * i])}">\n    </box>\n  </track>\n'
                                xml_file.write(start_tag + line + end_tag)
                                tracker_number += 1
                            row = txt_file.__next__()
                        else:
                            break
                except StopIteration:
                    return
