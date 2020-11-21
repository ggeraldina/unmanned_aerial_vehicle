import datetime
import os
import csv
import xml.etree.ElementTree as xml

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

    def convert_xml_to_my_csv(self):
        now = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_"))        
        name_input_file = os.path.basename(self._path_in_file).split(".")[0]
        csv_file_name = DIRECTORY_SAVING + now + name_input_file + ".csv"
        fieldnames = ["frame", "x", "y", "w", "h", "logs"]
        with open(csv_file_name, "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            xml_tree = xml.parse(self._path_in_file)
            xml_root = xml_tree.getroot()
            for box in xml_root.findall(".//box[@outside='0']"):
                frame = int(box.get("frame"))
                x = int(float(box.get("xtl")))
                y = int(float(box.get("ytl")))
                w = int(float(box.get("xbr"))) - x
                h = int(float(box.get("ybr"))) - y        
                writer.writerow(
                    {"frame": frame, "x": x, "y": y, "w": w, "h": h}
                )
        self.sort_csv(csv_file_name, fieldnames)

    def sort_csv(self, csv_file_name, fieldnames):
        sorted_list = []
        with open(csv_file_name, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            sorted_list = sorted(reader, key=lambda row:(int(row["frame"])), reverse=False)
        with open(csv_file_name, "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_list)

