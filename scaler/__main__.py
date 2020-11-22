import argparse

from .scaler import Scaler


def parse():
    parser = argparse.ArgumentParser(
        description="This example demonstrates scaling."
    )
    parser.add_argument("--video", "-v", type=str, help="path to input video file")
    parser.add_argument("--csv", "-csv", type=str, help="path to input csv file")
    parser.add_argument("--framescsv", "-f", type=str, help="path to input frame")
    parser.add_argument("--result", "-rst", type=str, default=None, help="result csv")
    parser.add_argument("--width", "-w", type=int, help="new width frame")
    parser.add_argument("--height", "-hgt", type=int, default=None, help="new height frame")
    return parser.parse_args()


args = vars(parse())
if not (
        args.get("video", False) 
        or args.get("csv", False)  
        or args.get("result", False) 
        or args.get("framescsv", False)
        or args.get("width", False)
    ):
    print("Нужно указать путь к исходным файлам. Параметр --video, --csv, --framescsv, --result, --width, --height.")
else: 
    scaler = Scaler(args["video"], args["csv"], args["framescsv"], args["result"], args["width"], args["height"])
    scaler.run()
