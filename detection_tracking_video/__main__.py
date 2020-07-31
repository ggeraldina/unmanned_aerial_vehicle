import argparse

from .auto_tracker import AutoTracker


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--video", type=str, help="path to input video file"
    )
    parser.add_argument(
        "-t", "--tracker", type=str, default="kcf", help="OpenCV object tracker type"
    )
    return parser.parse_args()


args = vars(parse())
if not args.get("video", False):
    print("Нужно указать путь к видео. Параметр -v или --video.")
else:
    tracker = AutoTracker(args["video"], args["tracker"])
    tracker.run()
