import datetime
import os
import csv

from .constants import *


class Converter:
    def __init__(self, path_csv):
        self._path_csv = path_csv

    def run(self):
        now = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_"))        
        name_video = os.path.basename(self._path_csv).split(".")[0]
        xml_file_name = DIRECTORY_SAVING + now + name_video + ".txt"
        with open(xml_file_name, "w") as xml_file:
            with open(self._path_csv, newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                row = next(reader, None)
                while(True):
                    if not row is None and not row["logs"] == "":
                        row = reader.__next__()
                        continue
                    elif not row is None:
                        line = f'<box frame="{row["frame"]}" outside="0" occluded="0" keyframe="1" xtl="{int(row["x"])}" ytl="{int(row["y"])}" xbr="{int(row["x"]) + int(row["w"])}" ybr="{int(row["y"]) + int(row["h"])}">\n</box>'
                        xml_file.write(line + '\n')
                        row = next(reader, None)
