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
    parser.add_argument(
        "-sv", "--saving_videos", type=bool, default=False, help="saving video"
    )
    return parser.parse_args()


args = vars(parse())
if not args.get("video", False):
    print("Нужно указать путь к видео. Параметр -v или --video.")
else:
    tracker = AutoTracker(args["video"], args["tracker"], args["saving_videos"])
    tracker.run()
